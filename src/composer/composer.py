# 標準庫導入
import json

# 第三方庫導入
from music21 import *
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from rich import box

# LangChain 相關
from langchain_google_genai import ChatGoogleGenerativeAI

# 內部模組導入
# Composer 相關模組
from src.composer.composition_planner import CompositionPlanner
from src.composer.instruction_generator import InstructionGenerator
from src.composer.music_theory_database import MusicTheoryDatabase
from src.composer.score_evaluator import ScoreEvaluator
from src.composer.style_analyzer import StyleAnalyzer

# 音樂相關模組
from src.music.agent import *
from src.music.music_player import MusicPlayer

# 工具模組
from src.tool import save_to_temp, load_from_temp

class ConductorAgent:
    STAGES = [
        "design_framework",       
        "plan_composition",       
        "generate_instructions",  
        "generate_scores",         
        "evaluate_and_revise"      
    ]
    
    def __init__(self, style: str = "classical",
                 tempo: int = 120, key: str = "C major", 
                 time_signature: str = "4/4", 
                 num_measures: int = 4,
                 musescore_path: str = "/Applications/MuseScore 4.app/Contents/MacOS/mscore",
                 api_provider: str = "gemini",  # 可選 "openai" 或 "gemini"
                 api_key: str = None,
                 temperature: float = 0.7,
                 top_p: float = 0.9):
        
        self.api_provider = api_provider
        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        
        # 初始化選擇的 LLM
        if api_provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                temperature=self.temperature, top_p=self.top_p, api_key= self.api_key)
        elif api_provider == "openai":
            if not api_key:
                
                raise ValueError("OpenAI 需要提供 API 金鑰")
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(api_key=api_key, top_p=self.top_p , temperature=self.temperature)
        else:
            raise ValueError("不支援的 API 提供者，請選擇 'gemini' 或 'openai'")
        
        
        self.player = MusicPlayer(musescore_path=musescore_path)
        self.params = {
            "style": style,
            "tempo": tempo,
            "key": key,
            "time_signature": time_signature,
            "num_measures": num_measures,
            "structure": {},
            "instruments": []
        }
        
        
        self.musicians = {
            "violin": ViolinAgent("Violinist",api_provider=api_provider, api_key=api_key,),
            "viola": ViolaAgent("Violaist", api_provider=api_provider, api_key=api_key,),
            "cello": CelloAgent("Cellist", api_provider=api_provider, api_key=api_key,),
            "flute": FluteAgent("Flutist", api_provider=api_provider, api_key=api_key,),
            "clarinet": ClarinetAgent("Clarinetist", api_provider=api_provider,api_key=api_key, ),
            "trumpet": TrumpetAgent("Trumpeter", api_provider=api_provider, api_key=api_key,),
            "timpani": TimpaniAgent("Timpanist", api_provider=api_provider, api_key=api_key,),
            "paino": PianistAgent("Pianist", api_provider=api_provider, api_key=api_key,)
        }
        self.score_drafts = {}
        self.instructions = {}
        
        # 初始化輔助類
        self.style_analyzer = StyleAnalyzer(style)
        self.theory_db = MusicTheoryDatabase()
        self.composition_planner = CompositionPlanner(self.llm, self.params, self.style_analyzer, self.theory_db)
        self.instruction_generator = InstructionGenerator(self.llm, self.params, self.musicians)
        self.score_evaluator = ScoreEvaluator(self.llm)

    def add_instrument(self, instrument_type: str, role: str):
        if instrument_type not in self.musicians:
            raise ValueError(f"Unsupported instrument: {instrument_type}")
        self.params["instruments"].append(instrument_type)

    def compose(self, output_file: str = "symphony", dev_mode: bool = False, start_from: str = None) -> dict:
        console = Console()
        STAGES = ["design_framework", "plan_composition", "generate_instructions", "generate_scores", "evaluate_and_revise"]

        # 如果啟用了開發模式並指定了起始階段，嘗試加載之前的結果
        if dev_mode and start_from:
            for stage in STAGES:
                if stage == start_from:
                    break
                loaded_data = load_from_temp(stage)
                if loaded_data:
                    console.print(Panel(
                        f"已載入 [bold cyan]{stage}[/bold cyan]...",
                        border_style="green",
                        padding=(0, 1)
                    ))
                    if stage == "design_framework":
                        self.params["structure"] = loaded_data
                    elif stage == "plan_composition":
                        self.params["plan"] = loaded_data
                    elif stage == "generate_instructions":
                        self.instructions = loaded_data
                    elif stage == "generate_scores":
                        self.score_drafts = loaded_data
                else:
                    console.print(f"[red]錯誤：無法找到 {stage} 的臨時文件[/red]")
                    return {}

        # 階段 1：設計框架
        if not dev_mode or start_from == "design_framework":
            framework = self.composition_planner.design_framework()
            self.params["structure"] = framework
            if dev_mode:
                save_to_temp("design_framework", framework)  # 保存結果
            
            # 生成音樂結構，使用 Panel 展示理由
            console.print(Panel(
                f"[bold]結構選擇理由:[/bold]\n{framework['rationale']}",
                title="[bold green]🎼 生成音樂結構[/bold green]",
                border_style="yellow",
                padding=(0, 1)
            ))
        elif "structure" in self.params and dev_mode:
            console.print(Panel(
                f"載入 [bold cyan]design_framework[/bold cyan] 所以 pass 通過",
                border_style="green",
                padding=(0, 1)
            ))

        # 階段 2：作曲計畫
        if not dev_mode or start_from in ["design_framework", "plan_composition"]:
            plan = self.composition_planner.plan_composition()
            self.params["plan"] = plan
            if dev_mode:
                save_to_temp("plan_composition", plan)  # 保存結果
            
            # 使用 Table 展示作曲計畫
            table = Table(box=box.SIMPLE, border_style="yellow")
            table.add_column("項目", style="bold", justify="left")
            table.add_column("內容", justify="left")
            table.add_row("Overall Structure", plan["overall_structure"])
            table.add_row("Harmony and Dynamics", plan["harmonic_and_dynamic_plan"])
            # 內嵌子 Table 展示樂器角色
            instrument_table = Table(box=box.SIMPLE)
            instrument_table.add_column("樂器", justify="left")
            instrument_table.add_column("角色", justify="left")
            for inst, role in plan["instrument_roles"].items():
                instrument_table.add_row(inst, role)
            table.add_row("Instrument Roles", str(instrument_table))
            
            console.print(Panel(
                table,
                title="[bold green]🤔 指揮家作曲計畫[/bold green]",
                border_style="yellow",
                padding=(0, 1)
            ))
        elif "plan" in self.params and dev_mode:
            console.print(Panel(
                f"載入 [bold cyan]plan_composition[/bold cyan] 所以 pass 通過",
                border_style="green",
                padding=(0, 1)
            ))

        # 階段 3：生成聲部指令
        if not dev_mode or start_from in ["design_framework", "plan_composition", "generate_instructions"]:
            self.instructions = self.instruction_generator.generate_part_instructions()
            if dev_mode:
                save_to_temp("generate_instructions", self.instructions)  # 保存結果
            
            # 展示各聲部演奏指令
            console.print(Panel(
                "[bold blue]🎻 各聲部演奏指令[/bold blue]",
                title="[bold green]🎻 各聲部演奏指令[/bold green]",
                border_style="yellow",
                padding=(0, 1)
            ))
            # 以 Violin 為例展示一個聲部指令
            for inst, inst_instructions in self.instructions.items():
                inst_table = Table(box=box.SIMPLE)
                inst_table.add_column("類別", style="bold", justify="left")
                inst_table.add_column("內容", justify="left")
                for key, value in inst_instructions.items():
                    inst_table.add_row(key, str(value))
                console.print(Panel(
                    inst_table,
                    title=f"{inst.capitalize()}",
                    border_style="yellow",
                    padding=(0, 1)
                ))
                break  # 只展示一個作為範例
        elif self.instructions and dev_mode:
            console.print(Panel(
                f"載入 [bold cyan]generate_instructions[/bold cyan] 所以 pass 通過",
                border_style="green",
                padding=(0, 1)
            ))

        # 階段 4：生成樂譜草案
        if not dev_mode or start_from in ["design_framework", "plan_composition", "generate_instructions", "generate_scores"]:
            console.print("[bold yellow]🎼 開始生成樂譜草案...[/bold yellow]")
            
            # 使用 rich 的 Progress 來顯示進度條
            from rich.progress import Progress
            with Progress(console=console) as progress:
                task = progress.add_task("[cyan]生成樂譜中...", total=len(self.musicians))
                for inst, agent in self.musicians.items():
                    self.score_drafts[inst] = agent.generate_score(self.params, self.instructions[inst])
                    progress.update(task, advance=1)  # 每次完成一個樂器，更新進度
                
            if dev_mode:
                save_to_temp("generate_scores", self.score_drafts)  # 保存結果
            console.print(f"[bold green]✅ 所有樂譜草案生成完成！共 {len(self.musicians)} 個聲部[/bold green]")
            
            
        elif self.score_drafts and dev_mode:
            console.print(Panel(
                f"載入 [bold cyan]generate_scores[/bold cyan] 所以 pass 通過",
                border_style="green",
                padding=(0, 1)
            ))

        # # 階段 5：評估與修正
        # if not dev_mode or start_from in ["design_framework", "plan_composition", "generate_instructions", "generate_scores", "evaluate_and_revise"]:
        #     evaluation = self.score_evaluator.evaluate_score(self.score_drafts, self.musicians)
        #     attempt = 1
        #     while not evaluation["passed"]:
        #         console.print(f"[bold yellow]⚠️ 樂譜需要修正 (嘗試 {attempt})[/bold yellow]")
        #         for feedback in evaluation["feedback"]:
        #             target_inst = feedback["target"]
        #             if target_inst in self.musicians:
        #                 console.log(f"正在修正 -> {target_inst}")
        #                 self.score_drafts[target_inst] = self.musicians[target_inst].revise_score(
        #                     self.params, feedback, self.score_drafts[target_inst]
        #                 )
        #             else:
        #                 console.print(f"[yellow]忽略無效目標 '{target_inst}' 的反饋[/yellow]")
                
        #         # 先生成 MIDI 文件
        #         midi_file = f"fixup_song_{attempt}"
        #         self.player.generate_midi(self.score_drafts, midi_file)
        #         console.print(f"[bold cyan]已生成 MIDI 文件：{midi_file}.mid[/bold cyan]")
                
        #         # 詢問用戶是否繼續修正
        #         continue_fixing = Confirm.ask("請檢查生成的 MIDI 文件。你想繼續修正樂譜嗎？", default=True)
        #         if not continue_fixing:
        #             console.print("[bold green]用戶選擇停止修正，當前版本已保存。[/bold green]")
        #             break
                
        #         # 如果繼續，重新評估
        #         evaluation = self.score_evaluator.evaluate_score(self.score_drafts, self.musicians)
        #         attempt += 1
            
        #     # 最終通過或用戶停止時顯示訊息
        #     if evaluation["passed"]:
        #         console.print("[bold green]🎉 樂譜最終版本通過審核！[/bold green]")
        #     else:
        #         console.print("[yellow]修正流程已終止，未完全通過審核。[/yellow]")

        return self.score_drafts