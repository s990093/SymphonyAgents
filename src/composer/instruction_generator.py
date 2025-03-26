
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from music21 import *
import json

# 第三方函式庫

# LangChain 相關
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from rich.progress import Progress
from rich.progress import Progress
# Pydantic 資料驗證

from src.composer.model import PartInstruction

# Pydantic 資料驗證
class InstructionGenerator:
    def __init__(self, llm, params: dict, musicians: dict):
        self.llm = llm
        self.params = params
        self.musicians = musicians

    def generate_part_instructions(self) -> dict:

        instructions = {}
        parser = JsonOutputParser(pydantic_object=PartInstruction)
        prompt_template = ChatPromptTemplate.from_messages([
            ("user", """根據總譜結構生成{instrument}聲部指令：

            總結構：{structure}
            樂器角色：{role_desc}

            請直接返回一個有效的 JSON 物件，符合以下結構：
            - melody_position (str): 主要旋律出現位置，例如 "measures 1-2" 或 "entire piece"
            - coordination_points (list[str]): 與其它聲部的配合點，例如 ["align with piano at measure 3", "support violin at measure 5"]
            - technical_challenges (list[str]): 技術難點提示，例如 ["rapid arpeggios in measure 4", "high register sustain"]

            不要包含任何其他文字、格式、註釋或代碼塊。只返回純 JSON。""")
        ])
        
        chain = prompt_template | self.llm | parser

        with Progress() as progress:
            task = progress.add_task("[cyan]生成樂器指令...", total=len(self.musicians))
            for inst, agent in self.musicians.items():
                role_desc = self.params["structure"]["instrumentation_roles"].get(inst, "")
                input_params = {
                    "instrument": inst,
                    "structure": json.dumps(self.params["structure"], ensure_ascii=False),
                    "role_desc": role_desc
                }
                try:
                    instructions[inst] = chain.invoke(input_params)
                    progress.update(task, advance=1, description=f"[green]已完成: {inst}")
                except Exception as e:
                    progress.update(task, advance=1, description=f"[red]錯誤: {inst} - {str(e)}")
                    print(f"生成 {inst} 指令失敗：{str(e)}")
        return instructions
    
