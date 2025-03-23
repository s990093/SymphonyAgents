import os
import json
from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from music21 import stream, midi, environment


# 初始化音乐环境
env = environment.Environment()
env['musicxmlPath'] = '/usr/bin/musescore'
env['musescoreDirectPNGPath'] = '/usr/bin/musescore'
os.environ["GOOGLE_API_KEY"] = "AIzaSyCCjszxRvE87Pep8w5LkikhxnCNOH2aMQY"

class ConductorAgent:
    """指挥家核心代理"""
    def __init__(self, style: str = "classical", tempo: int = 120, key: str = "C major"):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
        self.params = {
            "style": style,
            "tempo": tempo,
            "key": key,
            "structure": {},
            "instruments": []
        }
        self.musicians = {}
        self.score_drafts = {}
        
    def add_instrument(self, instrument_type: str, role: str):
        """添加乐器代理"""
        instrument_map = {
            "piano": PianistAgent,
            "violin": ViolinistAgent,
            "cello": CellistAgent
        }
        if instrument_type not in instrument_map:
            raise ValueError(f"Unsupported instrument: {instrument_type}")
        self.musicians[instrument_type] = instrument_map[instrument_type](role)
        self.params["instruments"].append(instrument_type)
        
    def design_framework(self) -> Dict:
        """生成音乐结构框架"""
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """您是一位专业交响乐指挥家，请根据以下参数设计音乐结构：
              风格：{style}
              速度：{tempo} BPM
              调性：{key}
              包含乐器：{instruments}
              请以JSON格式返回包含以下字段的结构：
              - form (曲式类型)
              - harmonic_progression (和声进行)
              - instrumentation_roles (各乐器角色)
              - dynamic_plan (动态变化计划)""")
        ])
        chain = prompt_template | self.llm
        result = chain.invoke(self.params)
        self.params["structure"] = json.loads(result.content)
        return self.params["structure"]
    
    def generate_part_instructions(self) -> Dict:
        """生成各声部详细指令"""
        instructions = {}
        for inst, agent in self.musicians.items():
            role_desc = self.params["structure"]["instrumentation_roles"].get(inst, "")
            prompt = f"""根据总谱结构生成{inst}声部指令：
            总结构：{json.dumps(self.params['structure'], ensure_ascii=False)}
            乐器角色：{role_desc}
            请包含：
            - 主要旋律出现位置
            - 与其它声部的配合点
            - 技术难点提示
            用JSON格式返回："""
            response = self.llm.invoke(prompt)
            instructions[inst] = json.loads(response.content)
        return instructions
    
    def evaluate_score(self, scores: Dict) -> Dict:
        """结构化乐谱评估"""
        rubric = {
            "harmonic_consistency": 0.3,
            "dynamic_balance": 0.25,
            "style_compliance": 0.2,
            "technical_feasibility": 0.25
        }
        
        evaluation = {"passed": False, "feedback": []}
        total_score = 0
        
        # 和声一致性检查
        harmony_check = self.llm.invoke(f"""检查以下乐谱的和声一致性：
        {json.dumps(scores)}
        参考和声进行：{self.params['structure']['harmonic_progression']}
        返回JSON：{{"score":0-1, "issues":[...]}}""")
        harmony_result = json.loads(harmony_check.content)
        total_score += harmony_result["score"] * rubric["harmonic_consistency"]
        evaluation["feedback"].extend(harmony_result["issues"])
        
        # 动态平衡检查
        balance_check = self.llm.invoke(f"""分析声部动态平衡：
        {json.dumps(scores)}
        预期动态计划：{self.params['structure']['dynamic_plan']}
        返回JSON：{{"score":0-1, "adjustments":[...]}}""")
        balance_result = json.loads(balance_check.content)
        total_score += balance_result["score"] * rubric["dynamic_balance"]
        evaluation["feedback"].extend(balance_result["adjustments"])
        
        evaluation["passed"] = total_score >= 0.75
        return evaluation
    
    def compose(self, output_file: str = "symphony") -> str:
        """完整创作流程"""
        # 生成结构框架
        framework = self.design_framework()
        print(f"🎼 生成音乐结构：{framework}")
        
        # 生成各声部指令
        instructions = self.generate_part_instructions()
        
        # 各声部生成乐谱
        for inst, agent in self.musicians.items():
            self.score_drafts[inst] = agent.generate_score(
                self.params, 
                instructions[inst]
            )
        
        # 审核与修正循环
        evaluation = self.evaluate_score(self.score_drafts)
        while not evaluation["passed"]:
            print("⚠️ 乐谱需要修正：")
            for feedback in evaluation["feedback"]:
                target_inst = feedback["target"]
                print(f"→ {target_inst}: {feedback['message']}")
                revised = self.musicians[target_inst].revise_score(
                    self.params,
                    feedback
                )
                self.score_drafts[target_inst] = revised
            evaluation = self.evaluate_score(self.score_drafts)
        
        # 混音输出
        return self._render_audio(output_file)
    
    def _render_audio(self, filename: str) -> str:
        """生成音频文件"""
        score = stream.Score()
        for part in self.score_drafts.values():
            score.append(part.to_music21())
        
        # 导出MIDI
        midi_path = f"{filename}.mid"
        mf = midi.translate.streamToMidiFile(score)
        mf.open(midi_path, 'wb')
        mf.write()
        mf.close()
        
        # 转换为MP3
        mp3_path = f"{filename}.mp3"
        os.system(f'fluidsynth -ni /usr/share/soundfonts/FluidR3_GM.sf2 {midi_path} -F temp.wav')
        os.system(f'ffmpeg -i temp.wav -acodec libmp3lame {mp3_path}')
        
        return mp3_path

