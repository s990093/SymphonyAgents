# 標準函式庫
import json
from typing import Dict
from music21 import *
from src.music.model import PartData

# 第三方函式庫

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


# Pydantic 資料驗證
# 音樂相關
from music21 import stream  # 樂譜處理

from rich.console import Console

from src.music.musician_agent import MusicianAgent

__all__ = [
    'ViolinAgent',
    'ViolaAgent',
    'CelloAgent',
    'ClarinetAgent',
    'FluteAgent',
    'TrumpetAgent',
    'TimpaniAgent',
    'PianistAgent'
]
console = Console()

"""提琴聲部代理"""

class ViolinAgent(MusicianAgent):
    """
    小提琴聲部代理

    Attributes:
        role (str): 演奏者的角色。
        api_provider (str): API 提供者，例如 "openai" 或 "google"。
        api_key (str): API 金鑰。
    """
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        """
        初始化 ViolinAgent 實例。

        Args:
            role (str): 演奏者的角色，例如 "Violinist"。
            api_provider (str): API 提供者名稱。
            api_key (str): API 驗證金鑰。
        """
        super().__init__(
            role=role,
            instrument_name="Violin",
            default_clef="treble",
            techniques=["arco", "pizz"],
            pitch_range=("G3", "E6"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請確保旋律具有起承轉合的結構，避免單純的音階重複
        """)
        
        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser 
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "instruction": instruction.get("instruction", "")
        })
        self.part = self._parse_score(response)
        return self.part
    
class ViolaAgent(MusicianAgent):
    """中提琴聲部代理"""
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Viola",
            default_clef="alto",
            techniques=["arco", "pizz"],
            pitch_range=("C3", "A5"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請確保旋律具有起承轉合的結構，避免單純的音階重複
        """)

        # 從 instruction 中獲取主題、和聲和動態信息，若無則使用默認值
        theme_description = instruction.get("theme", "請創作一個具有特色的旋律動機")
        harmonic_progression = instruction.get("harmonic_progression", "自由和聲進行")
        dynamic_plan = instruction.get("dynamic_plan", "自由動態變化")

        parser = JsonOutputParser(pydantic_object=PartData)
        chain = prompt | self.llm | parser
        response = chain.invoke({
            "role": self.role,
            "style": global_params["style"],
            "tempo": global_params["tempo"],
            "key": global_params["key"],
            "time_signature": global_params["time_signature"],
            "theme_description": theme_description,
            "harmonic_progression": harmonic_progression,
            "dynamic_plan": dynamic_plan,
            "instruction": json.dumps(instruction, ensure_ascii=False)
        })
        self.part = self._parse_score(response)
        return self.part
    
    
class CelloAgent(MusicianAgent):
    """大提琴聲部代理"""
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Cello",
            default_clef="bass",
            techniques=["arco", "pizz"],
            pitch_range=("C2", "A3"),
            api_provider=api_provider,
            api_key=api_key
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
        請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
        {{
            "notes": [
                {{"pitch": "C2", "duration": 1.0, "technique": "arco"}},
                {{"pitch": "G2", "duration": 2.0, "technique": "pizz"}},
                ...
            ],
            "clef": "bass",
            "instrument": "Cello"
        }}
        
        請嚴格依照此格式生成輸出，且不要包含任何註解或其他非 JSON 文本。

        
        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 C2 到 A3
        - duration 以四分音符為單位
        - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
        - 可使用 "rest" 表示休止符
        - 總時長應符合拍號 {time_signature}
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
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
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Clarinet",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("E3", "C7"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
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
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Flute",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("C4", "C7"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
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
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Trumpet",
            default_clef="treble",
            techniques=["slur", "tongued"],
            pitch_range=("F#3", "C6"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
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
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Timpani",
            default_clef="bass",
            techniques=["roll", "strike"],
            pitch_range=("C2", "C4"),
            api_provider=api_provider,
            api_key=api_key
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
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。
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
        - 請生成一個純粹的 JSON 對象，請勿包含任何註解或額外文字，輸出必須符合標準 JSON 格式。

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
    
    def __init__(self, role: str, api_provider: str, api_key: str):
        super().__init__(
            role=role,
            instrument_name="Piano",
            default_clef="both",
            techniques=[
                "legato", 
                "staccato", 
                "pedal",
                "chord",
                "arpeggio"
            ],
            pitch_range=("A0", "C8"),
            api_provider=api_provider,
            api_key=api_key
        )
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'stream.Part':
        """
        根據全局參數和指令生成鋼琴的樂譜。

        Args:
            global_params (Dict): 包含音樂創作的全局參數。
            instruction (Dict): 包含具體的創作指令。

        Returns:
            stream.Part: 生成的鋼琴樂譜部分。
        """
        prompt = ChatPromptTemplate.from_template("""
        作為{role}演奏家，請創作鋼琴聲部，並以 JSON 格式輸出：

        [參數]
        風格：{style}
        速度：{tempo}BPM
        調號：{key}
        拍號：{time_signature}

        [協調點]
        {coordination_points}

        [技術挑戰]
        {technical_challenges}

        [旋律位置]
        {melody_position}

        [指令]
        {instruction}

        [技術要求]
        - 注意左右手的配合與平衡
        - 和弦進行要符合和聲學原理
        - 適當使用踏板標記
        - 注意雙手交錯時的演奏可行性
        - 確保旋律線條清晰
        - 適當運用鋼琴的力度變化

        [輸出要求]
        生成一個 JSON 對象，結構如下：
        {{
            "notes": [
                {{"pitch": "C4", "duration": 1.0, "technique": "legato", "dynamic": "mf"}},
                {{"pitch": "E4,G4,C5", "duration": 2.0, "technique": "chord", "dynamic": "f"}},
                ...
            ],
            "clef": "both",
            "instrument": "Piano"
        }}

        [格式規則]
        - pitch 使用 MIDI 音高表示法，音域為 A0 到 C8
        - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符）
        - technique 可為 "legato", "staccato", "pedal", "chord", "arpeggio"
        - dynamic 可為 "pp", "p", "mp", "mf", "f", "ff"
        - 可使用 "rest" 表示休止符
        - 和弦使用逗號分隔的音高列表
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
            "instruction": instruction.get("instruction", ""),
            "coordination_points": instruction.get("coordination_points", ""),
            "technical_challenges": instruction.get("technical_challenges", ""),
            "melody_position": instruction.get("melody_position", "")
        })
        
        self.part = self._parse_score(response)
        return self.part

