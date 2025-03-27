from music21 import *
from music21 import instrument

# 創建樂器聲部
violin = stream.Part()
violin.id = 'Violin'
violin.insert(0, instrument.Violin())  # 確保 instrument 是 music21 的模組

viola = stream.Part()
viola.id = 'Viola'
viola.insert(0, instrument.Viola())

cello = stream.Part()
cello.id = 'Cello'
cello.insert(0, instrument.Violoncello())

flute = stream.Part()
flute.id = 'Flute'
flute.insert(0, instrument.Flute())

clarinet = stream.Part()
clarinet.id = 'Clarinet'
clarinet.insert(0, instrument.Clarinet())

trumpet = stream.Part()
trumpet.id = 'Trumpet'
trumpet.insert(0, instrument.Trumpet())

timpani = stream.Part()
timpani.id = 'Timpani'
timpani.insert(0, instrument.Timpani())

piano = stream.Part()
piano.id = 'Piano'

piano.insert(0, instrument.Piano())

# 主題1：C大調上行級進，節奏 0.5-1.0-0.5-1.0
theme1_notes = ['C4', 'D4', 'E4', 'F4', 'G4']
theme1_durations = [0.5, 1.0, 0.5, 1.0, 1.0]

# 主題2：G大調下行琶音，節奏 1.0
theme2_notes = ['G4', 'D4', 'G4', 'E4', 'C4']
theme2_durations = [1.0, 1.0, 1.0, 1.0, 1.0]


# 呈示部 - 小提琴（主題1和主題2，重複兩次）
for _ in range(2):
    for note_name, dur in zip(theme1_notes, theme1_durations):
        n = note.Note(note_name, quarterLength=dur)
        n.volume.velocity = 80  # 中強 (mf)
        violin.append(n)
    for note_name, dur in zip(theme2_notes, theme2_durations):
        n = note.Note(note_name, quarterLength=dur)
        n.volume.velocity = 60  # 中弱 (mp)
        violin.append(n)

# 呈示部 - 中提琴（和聲支持）
viola_notes = ['E4', 'G4', 'C5', 'B4', 'G4', 'D5'] * 2
viola_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0] * 2
for note_name, dur in zip(viola_notes, viola_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 70  # 中間力度
    viola.append(n)

# 呈示部 - 大提琴（低音線條）
cello_notes = ['C2', 'G2', 'C3', 'G2', 'D3', 'G3'] * 2
cello_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0] * 2
for note_name, dur in zip(cello_notes, cello_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 80  # 中強 (mf)
    cello.append(n)

# 呈示部 - 長笛（高音裝飾）
flute_notes = ['G5', 'A5', 'B5', 'C6', 'G5', 'D5', 'G5', 'E5', 'C5'] * 2
flute_durations = [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0] * 2
for note_name, dur in zip(flute_notes, flute_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 60  # 中弱 (mp)
    flute.append(n)

# 呈示部 - 單簧管（中音和聲填充）
clarinet_notes = ['E4', 'F4', 'G4', 'B4', 'A4', 'G4'] * 2
clarinet_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0] * 2
for note_name, dur in zip(clarinet_notes, clarinet_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 70
    clarinet.append(n)

# 呈示部 - 小號（強調力度，在主題1結尾）
trumpet_notes = ['G4', 'C5', 'G4'] * 2
trumpet_durations = [1.0, 1.0, 1.0] * 2
for note_name, dur in zip(trumpet_notes, trumpet_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 90  # 強 (f)
    trumpet.append(n)

# 呈示部 - 定音鼓（節奏骨架）
timpani_notes = ['C2', 'G2', 'C2', 'G2'] * 2
timpani_durations = [1.0, 1.0, 1.0, 1.0] * 2
for note_name, dur in zip(timpani_notes, timpani_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 80
    timpani.append(n)

# 呈示部 - 鋼琴（和弦伴奏）
piano_chords = [chord.Chord(['C4', 'E4', 'G4']), chord.Chord(['G4', 'B4', 'D5'])] * 2
piano_durations = [2.0, 2.0] * 2
for ch, dur in zip(piano_chords, piano_durations):
    ch.quarterLength = dur
    ch.volume.velocity = 70
    piano.append(ch)
    
    
# 發展部 - 小提琴（主題1片段轉調）
dev_notes_violin = ['A4', 'B4', 'C#5', 'D5', 'F5', 'G5', 'A5', 'B5', 'D5', 'E5', 'F#5', 'G5'] * 2
dev_durations_violin = [0.5, 1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 1.0] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_violin, dev_durations_violin)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5  # 從弱 (p) 到極強 (ff)
    violin.append(n)

# 發展部 - 中提琴（對位）
dev_notes_viola = ['C5', 'D5', 'E5', 'F#5', 'A4', 'B4', 'D5', 'G5'] * 2
dev_durations_viola = [0.5, 1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 1.0] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_viola, dev_durations_viola)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5
    viola.append(n)

# 發展部 - 大提琴（低音進行）
dev_notes_cello = ['G2', 'A2', 'E3', 'D3'] * 2
dev_durations_cello = [1.0, 1.0, 1.0, 1.0] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_cello, dev_durations_cello)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 10
    cello.append(n)

# 發展部 - 長笛（快速音群）
dev_notes_flute = ['A5', 'B5', 'C#6', 'D6', 'F6', 'G6', 'E6', 'D6'] * 2
dev_durations_flute = [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_flute, dev_durations_flute)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5
    flute.append(n)

# 發展部 - 單簧管（中音對位）
dev_notes_clarinet = ['C5', 'D5', 'E5', 'F#5', 'A4', 'B4', 'D5', 'G5'] * 2
dev_durations_clarinet = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_clarinet, dev_durations_clarinet)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5
    clarinet.append(n)

