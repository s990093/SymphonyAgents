"""
SymphonyAgents Main Script
用於初始化和運行音樂生成系統
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

DEFAULT_PARAMS = {
    "style": "classical",
    "tempo": 120,
    "key": "C major",
    "time_signature": "4/4",
    "num_measures": 4
}

INSTRUMENT_CONFIG = [
    {"name": "violin", "role": "melody"},
    {"name": "viola", "role": "harmony"},
    {"name": "cello", "role": "bass"},
    {"name": "flute", "role": "melody"},
    {"name": "clarinet", "role": "harmony"},
    {"name": "trumpet", "role": "highlight"},
    {"name": "timpani", "role": "rhythm"}
]



def main():
    """
    主程序入口
    """
    load_dotenv()
    
    # TODO: 可以修掉 GOOGLE_API_KEY or OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")

    
    # 設置環境
    if not api_key:
        raise ValueError("未找到 API 金鑰，請確認 .env 文件設置正確")
    
    # 初始化指揮家
    # openai or gemini 
    #TODO: gemini 效果比較好
    conductor = ConductorAgent(
        **DEFAULT_PARAMS,
        api_provider="openai",
        api_key=api_key,
        temperature=0.6,
        top_p=0.9
    )
    
    # 添加樂器
    for instrument in INSTRUMENT_CONFIG:
        conductor.add_instrument(
            instrument["name"],
            instrument["role"]
        )
    

    # 開始作曲過程
    score_drafts = conductor.compose(
        dev_mode=True,
        start_from="design_framework"
    )
    
    # 初始化播放器
    player = MusicPlayer(musescore_path="/Applications/MuseScore 4.app/Contents/MacOS/mscore")

    # 生成 MIDI
    midi_path = player.generate_mp3(score_drafts, "my_song")
    if midi_path:
        # 載入剛生成的 MIDI
        player.load_file(midi_path)
        # 播放
        player.play()
        # 儲存為 MusicXML
        player.save("my_song_converted", format="musicxml")
    
if __name__ == "__main__":
    main()