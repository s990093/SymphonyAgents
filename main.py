"""
SymphonyAgents Main Script
用於初始化和運行音樂生成系統

此腳本提供了一個完整的音樂生成流程，包括：
1. 環境設置和API配置
2. 樂器配置和初始化
3. 音樂生成
4. 音頻輸出和播放
"""

import os
from dotenv import load_dotenv
from music21 import *

# 內部模組導入
from src.music.music_player import MusicPlayer
from src.composer.composer import ConductorAgent

# 常量定義
COMPOSITION_STAGES = [
    "design_framework",      # 設計音樂結構
    "plan_composition",      # 生成作曲計畫
    "generate_instructions", # 生成聲部指令
    "generate_scores",       # 生成樂譜草案
    "evaluate_and_revise"    # 評估與修正
]

# 默認音樂參數設置
DEFAULT_PARAMS = {
    "style": "classical",    # 音樂風格：古典
    "tempo": 120,           # 速度：120拍/分鐘
    "key": "C major",       # 調性：C大調
    "time_signature": "4/4", # 拍號：4/4
    "num_measures": 4       # 小節數：4
}

# 樂器配置
INSTRUMENT_CONFIG = [
    {"name": "violin", "role": "melody"},     # 小提琴：主旋律
    {"name": "viola", "role": "harmony"},     # 中提琴：和聲
    {"name": "cello", "role": "bass"},        # 大提琴：低音
    {"name": "flute", "role": "melody"},      # 長笛：主旋律
    {"name": "clarinet", "role": "harmony"},  # 單簧管：和聲
    {"name": "trumpet", "role": "highlight"}, # 小號：重點段落
    {"name": "timpani", "role": "rhythm"}     # 定音鼓：節奏
]

def main():
    """
    主程序入口
    
    執行步驟：
    1. 載入環境變數
    2. 初始化指揮家代理
    3. 配置樂器
    4. 生成音樂
    5. 輸出並播放
    """
    # 載入環境變數
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")  # 可選擇 OPENAI_API_KEY 或 GOOGLE_API_KEY
    
    # 檢查 API 金鑰
    if not api_key:
        raise ValueError("未找到 API 金鑰，請確認 .env 文件設置正確")
    
    # 初始化指揮家代理
    conductor = ConductorAgent(
        **DEFAULT_PARAMS,
        api_provider="openai",  # 可選 "openai" 或 "gemini"
        api_key=api_key,
        temperature=0.6,        # 控制創意度
        top_p=0.9 ,             # 控制多樣性
        musescore_path="/Applications/MuseScore 4.app/Contents/MacOS/mscore"
    )
    
    # 配置樂器
    for instrument in INSTRUMENT_CONFIG:
        conductor.add_instrument(
            instrument["name"],
            instrument["role"]
        )
    
    # 生成音樂
    score_drafts = conductor.compose(
        dev_mode=True,          # 開啟開發模式，顯示詳細信息
        start_from="evaluate_and_revise"  # 從框架設計開始
    )
    
    # 初始化音樂播放器
    player = MusicPlayer(musescore_path="/Applications/MuseScore 4.app/Contents/MacOS/mscore")

    # 生成並播放音樂
    midi_path = player.generate_mp3(score_drafts, "my_song")
    if midi_path:
        player.load_file(midi_path)
        player.play()
        player.save("my_song_converted", format="musicxml")

if __name__ == "__main__":
    main()