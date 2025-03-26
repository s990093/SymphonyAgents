
from music21 import *

__all__ = ['StyleAnalyzer']

class StyleAnalyzer:
    def __init__(self, style: str):
        self.style = style
        self.style_guidelines = {
            "classical": {
                "form_options": ["Sonata", "Theme and Variations", "Rondo"],
                "harmonic_features": "強調功能性和聲進行，注重主-屬關係",
                "orchestration": "標準古典編制，弦樂為核心，木管與銅管平衡使用",
                "dynamic_character": "階梯式力度變化，清晰結構劃分"
            },
            "romantic": {
                "form_options": ["Symphonic Poem", "Character Piece", "Expanded Sonata"],
                "harmonic_features": "使用半音化和聲與遠關係轉調",
                "orchestration": "大型編制，突出銅管與打擊樂，弦樂分部細膩",
                "dynamic_character": "戲劇性漸強與突然對比"
            },
            "baroque": {
                "form_options": ["Fugue", "Concerto Grosso", "Dance Suite"],
                "harmonic_features": "通奏低音與數字低音記譜",
                "orchestration": "以小編制弦樂與通奏低音為主",
                "dynamic_character": "階梯力度與斷連奏對比"
            }
        }
        self.historical_contexts = {
            "classical": "古典時期（約1750-1820），強調形式平衡與清晰結構，代表作曲家有海頓、莫札特",
            "romantic": "浪漫時期（約1820-1900），注重情感表達與個人主義，代表作曲家有柴可夫斯基、馬勒",
            "baroque": "巴洛克時期（約1600-1750），以複雜對位與裝飾音為特色，代表作曲家有巴赫、韓德爾"
        }

    def get_style_analysis(self) -> str:
        guidelines = self.style_guidelines.get(self.style, {})
        analysis = [
            f"[歷史背景] {self.get_historical_context()}",
            f"[曲式選擇] 可選形式：{', '.join(guidelines.get('form_options', []))}",
            f"[和聲特徵] {guidelines.get('harmonic_features', '')}",
            f"[配器特點] {guidelines.get('orchestration', '')}",
            f"[力度特徵] {guidelines.get('dynamic_character', '')}"
        ]
        return "\n".join(analysis)

    def get_historical_context(self) -> str:
        return self.historical_contexts.get(self.style, "通用音樂創作原則")
