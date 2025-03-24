# 標準函式庫
import json
from typing import Dict, List, Tuple
from music21 import *

# 第三方函式庫

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

# Pydantic 資料驗證
from pydantic import BaseModel, Field

# 音樂相關
from music21 import stream  # 樂譜處理

import traceback
from rich.console import Console
from rich.panel import Panel

__all__ = [
    'NoteData',
    'PartData',
    'MusicianAgent',
    'ViolinAgent',
    'ViolaAgent',
    'CelloAgent',
    'ClarinetAgent',
    'FluteAgent',
    'TrumpetAgent',
    'TimpaniAgent'
]

# 定義音樂數據的 Pydantic 模型
class NoteData(BaseModel):
    pitch: str = Field(description="音高，例如 'C4' 或 'G3'")
    duration: float = Field(description="音符時長（以四分音符為單位），例如 1.0（四分音符）、2.0（二分音符）、4.0（全音符）")
    technique: str = Field(default="arco", description="演奏技巧，例如 'arco'（拉弓）或 'pizz'（撥弦）")

class PartData(BaseModel):
    notes: List[NoteData] = Field(description="音符列表")
    clef: str = Field(description="譜號，例如 'treble' 或 'bass'")
    instrument: str = Field(description="樂器名稱，例如 'Cello' 或 'Piano RH'")

class MusicianAgent:
    """樂器代理基類，支援多種樂器及其特性"""
    
    def __init__(self, role: str, instrument_name: str, default_clef: str, techniques: List[str], pitch_range: Tuple[str, str]):
        """
        初始化樂器代理。
        
        參數：
        - role: 樂器的角色（例如 "melody", "harmony"）
        - instrument_name: 樂器名稱（例如 "Violin", "Flute"）
        - default_clef: 預設譜號（例如 "treble", "bass", "alto"）
        - techniques: 支援的演奏技巧列表（例如 ["arco", "pizz"]）
        - pitch_range: 音域範圍（例如 ("G3", "E6")）
        """
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
        self.role = role
        self.instrument_name = instrument_name
        self.default_clef = default_clef
        self.techniques = techniques
        self.pitch_range = pitch_range  # (最低音高, 最高音高)
        self.part = None
        self.max_retries = 3

    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        """生成樂譜，具體實現由子類提供"""
        raise NotImplementedError

    def revise_score(self, global_params: Dict, feedback: Dict) -> 'stream.Part':
        """根據指揮家反饋修改樂譜"""
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
        """)
        
        parser = JsonOutputParser()  # 假設 PartData 已定義為 Pydantic 模型
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "score": json.dumps(self._part_to_json(self.part)),
            "feedback": feedback['message'],
            "clef": self.default_clef,
            "instrument": self.instrument_name,
            "technique": self.techniques[0],  # 預設使用第一個技巧
            "min_pitch": self.pitch_range[0],
            "max_pitch": self.pitch_range[1],
            "techniques": ", ".join(self.techniques)
        })
        self.part = self._json_to_part(response)
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
            if retries < self.max_retries:
                console.print(f"[yellow]重試第 {retries + 1} 次...[/yellow]")
                revised_response = self._retry_generate(response, error_message)
                return self._parse_score(revised_response, retries + 1)
            else:
                raise RuntimeError(f"達到最大重試次數 {self.max_retries}，無法生成有效的樂譜。")
    

    def _retry_generate(self, original_data: Dict, error_message: str) -> Dict:
        """重試生成樂譜"""
        retry_prompt = ChatPromptTemplate.from_template("""
        之前的樂譜生成失敗，錯誤信息如下：
        {error_message}
        
        原始樂譜數據：
        {original_data}
        
        請修正並重新生成有效的 JSON 格式樂譜，符合以下結構：
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "{technique}"}},
                ...
            ],
            "clef": "{clef}",
            "instrument": "{instrument}"
        }}
        
        [修正要求]
        - pitch 使用 MIDI 音高表示法，音域為 {min_pitch} 到 {max_pitch}
        - duration 以四分音符為單位
        - technique 可為 {techniques}
        - 確保音高在樂器音域內
        """)
        
        parser = JsonOutputParser()
        chain = retry_prompt | self.llm | parser
        response = chain.invoke({
            "error_message": error_message,
            "original_data": json.dumps(original_data),
            "clef": self.default_clef,
            "instrument": self.instrument_name,
            "technique": self.techniques[0],
            "min_pitch": self.pitch_range[0],
            "max_pitch": self.pitch_range[1],
            "techniques": ", ".join(self.techniques)
        })
        return response

"""提琴聲部代理"""

class ViolinAgent(MusicianAgent):
    """小提琴聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Viola",
            default_clef="alto",
            techniques=["arco", "pizz"],
            pitch_range=("C3", "A5")
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作小提琴聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與撥弦
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "G3", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "A3", "duration": 2.0, "technique": "pizz"}},
                ...
            ],
            "clef": "treble",
            "instrument": "Violin"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 G3 到 E6
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符）
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part
    
class ViolaAgent(MusicianAgent):
    """中提琴聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Viola",
            default_clef="alto",
            techniques=["arco", "pizz"],
            pitch_range=("C3", "A5")
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作中提琴聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與撥弦
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C3", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "D3", "duration": 2.0, "technique": "pizz"}},
                ...
            ],
            "clef": "alto",
            "instrument": "Viola"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C3 到 A5
        - duration 以四分音符為單位
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part
    
class CelloAgent(MusicianAgent):
    """大提琴聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Cello",
            default_clef="bass",
            techniques=["arco", "pizz"],
            pitch_range=("C2", "A3")
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作大提琴聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與撥弦
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C2", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "G2", "duration": 2.0, "technique": "pizz"}},
                ...
            ],
            "clef": "bass",
            "instrument": "Cello"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C2 到 A3
        - duration 以四分音符為單位
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part
    
