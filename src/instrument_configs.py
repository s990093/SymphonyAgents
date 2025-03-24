# 樂器參數映射表
from music21 import instrument


instrument_configs = {
    "piano": {
        "agent_class": "PianoAgent",
        "default_clef": "treble",  # 鋼琴通常使用高音譜號（右手），低音譜號（左手）需額外處理
        "techniques": ["normal"],  # 鋼琴無特殊技巧，統一為 "normal"
        "pitch_range": ("A0", "C8"),
        "music21_instrument": instrument.Piano()
    },
    "violin": {
        "agent_class": "ViolinAgent",
        "default_clef": "treble",
        "techniques": ["arco", "pizz"],
        "pitch_range": ("G3", "E6"),
        "music21_instrument": instrument.Violin()
    },
    "viola": {
        "agent_class": "ViolaAgent",
        "default_clef": "alto",
        "techniques": ["arco", "pizz"],
        "pitch_range": ("C3", "A5"),
        "music21_instrument": instrument.Viola()
    },
    "cello": {
        "agent_class": "CelloAgent",
        "default_clef": "bass",
        "techniques": ["arco", "pizz"],
        "pitch_range": ("C2", "A3"),
        "music21_instrument": instrument.Violoncello()
    },
    "flute": {
        "agent_class": "FluteAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("C4", "C7"),
        "music21_instrument": instrument.Flute()
    },
    "clarinet": {
        "agent_class": "ClarinetAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("E3", "C7"),
        "music21_instrument": instrument.Clarinet()
    },
    "trumpet": {
        "agent_class": "TrumpetAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("F#3", "C6"),
        "music21_instrument": instrument.Trumpet()
    },
    "timpani": {
        "agent_class": "TimpaniAgent",
        "default_clef": "bass",
        "techniques": ["roll", "strike"],
        "pitch_range": ("C2", "C4"),
        "music21_instrument": instrument.Timpani()
    },
    "double bass": {
        "agent_class": "DoubleBassAgent",
        "default_clef": "bass",
        "techniques": ["arco", "pizz"],
        "pitch_range": ("E2", "G4"),
        "music21_instrument": instrument.Contrabass()
    },
    "oboe": {
        "agent_class": "OboeAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("Bb3", "G6"),
        "music21_instrument": instrument.Oboe()
    },
    "bassoon": {
        "agent_class": "BassoonAgent",
        "default_clef": "bass",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("Bb1", "Eb5"),
        "music21_instrument": instrument.Bassoon()
    },
    "horn": {
        "agent_class": "HornAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("F2", "C6"),
        "music21_instrument": instrument.Horn()
    },
    "trombone": {
        "agent_class": "TromboneAgent",
        "default_clef": "bass",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("E2", "Bb4"),
        "music21_instrument": instrument.Trombone()
    },
    "tuba": {
        "agent_class": "TubaAgent",
        "default_clef": "bass",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("D1", "F4"),
        "music21_instrument": instrument.Tuba()
    },
    "harp": {
        "agent_class": "HarpAgent",
        "default_clef": "treble",  # 豎琴通常使用雙譜表，這裡簡化為高音譜號
        "techniques": ["pluck"],
        "pitch_range": ("Cb1", "G#7"),
        "music21_instrument": instrument.Harp()
    },
    "percussion": {
        "agent_class": "PercussionAgent",
        "default_clef": "percussion",  # 使用打擊樂專用譜號
        "techniques": ["strike"],
        "pitch_range": ("C4", "C4"),  # 打擊樂器音高不固定，這裡簡化處理
        "music21_instrument": instrument.Percussion()
    },
    "saxophone": {
        "agent_class": "SaxophoneAgent",
        "default_clef": "treble",
        "techniques": ["slur", "tongued"],
        "pitch_range": ("Bb3", "F6"),  # 以中音薩克斯風為例
        "music21_instrument": instrument.Saxophone()
    }
}