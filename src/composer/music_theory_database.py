from src.composer.model import EvaluationResult

import json
from langchain_core.prompts import ChatPromptTemplate
from music21 import *
import json

# 第三方函式庫
from rich.console import Console  # 美化終端輸出

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
from rich.console import Console
from rich.console import Console
# Pydantic 資料驗證
from pydantic import BaseModel, Field, validator
from typing import List
from langchain.output_parsers import PydanticOutputParser

class MusicTheoryDatabase:
    def __init__(self):
        self.harmonic_progressions = {
            "classical": [
                {"name": "Authentic Cadence", "sequence": ["V", "I"], "usage": "终止式，强调调性"},
                {"name": "Plagal Cadence", "sequence": ["IV", "I"], "usage": "教会终止式"}
            ],
            "romantic": [
                {"name": "Chromatic Mediant", "sequence": ["I", "III"], "usage": "色彩性转调"},
                {"name": "Neapolitan Chord", "sequence": ["N6", "V"], "usage": "制造戏剧张力"}
            ]
        }
        self.form_analysis = {
            "sonata": {
                "structure": ["Exposition", "Development", "Recapitulation"],
                "tonal_plan": "主调→属调→关系调→主调",
                "classic_example": "莫札特第40號交響曲第一樂章"
            },
            "rondo": {
                "structure": ["A", "B", "A", "C", "A"],
                "tonal_plan": "主调持续回归",
                "classic_example": "貝多芬《悲愴》奏鳴曲第三樂章"
            }
        }

    def get_harmonic_options(self, style: str) -> list:
        return self.harmonic_progressions.get(style, [])

    def get_form_options(self) -> dict:
        return self.form_analysis