# 發展部 - 小號（高潮）
dev_notes_trumpet = ['G5', 'A5', 'B5', 'C6', 'D5', 'E5', 'F#5', 'G5'] * 2
dev_durations_trumpet = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_trumpet, dev_durations_trumpet)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5
    trumpet.append(n)

# 發展部 - 定音鼓（轟鳴）
dev_notes_timpani = ['C2', 'G2', 'C3', 'G2', 'D3', 'G2', 'C3', 'G2'] * 2
dev_durations_timpani = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] * 2
for i, (note_name, dur) in enumerate(zip(dev_notes_timpani, dev_durations_timpani)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 40 + i * 5
    timpani.append(n)

# 發展部 - 鋼琴（快速和弦）
dev_chords_piano = [chord.Chord(['C4', 'E4', 'G4']), chord.Chord(['D4', 'F#4', 'A4'])] * 4
dev_durations_piano = [0.25, 0.25] * 4
for i, (ch, dur) in enumerate(zip(dev_chords_piano, dev_durations_piano)):
    ch.quarterLength = dur
    ch.volume.velocity = 40 + i * 10
    piano.append(ch)
    
    
# 再現部 - 小提琴（主題1和主題2，回歸C大調）
for note_name, dur in zip(theme1_notes, theme1_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 80  # 中強 (mf)
    violin.append(n)
theme2_recap_notes = ['C4', 'G3', 'C4', 'A3', 'F3']
for note_name, dur in zip(theme2_recap_notes, theme2_durations):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 60  # 中弱 (mp)
    violin.append(n)
# 尾聲
coda_notes = ['G4', 'F4', 'E4', 'C4']
for i, note_name in enumerate(coda_notes):
    n = note.Note(note_name, quarterLength=2.0)
    n.volume.velocity = 60 - i * 10  # 漸弱
    violin.append(n)

# 再現部 - 中提琴（伴奏）
viola_recap_notes = ['E4', 'G4', 'C5', 'G4', 'E4', 'C5', 'G4', 'E4']
viola_recap_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]
for i, (note_name, dur) in enumerate(zip(viola_recap_notes, viola_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 70 - i * 5
    viola.append(n)

# 再現部 - 大提琴（低音線條）
cello_recap_notes = ['C2', 'G2', 'C3', 'C2', 'G2', 'C3', 'G2', 'C2']
cello_recap_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]
for i, (note_name, dur) in enumerate(zip(cello_recap_notes, cello_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 80 - i * 5
    cello.append(n)

# 再現部 - 長笛（裝飾）
flute_recap_notes = ['G5', 'A5', 'B5', 'C6', 'C6', 'G5', 'C6', 'A5', 'F5']
flute_recap_durations = [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0]
for i, (note_name, dur) in enumerate(zip(flute_recap_notes, flute_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 60 - i * 5
    flute.append(n)

# 再現部 - 單簧管（和聲填充）
clarinet_recap_notes = ['E4', 'F4', 'G4', 'G4', 'E4', 'C5', 'G4', 'E4']
clarinet_recap_durations = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]
for i, (note_name, dur) in enumerate(zip(clarinet_recap_notes, clarinet_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 70 - i * 5
    clarinet.append(n)

# 再現部 - 小號（強調力度）
trumpet_recap_notes = ['G4', 'C5', 'C5', 'G4']
trumpet_recap_durations = [1.0, 1.0, 1.0, 2.0]
for i, (note_name, dur) in enumerate(zip(trumpet_recap_notes, trumpet_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 90 - i * 10
    trumpet.append(n)

# 再現部 - 定音鼓（節奏骨架）
timpani_recap_notes = ['C2', 'G2', 'C2', 'G2', 'C2']
timpani_recap_durations = [1.0, 1.0, 1.0, 1.0, 2.0]
for i, (note_name, dur) in enumerate(zip(timpani_recap_notes, timpani_recap_durations)):
    n = note.Note(note_name, quarterLength=dur)
    n.volume.velocity = 80 - i * 10
    timpani.append(n)

# 再現部 - 鋼琴（和弦伴奏）
piano_recap_chords = [chord.Chord(['C4', 'E4', 'G4']), chord.Chord(['F4', 'A4', 'C5'])]
piano_recap_durations = [2.0, 4.0]
for i, (ch, dur) in enumerate(zip(piano_recap_chords, piano_recap_durations)):
    ch.quarterLength = dur
    ch.volume.velocity = 70 - i * 20
    piano.append(ch)
# 創建樂譜
symphony = stream.Score()
symphony.append([violin, viola, cello, flute, clarinet, trumpet, timpani, piano])

# 展示樂譜（需安裝 MuseScore 或其他音樂軟件）
symphony.show()

# 可選：保存為 MIDI 或 MusicXML 檔案
symphony.write('midi', 'symphony.mid')
symphony.write('musicxml', 'symphony.xml')