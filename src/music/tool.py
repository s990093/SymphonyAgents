# 標準函式庫
from music21 import *

# 第三方函式庫

# LangChain 相關

# Pydantic 資料驗證

# 音樂相關


import os
# tool.py
import os
import pickle



def generate_common_template(role: str, style: str, tempo: int, key: str, time_signature: str, 
                             instruction: str, part_name: str, clef: str, instrument: str, 
                             pitch_range: str, additional_rules: str, 
                             coordination_points: str = "", 
                             technical_challenges: str = "", 
                             melody_position: str = "") -> str:
    return f"""
    作為{role}演奏家，請創作{part_name}聲部，並以 JSON 格式輸出：

    [參數]
    風格：{style}
    速度：{tempo}BPM
    調號：{key}
    拍號：{time_signature}
    技術重點：連奏與撥弦

    [協調點]
    {coordination_points}

    [技術挑戰]
    {technical_challenges}

    [旋律位置]
    {melody_position}

    [指令]
    {instruction}

    [輸出要求]
    生成一個 JSON 對象，結構如下：
    {{
        "notes": [
            {{"pitch": "G3", "duration": 1.0, "technique": "arco"}},
            {{"pitch": "A3", "duration": 2.0, "technique": "pizz"}},
            ...
        ],
        "clef": "{clef}",
        "instrument": "{instrument}"
    }}

    [格式規則]
    - pitch 使用 MIDI 音高表示法，音域為 {pitch_range}
    - duration 以四分音符為單位（1.0 = 四分音符，2.0 = 二分音符）
    - technique 可為 'arco'（拉弓）或 'pizz'（撥弦）
    - 可使用 "rest" 表示休止符
    - 總時長應符合拍號 {time_signature}
    - 請確保旋律具有起承轉合的結構，避免單純的音階重複
    {additional_rules}
    """
    
    




# tool.py
import os
import pickle

TEMP_DIR = "temp"

def save_to_temp(stage: str, data: dict):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)  # 如果資料夾不存在，創建它
    with open(os.path.join(TEMP_DIR, f"{stage}.pkl"), "wb") as f:
        pickle.dump(data, f)

def load_from_temp(stage: str) -> dict:
    file_path = os.path.join(TEMP_DIR, f"{stage}.pkl")
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return pickle.load(f)
    return None