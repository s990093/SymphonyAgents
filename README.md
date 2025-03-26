# SymphonyAgents

SymphonyAgents 是一個 AI 驅動的交響樂創作系統，旨在自動生成多風格的音樂作品，從古典到現代，並支持即時協作和動態調整。

## 目錄

1. [系統概述](#系統概述)
2. [核心功能](#核心功能)
3. [使用指南](#使用指南)
4. [API 端點](#api-端點)
5. [音樂知識庫](#音樂知識庫)
6. [異常處理機制](#異常處理機制)
7. [效能優化](#效能優化)
8. [進階應用場景](#進階應用場景)

## 系統概述

### 設計目標

SymphonyAgents 的設計目標是提供一個靈活且強大的平台，能夠根據用戶輸入的參數自動生成不同風格的音樂作品。系統支持多種音樂風格，包括古典、爵士和電子音樂，並能生成相應的音樂結構和效果配置。

### 實際參數傳遞範例

以下是系統接受的參數配置示例：

```python
composition_params = {
    "metadata": {
        "title": "月光幻想曲",
        "composer": "AI-Maestro/1.0",
        "opus": "Op.3 No.2"
    },
    "structure": {
        "form": "sonata",
        "movements": [
            {"tempo": 92, "key": "c# minor", "mood": "dramatic"},
            {"tempo": 68, "key": "E major", "mood": "lyrical"},
            {"tempo": 120, "key": "a minor", "mood": "agitato"}
        ]
    },
    "instrumentation": {
        "strings": {
            "violin": {"section_size": 12, "role": "melody"},
            "cello": {"section_size": 8, "role": "bassline"}
        },
        "woodwinds": {
            "flute": {"solo_passages": [45, 89]}
        }
    }
}
```

## 核心功能

### 指揮家 Agent 決策流程

- 處理參數優先級和衝突
- 生成時間軸模板
- 自動添加即興段落標記（適用於爵士風格）

### 樂器 Agent 參數處理

- 支持多種技術參數和動態範圍設置
- 提供旋律變化規則和裝飾音頻率控制

## 使用指南

1. 初始化 Composer 類別，設置風格、速度、調性等參數。
2. 添加樂器並指定其角色。
3. 調用 `compose` 方法生成樂譜。

## API 端點

### 進階創作接口

- `POST /v2/compose`：接受 JSON 格式的創作參數，返回生成的樂譜和演奏指令。

### 即時協作接口

- `WS /ws/collaborate`：支持即時動態調整和協作創作。

## 音樂知識庫

- 提供風格特徵矩陣和樂器資料庫，支持多種音樂風格和樂器特性。

## 異常處理機制

- 自動檢測和解決參數衝突
- 提供錯誤代碼和處理建議

## 效能優化

- 使用預處理快取機制加速和聲模板生成
- 分散式生成架構提高系統響應速度

## 進階應用場景

- 支持即時演出系統整合，適用於現場音樂會和電影配樂創作。