class ClarinetAgent(MusicianAgent):
    """單簧管聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Clarinet",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("E3", "C7")
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作單簧管聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與跳舌
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "E3", "duration": 1.0, "technique": "slur"}},
                {{"pitch": "F3", "duration": 2.0, "technique": "tongued"}},
                ...
            ],
            "clef": "treble",
            "instrument": "Clarinet"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 E3 到 C7
        - duration 以四分音符為單位
        - technique 可為 'slur'（連奏）或 'tongued'（跳舌）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part    
    
"""笛聲部代理"""
    
class FluteAgent(MusicianAgent):
    """長笛聲部代理"""
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Flute",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("C4", "C7")
        )
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作長笛聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與跳舌
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "slur"}},
                {{"pitch": "D4", "duration": 2.0, "technique": "tongued"}},
                ...
            ],
            "clef": "treble",
            "instrument": "Flute"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C4 到 C7
        - duration 以四分音符為單位
        - technique 可為 'slur'（連奏）或 'tongued'（跳舌）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part


class TrumpetAgent(MusicianAgent):
    """小號聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Trumpet",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("F#3", "C6")
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作小號聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：連奏與跳舌
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "F#3", "duration": 1.0, "technique": "slur"}},
                {{"pitch": "G3", "duration": 2.0, "technique": "tongued"}},
                ...
            ],
            "clef": "treble",
            "instrument": "Trumpet"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 F#3 到 C6
        - duration 以四分音符為單位
        - technique 可為 'slur'（連奏）或 'tongued'（跳舌）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part
    
    
class TimpaniAgent(MusicianAgent):
    """定音鼓聲部代理"""
    
    def __init__(self, role: str):
        super().__init__(
            role=role,
            instrument_name="Timpani",
            default_clef="bass",
            techniques=["roll", "strike"],
            pitch_range=("C2", "C4")
        )
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作定音鼓聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：滾奏與單擊
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C2", "duration": 1.0, "technique": "roll"}},
                {{"pitch": "G2", "duration": 2.0, "technique": "strike"}},
                ...
            ],
            "clef": "bass",
            "instrument": "Timpani"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C2 到 C4
        - duration 以四分音符為單位
        - technique 可為 'roll'（滾奏）或 'strike'（單擊）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part





"""old"""

class CellistAgent(MusicianAgent):
    """大提琴聲部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作大提琴聲部，並以 JSON 格式輸出：
        
        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}
        技術重點：{techniques}
        
        [指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C2", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "E2", "duration": 1.0, "technique": "pizz"}},
                ...
            ],
            "clef": "bass",
            "instrument": "Cello"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C2 到 A3
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符，4.0 = 全音符）
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        
        [示例]
        {{
            "notes": [
                {{"pitch": "C2", "duration": 2.0, "technique": "arco"}},
                {{"pitch": "E2", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "G2", "duration": 1.0, "technique": "pizz"}},
                {{"pitch": "D3", "duration": 2.0, "technique": "arco"}}
            ],
            "clef": "bass",
            "instrument": "Cello"
        }}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "techniques": "持續低音與撥奏交替",
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part

class PianistAgent(MusicianAgent):
    """鋼琴聲部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作鋼琴聲部，並以 JSON 格式輸出：
        
        [創作參數]
        風格：{style}
        調性：{key}
        速度：{tempo}
        拍號：{time_signature}
        
        [結構要求]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "E4 G4", "duration": 2.0, "technique": "arco"}},
                ...
            ],
            "clef": "treble",  # 右手用高音譜號，左手用低音譜號
            "instrument": "Piano"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，右手音域為 C4 到 C6，左手音域為 C2 到 C4
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符，4.0 = 全音符）
        - technique 可為 'arco'（正常演奏），這裡僅作為佔位符，鋼琴無需特殊技巧
        - 和弦用空格分隔多個音高（例如 "C4 E4 G4"）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        
        [示例]
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "E4 G4", "duration": 2.0, "technique": "arco"}},
                {{"pitch": "D4", "duration": 1.0, "technique": "arco"}}
            ],
            "clef": "treble",
            "instrument": "Piano"
        }}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "key": global_params["key"],
            "tempo": global_params["tempo"],
            "time_signature": global_params["time_signature"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part

class ViolinistAgent(MusicianAgent):
    """小提琴聲部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作小提琴聲部，並以 JSON 格式輸出：
        
        [基本設置]
        拍號：{time_signature}
        調性：{key}
        
        [技術參數]
        - 音域：G3到E6
        - 技術要求：連奏與跳弓結合
        
        [創作指令]
        {instruction}
        
        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "G3", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "A3", "duration": 2.0, "technique": "pizz"}},
                ...
            ],
            "clef": "treble",
            "instrument": "Violin"
        }}
        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 G3 到 E6
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符，4.0 = 全音符）
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        
        [示例]
        {{
            "notes": [
                {{"pitch": "G3", "duration": 2.0, "technique": "arco"}},
                {{"pitch": "A3", "duration": 1.0, "technique": "pizz"}},
                {{"pitch": "B3", "duration": 1.0, "technique": "arco"}}
            ],
            "clef": "treble",
            "instrument": "Violin"
        }}
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "time_signature": global_params["time_signature"],
            "key": global_params["key"],
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part