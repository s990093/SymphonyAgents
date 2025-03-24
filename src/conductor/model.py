# 標準函式庫
import time
from datetime import datetime
import json
from typing import Dict, List
from rich.progress import track

# 第三方函式庫
from rich.console import Console  # 美化終端輸出
from rich.table import Table  # 表格顯示
from rich.panel import Panel  # 面板顯示
from rich.progress import Progress  # 進度條功能
from rich.live import Live  # 即時更新顯示
from rich.style import Style  # 樣式控制
from rich.text import Text  # 文字格式化
from rich.json import JSON  # JSON 格式化顯示

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

# Pydantic 資料驗證
from pydantic import BaseModel, Field

# 音樂相關
from music21 import stream, instrument  # 樂譜處理


__all__ = [
    'MusicStructure',
    'CompositionPlan',
    'PartInstruction',
    'PartInstruction',
    'FeedbackItem',
    'EvaluationResult',
]
# 定義 Pydantic 模型來表示音樂結構
class MusicStructure(BaseModel):
    form: str = Field(description="曲式類型，例如 'Sonata' 或 'Theme and Variation'")
    harmonic_progression: List[str] = Field(description="和聲進行，例如 ['I', 'IV', 'V', 'I']")
    instrumentation_roles: Dict[str, str] = Field(description="各樂器角色，例如 {'piano': 'melody', 'violin': 'harmony'}")
    dynamic_plan: str = Field(description="動態變化計劃，例如 'crescendo from pp to ff over 4 measures'")

class CompositionPlan(BaseModel):
    overall_structure: str = Field(description="整體結構安排，例如 'ABA form with an intro and coda'")
    instrument_roles: Dict[str, str] = Field(description="各樂器角色和任務，例如 {'piano': 'main melody', 'violin': 'counterpoint'}")
    harmonic_and_dynamic_plan: str = Field(description="和聲進行和動態變化的考慮，例如 'I-IV-V-I progression with crescendo in the middle'")

class PartInstruction(BaseModel):
    melody_position: str = Field(description="主要旋律出現位置，例如 'measures 1-2' 或 'entire piece'")
    coordination_points: List[str] = Field(description="與其它聲部的配合點，例如 ['align with piano at measure 3', 'support violin at measure 5']")
    technical_challenges: List[str] = Field(description="技術難點提示，例如 ['rapid arpeggios in measure 4', 'high register sustain']")

class FeedbackItem(BaseModel):
    target: str = Field(description="目標樂器，例如 'cello'、'piano' 或 'violin'")
    message: str = Field(description="建議內容，例如 'Cello 聲部音符數過少'")

class EvaluationResult(BaseModel):
    passed: bool = Field(description="是否通過評估，true 表示通過，false 表示需要修正")
    feedback: List[FeedbackItem] = Field(description="反饋列表，每項包含目標樂器和建議內容")
    