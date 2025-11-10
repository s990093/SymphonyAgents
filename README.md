# SymphonyAgents

SymphonyAgents 是一個 AI 驅動的交響樂創作系統，能夠自動生成多種風格的音樂作品。


## 🎬 影片連結


[![觀看影片](https://img.youtube.com/vi/67LR4dmu2mM/0.jpg)](https://youtu.be/67LR4dmu2mM?si=l3j00ZA6khAr5tsj&t=52)


## 安裝要求

### 必要軟體

- Python 3.8+
- MuseScore 4.0+
- 虛擬環境工具 (推薦使用 conda 或 venv)

### 安裝步驟

1. 克隆專案：

```bash
git clone https://github.com/s990093/SymphonyAgents
cd SymphonyAgents
```

2. 創建並啟動虛擬環境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安裝依賴：

```bash
pip install -r requirements.txt
pytohn check.py
```

## 配置

1. 創建 `.env` 文件，添加 API 金鑰：

```env
OPENAI_API_KEY=your_openai_api_key
# 或
GOOGLE_API_KEY=your_google_api_key
```

2. 確保 MuseScore 已正確安裝，並設置正確的路徑：

- macOS: `/Applications/MuseScore 4.app/Contents/MacOS/mscore`
- Windows: `C:\Program Files\MuseScore 4\bin\MuseScore4.exe`
- Linux: 通常是 `musescore`

## 使用方法

### 基本使用

1. 運行主程序：

```bash
python main.py
```

### 自定義設置

1. 修改音樂參數：

   - 在 `main.py` 中的 `DEFAULT_PARAMS` 調整風格、速度等
   - 支持的風格：classical, romantic, baroque
   - 速度範圍：60-180 BPM
   - 調性選項：C major, G major 等

2. 調整樂器配置：
   - 在 `INSTRUMENT_CONFIG` 中添加或移除樂器
   - 可用角色：melody, harmony, bass, highlight, rhythm

### 輸出文件

- MIDI 文件：`my_song.mid`
- MP3 文件：`my_song.mp3`
- MusicXML 文件：`my_song_converted.musicxml`

## 故障排除

1. API 金鑰錯誤：

   - 確認 `.env` 文件存在且包含正確的金鑰
   - 檢查金鑰格式是否正確

2. MuseScore 相關問題：

   - 確認 MuseScore 已正確安裝
   - 檢查 MuseScore 路徑設置
   - 確保有適當的執行權限

3. 音頻輸出問題：
   - 檢查系統音頻設置
   - 確認 MuseScore 可以正常運行
   - 檢查輸出目錄的寫入權限

## 進階功能

- 開發模式：設置 `dev_mode=True` 查看詳細生成過程
- 自定義起始階段：使用 `start_from` 參數
- 調整創意參數：修改 `temperature` 和 `top_p` 值

## 貢獻指南

歡迎提交 Pull Requests 和 Issues！

## 授權

[您的授權信息]
