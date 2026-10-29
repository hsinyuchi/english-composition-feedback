# -*- coding: utf-8 -*-
"""
build_master_option_a.py
The Ultimate Master Generator for Sylvia's English Composition Diagnostic Suite
Implementing Option A:
- Page 1: Precision Non-Overlapping Anchors (①, ②, ③, ...) on Handwriting Scan +
          Teacher Diagnostic & Edit Box (【教師逐項精修便當盒】) / Masterclass Breakdown Box
- Page 2: Grayscale Zoned Layout (Part A, Part B, Part C) with 45pt Safety Bleed Margins
- 1-Page Spot-the-Error Worksheets (學用版 & 教用解答版, ZERO glyph bugs)
- 16:9 Large Typography Classroom Slides (PDF & HTML)
Covers BOTH 111 and 110 Exam Topics!
"""

import os, sys, math
from pathlib import Path
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
import reportlab.pdfbase.ttfonts as ttfonts
import reportlab.pdfbase.pdfmetrics as pdfmetrics
from pypdf import PdfWriter, PdfReader
import fitz

# Register Fonts
pdfmetrics.registerFont(ttfonts.TTFont('JH', 'C:/Windows/Fonts/msjh.ttc'))
pdfmetrics.registerFont(ttfonts.TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc'))
pdfmetrics.registerFont(ttfonts.TTFont('Georgia', 'C:/Windows/Fonts/georgia.ttf'))
pdfmetrics.registerFont(ttfonts.TTFont('GeorgiaBold', 'C:/Windows/Fonts/georgiab.ttf'))
pdfmetrics.registerFont(ttfonts.TTFont('GeorgiaItalic', 'C:/Windows/Fonts/georgiai.ttf'))

# Directories
OUT_111 = Path("H:/我的雲端硬碟/# Sylvia's Workspace/01 講師素材/[置頂] My Workshop Materials/研習素材包/學測英文作文學生原稿/301 111學測作文 (喜歡的公園類型)/output")
OUT_110 = Path("H:/我的雲端硬碟/# Sylvia's Workspace/01 講師素材/[置頂] My Workshop Materials/研習素材包/學測英文作文學生原稿/110學測_亂入花圃學生稿/去識別化版之學生作文/output")
TMP = Path("C:/Users/user/.gemini/antigravity/brain/7148bf21-122a-418b-a09d-b71b1a4f0440/scratch")

OUT_111.mkdir(parents=True, exist_ok=True)
OUT_110.mkdir(parents=True, exist_ok=True)

# Styles
GREEN = '#006A4E'
RED = '#BC1632'
BLUE = '#2563EB'
GOLD = '#B45309'

DARK_PILL = '#1E293B'
BORDER_COLOR = '#CBD5E1'
TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'
LINE_DOTTED = '#94A3B8'
BG_LIGHT_GRAY = '#F8FAFC'

SLIDE_W, SLIDE_H = 960, 540

# ==================== DATA DEFINITIONS ====================

# ----- 111 Topic Data -----
DATA_111_S01 = {
    'id': '301_01',
    'exam_year': '111',
    'exam_topic': '規劃理想新公園',
    'title': '301 班第一篇 (6號同學 練習原稿)',
    'subtitle': '學測英文作文個人診斷與精修歷程單',
    'words': 124,
    'total': 9.0,
    'grade_tier': '待加強 (第2級距)',
    'total_desc': '實測 124 字（達 120 字標）；扣除 0 分',
    'scores': [
        ('內容 (Content)', '2.5', '能提及公園 A（設施）與 B（樹木），但理由撰寫較單薄，好處僅簡述涼爽。'),
        ('組織 (Organization)', '2.5', '具兩段式雛形（對比童年 vs. 長大），但轉折詞誤用（In reverse 應為 In contrast）。'),
        ('文法 (Grammar)', '2.0', '多處主詞動詞不一致 (have)、雙動詞混淆 (are be set) 及 will 後漏 be。'),
        ('字彙 (Vocabulary)', '2.0', '詞性混淆 (differ)、搭配詞不自然 (take a picnic 建議用 have a picnic)。')
    ],
    'feedback_zh': '段落架構清晰，能以自身成長經驗構思新公園，兼顧設施與綠意！建議下次著重三點：1. 單數動詞加 s（Picture A has）；2. 避免中式直譯（as I grew older）；3. will 後方形容詞補原形 be（it will be cool）。',
    'feedback_en': "Your idea of blending fun facilities with greenery is authentic! Next draft, focus on: 1. Subject-verb agreement; 2. Natural expressions instead of direct translation; 3. Add 'be' after 'will'.",
    'tasks': [
        ('【任務 1：基礎主謂一致與助動詞】修正第 4 行「Picture A have」與第 12 行「it will very cool」，寫出兩句完整正句。', 1),
        ('【任務 2：戒除中式直譯】將第 8 行「along with my ages going up」改寫為地道自然的「as I grew older」。', 1),
        ('【任務 3：地道搭配詞練習】修正「differ parks」與「take a picnic」，將其替換為符合大考水準的精準字詞。', 2)
    ],
    'is_ceec': False,
    'img_name': '111_s01_enhanced.png',
    'anchors': [
        ('1', 0.08, 0.22, 0.07, BLUE, False),  # In this day
        ('2', 0.24, 0.32, 0.21, RED, True),    # differ parks
        ('3', 0.27, 0.33, 0.28, RED, True),    # Picture A have
        ('4', 0.70, 0.88, 0.28, RED, True),    # are be set
        ('5', 0.24, 0.64, 0.58, BLUE, False),  # along with my ages...
        ('6', 0.60, 0.88, 0.73, BLUE, False),  # take a picnic
        ('7', 0.16, 0.26, 0.86, RED, True),    # it will very cool
    ],
    'edit_box': [
        ('①', 'In this day', '【修辭更佳】', BLUE, '(建議用 Nowadays 或 In recent years 更佳)', '原句可通，但大考寫作採用書面副詞能讓開篇更具語氣權威感。'),
        ('②', 'differ parks', '【文法更正】', RED, 'different parks', '修飾名詞 parks 應使用形容詞 different，而非動詞 differ。'),
        ('③', 'Picture A have', '【文法更正】', RED, 'Picture A has', '主詞 Picture A 為第三人稱單數，現在式動詞應加 -s 改為 has。'),
        ('④', 'are be set', '【文法更正】', RED, 'are set up / are built', '設施配置應用被動語態 are set up，不可 are 與 be 兩動詞疊用。'),
        ('⑤', 'along with my ages...', '【修辭更佳】', BLUE, '= as I grew older,', '中文「隨著年齡增長」英文地道慣用語為 as I grew older，避免逐字中翻英。'),
        ('⑥', 'take a picnic', '【修辭更佳】', BLUE, '(建議用 have a picnic 更佳)', '生活中最道地之動賓搭配詞為 have a picnic 或 go on a picnic。'),
        ('⑦', 'it will very cool', '【文法更正】', RED, 'it will be very cool', '助動詞 will 後方接形容詞 cool，必須補上原形動詞 be。')
    ]
}

DATA_111_CEEC = {
    'id': '111_CEEC_01',
    'exam_year': '111',
    'exam_topic': '規劃理想新公園',
    'title': '大考中心官方公布之佳作 01',
    'subtitle': '學測英文作文個人診斷與精修歷程單 (特優典範)',
    'words': 248,
    'total': 18.5,
    'grade_tier': '特優 (第5級距 / 前1%)',
    'total_desc': '實測 248 字；篇幅宏大、層次深邃；思維細膩、用字極雅；扣除 0 分',
    'scores': [
        ('內容 (Content)', '5.0', '兼顧設施多元與生態寧靜，論點成熟具前瞻性，描摹生動。'),
        ('組織 (Organization)', '4.5', '起承轉合極致自然，轉折詞銜接無縫，層次推進水到渠成。'),
        ('文法 (Grammar)', '4.5', '句型多樣（分詞構句、關係代名詞非限定、虛主詞），零重大瑕疵。'),
        ('字彙 (Vocabulary)', '4.5', '用字精準典雅，精準使用 tranquil oasis, harmonious blend 等亮點詞。')
    ],
    'feedback_zh': '全篇展現超群之寫作素養！將公園定位為現代都市中的「心靈綠洲」，以設施活力與自然靜謐相互映襯，論點極具說服力與美感。',
    'feedback_en': "A flawless exemplary model. Your holistic vision of modern urban parks—balancing functional energy with ecological peace—demonstrates native-level fluency.",
    'tasks': [
        ('【任務 1：高階意象金句摘錄】從第一段找出形容綠意與放鬆的 2 個極佳搭配詞，並記錄於下方。', 1),
        ('【任務 2：複合句型仿寫】模仿第 2 段開頭之「融合理想」句型，自己造出 1 個複合句。', 1),
        ('【任務 3：典範修辭移植】將本文精選名詞「tranquil oasis」納入自己的下一篇寫作草稿中。', 2)
    ],
    'is_ceec': True,
    'img_col1': '111_ceec_col1_enhanced.png',
    'img_col2': '111_ceec_col2_enhanced.png',
    'anchors': [
        ('❶', 0.12, 0.40, 0.15, GOLD, False, 1), # Col 1
        ('❷', 0.10, 0.45, 0.48, GOLD, False, 1), # Col 1
        ('❸', 0.12, 0.42, 0.20, GOLD, False, 2), # Col 2
        ('❹', 0.10, 0.48, 0.55, GOLD, False, 2), # Col 2
    ],
    'edit_box': [
        ('❶', 'urban sanctuaries & green haven', '【意象建立】', GOLD, '自然景觀鋪陳', '開篇立即營造公園作為城市綠洲的安寧畫面感，跳脫模板。'),
        ('❷', 'Not only does it offer..., but...', '【句構變化】', GOLD, '部分倒裝句型', '精準運用 Not only 置於句首引發倒裝，強化排比氣勢與論證力。'),
        ('❸', 'a harmonious blend of nature & leisure', '【學術搭配】', GOLD, '高階動賓/名詞搭配', 'blend 搭配 of 展現高度精煉之語言掌控力，為大考高分關鍵。'),
        ('❹', 'fostering a sense of belonging', '【深層哲理】', GOLD, '分詞構句深化結尾', '以 V-ing 分詞構句收尾，將休閒場域昇華為社區情感連結。')
    ]
}

# ----- 110 Topic Data -----
DATA_110_S01 = {
    'id': 'Student_01',
    'exam_year': '110',
    'exam_topic': '花圃踩踏情境題',
    'title': '學生練習 Student 01',
    'subtitle': '學測英文作文個人診斷與精修歷程單',
    'words': 118,
    'total': 10.0,
    'grade_tier': '及格 (第3級距)',
    'total_desc': '實測 118 字（逼近 120 字標）；兩段式結構完整；扣除 0 分',
    'scores': [
        ('內容 (Content)', '2.5', '切入花圃被破壞之情境，但第 1 段僅述及 40 字，缺乏現場遊客踩踏細節。'),
        ('組織 (Organization)', '2.5', '兩段分明，但第二段因果句型串接重複 (I would feel... because...)。'),
        ('文法 (Grammar)', '2.5', '以簡易句為主，第二段假設法時態前後不一致 (were 誤用，應修為 would be)。'),
        ('字彙 (Vocabulary)', '2.5', '詞彙生活化，但出現形似字混淆：sigh (嘆氣) 誤寫為 sign (指示牌)。')
    ],
    'feedback_zh': '精確掌握花圃主人的心痛與憤怒，立場清晰！建議下次第 1 段多描寫 1-2 句遊客踩踏的視覺細節；改正 sign 的拼字，並注意假設法動詞的一致性。',
    'feedback_en': "You clearly understand the garden owner's feelings. For the next draft, add 1-2 visual sentences in paragraph 1, correct the spelling of 'sign', and keep verb tenses consistent.",
    'tasks': [
        ('【任務 1：字彙拼寫與搭配詞】請將第 2 行 sigh 改為 sign，並將 public manners 替換為自然的地道詞彙。', 1),
        ('【任務 2：句型串接與轉折簡練】將第 3 行「Because of that...」精簡為轉折副詞「Therefore,...」，使語氣更精鍊。', 1),
        ('【任務 3：細節增補挑戰】在第 1 段補寫 1 句（約 15 字），生動描繪遊客為了拍照而踩踏花草的具體動作。', 2)
    ],
    'is_ceec': False,
    'img_name': 's01_enhanced_crop.png',
    'anchors': [
        ('1', 0.52, 0.90, 0.07, BLUE, False),  # in a field of flowers
        ('2', 0.58, 0.68, 0.145, RED, True),   # sigh -> sign
        ('3', 0.22, 0.44, 0.219, BLUE, False), # Because of that
        ('4', 0.46, 0.58, 0.368, RED, True),   # heartbroken (need was)
        ('5', 0.40, 0.48, 0.526, RED, True),   # were -> would be
        ('6', 0.06, 0.31, 0.772, BLUE, False), # public manners
    ],
    'edit_box': [
        ('①', 'in a field of flowers', '【修辭更佳】', BLUE, '(建議用 in a flower garden 更佳)', '原句文意清楚，但以 a flower garden 描摹私人精心照料之花園更為地道精準。'),
        ('②', 'sigh', '【文法更正】', RED, 'sign (告示牌)', '形似字筆誤。sigh 為「嘆氣」，表示「設立告示牌」應使用 sign。'),
        ('③', 'Because of that', '【修辭更佳】', BLUE, '(建議用 Therefore 或 As a result 更佳)', '原文文法正確！但大考學術寫作多採用轉折副詞 Therefore 連接，語氣更顯成熟。'),
        ('④', 'heartbroken', '【文法更正】', RED, 'was heartbroken', '主詞 I 後方缺少主要動詞，應補上 be 動詞 was 形成完整的形容詞述語。'),
        ('⑤', 'were', '【文法更正】', RED, 'would be', '第二段設想若自己是主人之假想情境，後句主要子句動詞應用 would be。'),
        ('⑥', 'public manners', '【修辭更佳】', BLUE, '(建議用 good manners 或 civic awareness 更佳)', '形容公眾公德心或規矩，常用 good manners 或 civic awareness。')
    ]
}

DATA_110_S35 = {
    'id': 'Student_35',
    'exam_year': '110',
    'exam_topic': '花圃踩踏情境題',
    'title': '學生練習 Student 35 (30135)',
    'subtitle': '學測英文作文個人診斷與精修歷程單',
    'words': 167,
    'total': 14.0,
    'grade_tier': '良好 (第4級距)',
    'total_desc': '實測 167 字；兩段篇幅厚實；結尾點出「欣賞始於尊重」；扣除 0 分',
    'scores': [
        ('內容 (Content)', '3.5', '切入園主立場深刻，末段「欣賞始於尊重」思想成熟；但首段實景描摹略少。'),
        ('組織 (Organization)', '3.5', '兩段式架構分明，首尾呼應；但第二段出現 Because 從屬子句獨立成句之破句。'),
        ('文法 (Grammar)', '3.5', '善用假設條件句；但出現 Because 破句（Sentence Fragment），需留意主句。'),
        ('字彙 (Vocabulary)', '3.5', '詞彙豐富且切題，出現明顯筆誤 destory (應為 destroy)，另 space owners 宜修。')
    ],
    'feedback_zh': '結尾點出「真正的欣賞始於尊重」，立意高遠極具說服力！建議第 1 段補強對花圃遭踐踏的視覺實景描摹；修正 Because 開頭的破句，將其與後句合併。',
    'feedback_en': "Your concluding insight that 'true appreciation begins with respect' elevates the moral depth of your essay. Connect the fragment starting with 'Because' and fix 'destory'.",
    'tasks': [
        ('【任務 1：拼字與用詞精修】修正 destory 為 destroy，並將 space owners 替換為 garden owners。', 1),
        ('【任務 2：破句重組】將第 6 行「Because this place means a lot to me...」從屬子句合併至後方主句。', 1),
        ('【任務 3：感官細節增補】在第 1 段補寫 1 句（約 15-20 字），描繪花草被踩扁凋零的視覺畫面。', 2)
    ],
    'is_ceec': False,
    'img_name': 's35_full_enhanced_crop.png',
    'anchors': [
        ('1', 0.10, 0.32, 0.08, BLUE, False),  # In modern times
        ('2', 0.14, 0.45, 0.16, BLUE, False),  # floral exhibitions
        ('3', 0.74, 0.86, 0.35, RED, True),    # destory
        ('4', 0.50, 0.72, 0.44, BLUE, False),  # space owners
        ('5', 0.08, 0.24, 0.52, RED, True),    # Because fragment
        ('6', 0.62, 0.80, 0.86, BLUE, False),  # not only... but also
    ],
    'edit_box': [
        ('①', 'In modern times', '【修辭更佳】', BLUE, '(建議用 In modern society 或 Nowadays 更佳)', '英文習慣以 In modern society 或 Nowadays 表達當今社會現況。'),
        ('②', 'floral exhibitions', '【修辭更佳】', BLUE, '(建議用 visit flower fields 更佳)', '一般農家花田非正式展覽會，用 flower fields 語意更加切題生活化。'),
        ('③', 'destory', '【文法更正】', RED, 'destroy', '拼字筆誤。正確拼法為 destroy。'),
        ('④', 'space owners', '【修辭更佳】', BLUE, '(建議用 garden owners 或 growers 更佳)', 'space 過於籠統，改用 garden owners 或 growers 更精準地道。'),
        ('⑤', 'Because this place...', '【文法更正】', RED, '破句重組 (Sentence Fragment)', 'Because 引導從屬子句不可單獨成句，應與後方主句用逗號串聯成完整句。'),
        ('⑥', 'not only for..., but...', '【修辭更佳】', BLUE, 'not only to appreciate..., but also to respect...', '平行對稱結構：前後兩端介系詞或不定詞形式應保持對稱整齊。')
    ]
}

DATA_110_CEEC = {
    'id': '110_CEEC_01',
    'exam_year': '110',
    'exam_topic': '花圃踩踏情境題',
    'title': '大考中心官方公布之佳作 01',
    'subtitle': '學測英文作文個人診斷與精修歷程單 (特優典範)',
    'words': 284,
    'total': 18.5,
    'grade_tier': '特優 (第5級距 / 前1%)',
    'total_desc': '實測 284 字；篇幅宏大、層次深邃；思維深刻、用字極雅；扣除 0 分',
    'scores': [
        ('內容 (Content)', '5.0', '以遊客自省切入，深刻剖析從眾心理與盲點，思維成熟極具說服力。'),
        ('組織 (Organization)', '4.5', '起承轉合極致自然，轉折詞運用無縫銜接，行文如行雲流水。'),
        ('文法 (Grammar)', '4.5', '句型結構豐富多元（倒裝句、名詞子句、假設法），幾無語病。'),
        ('字彙 (Vocabulary)', '4.5', '用字精準典雅，精準運用 aesthetic appreciation, self-discipline 等詞。')
    ],
    'feedback_zh': '全篇兼具文學美感與哲思深度！以遊客第一人稱視角切入，深刻反省「自私之愛」的盲點，流暢純熟，足以作為全國高中生之終極學習標竿。',
    'feedback_en': "A masterclass in high-school composition. Your reflective stance moves far beyond clichés, showcasing sublime vocabulary and diverse sentence architecture.",
    'tasks': [
        ('【任務 1：哲學反思金句摘錄】從本文中找出 1 句最令你震撼的哲思金句，並試著仿寫於下方。', 1),
        ('【任務 2：名詞子句串接】找出作者如何運用名詞子句表達心境轉折，並寫出 1 句相似句型。', 1),
        ('【任務 3：典範修辭移植】將本文精選搭配詞「aesthetic appreciation」融入自己的下一篇寫作草稿中。', 2)
    ],
    'is_ceec': True,
    'img_col1': 'ceec_col1_enhanced.png',
    'img_col2': 'ceec_col2_enhanced.png',
    'anchors': [
        ('❶', 0.10, 0.45, 0.12, GOLD, False, 1),
        ('❷', 0.12, 0.48, 0.45, GOLD, False, 1),
        ('❸', 0.08, 0.42, 0.22, GOLD, False, 2),
        ('❹', 0.10, 0.50, 0.60, GOLD, False, 2),
    ],
    'edit_box': [
        ('❶', 'Captivated by the floral tapestry...', '【分詞構句】', GOLD, '畫面感生動鋪陳', '以 V-ed 分詞構句開篇，迅速建立陶醉花海的立體視覺感。'),
        ('❷', 'blinded by our desire for vanity', '【哲思深度】', GOLD, '精闢剖析自私心態', '精準點出遊客為拍美照而無視自然被毀之「虛榮盲點」，立意高遠。'),
        ('❸', 'True appreciation stems from...', '【名言式總結】', GOLD, '主題昇華與思想定錨', '以肯定句式直接定義「真正的鑑賞始於敬畏」，具格言式震撼力。'),
        ('❹', 'a delicate balance between nature & human', '【人文反思】', GOLD, '格局宏大之結語', '將單純的觀光事件提升至人與自然和諧共存之宏觀哲理層次。')
    ]
}

# ==================== PAGE 1 RENDER ENGINE (OPTION A) ====================

def render_page_1_option_a(data, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    left = 40
    avail_w = w - 80

    # Top Ribbon (Magazine Header)
    c.setFillColor(colors.HexColor(GREEN))
    c.rect(0, h - 8, w, 8, fill=1, stroke=0)
    c.setFont('GeorgiaBold', 10)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(left, h - 25, 'THE WRITING EDIT  |  ESSAY DIAGNOSTIC REPORT')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(w - left, h - 25, '學測英文作文個人診斷與精修歷程單 (第1頁)')

    # Title & Metadata
    c.setFont('JHB', 15)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 50, data['title'])
    c.setFont('JH', 9)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, h - 66, f"{data['exam_year']} 學測英文作文（{data['exam_topic']}）  |  實測字數：{data['words']} 字  |  總分：{data['total']} 分")

    # Score Pill Badge on Top Right
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(w - left - 105, h - 70, 105, 26, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('GeorgiaBold', 12)
    c.drawCentredString(w - left - 52, h - 55, f"{data['total']} / 20")
    c.setFont('JH', 7)
    c.drawCentredString(w - left - 52, h - 65, data['grade_tier'].split(' ')[0])

    # Divider
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 76, w - left, h - 76)

    # 1. Image Scan Placement
    if not data['is_ceec']:
        # Single Student Scan
        img_p = TMP / data['img_name']
        im = Image.open(img_p)
        im_w, im_h = im.size
        
        # Determine optimal scaling
        # Cap height so Edit Box has ample room
        max_scan_h = 360 if im_h / im_w < 0.85 else 410
        draw_w = avail_w
        draw_h = draw_w * (im_h / im_w)
        if draw_h > max_scan_h:
            draw_h = max_scan_h
            draw_w = draw_h * (im_w / im_h)
            draw_x = left + (avail_w - draw_w) / 2
        else:
            draw_x = left
            
        draw_y = h - 86 - draw_h

        c.drawImage(str(img_p), draw_x, draw_y, width=draw_w, height=draw_h)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.rect(draw_x, draw_y, draw_w, draw_h)

        # Draw Clean Anchors (ONLY badge + underline, ZERO overlapping English text!)
        for num, x1, x2, y_rel, col, is_error in data['anchors']:
            px1 = draw_x + x1 * draw_w
            px2 = draw_x + x2 * draw_w
            py = draw_y + draw_h - y_rel * draw_h

            # Subtle underline on original word
            c.setStrokeColor(colors.HexColor(col))
            c.setLineWidth(1.2)
            if not is_error:
                c.setDash(2, 2)
            else:
                c.setDash()
            c.line(px1, py - 2, px2, py - 2)
            c.setDash()

            # Circle badge at px1 - 7
            badge_x = px1 - 7
            badge_y = py + 3
            c.setFillColor(colors.HexColor(col))
            c.circle(badge_x, badge_y, 6.5, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont('GeorgiaBold', 7.5)
            c.drawCentredString(badge_x, badge_y - 2.5, num)

    else:
        # CEEC Two-Column Side-by-Side Scan
        im1 = Image.open(TMP / data['img_col1'])
        im2 = Image.open(TMP / data['img_col2'])
        w1, h1 = im1.size
        w2, h2 = im2.size

        col_w = (avail_w - 12) / 2
        col1_h = col_w * (h1 / w1)
        col2_h = col_w * (h2 / w2)
        draw_h = max(col1_h, col2_h)
        if draw_h > 315:
            scale = 315 / draw_h
            col_w *= scale
            col1_h *= scale
            col2_h *= scale
            draw_h = 315

        x_col1 = left + (avail_w - (col_w * 2 + 12)) / 2
        x_col2 = x_col1 + col_w + 12
        draw_y = h - 86 - draw_h

        c.drawImage(str(TMP / data['img_col1']), x_col1, draw_y + (draw_h - col1_h), width=col_w, height=col1_h)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.rect(x_col1, draw_y + (draw_h - col1_h), col_w, col1_h)

        c.drawImage(str(TMP / data['img_col2']), x_col2, draw_y + (draw_h - col2_h), width=col_w, height=col2_h)
        c.rect(x_col2, draw_y + (draw_h - col2_h), col_w, col2_h)

        # Draw CEEC Gold Badges
        for num, x1, x2, y_rel, col, is_error, col_idx in data['anchors']:
            base_x = x_col1 if col_idx == 1 else x_col2
            curr_h = col1_h if col_idx == 1 else col2_h
            curr_y = draw_y + (draw_h - curr_h)

            px1 = base_x + x1 * col_w
            px2 = base_x + x2 * col_w
            py = curr_y + curr_h - y_rel * curr_h

            c.setStrokeColor(colors.HexColor(col))
            c.setLineWidth(1.2)
            c.setDash(2, 2)
            c.line(px1, py - 2, px2, py - 2)
            c.setDash()

            badge_x = px1 - 7
            badge_y = py + 3
            c.setFillColor(colors.HexColor(col))
            c.circle(badge_x, badge_y, 6.5, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont('GeorgiaBold', 7.5)
            c.drawCentredString(badge_x, badge_y - 2.5, num)

    # 2. Bottom Bento Box (The Diagnostic & Edit Box / Masterclass Box)
    box_top = draw_y - 10
    box_bottom = 25
    box_h = box_top - box_bottom
    box_w = avail_w

    # Card Background
    c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
    c.roundRect(left, box_bottom, box_w, box_h, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, box_bottom, box_w, box_h, 6, fill=0, stroke=1)

    # Card Header Pill
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(left + 6, box_top - 20, box_w - 12, 17, 3, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('JHB', 8.5)

    if not data['is_ceec']:
        c.drawString(left + 12, box_top - 14, '【教師逐項精修便當盒】 (The Diagnostic & Edit Box)')
        c.setFont('JH', 7)
        c.drawRightString(left + box_w - 12, box_top - 14, '紅點/實線為文法硬性更正 | 藍點/虛線為修辭更佳建議（保留學生原意）')
    else:
        c.drawString(left + 12, box_top - 14, '【大考佳作大師賞析盒】 (Masterclass Highlights & Rhetorical Breakdown)')
        c.setFont('JH', 7)
        c.drawRightString(left + box_w - 12, box_top - 14, '金點標記為全國頂尖得獎亮點（倒裝句、感官沉浸、高階搭配詞與層次推進）')

    # Table Assembly
    style_orig = ParagraphStyle('Orig', fontName='GeorgiaBold', fontSize=8, leading=9.5, textColor=colors.HexColor(TEXT_DARK))
    style_sol = ParagraphStyle('Sol', fontName='JH', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1E293B'))

    table_data = [
        [
            Paragraph('<b>編號</b>', ParagraphStyle('TH', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED), alignment=1)),
            Paragraph('<b>原文語句</b>' if not data['is_ceec'] else '<b>典範佳句摘錄</b>', ParagraphStyle('TH2', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED))),
            Paragraph('<b>類別</b>' if not data['is_ceec'] else '<b>手法</b>', ParagraphStyle('TH3', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED), alignment=1)),
            Paragraph('<b>精修建議與考點解析</b>' if not data['is_ceec'] else '<b>大考得分關鍵解析</b>', ParagraphStyle('TH4', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED)))
        ]
    ]

    for item in data['edit_box']:
        num_str, orig_txt, cat_txt, cat_col, sol_title, sol_desc = item
        style_cat = ParagraphStyle('Cat', fontName='JHB', fontSize=7.5, leading=9, textColor=colors.HexColor(cat_col), alignment=1)
        
        row = [
            Paragraph(f'<font color="{cat_col}"><b>{num_str}</b></font>', ParagraphStyle('NUM', fontName='JHB', fontSize=8.5, leading=9.5, alignment=1)),
            Paragraph(orig_txt, style_orig),
            Paragraph(cat_txt, style_cat),
            Paragraph(f'<b>{sol_title}</b><br/><font color="#64748B">{sol_desc}</font>', style_sol)
        ]
        table_data.append(row)

    col_w = [26, 110, 65, box_w - 26 - 110 - 65 - 12]
    table = Table(table_data, colWidths=col_w)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(BORDER_COLOR)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    tw, th = table.wrap(box_w - 12, box_h - 26)
    table_y = box_top - 24 - th
    table.drawOn(c, left + 6, table_y)

    c.save()
    print(f"Page 1 rendered: {out_pdf_path.name}")

