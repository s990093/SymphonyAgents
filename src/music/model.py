from pydantic import BaseModel, Field, validator
from typing import Dict, List, Tuple

# 已有的模型（假設已定義）
class NoteData(BaseModel):
    pitch: str = Field(description="Pitch in MIDI notation, e.g., 'C4' or 'rest'")
    duration: float = Field(description="Duration in quarter note units, e.g., 1.0 for a quarter note")
    technique: str = Field(description="Playing technique, e.g., 'arco' or 'pizz'")

class PartData(BaseModel):
    notes: List[NoteData] = Field(description="List of notes in the part")
    clef: str = Field(description="Clef type, e.g., 'treble' or 'bass'")
    instrument: str = Field(description="Instrument name, e.g., 'Violin'")

# 為 revise_score 的輸入定義新模型
class FeedbackItem(BaseModel):
    target: str = Field(description="The target instrument name, e.g., 'violin'")
    message: str = Field(description="Detailed feedback message from the conductor")

class ReviseInput(BaseModel):
    global_params: Dict = Field(description="Global parameters including style, tempo, key, etc.")
    feedback: FeedbackItem = Field(description="Feedback from the conductor with target and message")
    
# 為 _retry_generate 的輸入定義新模型
class RetryInput(BaseModel):
    error_message: str = Field(description="Error message from the previous generation attempt")
    original_data: Dict = Field(description="Original score data that failed, in JSON-compatible dictionary format")
    
class Note(BaseModel):
    pitch: str = Field(..., description="音高，使用 MIDI 表示法（如 'C4'）")
    duration: float = Field(..., description="時值，以四分音符為單位（如 1.0 表示四分音符）")
    technique: str = Field(..., description="演奏技巧")

    @validator("duration")
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("時值必須大於 0")
        return v

class ScoreData(BaseModel):
    notes: List[Note] = Field(..., description="音符列表")
    clef: str = Field(..., description="譜號，如 'treble' 或 'bass'")
    instrument: str = Field(..., description="樂器名稱")

    @validator("notes")
    def notes_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("音符列表不能為空")
        return v
    