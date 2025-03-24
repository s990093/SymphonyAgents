import tempfile
import subprocess
import os
from music21 import stream, converter, instrument

from src.instrument_configs import instrument_configs

__all__ = ["MusicPlayer"]

class MusicPlayer:
    def __init__(self, musescore_path="/Applications/MuseScore 4.app/Contents/MacOS/mscore"):
        self.musescore_path = musescore_path
        self.score = None

    def assign_instrument(self, part, inst_name):
        """
        根據樂器名稱為聲部分配音色。
        :param part: stream.Part 物件
        :param inst_name: 樂器名稱（例如 "piano", "violin"）
        :return: 更新後的 part
        """
        inst_map = {name: config["music21_instrument"] for name, config in instrument_configs.items()}

        selected_inst = inst_map.get(inst_name.lower(), instrument.Piano())  # 預設為鋼琴
        part.insert(0, selected_inst)  # 在聲部開頭插入樂器音色
        return part

    def generate_midi(self, score_drafts, output_file="symphony"):
        self.score = stream.Score()
        for inst_name, part in score_drafts.items():
            # 為每個聲部分配音色
            updated_part = self.assign_instrument(part, inst_name)
            self.score.insert(0, updated_part)

        with tempfile.TemporaryDirectory() as temp_dir:
            xml_file = f"{temp_dir}/{output_file}.musicxml"
            self.score.write('musicxml', fp=xml_file)
            print(f"已生成暫存 MusicXML 檔案：{xml_file}")
            midi_file = f"{output_file}.mid"
            try:
                subprocess.run([self.musescore_path, "-o", midi_file, xml_file], check=True)
                print(f"MIDI 檔案生成成功：{midi_file}")
                return midi_file
            except subprocess.CalledProcessError as e:
                print(f"MIDI 檔案生成失敗：{str(e)}")
                return None

    def generate_mp3(self, score_drafts=None, output_file="symphony", input_file=None):
        """
        將樂譜或 MIDI 檔案轉換為 MP3，並為不同樂器分配音色。
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            if score_drafts:
                self.score = stream.Score()
                for inst_name, part in score_drafts.items():
                    updated_part = self.assign_instrument(part, inst_name)
                    self.score.insert(0, updated_part)
                xml_file = f"{temp_dir}/{output_file}.musicxml"
                self.score.write('musicxml', fp=xml_file)
            elif input_file and os.path.exists(input_file):
                xml_file = input_file
            else:
                print("錯誤：必須提供 score_drafts 或有效的 input_file")
                return None

            mp3_file = f"{output_file}.mp3"
            try:
                subprocess.run([self.musescore_path, "-o", mp3_file, xml_file], check=True)
                print(f"MP3 檔案生成成功：{mp3_file}")
                return mp3_file
            except subprocess.CalledProcessError as e:
                print(f"MP3 檔案生成失敗：{str(e)}")
                return None

    def load_file(self, file_path):
        try:
            self.score = converter.parse(file_path)
            print(f"已成功載入檔案：{file_path}")
            return True
        except Exception as e:
            print(f"載入檔案失敗：{str(e)}")
            return False

    def play(self):
        if self.score is None:
            print("錯誤：尚未載入或生成樂譜。")
            return
        try:
            self.score.show('midi')
            print("正在播放音樂 (music21)...")
        except Exception as e:
            print(f"播放失敗：{str(e)}")
            temp_midi = "temp.mid"
            self.score.write('midi', fp=temp_midi)
            os.system(f"open {temp_midi}")
            print("正在使用系統播放器播放音樂...")

    def save(self, output_file, format="midi"):
        if self.score is None:
            print("錯誤：尚未載入或生成樂譜。")
            return None
        output_path = f"{output_file}.{format}"
        self.score.write(format, fp=output_path)
        print(f"已儲存檔案：{output_path}")
        return output_path