# ==================== PAGE 2 RENDER ENGINE (BLEED SAFE & MONOCHROME) ====================

def render_page_2_option_a(data, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    left = 45
    avail_w = w - 90  # 505.28 pt strict safety margin

    # Header Ribbon
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.rect(0, h - 8, w, 8, fill=1, stroke=0)
    c.setFont('GeorgiaBold', 10)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 25, 'THE WRITING EDIT  |  LEARNING & REVISION WORKBENCH')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(w - left, h - 25, '學測英文作文個人診斷與自主修訂反思 (第2頁)')

    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 34, w - left, h - 34)

    # ---------------- PART A: 大考規準評分與教師評語 ----------------
    cur_y = h - 42
    
    # Part A Pill Header
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(left, cur_y - 18, 230, 18, 3, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('JHB', 8.5)
    c.drawString(left + 8, cur_y - 13, 'PART A | 大考規準評分與教師評語 (Assessment)')
    
    cur_y -= 24

    # 3-Column Summary Table (Total | Tier | Word Count)
    summary_data = [
        [
            Paragraph(f"<b>總分 (Total)</b>: <font color=\"#0F172A\"><b>{data['total']} / 20 分</b></font>", ParagraphStyle('Sum1', fontName='JH', fontSize=8, leading=9.5)),
            Paragraph(f"<b>大考級距</b>: <font color=\"#0F172A\"><b>{data['grade_tier']}</b></font>", ParagraphStyle('Sum2', fontName='JH', fontSize=8, leading=9.5, alignment=1)),
            Paragraph(f"<b>實測字數</b>: <font color=\"#0F172A\"><b>{data['words']} 字</b></font> ({'達標' if data['words']>=120 else '未達標'})", ParagraphStyle('Sum3', fontName='JH', fontSize=8, leading=9.5, alignment=2))
        ]
    ]
    t_sum = Table(summary_data, colWidths=[150, 205, 150])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(BG_LIGHT_GRAY)),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor(BORDER_COLOR)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    sw, sh = t_sum.wrap(avail_w, 30)
    t_sum.drawOn(c, left, cur_y - sh)
    cur_y -= (sh + 6)

    # 4 Rubric Criteria Table
    style_dim = ParagraphStyle('Dim', fontName='JHB', fontSize=7.5, leading=9, textColor=colors.HexColor(TEXT_DARK))
    style_sc = ParagraphStyle('Sc', fontName='GeorgiaBold', fontSize=8, leading=9, textColor=colors.HexColor(TEXT_DARK), alignment=1)
    style_ev = ParagraphStyle('Ev', fontName='JH', fontSize=7.5, leading=9, textColor=colors.HexColor(TEXT_MUTED))

    rubric_data = [
        [
            Paragraph('<b>評量維度 (Rubrics)</b>', ParagraphStyle('RH1', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED))),
            Paragraph('<b>得分</b>', ParagraphStyle('RH2', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED), alignment=1)),
            Paragraph('<b>具體學習表現與大考徵狀分析</b>', ParagraphStyle('RH3', fontName='JHB', fontSize=7.5, leading=8.5, textColor=colors.HexColor(TEXT_MUTED)))
        ]
    ]
    for dim, sc, ev in data['scores']:
        rubric_data.append([
            Paragraph(dim, style_dim),
            Paragraph(f"{sc} / 5", style_sc),
            Paragraph(ev, style_ev)
        ])

    t_rubric = Table(rubric_data, colWidths=[110, 50, avail_w - 160])
    t_rubric.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor(BORDER_COLOR)),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    rw, rh = t_rubric.wrap(avail_w, 100)
    t_rubric.drawOn(c, left, cur_y - rh)
    cur_y -= (rh + 6)

    # Teacher Comprehensive Feedback Box
    fb_data = [
        [
            Paragraph(f"<b>【導師總評】</b> {data['feedback_zh']}<br/><font color=\"#475569\"><b>Teacher's Note:</b> {data['feedback_en']}</font>",
                      ParagraphStyle('FB', fontName='JH', fontSize=7.5, leading=9.5, textColor=colors.HexColor(TEXT_DARK)))
        ]
    ]
    t_fb = Table(fb_data, colWidths=[avail_w])
    t_fb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(BG_LIGHT_GRAY)),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor(BORDER_COLOR)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    fw, fh = t_fb.wrap(avail_w, 60)
    t_fb.drawOn(c, left, cur_y - fh)
    cur_y -= (fh + 12)

    # ---------------- PART B: 學生自主修訂任務 ----------------
    # Part B Pill Header
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(left, cur_y - 18, 250, 18, 3, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('JHB', 8.5)
    c.drawString(left + 8, cur_y - 13, 'PART B | 學生自主修訂任務 (Personalized Tasks)')
    
    cur_y -= 24

    for t_idx, (t_desc, t_lines) in enumerate(data['tasks'], 1):
        # Task title inside light pill
        c.setFillColor(colors.HexColor('#F1F5F9'))
        c.roundRect(left, cur_y - 14, avail_w, 14, 2, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.5)
        c.roundRect(left, cur_y - 14, avail_w, 14, 2, fill=0, stroke=1)
        
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.setFont('JHB', 7.5)
        c.drawString(left + 6, cur_y - 10, t_desc)
        cur_y -= 18

        # Writing Lines (Ample spacing 24pt for student handwriting)
        for line_i in range(t_lines):
            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.8)
            c.setDash(2, 2)
            c.line(left + 15, cur_y - 6, left + avail_w - 5, cur_y - 6)
            c.setDash()
            
            c.setFont('GeorgiaItalic', 7)
            c.setFillColor(colors.HexColor('#94A3B8'))
            c.drawString(left + 2, cur_y - 7, f"L{line_i+1}")
            cur_y -= 24
        cur_y -= 4

    cur_y -= 4

    # ---------------- PART C: 學習歷程與後設反思 ----------------
    # Part C Pill Header
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(left, cur_y - 18, 240, 18, 3, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('JHB', 8.5)
    c.drawString(left + 8, cur_y - 13, 'PART C | 學習歷程與後設反思 (Metacognition)')

    cur_y -= 22

    # Slider Scale Bar (Clean 1 to 5 circles, NO cluttering preset labels!)
    c.setFont('JH', 7.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, cur_y, '本次寫作自我效能自評：')
    
    scale_x = left + 120
    for s_i in range(1, 6):
        cx = scale_x + (s_i - 1) * 70
        cy = cur_y + 2
        c.setStrokeColor(colors.HexColor(DARK_PILL))
        c.setLineWidth(1)
        c.circle(cx, cy, 6, fill=0, stroke=1)
        c.setFont('GeorgiaBold', 7.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawCentredString(cx, cy - 2.5, str(s_i))
        if s_i < 5:
            c.setStrokeColor(colors.HexColor('#CBD5E1'))
            c.setLineWidth(0.8)
            c.line(cx + 8, cy, cx + 62, cy)
            
    c.setFont('JH', 7)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(left + avail_w, cur_y, '(1: 極不滿意  ←  自評量表  →  5: 非常滿意)')

    cur_y -= 14

    # 2x2 Reflection Bento Grid
    box_w = (avail_w - 8) / 2
    box_h = 44

    prompts = [
        ('【今日最有收穫的句型 / 單字】', left, cur_y - box_h),
        ('【下次寫作一定要避開的盲區】', left + box_w + 8, cur_y - box_h),
        ('【我覺得寫得最滿意的一句話】', left, cur_y - box_h * 2 - 6),
        ('【教師簽章與評語 / 努力目標】', left + box_w + 8, cur_y - box_h * 2 - 6),
    ]

    for p_title, bx, by in prompts:
        c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
        c.roundRect(bx, by, box_w, box_h, 3, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.6)
        c.roundRect(bx, by, box_w, box_h, 3, fill=0, stroke=1)

        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.setFont('JHB', 7)
        c.drawString(bx + 6, by + box_h - 10, p_title)

        # Dotted handwriting guide line
        c.setStrokeColor(colors.HexColor(LINE_DOTTED))
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(bx + 8, by + 12, bx + box_w - 8, by + 12)
        c.setDash()

    # Footer Sign-off
    c.setFont('JH', 7)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, 18, '評量標準完全依據教育部大考中心 (CEEC) 英文科閱卷評分規準 (Content / Organization / Grammar / Vocabulary)')
    c.drawRightString(w - left, 18, 'THE WRITING EDIT • 高中職英文寫作雙軌診斷系統')

    c.save()
    print(f"Page 2 rendered: {out_pdf_path.name}")

# ==================== COMBINE TO PRINTABLE 2-PAGE PDF ====================

def combine_to_print_pdf(p1_path, p2_path, out_path):
    writer = PdfWriter()
    r1 = PdfReader(str(p1_path))
    r2 = PdfReader(str(p2_path))
    writer.add_page(r1.pages[0])
    writer.add_page(r2.pages[0])
    with open(out_path, 'wb') as f:
        writer.write(f)
    print(f"Combined 2-Page Print PDF created: {out_path.name}")

# ==================== SPOT-THE-ERROR WORKSHEETS ====================

def build_worksheet_option_a(exam_year, exam_topic, is_teacher, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    left = 45
    avail_w = w - 90

    # Header Ribbon
    tag = "【教用解答解析版】" if is_teacher else "【學生課堂練習版】"
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.rect(0, h - 8, w, 8, fill=1, stroke=0)

    c.setFont('GeorgiaBold', 10)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 25, 'THE WRITING EDIT  |  SPOT THE ERRORS WORKBENCH')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(w - left, h - 25, f"{exam_year} 學測英文作文課堂微講義")

    c.setFont('JHB', 15)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 50, f"大家來找碴：{exam_year} 學測寫作五大集體盲區微講義 {tag}")
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, h - 65, f"作文主題：{exam_topic}  |  請診斷下方五句大考學生原稿句，圈出錯誤並於空白處完成修訂")

    # Student metadata box on top right
    if not is_teacher:
        c.setFont('JH', 8.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawRightString(w - left - 100, h - 50, '班級：________  座號：____  姓名：____________')

    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 75, w - left, h - 75)

    cur_y = h - 88

    # 5 Real Sentences from Student Essays
    if exam_year == '111':
        items = [
            (
                "盲區 1：詞性混淆（動詞與形容詞錯置）",
                "Differ parks have vary features for children to play.",
                "Different parks have various features for children to play.",
                "differ 為動詞，修飾名詞 parks 必須改用形容詞 different；同理 vary 亦為動詞，應修為 various。"
            ),
            (
                "盲區 2：主詞動詞不一致（單數動詞漏加 -s）",
                "Picture A have more facilities, which is popular with kids.",
                "Picture A has more facilities, which are popular with kids.",
                "主詞 Picture A 為第三人稱單數，現在式動詞應為 has；後方關代 which 指先行詞 facilities，be 動詞應用 are。"
            ),
            (
                "盲區 3：助動詞與形容詞疊用（漏補原形 be）",
                "If the government builds more trees, it will very cool in summer.",
                "If the government plants more trees, it will be very cool in summer.",
                "will 後方接形容詞 cool，必須補上原形動詞 be；另外「種樹」慣用 plant trees，不用 build trees。"
            ),
            (
                "盲區 4：中式思維逐字直譯（缺乏地道英語慣用語）",
                "Along with my ages going up, my preferences have changed a lot.",
                "As I grew older, my preferences changed a lot.",
                "中文「隨著年齡增長」切勿直譯為 ages going up，地道英文慣用 as I grew older。"
            ),
            (
                "盲區 5：動賓搭配詞不自然（強行英譯）",
                "People can take a picnic and make exercises under the big trees.",
                "People can have a picnic and exercise [work out] under the big trees.",
                "野餐之最道地搭配詞為 have a picnic / go on a picnic；做運動為 exercise 或 do exercise，不用 make。"
            )
        ]
    else:
        items = [
            (
                "盲區 1：形似字混淆與重大筆誤",
                "The owner set up a sigh to warn tourists not to destory flowers.",
                "The owner set up a sign to warn tourists not to destroy flowers.",
                "sigh 為「嘆氣」，告示牌應為 sign；另 destroy (破壞) 為高頻大考字，常誤拼為 destory。"
            ),
            (
                "盲區 2：破句與殘缺子句（Sentence Fragment）",
                "Because this place means a lot to me. I was completely heartbroken.",
                "Because this place means a lot to me, I was completely heartbroken.",
                "Because 引導的是副詞從屬子句，不能獨立句點成句，必須用逗號與主句連接。"
            ),
            (
                "盲區 3：主句主要動詞遺漏（欠缺 be 動詞）",
                "Seeing the crushed blossoms, the farmer heartbroken and angry.",
                "Seeing the crushed blossoms, the farmer was heartbroken and angry.",
                "分詞構句後的主句中，heartbroken 為形容詞，必須補上主要動詞 was。"
            ),
            (
                "盲區 4：假設法條件句時態混亂",
                "If I were the owner, I were so angry that I would close the garden.",
                "If I were the owner, I would be so angry that I would close the garden.",
                "與現在事實相反的假設法，條件句用 were，主要子句助動詞應使用 would + 原形動詞 be。"
            ),
            (
                "盲區 5：平行結構不對稱（Not only... but also... 殘缺）",
                "Visitors come not only for taking pictures, but also destroy plants.",
                "Visitors come not only to take pictures, but also to destroy plants [crush blossoms].",
                "Not only 與 but also 後方接續之文法結構必須嚴格平行對稱（同為不定詞片語或介系詞片語）。"
            )
        ]

    box_h = 132 if not is_teacher else 132
    for idx, (b_title, orig_s, corr_s, exp_s) in enumerate(items, 1):
        # Container Card
        c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
        c.roundRect(left, cur_y - box_h, avail_w, box_h, 4, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.roundRect(left, cur_y - box_h, avail_w, box_h, 4, fill=0, stroke=1)

        # Title Pill
        c.setFillColor(colors.HexColor(DARK_PILL))
        c.roundRect(left + 8, cur_y - 20, 260, 16, 2, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 8)
        c.drawString(left + 14, cur_y - 15, f"第 {idx} 題｜{b_title}")

        # Content Table with ZERO glyph bugs!
        # Explicitly separate Chinese label in JHB and English quote in Georgia!
        p_orig = Paragraph(
            f'<font name=\"JHB\" color=\"#0F172A\">【原句診斷】</font> <font name=\"GeorgiaBold\" color=\"#BC1632\">\"{orig_s}\"</font>',
            ParagraphStyle('OrigW', fontSize=8, leading=10)
        )

        if not is_teacher:
            p_action = Paragraph(
                '<font name=\"JHB\" color=\"#475569\">【請挑出錯誤並於下方整句重寫】：</font>',
                ParagraphStyle('ActW', fontSize=7.5, leading=9)
            )
            content_data = [[p_orig], [p_action]]
            t_box = Table(content_data, colWidths=[avail_w - 20])
            t_box.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            bw, bh = t_box.wrap(avail_w - 20, 40)
            t_box.drawOn(c, left + 10, cur_y - 24 - bh)

            # Two generous dotted lines for student handwriting
            line1_y = cur_y - 24 - bh - 20
            line2_y = line1_y - 24

            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.8)
            c.setDash(2, 2)
            c.line(left + 20, line1_y, left + avail_w - 12, line1_y)
            c.line(left + 20, line2_y, left + avail_w - 12, line2_y)
            c.setDash()

            c.setFont('GeorgiaItalic', 7)
            c.setFillColor(colors.HexColor('#94A3B8'))
            c.drawString(left + 8, line1_y - 1, '1.')
            c.drawString(left + 8, line2_y - 1, '2.')

        else:
            p_corr = Paragraph(
                f'<font name=\"JHB\" color=\"#0F172A\">【精修解答】</font> <font name=\"GeorgiaBold\" color=\"#006A4E\">\"{corr_s}\"</font>',
                ParagraphStyle('CorrW', fontSize=8, leading=10)
            )
            p_exp = Paragraph(
                f'<font name=\"JHB\" color=\"#0F172A\">【大考考點解析】</font> <font name=\"JH\" color=\"#334155\">{exp_s}</font>',
                ParagraphStyle('ExpW', fontSize=7.5, leading=9.5)
            )
            content_data = [[p_orig], [p_corr], [p_exp]]
            t_box = Table(content_data, colWidths=[avail_w - 20])
            t_box.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            bw, bh = t_box.wrap(avail_w - 20, 95)
            t_box.drawOn(c, left + 10, cur_y - 24 - bh)

        cur_y -= (box_h + 8)

    # Footer
    c.setFont('JH', 7)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, 18, f"THE WRITING EDIT • {exam_year} 學測英文作文挑錯微講義")
    c.drawRightString(w - left, 18, '© 高中職英文寫作實戰微課程')

    c.save()
    print(f"Worksheet rendered: {out_pdf_path.name}")

