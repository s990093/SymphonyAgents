from langgraph.graph import StateGraph, END
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from music21 import stream

# 定義狀態
class MusicState(Dict[str, Any]):
    pass

# 初始化 LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

# 定義代理函數
def style_analysis_node(state: MusicState) -> MusicState:
    agent = StyleAnalyzerAgent(llm)
    state["style_analysis"] = agent.analyze(state["params"]["style"])
    return state

def form_design_node(state: MusicState) -> MusicState:
    agent = FormDesignerAgent(llm)
    state["structure"] = agent.design(state["style_analysis"], state["params"])
    return state

def score_generation_node(state: MusicState) -> MusicState:
    agent = ScoreGeneratorAgent(llm)
    state["scores"] = agent.generate(state["instructions"], state["harmony"], state["structure"])
    return state

# 構建工作流程圖
graph = StateGraph(MusicState)
graph.add_node("start", lambda state: state)
graph.add_node("style_analysis", style_analysis_node)
graph.add_node("form_design", form_design_node)
graph.add_node("harmony_planning", lambda state: state) 
graph.add_node("instruction_generation", lambda state: state)
graph.add_node("score_generation", score_generation_node)
graph.add_node("evaluation", lambda state: state)
graph.add_node("end", lambda state: state)

# 定義邊
graph.set_entry_point("start")
graph.add_edge("start", "style_analysis")
graph.add_edge("style_analysis", "form_design")
graph.add_edge("form_design", "harmony_planning")
graph.add_edge("harmony_planning", "instruction_generation")
graph.add_edge("instruction_generation", "score_generation")
graph.add_edge("score_generation", "evaluation")
graph.add_conditional_edges("evaluation", lambda state: "score_generation" if not state["passed"] else "end")

# 編譯並運行
app = graph.compile()
initial_state = MusicState({"params": {"style": "classical", "tempo": 120, "key": "C major"}})
result = app.invoke(initial_state)
print(result["scores"])