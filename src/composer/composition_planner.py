from src.composer.music_theory_database import MusicTheoryDatabase
from src.composer.style_analyzer import StyleAnalyzer
from src.composer.model import CompositionPlan

import json
from langchain_core.prompts import ChatPromptTemplate
from music21 import *
import json
from langchain_core.output_parsers import JsonOutputParser

# 第三方函式庫

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
# Pydantic 資料驗證

class CompositionPlanner:
    def __init__(self, llm, params: dict, style_analyzer: StyleAnalyzer, theory_db: MusicTheoryDatabase):
        self.llm = llm
        self.params = params
        self.style_analyzer = style_analyzer
        self.theory_db = theory_db

    def design_framework(self) -> dict:
        prompt_template = ChatPromptTemplate.from_messages([
            ("user", """您是一位{style}風格專家指揮家，請設計一個豐富的交響樂結構：

            [風格分析]
            {style_analysis}

            [音樂理論參考]
            和聲進行選項：{harmonic_options}
            曲式結構參考：{form_options}

            [創作參數]
            速度：{tempo} BPM
            調性：{key}
            拍子：{time_signature}
            小節數：{num_measures}
            樂器：{instruments}

            請設計包含以下元素的結構：
            - 曲式類型（如奏鳴曲式、迴旋曲式）
            - 主要主題（至少兩個有特色的旋律動機，描述其節奏與音高特徵）
            - 和聲進行（包括轉調、借用和弦等具體方案）
            - 動態與速度變化（具體規劃，如漸強、漸慢）
            - 聲部間的呼應與對話

            返回 JSON：
            {{
                "form": "曲式類型",
                "themes": ["主題1描述", "主題2描述"],
                "harmonic_progression": ["和聲進行1", "和聲進行2"],
                "dynamic_plan": "動態變化計劃",
                "instrumentation_roles": {{"樂器": "角色"}},
                "rationale": "設計理由"
            }}""")
        ])
        
        input_params = self.params.copy()
        input_params["style_analysis"] = self.style_analyzer.get_style_analysis()
        input_params["harmonic_options"] = json.dumps(self.theory_db.get_harmonic_options(self.params["style"]), ensure_ascii=False)
        input_params["form_options"] = json.dumps(self.theory_db.get_form_options(), ensure_ascii=False)
        input_params["instruments"] = ", ".join(self.params["instruments"])
        
        chain = prompt_template | self.llm | JsonOutputParser()
        result = chain.invoke(input_params)
        
        return result

    def plan_composition(self) -> dict:
        from pydantic import BaseModel

        parser = JsonOutputParser(pydantic_object=CompositionPlan)
        prompt_template = ChatPromptTemplate.from_messages([
            ("user", """作為指揮家，請思考如何根據以下參數創作一首交響樂：

            風格：{style}
            速度：{tempo} BPM
            調性：{key}
            拍子：{time_signature}
            小節數：{num_measures}
            包含樂器：{instruments}

            請直接返回一個有效的 JSON 物件，符合以下結構：
            - overall_structure (str): 整體結構安排，例如 "ABA form with an intro and coda"
            - instrument_roles (dict[str, str]): 各樂器角色和任務，例如 {{"piano": "main melody", "violin": "counterpoint"}}
            - harmonic_and_dynamic_plan (str): 和聲進行和動態變化的考慮，例如 "I-IV-V-I progression with crescendo in the middle"

            不要包含任何其他文字、格式、註釋或代碼塊。只返回純 JSON。""")
        ])
        
        chain = prompt_template | self.llm | parser
        input_params = self.params.copy()
        input_params["instruments"] = ", ".join(self.params["instruments"])
        plan = chain.invoke(input_params)
        return plan