# ==================== 16:9 CLASSROOM SLIDES ====================

def build_slides_option_a(exam_year, exam_topic, out_pdf_path, out_html_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=(SLIDE_W, SLIDE_H))

    if exam_year == '111':
        slide_items = [
            ("盲區 1：詞性錯置（動詞當形容詞）", "Differ parks have vary features...", "Different parks have various features...", "修飾名詞必須嚴格使用形容詞！differ/vary 皆為動詞，大考閱卷必扣文法分。"),
            ("盲區 2：主謂不一致與漏原形動詞", "Picture A have more facilities... it will very cool.", "Picture A has more facilities... it will be very cool.", "第三人稱單數動詞加 -s！will 助動詞後方接形容詞時，永遠必須補上原形 be！"),
            ("盲區 3：中式直譯與搭配詞破綻", "Along with my ages going up, people take a picnic...", "As I grew older, people have a picnic...", "戒除逐字英譯！英文表達年齡增長為 as I grew older；野餐地道動詞為 have a picnic。")
        ]
    else:
        slide_items = [
            ("盲區 1：形似字混淆與破句（Fragment）", "The owner set a sigh... Because this place means...", "The owner set a sign... Because this place means..., I was...", "告示牌是 sign (sigh是嘆氣)！Because 從屬子句絕不可單獨成句，必須連主句！"),
            ("盲區 2：主要子句漏動詞與假設法時態", "The farmer heartbroken... If I were him, I were angry...", "The farmer was heartbroken... If I were him, I would be angry...", "heartbroken 是形容詞，主句必補 was！假設法與現在事實相反，主句用 would + V！"),
            ("盲區 3：平行結構不對稱", "Visitors come not only for taking pictures, but destroy...", "Visitors come not only to take pictures, but also to protect...", "Not only 與 but also 後方詞性結構必須嚴格對稱！不定詞對不定詞、介系詞對介系詞！")
        ]

    # Slide 1: Cover Slide
    c.setFillColor(colors.HexColor('#0F172A'))
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=1, stroke=0)

    c.setFillColor(colors.HexColor('#10B981'))
    c.roundRect(60, SLIDE_H - 110, 280, 32, 6, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('JHB', 14)
    c.drawCentredString(200, SLIDE_H - 90, f'大考寫作課堂精準診斷')

    c.setFont('JHB', 34)
    c.setFillColor(colors.white)
    c.drawString(60, SLIDE_H - 180, f'{exam_year} 學測英文作文：全班三大集體盲區')

    c.setFont('JH', 16)
    c.setFillColor(colors.HexColor('#94A3B8'))
    c.drawString(60, SLIDE_H - 225, f'寫作主題：{exam_topic}  |  大考中心評分規準深度解密')

    c.setStrokeColor(colors.HexColor('#334155'))
    c.setLineWidth(1)
    c.line(60, SLIDE_H - 260, SLIDE_W - 60, SLIDE_H - 260)

    # 3 Highlights Preview
    for i, (title, _, _, _) in enumerate(slide_items):
        cx = 60 + i * 290
        cy = 100
        c.setFillColor(colors.HexColor('#1E293B'))
        c.roundRect(cx, cy, 270, 120, 8, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#38BDF8'))
        c.setFont('GeorgiaBold', 22)
        c.drawString(cx + 16, cy + 80, f"0{i+1}")
        c.setFont('JHB', 12)
        c.setFillColor(colors.white)
        c.drawString(cx + 16, cy + 45, title.split('：')[0])
        c.setFont('JH', 9.5)
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.drawString(cx + 16, cy + 22, title.split('：')[1])

    c.showPage()

    # Slides 2-4: The 3 Blind Spots
    for idx, (title, wrong_s, right_s, rule_s) in enumerate(slide_items, 1):
        c.setFillColor(colors.HexColor('#0F172A'))
        c.rect(0, 0, SLIDE_W, SLIDE_H, fill=1, stroke=0)

        # Header Pill
        c.setFillColor(colors.HexColor('#EF4444'))
        c.roundRect(60, SLIDE_H - 70, 160, 28, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 12)
        c.drawCentredString(140, SLIDE_H - 52, f"集體盲區 0{idx}")

        c.setFont('JHB', 22)
        c.setFillColor(colors.white)
        c.drawString(240, SLIDE_H - 52, title)

        # Bento Card Left: Original Buggy Sentence
        c.setFillColor(colors.HexColor('#1E293B'))
        c.roundRect(60, 170, 400, 260, 10, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor('#EF4444'))
        c.setLineWidth(1.5)
        c.roundRect(60, 170, 400, 260, 10, fill=0, stroke=1)

        c.setFillColor(colors.HexColor('#EF4444'))
        c.setFont('JHB', 13)
        c.drawString(85, 395, '❌  全班典型常犯原句 (Original Trap)')
        c.setFont('GeorgiaBold', 15)
        c.setFillColor(colors.HexColor('#FCA5A5'))
        p_wrong = Paragraph(f'"{wrong_s}"', ParagraphStyle('SlW', fontName='GeorgiaBold', fontSize=14, leading=20, textColor=colors.HexColor('#FCA5A5')))
        p_wrong.wrapOn(c, 350, 160)
        p_wrong.drawOn(c, 85, 270)

        # Bento Card Right: Revision
        c.setFillColor(colors.HexColor('#1E293B'))
        c.roundRect(500, 170, 400, 260, 10, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor('#10B981'))
        c.setLineWidth(1.5)
        c.roundRect(500, 170, 400, 260, 10, fill=0, stroke=1)

        c.setFillColor(colors.HexColor('#10B981'))
        c.setFont('JHB', 13)
        c.drawString(525, 395, '✨  地道高分精修句 (The Writing Edit)')
        p_right = Paragraph(f'"{right_s}"', ParagraphStyle('SlR', fontName='GeorgiaBold', fontSize=14, leading=20, textColor=colors.HexColor('#6EE7B7')))
        p_right.wrapOn(c, 350, 160)
        p_right.drawOn(c, 525, 270)

        # Bottom Master Rule Card
        c.setFillColor(colors.HexColor('#1E293B'))
        c.roundRect(60, 50, 840, 95, 8, fill=1, stroke=0)
        c.setStrokeColor(colors.HexColor('#38BDF8'))
        c.setLineWidth(1.2)
        c.roundRect(60, 50, 840, 95, 8, fill=0, stroke=1)

        c.setFillColor(colors.HexColor('#38BDF8'))
        c.setFont('JHB', 13)
        c.drawString(85, 115, '💡  大考閱卷心法與黃金解題鐵律：')
        p_rule = Paragraph(rule_s, ParagraphStyle('SlRule', fontName='JH', fontSize=12, leading=17, textColor=colors.HexColor('#E2E8F0')))
        p_rule.wrapOn(c, 790, 60)
        p_rule.drawOn(c, 85, 68)

        c.showPage()

    c.save()
    print(f"Slides PDF rendered: {out_pdf_path.name}")

    # Generate HTML Slides
    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{exam_year} 學測英文作文：全班三大集體盲區課堂簡報</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0b1120; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        .slide-card {{ transition: transform 0.2s ease, box-shadow 0.2s ease; }}
        .slide-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 24px -10px rgba(0,0,0,0.5); }}
    </style>