class MusicianAgent:
    """乐器代理基类"""
    
    def __init__(self, role: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.5)
        self.role = role
        self.part = None
        
    def generate_score(self, global_params: Dict, instruction: Dict) -> 'Part':
        """生成乐谱（需子类实现）"""
        raise NotImplementedError
        
    def revise_score(self, global_params: Dict, feedback: Dict) -> 'Part':
        """修正乐谱"""
        prompt = f"""根据指挥家反馈修改乐谱：
        原乐谱：{self.part}
        反馈意见：{feedback['message']}
        修改要求：{feedback.get('instruction', '')}
        请输出修订后的乐谱："""
        revised = self.llm.invoke(prompt)
        return self._parse_score(revised.content)
    
    def _parse_score(self, text: str) -> stream.Part:
        """将文本乐谱转换为music21对象"""
        # 简化的ABC记谱法解析
        from music21 import converter
        return converter.parse(text, format='abc')

class CellistAgent(MusicianAgent):
    """大提琴声部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> stream.Part:
        prompt = ChatPromptTemplate.from_template("""
        作为{role}演奏家，请创作大提琴声部：
        - 风格：{style}
        - 速度：{tempo}BPM
        - 调性：{key}
        - 结构指令：{instruction}
        请用ABC记谱法输出包含：
        - 主要旋律或低音线条
        - 技术要求（如拨弦、泛音等）
        """)
        chain = prompt | self.llm
        response = chain.invoke({
            "role": self.role,
            **global_params,
            "instruction": json.dumps(instruction)
        })
        self.part = self._parse_score(response.content)
        return self.part
class PianistAgent(MusicianAgent):
    """钢琴声部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> stream.Part:
        prompt = ChatPromptTemplate.from_template("""
        作为{role}演奏家，请创作符合以下要求的钢琴声部：
        - 风格：{style}
        - 速度：{tempo}BPM
        - 调性：{key}
        - 结构指令：{instruction}
        请用ABC记谱法输出包含：
        - 右手旋律声部
        - 左手伴奏声部
        """)
        chain = prompt | self.llm
        response = chain.invoke({
            "role": self.role,
            **global_params,
            "instruction": json.dumps(instruction)
        })
        self.part = self._parse_score(response.content)
        return self.part

class ViolinistAgent(MusicianAgent):
    """小提琴声部代理"""
    
    def generate_score(self, global_params: Dict, instruction: Dict) -> stream.Part:
        prompt = ChatPromptTemplate.from_template("""
        作为{role}演奏家，请创作小提琴声部：
        - 使用{key}调性
        - 主要技术：{techniques}
        - 结构角色：{instruction}
        输出要求：
        - 包含弓法标记
        - 标明揉弦位置
        - ABC记谱格式
        """)
        chain = prompt | self.llm
        response = chain.invoke({
            "role": self.role,
            **global_params,
            "techniques": "连奏与跳弓结合",
            "instruction": json.dumps(instruction)
        })
        self.part = self._parse_score(response.content)
        return self.part





# 使用示例
if __name__ == "__main__":
    # 初始化指挥家
    conductor = ConductorAgent(
        style="romantic",
        tempo=92,
        key="c minor"
    )
    