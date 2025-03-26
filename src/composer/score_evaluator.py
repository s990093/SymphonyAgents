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

class Feedback(BaseModel):
    target: str = Field(..., description="樂器名稱")
    message: str = Field(..., description="建議內容")

class EvaluationResult(BaseModel):
    passed: bool = Field(..., description="是否通過評估")
    feedback: List[Feedback] = Field(..., description="反饋列表")
    
__all__ = ['ScoreEvaluator']

class ScoreEvaluator:
    def __init__(self, llm):
        self.llm = llm
        self.console = Console()

    def evaluate_score(self, scores: dict, musicians: dict) -> dict:
        instruments_list = list(scores.keys())
        
        
        class DynamicEvaluationResult(EvaluationResult):
            @validator("feedback", each_item=True)
            def restrict_target(cls, fb):
                if fb.target not in instruments_list:
                    raise ValueError(f"Target '{fb.target}' 不在允許的樂器列表 {instruments_list} 中")
                return fb
        
        parser = PydanticOutputParser(pydantic_object=DynamicEvaluationResult)
        
        harmony_prompt = ChatPromptTemplate.from_template("""
        檢查以下樂譜的音樂性與和聲一致性：
        
        [樂譜數據]
        {score_json}
        
        [要求]
        - 只針對以下樂器進行評估：{instruments_list}
        - 檢查是否有明確的主題及其發展（避免單純音階或重複音型）。
        - 檢查和聲是否豐富（必須包含轉調、借用和弦或非功能和聲）。
        - 檢查是否有動態或表情變化（必須包含力度記號或表情術語）。
        - 確保音符數量足夠（至少8個音符）。
        - 提供具體建議，如果有問題。
        
        [評估標準]
        - 如果任何樂器聲部缺乏明確的主題發展、和聲單調或無動態/表情變化，設置 "passed" 為 false。
        - 只有當所有聲部都滿足以上要求時，"passed" 才為 true。
        
        [輸出格式]
        返回一個 JSON 對象，遵循以下結構：
        {format_instructions}
        其中 "target" 必須是 {instruments_list} 中的一個樂器名稱，不允許其他值。
        """)
        
        score_json = {inst: musicians[inst]._part_to_json(part) for inst, part in scores.items()}
        chain = harmony_prompt | self.llm | parser
        try:
            evaluation = chain.invoke({
                "score_json": json.dumps(score_json, ensure_ascii=False),
                "instruments_list": ", ".join(instruments_list),
                "format_instructions": parser.get_format_instructions()
            })
        except Exception as e:
            self.console.print(f"[red]解析錯誤：{str(e)}[/red]")
            evaluation = {"passed": False, "feedback": []}
        
        # 轉換為字典
        evaluation_dict = evaluation.dict() if hasattr(evaluation, "dict") else evaluation
        
        # 額外檢查音符數量並根據反饋調整 passed
        for inst, part in scores.items():
            note_count = len(part.flatten().notesAndRests)
            if note_count < 8:
                evaluation_dict["passed"] = False
                evaluation_dict["feedback"].append({
                    "target": inst,
                    "message": f"{inst.capitalize()} 聲部音符數 ({note_count}) 過少，請增加至至少 8 個音符。"
                })
        
        # 根據反饋內容進一步檢查 passed
        for fb in evaluation_dict["feedback"]:
            message = fb["message"].lower()
            critical_issues = [
                "缺乏明確的主題", "和聲單調", "無動態", "無表情變化",
                "缺乏旋律性", "過於單調", "缺乏和聲變化"
            ]
            if any(issue in message for issue in critical_issues):
                evaluation_dict["passed"] = False
        
        self.console.print(evaluation_dict)
        return evaluation_dict