</head>
<body class="p-6 md:p-12 max-w-6xl mx-auto">
    <header class="mb-12 border-b border-slate-800 pb-8">
        <div class="inline-block bg-emerald-500 text-slate-950 font-bold px-3 py-1 rounded-md text-sm mb-3">大考寫作課堂精準診斷</div>
        <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-3">{exam_year} 學測英文作文：全班三大集體盲區</h1>
        <p class="text-slate-400 text-lg">寫作主題：{exam_topic} | 大考中心 108 課綱評分規準深度解密</p>
    </header>

    <main class="space-y-12">
"""
    for idx, (title, wrong_s, right_s, rule_s) in enumerate(slide_items, 1):
        html_content += f"""
        <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 slide-card">
            <div class="flex items-center space-x-3 mb-6">
                <span class="bg-rose-600 text-white font-bold px-3 py-1 rounded-lg text-sm">集體盲區 0{idx}</span>
                <h2 class="text-xl md:text-2xl font-bold text-white">{title}</h2>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6 mb-6">
                <div class="bg-slate-950 border border-rose-500/40 rounded-xl p-5">
                    <div class="text-rose-400 font-bold text-sm mb-2 flex items-center">
                        <span class="mr-2">❌</span> 全班典型常犯原句 (Original Trap)
                    </div>
                    <p class="font-serif italic text-rose-200 text-lg">"{wrong_s}"</p>
                </div>
                
                <div class="bg-slate-950 border border-emerald-500/40 rounded-xl p-5">
                    <div class="text-emerald-400 font-bold text-sm mb-2 flex items-center">
                        <span class="mr-2">✨</span> 地道高分精修句 (The Writing Edit)
                    </div>
                    <p class="font-serif italic text-emerald-200 text-lg font-semibold">"{right_s}"</p>
                </div>
            </div>

            <div class="bg-slate-800/60 border border-sky-500/30 rounded-xl p-4 md:p-5">
                <div class="text-sky-400 font-bold text-sm mb-1 flex items-center">
                    <span class="mr-2">💡</span> 大考閱卷心法與黃金解題鐵律
                </div>
                <p class="text-slate-300 text-base leading-relaxed">{rule_s}</p>
            </div>
        </section>
