from src.music.model import PartData, RetryInput, ScoreData


from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from music21 import articulations, chord, clef, key, meter, note, pitch, stream
from rich.console import Console
from rich.panel import Panel


import json
import traceback
from typing import Dict, List, Tuple

console = Console()

class MusicianAgent:
    """樂器代理基類，支援多種樂器及其特性"""

    def __init__(self, role: str, instrument_name: str, default_clef: str, 
                 techniques: List[str], pitch_range: Tuple[str, str], 
                 api_provider: str = "gemini", api_key: str = None,
                 temperature: float = 0.6, top_p: float = 0.9, 
                 max_retries: int = 3):     
        
        self.api_provider = api_provider
        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        
        # 初始化選擇的 LLM
        if api_provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                temperature=self.temperature, top_p=self.top_p, api_key=api_key)
        elif api_provider == "openai":
            if not api_key:
                
                raise ValueError("OpenAI 需要提供 API 金鑰")
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(api_key=api_key, top_p=self.top_p , temperature=self.temperature)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
        self.role = role
        self.instrument_name = instrument_name
        self.default_clef = default_clef
        self.techniques = techniques
        self.pitch_range = pitch_range  # (最低音高, 最高音高)
        self.part = None
        self.max_retries = max_retries

    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        """生成樂譜，具體實現由子類提供"""
        raise NotImplementedError

    def revise_score(self, global_params: Dict, feedback: Dict, part: 'stream.Part') -> 'stream.Part':
        """根據指揮家反饋修改樂譜"""
        # 定義提示詞
        prompt = ChatPromptTemplate.from_template("""
        根據指揮家反饋修改樂譜：
        
        [原始樂譜]
        {score}
        
        [反饋意見]
        {feedback}
        
        [輸出要求]
        請生成一個 JSON 格式的樂譜，符合以下結構：
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "{technique}"}},
                ...
            ],
            "clef": "{clef}",
            "instrument": "{instrument}"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 {min_pitch} 到 {max_pitch}
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符，4.0 = 全音符）
        - technique 可為 {techniques}
        - 確保音高在樂器音域內
        - 只返回純 JSON，不要包含其他文字或註釋
        """)

        # 使用 Pydantic 模型的 JsonOutputParser
        parser = JsonOutputParser(pydantic_object=ScoreData)
        chain = prompt | self.llm | parser

        # 準備輸入數據
        input_data = {
            "score": json.dumps(self._part_to_json(part)),
            "feedback": feedback['message'],
            "clef": self.default_clef,
            "instrument": self.instrument_name,
            "technique": self.techniques[0],  # 預設使用第一個技巧
            "min_pitch": self.pitch_range[0],
            "max_pitch": self.pitch_range[1],
            "techniques": ", ".join(self.techniques)
        }

        # 調用 LLM 並解析結果
        try:
            response = chain.invoke(input_data)
            # console.print("[bold cyan]LLM 回傳的 JSON:[/bold cyan]")
            # console.print(response)
        except Exception as e:
            console.print(f"[red]解析錯誤：{str(e)}[/red]")
            raise ValueError("LLM 回傳的 JSON 無效，無法生成樂譜")

        # 將 JSON 轉換為 Part 對象
        self.part = self._json_to_part(response)
        if self.part is None:
            console.print("[red]錯誤：_json_to_part 返回 None，無法生成有效 Part 對象[/red]")
            raise ValueError("無法根據 LLM 回傳生成樂譜")

        return self.part

    def _part_to_json(self, part: 'stream.Part') -> Dict:
        """將 music21 Part 轉換為 JSON"""
        notes_data = []
        for element in part.flat.notesAndRests:
            if isinstance(element, note.Note):
                technique = self._get_technique(element)
                notes_data.append({
                    "pitch": element.pitch.nameWithOctave,
                    "duration": float(element.quarterLength),
                    "technique": technique
                })
            elif isinstance(element, note.Rest):
                notes_data.append({"pitch": "rest", "duration": float(element.quarterLength), "technique": "none"})
            elif isinstance(element, chord.Chord):
                pitches = [p.nameWithOctave for p in element.pitches]
                technique = self._get_technique(element)
                notes_data.append({
                    "pitch": " ".join(pitches),
                    "duration": float(element.quarterLength),
                    "technique": technique
                })
        return {
            "notes": notes_data,
            "clef": part.clef.sign if part.clef else self.default_clef,
            "instrument": self.instrument_name
        }

    def _get_technique(self, element) -> str:
        """根據樂器支持的技巧獲取音符或和弦的演奏技巧"""
        for art in element.articulations:
            if isinstance(art, articulations.Pizzicato) and "pizz" in self.techniques:
                return "pizz"
            # 可根據需要擴展其他技巧的判斷邏輯
        return self.techniques[0]  # 預設使用第一個技巧

    def _json_to_part(self, data: Dict) -> 'stream.Part':
        """將 JSON 轉換為 music21 Part"""
        part = stream.Part()
        part.insert(0, meter.TimeSignature("4/4"))  # 預設拍號
        part.insert(0, key.KeySignature(0))  # 預設 C 大調


        # 設置譜號
        if data["clef"].lower() == "bass":
            part.insert(0, clef.BassClef())
        elif data["clef"].lower() == "alto":
            part.insert(0, clef.AltoClef())
        elif data["clef"].lower() == "treble":
            part.insert(0, clef.TrebleClef())
        else:
            part.insert(0, clef.TrebleClef())  # 預設高音譜號

        # 添加音符並檢查音域
        min_pitch = pitch.Pitch(self.pitch_range[0])
        max_pitch = pitch.Pitch(self.pitch_range[1])
        for note_data in data["notes"]:
            if note_data["pitch"] == "rest":
                part.append(note.Rest(quarterLength=note_data["duration"]))
            elif " " in note_data["pitch"]:
                pitches = note_data["pitch"].split()
                if all(min_pitch <= pitch.Pitch(p) <= max_pitch for p in pitches):
                    ch = chord.Chord(pitches, quarterLength=note_data["duration"])
                    if note_data["technique"] in self.techniques:
                        self._apply_technique(ch, note_data["technique"])
                    part.append(ch)
                else:
                    print(f"警告：和弦 {pitches} 超出 {self.instrument_name} 的音域 {self.pitch_range}")
            else:
                p = pitch.Pitch(note_data["pitch"])
                if min_pitch <= p <= max_pitch:
                    n = note.Note(note_data["pitch"], quarterLength=note_data["duration"])
                    if note_data["technique"] in self.techniques:
                        self._apply_technique(n, note_data["technique"])
                    part.append(n)
                else:
                    print(f"警告：音高 {note_data['pitch']} 超出 {self.instrument_name} 的音域 {self.pitch_range}")
        return part

    def _apply_technique(self, element, technique: str):
        """根據演奏技巧應用相應的標記"""
        if technique == "pizz" and "pizz" in self.techniques:
            element.articulations.append(articulations.Pizzicato())
        # 可根據需要擴展其他技巧的應用，例如 "slur", "roll" 等

    def _parse_score(self, response: dict, retries: int = 0) -> 'stream.Part':
        """解析並驗證生成的樂譜"""
        console = Console()
        try:
            return self._json_to_part(response)
        except Exception as e:
            error_message = str(e)
            # 取得完整的 traceback 資訊
            tb_info = traceback.format_exc()
            # 使用 Rich Panel 輸出錯誤資訊與 traceback，讓錯誤追蹤更加美觀
            console.print(
                Panel(
                    f"[bold red]解析樂譜失敗[/bold red]：{error_message}\n\n[dim]{tb_info}[/dim]",
                    title="[red]錯誤追蹤[/red]",
                    border_style="red"
                )
            )
            console.print(Panel(f"[cyan]Response Data:[/cyan]\n{response}", title="📜 Response", border_style="blue"))

            if retries < self.max_retries:
                console.print(f"[yellow]重試第 {retries + 1} 次...[/yellow]")
                revised_response = self._retry_generate(response, error_message)
                return self._parse_score(revised_response, retries + 1)
            else:
                raise RuntimeError(f"達到最大重試次數 {self.max_retries}，無法生成有效的樂譜。")


    def _retry_generate(self, original_data: Dict, error_message: str) -> Dict:
        # 使用 Pydantic 驗證輸入數據
        retry_input = RetryInput(
            error_message=error_message,
            original_data=original_data
        )

        # 定義重試提示模板，轉義不需要動態填充的大括號
        retry_prompt = ChatPromptTemplate.from_template("""
        The previous score generation failed with the following error:
        {error_message}

        Original score data:
        {original_data}

        Please correct and regenerate a valid JSON-formatted score with the following structure:
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "{technique}"}},
                ...
            ],
            "clef": "{clef}",
            "instrument": "{instrument}"
        }}

        [Correction Requirements]
        - Use MIDI pitch notation (e.g., 'C4', 'rest'), within the range {min_pitch} to {max_pitch}.
        - Duration must be in quarter note units (e.g., 1.0 for a quarter note, 2.0 for a half note).
        - Technique must be one of: {techniques}.
        - Ensure all pitches are within the instrument's range.
        - Address the specific issue mentioned in the error message.
        """)

        # 使用 Pydantic 解析器驗證輸出
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = retry_prompt | self.llm | parser

        # 傳遞參數並執行重試生成
        response = chain.invoke({
            "error_message": retry_input.error_message,
            "original_data": json.dumps(retry_input.original_data, ensure_ascii=False),
            "clef": self.default_clef,
            "instrument": self.instrument_name,
            "technique": self.techniques[0],  # 預設使用第一個技巧
            "min_pitch": self.pitch_range[0],
            "max_pitch": self.pitch_range[1],
            "techniques": ", ".join(self.techniques)
        })

        # 返回驗證後的結果
        return response