"""

    html_content += """
    </main>

    <footer class="mt-16 text-center text-slate-500 text-sm border-t border-slate-800 pt-8">
        THE WRITING EDIT • 高中職英文寫作雙軌診斷系統 • 紀老師 Sylvia 教學研習專用
    </footer>
</body>
</html>
"""
    with open(out_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Slides HTML rendered: {out_html_path.name}")

# ==================== MASTER EXECUTION ====================

def run_all():
    print("="*60)
    print("STARTING MASTER OPTION A PRODUCTION RUN")
    print("="*60)

    # 1. Process 111 Topic (Park Planning)
    print("\n--- [1/2] Processing 111 Topic ---")
    # 111 Student 01
    p1_111_s01 = TMP / "111_s01_p1_opt_a.pdf"
    p2_111_s01 = TMP / "111_s01_p2_opt_a.pdf"
    render_page_1_option_a(DATA_111_S01, p1_111_s01)
    render_page_2_option_a(DATA_111_S01, p2_111_s01)
    combine_to_print_pdf(p1_111_s01, p2_111_s01, OUT_111 / "301班_第1篇_前兩頁雙面列印_雜誌風.pdf")

    # 111 CEEC 01
    p1_111_ceec = TMP / "111_ceec_p1_opt_a.pdf"
    p2_111_ceec = TMP / "111_ceec_p2_opt_a.pdf"
    render_page_1_option_a(DATA_111_CEEC, p1_111_ceec)
    render_page_2_option_a(DATA_111_CEEC, p2_111_ceec)
    combine_to_print_pdf(p1_111_ceec, p2_111_ceec, OUT_111 / "111學測英文作文_大考中心佳作01_前兩頁雙面列印_雜誌風.pdf")

    # 111 Worksheets & Slides
    build_worksheet_option_a('111', '規劃理想新公園', False, OUT_111 / "111學測作文_大家來找碴_挑錯微講義_學用版.pdf")
    build_worksheet_option_a('111', '規劃理想新公園', True, OUT_111 / "111學測作文_大家來找碴_挑錯微講義_教用解答版.pdf")
    build_slides_option_a('111', '規劃理想新公園', OUT_111 / "111學測作文_全班三大集體盲區_課堂投影簡報.pdf", OUT_111 / "111學測作文_全班三大集體盲區_課堂投影簡報.html")

    # 2. Process 110 Topic (Flower Garden Intrusion)
    print("\n--- [2/2] Processing 110 Topic ---")
    # 110 Student 01
    p1_110_s01 = TMP / "110_s01_p1_opt_a.pdf"
    p2_110_s01 = TMP / "110_s01_p2_opt_a.pdf"
    render_page_1_option_a(DATA_110_S01, p1_110_s01)
    render_page_2_option_a(DATA_110_S01, p2_110_s01)
    combine_to_print_pdf(p1_110_s01, p2_110_s01, OUT_110 / "Student_01_前兩頁雙面列印_雜誌風.pdf")

    # 110 Student 35
    p1_110_s35 = TMP / "110_s35_p1_opt_a.pdf"
    p2_110_s35 = TMP / "110_s35_p2_opt_a.pdf"
    render_page_1_option_a(DATA_110_S35, p1_110_s35)
    render_page_2_option_a(DATA_110_S35, p2_110_s35)
    combine_to_print_pdf(p1_110_s35, p2_110_s35, OUT_110 / "Student_35_前兩頁雙面列印_雜誌風.pdf")

    # 110 CEEC 01
    p1_110_ceec = TMP / "110_ceec_p1_opt_a.pdf"
    p2_110_ceec = TMP / "110_ceec_p2_opt_a.pdf"
    render_page_1_option_a(DATA_110_CEEC, p1_110_ceec)
    render_page_2_option_a(DATA_110_CEEC, p2_110_ceec)
    combine_to_print_pdf(p1_110_ceec, p2_110_ceec, OUT_110 / "大考中心佳作01_前兩頁雙面列印_雜誌風.pdf")

    # 110 Worksheets & Slides
    build_worksheet_option_a('110', '花圃踩踏情境題', False, OUT_110 / "110學測作文_大家來找碴_挑錯微講義_學用版.pdf")
    build_worksheet_option_a('110', '花圃踩踏情境題', True, OUT_110 / "110學測作文_大家來找碴_挑錯微講義_教用解答版.pdf")
    build_slides_option_a('110', '花圃踩踏情境題', OUT_110 / "110學測作文_全班三大集體盲區_課堂投影簡報.pdf", OUT_110 / "110學測作文_全班三大集體盲區_課堂投影簡報.html")

    print("\n" + "="*60)
    print("ALL PRODUCTION RUNS SUCCESSFULLY COMPLETED!")
    print("="*60)

if __name__ == '__main__':
    run_all()
