# -*- coding: utf-8 -*-
"""
build_master_v15.py
Master refinement script for Sylvia's English Composition Diagnostic Suite:
1. Student 01, Student 35, CEEC 01:
   - Page 1: Precision non-overlapping red annotations, brackets [ ] for phrase rewrites,
     strikeout lines for errors, caret ^ for insertions, all floating safely in interlinear whitespace.
   - Page 2: Clean Magazine-style Zoning (Part A Scores & Comments, Part B Personalized Revision Tasks,
     Part C Reflection & Teacher Sign-off). Strictly Black/Grayscale palette for photocopiers.
2. 1-Page Spot-the-Error Worksheets (大家來找碴):
   - Pure typography (NO emojis/special symbols to prevent square box □ glyph bugs).
   - Student Practice & Teacher Key (45pt safety bleed margins, zero truncation).
3. 16:9 Classroom Slides (全班三大集體盲區):
   - Huge 20-40pt typography for classroom projection legibility.
   - Modern Bento-card visual comparison design.
   - PDF & HTML dual output.
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

# Register Fonts
pdfmetrics.registerFont(ttfonts.TTFont('JH', 'C:/Windows/Fonts/msjh.ttc'))
pdfmetrics.registerFont(ttfonts.TTFont('JHB', 'C:/Windows/Fonts/msjhbd.ttc'))
pdfmetrics.registerFont(ttfonts.TTFont('Georgia', 'C:/Windows/Fonts/georgia.ttf'))
pdfmetrics.registerFont(ttfonts.TTFont('GeorgiaBold', 'C:/Windows/Fonts/georgiab.ttf'))
pdfmetrics.registerFont(ttfonts.TTFont('Hand', 'C:/Windows/Fonts/Inkfree.ttf'))

# Output & Temp Dirs
OUT_DIR = Path("H:/我的雲端硬碟/# Sylvia's Workspace/01 講師素材/[置頂] My Workshop Materials/研習素材包/學測英文作文學生原稿/110學測_亂入花圃學生稿/去識別化版之學生作文/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP = Path("C:/Users/user/.gemini/antigravity/brain/7148bf21-122a-418b-a09d-b71b1a4f0440/scratch")

# Color Palettes
# Page 1 Accents
GREEN = '#006A4E'
RED = '#BC1632'
BLUE = '#164FB2'

# Page 2 Strictly Black & Grayscale Palette (Photocopier Safe)
DARK_PILL = '#1E293B'    # Solid deep charcoal / black for header pills
BORDER_COLOR = '#CBD5E1' # Crisp neutral 0.8pt borders
TEXT_DARK = '#0F172A'    # Primary readable black text
TEXT_MUTED = '#475569'   # Secondary dark slate text
LINE_DOTTED = '#94A3B8'  # Dotted lines for student handwriting
BG_LIGHT_GRAY = '#F8FAFC'# Very faint gray background

# Slide Dimensions
SLIDE_W, SLIDE_H = 960, 540

# ==================== DATA DEFINITIONS ====================

DATA_S01 = {
    'id': 'Student_01',
    'title': '去識別化 Student 01',
    'subtitle': '學測英文作文個人診斷與修訂歷程單',
    'words': 118,
    'total': 10.0,
    'grade_tier': '及格 (第 3 級分)',
    'total_desc': '實測 118 字（達 120 字基本要求）；兩段式結構完整；扣分 0。',
    'scores': [
        ('內容 (Content)', '2.5', '切合花圃被破壞之情境與立場，惟首段描述僅 40 字，缺少現場感官細節。'),
        ('組織 (Organization)', '2.5', '兩段架構分明，惟第二段因果句型串接較重複 (I would feel... because...)。'),
        ('文法 (Grammar)', '2.5', '以簡單句為主，第二段假設法時態前後不一致 (were 誤用，需改為 would be)。'),
        ('字彙 (Vocabulary)', '2.5', '詞彙生活化，出現形似字混淆：sigh (嘆氣) 誤寫為 sign (告示牌)。')
    ],
    'feedback_zh': '明確掌握花圃主人的心痛與憤怒，立場清晰。建議：第 1 段多描寫 1-2 句遊客踩踏的動作細節；訂正 sign 的拼字；並注意假設法時態的前後一致性。',
    'feedback_en': "You clearly understand the garden owner's feelings. For the next draft, add 1-2 visual sentences in paragraph 1, correct the spelling of 'sign', and keep verb tenses consistent.",
    'tasks': [
        ('【任務 1：字彙拼寫與搭配詞】請將第 2 行 sigh 改為 sign，並將 public manners 替換為自然道地的 good manners：', 1),
        ('【任務 2：句型串接與轉折簡化】請將第 3 行「Because of that, they walk...」簡化為「Therefore, they walk...」：', 1),
        ('【任務 3：細節增補挑戰】請在第 1 段補寫 1 句（約 15 字），生動描寫遊客為了拍照而踐踏花朵的動作：', 2)
    ],
    'annotations': [
        # Line 1: in a field of flowers -> [in a field of flowers] = in a flower garden
        {'type': 'bracket', 'x1': 0.52, 'x2': 0.92, 'y': 0.070, 'text': '= in a flower garden', 'dy': 22},
        # Line 2: sigh -> sign
        {'type': 'strike', 'x': 0.58, 'w': 0.09, 'y': 0.145, 'text': 'sign (告示牌)', 'tag': 'Sp', 'dy': 20},
        # Line 3: Because of that -> Therefore,
        {'type': 'strike', 'x': 0.22, 'w': 0.22, 'y': 0.219, 'text': 'Therefore,', 'tag': 'W', 'dy': 20},
        # Line 5: heartbroken with caret ^
        {'type': 'caret', 'x': 0.46, 'y': 0.368, 'text': 'heartbroken', 'dy': 18},
        # Line 7: were -> would be
        {'type': 'strike', 'x': 0.40, 'w': 0.08, 'y': 0.526, 'text': 'would be', 'tag': 'G', 'dy': 20},
        # Line 10: public manners -> good manners
        {'type': 'strike', 'x': 0.06, 'w': 0.25, 'y': 0.772, 'text': 'good manners', 'tag': 'W', 'dy': 20},
    ]
}

DATA_S35 = {
    'id': 'Student_35',
    'title': '去識別化 Student 35 (30135)',
    'subtitle': '學測英文作文個人診斷與修訂歷程單',
    'words': 167,
    'total': 14.0,
    'grade_tier': '良好 (第 4 級分)',
    'total_desc': '實測 167 字且分兩段，篇幅達標；結尾昇華「欣賞始於尊重」；扣分 0。',
    'scores': [
        ('內容 (Content)', '3.5', '選定花圃主人立場切題，末句「欣賞始於尊重」思想深刻；惟首段實景描摹略少。'),
        ('組織 (Organization)', '3.5', '兩段式架構分明，首尾呼應；惟第二段出現 Because 從屬子句獨立成句之破句。'),
        ('文法 (Grammar)', '3.5', '能運用假設法條件句；惟出現 Because 破句（Sentence Fragment），需改善。'),
        ('字彙 (Vocabulary)', '3.5', '詞彙豐富且切題；惟有明顯筆誤 destory (應為 destroy)，且 space owners 宜修為 garden owners。')
    ],
    'feedback_zh': '結尾點出「真正的欣賞始於尊重」展現難能可貴的思想深度！第 1 段宜加強對花圃遭踐踏的視覺實景描摹，並將以 Because 開頭的破句與前句合併為完整複合句。',
    'feedback_en': "Your concluding insight that 'true appreciation begins with respect' elevates the moral depth of your essay. Strengthen paragraph 1 by anchoring it in visible flowerbed details, and connect the fragment starting with 'Because'.",
    'tasks': [
        ('【任務 1：拼字與選詞】修正 destory 為 destroy，並將 space owners 替換為 garden owners / growers：', 1),
        ('【任務 2：破句重組】將第 6 句「Because this place means a lot to me...」與前句合併為完整複合句：', 1),
        ('【任務 3：感官細節擴充】在第 1 段增寫 1 句（約 15-20 字），描繪花瓣遭遊客踐踏倒伏的畫面：', 2)
    ],
    'annotations': [
        {'type': 'bracket', 'x1': 0.10, 'x2': 0.32, 'y': 0.08, 'text': '= In modern society,', 'dy': 22},
        {'type': 'bracket', 'x1': 0.14, 'x2': 0.45, 'y': 0.16, 'text': '= visit floral exhibitions', 'dy': 22},
        {'type': 'strike', 'x': 0.74, 'w': 0.12, 'y': 0.35, 'text': 'destroy', 'tag': 'Sp', 'dy': 20},
        {'type': 'strike', 'x': 0.50, 'w': 0.22, 'y': 0.44, 'text': 'garden owners', 'tag': 'W', 'dy': 20},
        {'type': 'strike', 'x': 0.08, 'w': 0.16, 'y': 0.52, 'text': 'This is because', 'tag': 'G', 'dy': 20},
        {'type': 'strike', 'x': 0.62, 'w': 0.18, 'y': 0.86, 'text': 'not only for..., but also for...', 'tag': 'G', 'dy': 20},
    ]
}

DATA_CEEC = {
    'id': '大考中心佳作01',
    'title': '大考中心公告之佳作 01',
    'subtitle': '學測英文作文個人診斷與修訂歷程單 (特優典範篇)',
    'words': 284,
    'total': 18.5,
    'grade_tier': '特優 (第 5 級分 / 全國前 1%)',
    'total_desc': '實測 284 字，篇幅宏大、層次深邃；思維圓融、文字極致流暢；扣分 0。',
    'scores': [
        ('內容 (Content)', '5.0', '以遊客自省立場出發，深刻剖析從眾心理與私慾盲點，思維深刻具高度說服力。'),
        ('組織 (Organization)', '4.5', '起承轉合極致自然，轉折詞與分詞構句無縫銜接，行文如行雲流水。'),
        ('文法 (Grammar)', '4.5', '高階句型（倒裝句、分詞構句、複合子句）融會貫通，幾無語法瑕疵。'),
        ('字彙 (Vocabulary)', '4.5', '用字精準典雅，展現驚人之搭配詞掌控力（如 aesthetic appreciation, self-discipline 等）。')
    ],
    'feedback_zh': '通篇兼具文學美感與哲理省思，以遊客第一人稱自省視角切入，深刻剖析從眾自私心理，文字流暢純熟，足為全國高中生之終極學習標竿。',
    'feedback_en': "A masterclass in high-school composition. Your reflective stance from the tourist's self-awareness moves far beyond cliches. Superb vocabulary and varied sentence architecture.",
    'tasks': [
        ('【任務 1：哲理名句提煉】請從本文挑選 1 句你最欣賞的哲理金句，並試著仿寫於下方：', 1),
        ('【任務 2：高階轉折串接】請找出本文如何運用分詞構句連結轉折，並造出 1 個相似句型：', 1),
        ('【任務 3：典範修辭移植】將本文精選搭配詞「aesthetic appreciation」融入自己的下一篇作文構思中：', 2)
    ],
    'annotations': [
        {'type': 'bracket', 'x1': 0.08, 'x2': 0.40, 'y': 0.10, 'text': 'Magnificent opening!', 'dy': 20},
        {'type': 'bracket', 'x1': 0.55, 'x2': 0.92, 'y': 0.35, 'text': 'Exquisite vocabulary', 'dy': 20},
        {'type': 'bracket', 'x1': 0.10, 'x2': 0.45, 'y': 0.65, 'text': 'Superb parallel structure', 'dy': 20},
    ]
}

# ==================== PAGE 1 ENGINE ====================

def render_page_1_clean(data, out_pdf_path):
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
    c.setFillColor(colors.HexColor('#475569'))
    c.drawRightString(w - left, h - 25, '學測英文作文個人診斷與修訂歷程單 (正面)')

    # Title & Metadata
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 52, data['title'])
    c.setFont('JH', 9.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, h - 68, f"110 學測英文作文（花圃踐踏情境題） |  實測字數：{data['words']} 字  |  總分：{data['total']} 分")

    # Score Pill Badge on Top Right
    c.setFillColor(colors.HexColor(DARK_PILL))
    c.roundRect(w - left - 110, h - 72, 110, 26, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont('GeorgiaBold', 13)
    c.drawCentredString(w - left - 55, h - 55, f"{data['total']} / 20")
    c.setFont('JH', 7.5)
    c.drawCentredString(w - left - 55, h - 66, data['grade_tier'].split(' ')[0])

    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 80, w - left, h - 80)

    # Handwriting Image Placement
    s_id = data['id']
    if s_id == 'Student_01':
        img_p = TMP / "s01_enhanced_crop.png"
        im = Image.open(img_p)
        im_w, im_h = im.size
        draw_w = avail_w
        draw_h = draw_w * (im_h / im_w)
        draw_x = left
        draw_y = h - 95 - draw_h

        c.drawImage(str(img_p), draw_x, draw_y, width=draw_w, height=draw_h)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.rect(draw_x, draw_y, draw_w, draw_h)
        draw_annotations(c, draw_x, draw_y, draw_w, draw_h, data['annotations'])

    elif s_id == 'Student_35':
        img_p = TMP / "s35_full_enhanced_crop.png"
        im = Image.open(img_p)
        im_w, im_h = im.size
        draw_w = avail_w
        draw_h = min(draw_w * (im_h / im_w), h - 140)
        draw_x = left
        draw_y = h - 95 - draw_h

        c.drawImage(str(img_p), draw_x, draw_y, width=draw_w, height=draw_h)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.rect(draw_x, draw_y, draw_w, draw_h)
        draw_annotations(c, draw_x, draw_y, draw_w, draw_h, data['annotations'])

    else: # CEEC 01 Two Columns
        col1_p = TMP / "ceec_col1_enhanced.png"
        col2_p = TMP / "ceec_col2_enhanced.png"
        col_w = (avail_w - 14) / 2
        im1 = Image.open(col1_p)
        draw_h = col_w * (im1.height / im1.width)
        draw_h = min(draw_h, h - 140)
        draw_y = h - 95 - draw_h

        c.drawImage(str(col1_p), left, draw_y, width=col_w, height=draw_h)
        c.drawImage(str(col2_p), left + col_w + 14, draw_y, width=col_w, height=draw_h)
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.rect(left, draw_y, col_w, draw_h)
        c.rect(left + col_w + 14, draw_y, col_w, draw_h)
        draw_annotations(c, left, draw_y, avail_w, draw_h, data['annotations'])

    # Bottom Folio
    c.setFont('JH', 8)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, 24, '紅筆手寫處為教師個別診斷標註  ·  完整分項評量、修訂任務與反思請見背面')
    c.setFont('GeorgiaBold', 9)
    c.drawRightString(w - left, 24, 'PAGE 01 / 02')

    c.save()
    print(f"Rendered Page 1: {out_pdf_path.name}")

def draw_annotations(c, nx, ny, nw, nh, annotations):
    for a in annotations:
        ay = ny + (1.0 - a['y']) * nh
        t = a['type']

        if t == 'bracket':
            bx1 = nx + a['x1'] * nw
            bx2 = nx + a['x2'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.4)
            # Draw brackets [ and ]
            c.line(bx1, ay - 3, bx1, ay + 12)
            c.line(bx1, ay - 3, bx1 + 6, ay - 3)
            c.line(bx1, ay + 12, bx1 + 6, ay + 12)
            c.line(bx2, ay - 3, bx2, ay + 12)
            c.line(bx2 - 6, ay - 3, bx2, ay - 3)
            c.line(bx2 - 6, ay + 12, bx2, ay + 12)
            # Red text above
            c.setFont('Hand', 11.5)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(bx1 + 10, ay + a.get('dy', 22), a['text'])

        elif t == 'strike':
            ax = nx + a['x'] * nw
            aw = a['w'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.6)
            c.line(ax, ay + 4, ax + aw, ay + 4) # Strikeout line
            # Red text above
            c.setFont('Hand', 11.5)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(ax, ay + a.get('dy', 20), a['text'])
            if 'tag' in a:
                c.setFillColor(colors.HexColor(RED))
                c.roundRect(ax - 25, ay + a.get('dy', 20) - 2, 22, 11, 2, fill=1, stroke=0)
                c.setFillColor(colors.white)
                c.setFont('Helvetica-Bold', 7)
                c.drawString(ax - 23, ay + a.get('dy', 20) + 1.5, a['tag'])

        elif t == 'caret':
            cx = nx + a['x'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.5)
            # Caret ^
            c.line(cx - 4, ay - 2, cx, ay + 8)
            c.line(cx, ay + 8, cx + 4, ay - 2)
            # Red text above
            c.setFont('Hand', 11.5)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(cx - 10, ay + a.get('dy', 18), a['text'])

# ==================== PAGE 2 ENGINE (ZONED & BLACK-AND-WHITE SAFE) ====================

def render_page_2_zoned(data, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    left = 40
    width = w - 80

    # Top Bar (Photocopier Friendly Dark Bar)
    c.setStrokeColor(colors.HexColor(DARK_PILL))
    c.setLineWidth(1.2)
    c.line(left, h - 28, left + width, h - 28)
    c.setFont('GeorgiaBold', 9.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 22, 'THE WRITING EDIT  |  DIAGNOSTIC & REVISION REPORT')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(left + width, h - 22, '學測英文作文個人診斷與修訂歷程單 (背面)')

    curr_y = h - 38

    def draw_pill_badge(c, x, y, text, w_badge=220):
        c.setFillColor(colors.HexColor(DARK_PILL))
        c.roundRect(x, y - 16, w_badge, 17, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 9)
        c.drawString(x + 8, y - 12.5, text)

    # ==================== PART A ====================
    part_a_h = 210
    draw_pill_badge(c, left, curr_y, 'PART A  評分依據與教師評語', 190)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, curr_y - part_a_h, width, part_a_h - 18, 4, fill=0, stroke=1)

    # Summary inside Part A
    ay = curr_y - 28
    c.setFont('JHB', 12)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, ay - 6, f"總分：{data['total']} / 20 分")
    c.setFont('JH', 9.5)
    c.drawString(left + 150, ay - 5, f"大考級距：{data['grade_tier']}")
    c.drawRightString(left + width - 12, ay - 5, data['total_desc'])

    # Rubric Table inside Part A
    table_rows = [
        [Paragraph('<b>分項評量指標</b>', ParagraphStyle('th1', fontName='JHB', fontSize=8.5, leading=11, textColor=colors.HexColor(TEXT_DARK))),
         Paragraph('<b>得分</b>', ParagraphStyle('th2', fontName='JHB', fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor(TEXT_DARK))),
         Paragraph('<b>大考中心評分依據與具體診斷</b>', ParagraphStyle('th3', fontName='JHB', fontSize=8.5, leading=11, textColor=colors.HexColor(TEXT_DARK)))]
    ]
    for r_label, r_score, r_desc in data['scores']:
        table_rows.append([
            Paragraph(f"<b>{r_label}</b>", ParagraphStyle('rl', fontName='JH', fontSize=8.5, leading=11)),
            Paragraph(f"<b>{r_score}</b>", ParagraphStyle('rs', fontName='GeorgiaBold', fontSize=9, alignment=1)),
            Paragraph(r_desc, ParagraphStyle('rd', fontName='JH', fontSize=8, leading=11))
        ])

    t = Table(table_rows, colWidths=[105, 45, width - 174])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor(BORDER_COLOR)),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    _, th = t.wrap(width - 24, 200)
    t.drawOn(c, left + 12, ay - 14 - th)

    # Feedback inside Part A
    f_y = ay - 20 - th
    c.setFont('JHB', 9)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, f_y, '【教師評語】')
    c.setFont('JH', 8.5)
    c.drawString(left + 80, f_y, f"中文：{data['feedback_zh'][:56]}...")
    c.drawString(left + 80, f_y - 12, f"英文：{data['feedback_en'][:70]}...")

    curr_y -= (part_a_h + 12)

    # ==================== PART B ====================
    part_b_h = 180
    draw_pill_badge(c, left, curr_y, 'PART B  個別化修訂任務 (請於下方橫線直接訂正)', 280)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, curr_y - part_b_h, width, part_b_h - 18, 4, fill=0, stroke=1)

    by = curr_y - 30
    for t_desc, num_lines in data['tasks']:
        c.setFont('JHB', 8.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(left + 12, by, t_desc)
        by -= 14
        for l_i in range(num_lines):
            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.7)
            c.setDash(2, 2)
            c.line(left + 12, by, left + width - 12, by)
            c.setDash()
            by -= 18
        by -= 6

    curr_y -= (part_b_h + 12)

    # ==================== PART C ====================
    part_c_h = 240
    draw_pill_badge(c, left, curr_y, 'PART C  學習歷程反思與教師核閱 (學習歷程檔案實作證明)', 320)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, curr_y - part_c_h, width, part_c_h - 18, 4, fill=0, stroke=1)

    cy = curr_y - 28
    # Q1: Continuous Scale Slider Bar (No preset labels!)
    c.setFont('JHB', 9)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, cy, '1. 本次寫作自我滿意度定位（請在 1～5 軸線上標記你對本次表現的感受位置）：')

    bar_x = left + 45
    bar_w = width - 90
    bar_y = cy - 20
    c.setStrokeColor(colors.HexColor('#94A3B8'))
    c.setLineWidth(2)
    c.line(bar_x, bar_y, bar_x + bar_w, bar_y)
    for s_idx in range(5):
        nx = bar_x + (bar_w / 4) * s_idx
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.HexColor(DARK_PILL))
        c.setLineWidth(1.2)
        c.circle(nx, bar_y, 8, fill=1, stroke=1)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.setFont('GeorgiaBold', 9.5)
        c.drawCentredString(nx, bar_y - 3.5, str(s_idx + 1))

    cy -= 46

    # Q2: 4-Part Reflection Grid
    c.setFont('JHB', 9)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, cy, '2. 學習歷程反思紀錄（請簡要填寫下列 4 個維度）：')
    cy -= 10

    ref_w = (width - 32) / 2
    ref_h = 58
    boxes = [
        (left + 12, cy - ref_h, '【本次作品亮點】這篇我寫得最好的一點是：'),
        (left + 20 + ref_w, cy - ref_h, '【遭遇寫作卡點】最困擾我或花最多時間的是：'),
        (left + 12, cy - ref_h*2 - 8, '【我的修訂策略】看過批改後，我具體修正了：'),
        (left + 20 + ref_w, cy - ref_h*2 - 8, '【給下篇作文的一句話】下次動筆前我要提醒自己：')
    ]

    for bx, by_box, title in boxes:
        c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.6)
        c.roundRect(bx, by_box, ref_w, ref_h, 3, fill=1, stroke=1)
        c.setFont('JHB', 8)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(bx + 6, by_box + ref_h - 12, title)
        # 2 writing lines inside box
        c.setStrokeColor(colors.HexColor(LINE_DOTTED))
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(bx + 6, by_box + ref_h - 26, bx + ref_w - 6, by_box + ref_h - 26)
        c.line(bx + 6, by_box + ref_h - 42, bx + ref_w - 6, by_box + ref_h - 42)
        c.setDash()

    # Q3: Teacher Verification & Stamp Row
    stamp_y = cy - ref_h*2 - 28
    c.setFont('JHB', 8.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, stamp_y, '教師核閱章 / 簽名：____________________    修訂等級核定：[  ] 達標特優    [  ] 通過良好    [  ] 需再面談')
    c.drawRightString(left + width - 12, stamp_y, '核閱日期：_____ 年 ___ 月 ___ 日')

    # Bottom Folio
    c.setFont('GeorgiaBold', 9)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(w - left, 22, 'PAGE 02 / 02')

    c.save()
    print(f"Rendered Page 2: {out_pdf_path.name}")

# ==================== 1-PAGE SPOT-THE-ERROR WORKSHEET (STUDENT & TEACHER) ====================

QUESTIONS_DATA = [
    {
        'num': 1,
        'tag': '盲區 1：破句急救 (Sentence Fragment)',
        'orig': 'The flower garden owner was heartbroken. Because thoughtless tourists destroyed his flowers.',
        'diag': '【破綻診斷】Because 引導從屬子句，缺乏主要子句支撐不能單獨成句。大考閱卷嚴重扣分。',
        'correct': '【標準改寫】The garden owner was heartbroken, because thoughtless tourists destroyed his flowers.（或改用 This was because...）',
        'script': '【教師引導話術】「大家看第 1 題句首的 Because，從屬子句一定要依靠主要子句！改成逗號串接，秒救 1 分！」'
    },
    {
        'num': 2,
        'tag': '盲區 2：形似字抓漏 (Confusing Word Pair)',
        'orig': 'Many visitors completely ignored the warning sigh that clearly said "Do not enter."',
        'diag': '【破綻診斷】sigh 是「嘆氣」，告示牌必須拼寫為 sign。said 亦可精修為 reads。',
        'correct': '【標準改寫】Many visitors completely ignored the warning sign that clearly read, "Do not enter."',
        'script': '【教師引導話術】「看到 sigh 老師都要嘆氣了！告示牌是 sign，請大家把 g 與 n 的位置看清楚，大考常考！」'
    },
    {
        'num': 3,
        'tag': '盲區 3：假設法時態一致 (Subjunctive Mood)',
        'orig': 'If I were the owner, I would feel angry because the blossoms are trampled by strangers.',
        'diag': '【破綻診斷】前段已建立假設法（If I were..., I would feel...），想像情境下後方的 are 須改為 would be。',
        'correct': '【標準改寫】If I were the owner, I would feel angry because the blossoms would be trampled by strangers.',
        'script': '【教師引導話術】「你現在不是花園主人，這是虛擬情境，後面花朵被踩也要維持時態一致，用 would be！」'
    },
    {
        'num': 4,
        'tag': '盲區 4：中式直譯詞彙升級 (Collocation Upgrade)',
        'orig': 'Those selfish tourists have no public manners and they just want to take pictures for internet.',
        'diag': '【破綻診斷】public manners 屬中式直譯，宜改為 good manners 或 civic decency；for internet 應為 for social media。',
        'correct': '【標準改寫】Those selfish tourists showed no respect for rules and only cared about taking photos for social media.',
        'script': '【教師引導話術】「『公德心』不要直接翻 public manners！用 respect for rules 或 civic decency 更道地！」'
    },
    {
        'num': 5,
        'tag': '盲區 5：消除機械式重複句型 (Repetitive Sentence Starters)',
        'orig': 'I would feel sad because the flowers were ruined. I would also feel angry because people broke the rules.',
        'diag': '【破綻診斷】連續兩句重複「I would feel... because...」，語氣機械單調，缺乏段落層次感。',
        'correct': '【標準改寫】On the one hand, I would be heartbroken by the ruined flowers; on the other hand, I would feel angry at the rule-breaking.',
        'script': '【教師引導話術】「連用兩次 I would feel... because 讀起來太生硬！善用 On the one hand... on the other hand 展現對比層次！」'
    }
]

def render_worksheet_master(is_teacher=False, out_path=None):
    c = canvas.Canvas(str(out_path), pagesize=A4)
    w, h = A4
    left = 45
    width = w - 90  # 45pt safety margins on both sides!

    # Top Ribbon
    c.setFillColor(colors.HexColor(GREEN))
    c.rect(0, h - 8, w, 8, fill=1, stroke=0)
    c.setFont('GeorgiaBold', 9)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(left, h - 25, 'THE WRITING EDIT  |  CLASSROOM SPOT-THE-ERROR CHALLENGE')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    lbl = '【教師解答與引導版】Teacher Answer Key' if is_teacher else '【學生隨堂練習版】Student Practice Worksheet'
    c.drawRightString(w - left, h - 25, f"110 學測英文作文  |  {lbl}")

    # Title
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    t_text = '英文作文「大家來找碴」：全班高頻破綻挑錯微講義' + (' (教師解析版)' if is_teacher else ' (學生練習版)')
    c.drawString(left, h - 46, t_text)
    c.setFont('JH', 9.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, h - 60, '以下 5 個句子均來自真實學生學測模擬考原稿。請仔細觀察，找出破綻並重新改寫符合大考要求的句子。')

    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 68, w - left, h - 68)

    curr_y = h - 80

    for q in QUESTIONS_DATA:
        # Question Tag Badge
        tag_col = RED if is_teacher else DARK_PILL
        c.setFillColor(colors.HexColor(tag_col))
        c.roundRect(left, curr_y - 14, 180, 16, 2, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 8.5)
        c.drawString(left + 6, curr_y - 11.5, q['tag'])

        c.setFont('GeorgiaBold', 10.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(left + 190, curr_y - 11, f"Question 0{q['num']}")
        curr_y -= 20

        # Original Sentence Box
        c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.roundRect(left, curr_y - 24, width, 22, 3, fill=1, stroke=1)
        c.setFont('Georgia', 10.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(left + 8, curr_y - 16, f"原句：\"{q['orig']}\"")
        curr_y -= 28

        if is_teacher:
            # Teacher Key & Script
            c.setFont('JHB', 9)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(left, curr_y - 10, q['diag'])
            curr_y -= 14

            c.setFillColor(colors.HexColor(GREEN))
            c.drawString(left, curr_y - 10, q['correct'])
            curr_y -= 14

            c.setFont('JH', 8.5)
            c.setFillColor(colors.HexColor(BLUE))
            c.drawString(left, curr_y - 10, q['script'])
            curr_y -= 18

        else:
            # Student Writing Lines (Font 11pt, Spacious 24pt Writing Lines!)
            # NO EMOJIS! Clean typographical brackets
            c.setFont('JHB', 10.5)
            c.setFillColor(colors.HexColor(TEXT_DARK))
            c.drawString(left, curr_y - 10, '【破綻診斷】找出原句語法或用詞問題：')
            curr_y -= 26
            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.6)
            c.setDash(2, 2)
            c.line(left + 10, curr_y + 8, w - left, curr_y + 8)
            c.setDash()

            c.setFont('JHB', 10.5)
            c.setFillColor(colors.HexColor(TEXT_DARK))
            c.drawString(left, curr_y - 8, '【精修改寫】重新寫出正確流暢之完整句子：')
            curr_y -= 26
            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.6)
            c.setDash(2, 2)
            c.line(left + 10, curr_y + 8, w - left, curr_y + 8)
            c.setDash()
            curr_y -= 4

        if q['num'] < 5:
            c.setStrokeColor(colors.HexColor('#E2E8F0'))
            c.setLineWidth(0.5)
            c.line(left, curr_y + 4, w - left, curr_y + 4)
            curr_y -= 8

    # Bottom Folio
    c.setStrokeColor(colors.HexColor(TEXT_DARK))
    c.setLineWidth(0.6)
    c.line(left, 30, w - left, 30)
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    if is_teacher:
        c.drawString(left, 16, '教師備課指引  ·  適合於投影簡報檢討後，帶全班進行 5~10 分鐘黑板互動隨堂帶練。')
        c.setFont('GeorgiaBold', 9)
        c.drawRightString(w - left, 16, 'TEACHER KEY  ·  PAGE 01 / 01')
    else:
        c.drawString(left, 16, '班級：________ 座號：____ 姓名：____________  得分：______ / 5  教師簽章：____________')
        c.setFont('GeorgiaBold', 9)
        c.drawRightString(w - left, 16, 'STUDENT PRACTICE  ·  PAGE 01 / 01')

    c.save()
    print(f"Saved Worksheet: {out_path.name}")

# ==================== 16:9 CLASSROOM SLIDES (HIGH-CONTRAST & LARGE PROJECTOR FONTS) ====================

def render_slides_master(out_path):
    c = canvas.Canvas(str(out_path), pagesize=(SLIDE_W, SLIDE_H))

    def draw_slide_top(slide_num, title_zh, category_tag):
        c.setFillColor(colors.HexColor(GREEN))
        c.rect(0, SLIDE_H - 10, SLIDE_W, 10, fill=1, stroke=0)
        c.setFont('GeorgiaBold', 12)
        c.setFillColor(colors.HexColor(GREEN))
        c.drawString(50, SLIDE_H - 35, 'THE WRITING EDIT  |  CLASSROOM DIAGNOSTIC SLIDES')
        c.setFont('JH', 11)
        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.drawRightString(SLIDE_W - 50, SLIDE_H - 35, '110 學測英文作文  |  全班三大集體盲區深度剖析')

        c.setFillColor(colors.HexColor(RED))
        c.roundRect(50, SLIDE_H - 85, 130, 28, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 14)
        c.drawCentredString(115, SLIDE_H - 77, category_tag)

        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.setFont('JHB', 28)
        c.drawString(195, SLIDE_H - 80, title_zh)

        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.setLineWidth(0.8)
        c.line(50, 42, SLIDE_W - 50, 42)
        c.setFont('JH', 11)
        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.drawString(50, 24, '高中英文寫作診斷課堂專用  |  大考中心 108 課綱評分規準對齊')
        c.setFont('GeorgiaBold', 12)
        c.drawRightString(SLIDE_W - 50, 24, f"SLIDE {slide_num:02d} / 05")

    # Slide 1: Cover
    c.setFillColor(colors.HexColor('#0F172A')) # Deep rich slate
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(GREEN))
    c.rect(0, SLIDE_H - 12, SLIDE_W, 12, fill=1, stroke=0)
    c.rect(60, SLIDE_H - 145, 8, 115, fill=1, stroke=0)

    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor('#94A3B8'))
    c.drawString(85, SLIDE_H - 135, 'THE WRITING EDIT  |  CLASSROOM DIAGNOSTIC SUITE')
    c.setFont('JHB', 40)
    c.setFillColor(colors.white)
    c.drawString(85, SLIDE_H - 190, '110 學測英文作文：全班三大集體盲區剖析')
    c.setFont('JH', 18)
    c.setFillColor(colors.HexColor('#CBD5E1'))
    c.drawString(85, SLIDE_H - 230, '從學生真實手寫原稿出發，突破「破句、形似字、空泛敘述」三大常見痛點')

    card_w = (SLIDE_W - 120 - 40) / 3
    card_y = 100
    card_h = 145
    cards = [
        ("盲區 1：語法破句", "Because 從屬子句獨立成句", "破句 (Sentence Fragment)\n大考閱卷每出現一次重扣 1 分"),
        ("盲區 2：字彙混淆", "sigh 與中式直譯 public manners", "sigh (嘆氣) vs. sign (告示牌)\n搭配詞缺乏道地語感"),
        ("盲區 3：細節空泛", "第一段缺乏感官實景細節", "40 字草草帶過現場畫面\n缺乏 Show, Don't Tell 鏡頭感")
    ]
    for idx, (head, sub, desc) in enumerate(cards):
        cx = 60 + idx * (card_w + 20)
        c.setFillColor(colors.HexColor('#1E293B'))
        c.roundRect(cx, card_y, card_w, card_h, 8, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#38BDF8'))
        c.setFont('JHB', 16)
        c.drawString(cx + 20, card_y + card_h - 30, head)
        c.setFillColor(colors.white)
        c.setFont('JHB', 16)
        c.drawString(cx + 20, card_y + card_h - 60, sub)
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.setFont('JH', 13)
        for line_i, line_t in enumerate(desc.split('\n')):
            c.drawString(cx + 20, card_y + card_h - 95 - line_i * 24, line_t)

    c.setFont('JH', 13)
    c.setFillColor(colors.HexColor('#64748B'))
    c.drawRightString(SLIDE_W - 60, 50, '高中英文寫作專題  |  課堂檢討指引')
    c.showPage()

    # Slide 2: Blind Spot 1
    draw_slide_top(2, '盲區 1：從屬連接詞 Because 獨立成句（破句）', '文法致命傷')
    box_w = 415

    # Left Box (Error)
    c.setFillColor(colors.HexColor('#FEF2F2'))
    c.setStrokeColor(colors.HexColor('#F87171'))
    c.setLineWidth(1.2)
    c.roundRect(50, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(70, 395, '【學生原稿真實破綻】')

    c.setFillColor(colors.white)
    c.roundRect(70, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(RED))
    c.line(70, 290, 70, 380)
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(85, 345, '"...making the space owners feel angry.')
    c.setFont('GeorgiaBold', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(85, 312, 'Because this place means a lot to me."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. Because 為從屬連接詞，無法單獨支撐句子。')
    c.drawString(70, 195, '2. 犯下「破句 (Sentence Fragment)」大忌。')
    c.drawString(70, 165, '3. 大考閱卷評分直接扣減文法分 1~2 分。')

    # Right Box (High-Scoring Solution)
    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【高分精修策略】')

    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(530, 345, '"...making the space owners feel angry,')
    c.setFont('GeorgiaBold', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(530, 312, 'as this place means a lot to me."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '解法 A：以逗號串接，改為複合句。')
    c.drawString(515, 195, '解法 B：獨立成句時改用「This is because...」。')
    c.drawString(515, 165, '解法 C：改用「Therefore,」或「As a result,」。')
    c.showPage()

    # Slide 3: Blind Spot 2
    draw_slide_top(3, '盲區 2：形似字混淆與中式直譯詞彙', '用詞地道度')

    # Left Box
    c.setFillColor(colors.HexColor('#FEF2F2'))
    c.setStrokeColor(colors.HexColor('#F87171'))
    c.setLineWidth(1.2)
    c.roundRect(50, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(70, 395, '【學生原稿常見地雷】')

    c.setFillColor(colors.white)
    c.roundRect(70, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(RED))
    c.line(70, 290, 70, 380)
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(85, 345, '1. "...might not notice the sigh that says..."')
    c.drawString(85, 312, '2. "...they have no public manners."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. sigh 是「嘆氣」，告示牌必須是 sign。')
    c.drawString(70, 195, '2. public manners 屬中式直譯，非母語搭配。')
    c.drawString(70, 165, '3. 連續出現會讓閱卷老師判定詞彙匱乏。')

    # Right Box
    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【母語級地道升級】')

    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(530, 345, '1. "...ignored the warning sign reading..."')
    c.drawString(530, 312, '2. "...exhibited no civic decency / etiquette."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '升級 1：告示牌 + 分詞 reading（道地美式）。')
    c.drawString(515, 195, '升級 2：公德心 ➔ civic decency 或 good manners。')
    c.drawString(515, 165, '升級 3：動詞升級：notice ➔ ignore / overlook。')
    c.showPage()

    # Slide 4: Blind Spot 3
    draw_slide_top(4, '盲區 3：第一段細節空泛，缺乏畫面感', '感官鏡頭感')

    # Left Box
    c.setFillColor(colors.HexColor('#FEF2F2'))
    c.setStrokeColor(colors.HexColor('#F87171'))
    c.setLineWidth(1.2)
    c.roundRect(50, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(70, 395, '【乾癟敘事（僅 40 字）】')

    c.setFillColor(colors.white)
    c.roundRect(70, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(RED))
    c.line(70, 290, 70, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(85, 345, '"In the picture, we see people in flowers.')
    c.drawString(85, 312, 'They walk into flower field and step on flowers."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. 連續重複 flowers 三次，詞彙貧乏。')
    c.drawString(70, 195, '2. 僅客觀陳述「走進去」，未描寫動作原因。')
    c.drawString(70, 165, '3. 閱卷老師無法感受現場花圃被破壞的痛心。')

    # Right Box
    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)

    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【Show, Don\'t Tell 畫面升級】')

    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(530, 345, '"Eager for snapshots, tourists ruthlessly')
    c.drawString(530, 312, 'trampled delicate petals underfoot."')

    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '策略 1：補足動機（Eager for snapshots）。')
    c.drawString(515, 195, '策略 2：強烈動詞替換（step on ➔ trample）。')
    c.drawString(515, 165, '策略 3：感官受詞（flowers ➔ delicate petals）。')
    c.showPage()

    # Slide 5: Summary Action Plan
    draw_slide_top(5, '課堂總結：學測英文作文突破 15+ 分三大鐵律', '實戰行動指南')

    card_y = 110
    card_h = 310
    c_w = (SLIDE_W - 100 - 40) / 3

    steps = [
        ("鐵律 1：語法嚴格校對", "文法是分數基石", "1. 寫完務必檢查句首！\n嚴禁 Because/Although 獨立成句。\n2. 動詞時態前後一致，特別是假設法。\n3. 連接詞與逗號不混用。"),
        ("鐵律 2：中式直譯降噪", "精準母語搭配詞", "1. 拋棄 public manners，用 good manners。\n2. 拋棄 Because of that，用 Therefore。\n3. 告示牌用 sign reading，不用 say。"),
        ("鐵律 3：感官畫面深耕", "Show, Don't Tell", "1. 描摹首段實景至少 70~80 字。\n2. 描寫動態動作與受害花瓣。\n3. 結尾昇華公德心與同理心。")
    ]

    for idx, (title, sub, body) in enumerate(steps):
        cx = 50 + idx * (c_w + 20)
        c.setFillColor(colors.HexColor('#F8FAFC'))
        c.setStrokeColor(colors.HexColor(DARK_PILL))
        c.setLineWidth(1.2)
        c.roundRect(cx, card_y, c_w, card_h, 8, fill=1, stroke=1)

        c.setFillColor(colors.HexColor(DARK_PILL))
        c.roundRect(cx, card_y + card_h - 40, c_w, 40, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 16)
        c.drawCentredString(cx + c_w/2, card_y + card_h - 26, title)

        c.setFillColor(colors.HexColor(GREEN))
        c.setFont('JHB', 15)
        c.drawString(cx + 16, card_y + card_h - 65, sub)

        c.setFont('JH', 13.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        for l_i, l_t in enumerate(body.split('\n')):
            c.drawString(cx + 16, card_y + card_h - 95 - l_i * 26, l_t)

    c.save()
    print(f"Saved Slides PDF: {out_path.name}")

# ==================== SLIDES HTML BUILDER ====================

def render_slides_html(out_path):
    html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>110 學測英文作文：全班三大集體盲區剖析簡報</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<style>
body { font-family: 'Noto Serif TC', serif; background-color: #0B132B; color: #F8FAFC; }
.slide { display: none; min-height: 100vh; }
.slide.active { display: flex; }
.eng-font { font-family: 'Playfair Display', serif; }
</style>
</head>
<body class="flex flex-col justify-between p-6 md:p-12">

<!-- Slide 1: Cover -->
<section id="slide-1" class="slide active flex-col justify-center items-center text-center">
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="inline-block px-4 py-1.5 bg-emerald-600/30 text-emerald-400 border border-emerald-500/50 rounded-full text-sm font-semibold tracking-wider uppercase">The Writing Edit · Classroom Diagnostic Suite</div>
    <h1 class="text-4xl md:text-6xl font-bold tracking-tight text-white leading-tight">110 學測英文作文<br><span class="text-emerald-400">全班三大集體盲區深度剖析</span></h1>
    <p class="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto">從學生真實手寫原稿出發，突破「破句、形似字、空泛敘述」三大常見痛點</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-8 text-left">
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-sky-400 font-bold uppercase tracking-wider">盲區 1：語法破句</span>
        <h4 class="text-lg font-bold text-white mt-1">Because 獨立成句</h4>
        <p class="text-xs text-slate-400 mt-2">破句 (Sentence Fragment) 大考閱卷每出現一次重扣 1 分</p>
      </div>
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-amber-400 font-bold uppercase tracking-wider">盲區 2：字彙混淆</span>
        <h4 class="text-lg font-bold text-white mt-1">sigh 與中式直譯</h4>
        <p class="text-xs text-slate-400 mt-2">sigh (嘆氣) vs. sign (告示牌)；public manners 缺乏道地語感</p>
      </div>
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-rose-400 font-bold uppercase tracking-wider">盲區 3：細節空泛</span>
        <h4 class="text-lg font-bold text-white mt-1">第一段缺乏感官實景</h4>
        <p class="text-xs text-slate-400 mt-2">40 字草草帶過現場畫面，缺乏 Show, Don't Tell 鏡頭感</p>
      </div>
    </div>
  </div>
</section>

<!-- Slide 2: Blind Spot 1 -->
<section id="slide-2" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-rose-900/60 text-rose-300 text-sm font-bold rounded">盲區 1 · 文法致命傷</span>
      <span class="text-slate-400 text-sm">SLIDE 02 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">從屬連接詞 Because 獨立成句（破句）</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 學生原稿真實破綻</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-lg text-rose-200">
          "...making space owners angry.<br><b class="text-rose-400">Because this place means a lot to me.</b>"
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. Because 為從屬連接詞，無法單獨支撐句子。</p>
          <p>2. 犯下「破句 (Sentence Fragment)」大忌。</p>
          <p>3. 大考閱卷直接扣減文法分 1~2 分。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ 高分精修策略</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-lg text-emerald-200">
          "...making space owners angry,<br><b class="text-emerald-400">as this place means a lot to me.</b>"
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>解法 A：以逗號串接，改為完整複合句。</p>
          <p>解法 B：獨立成句時改用「This is because...」。</p>
          <p>解法 C：改用「Therefore,」或「As a result,」。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Slide 3: Blind Spot 2 -->
<section id="slide-3" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-amber-900/60 text-amber-300 text-sm font-bold rounded">盲區 2 · 用詞地道度</span>
      <span class="text-slate-400 text-sm">SLIDE 03 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">形似字混淆與中式直譯詞彙</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 學生原稿常見地雷</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-base text-rose-200 space-y-2">
          <p>1. "...might not notice the <b class="text-rose-400 underline">sigh</b> that says..."</p>
          <p>2. "...they have no <b class="text-rose-400 underline">public manners</b>."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. sigh 是「嘆氣」，告示牌必須是 sign。</p>
          <p>2. public manners 屬中式直譯，非母語搭配詞。</p>
          <p>3. 連續出現會讓閱卷老師判定詞彙匱乏。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ 母語級地道升級</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-base text-emerald-200 space-y-2">
          <p>1. "...ignored the <b class="text-emerald-400">warning sign reading</b>..."</p>
          <p>2. "...exhibited no <b class="text-emerald-400">civic decency / etiquette</b>."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>升級 1：告示牌 + 分詞 reading（道地美式用法）。</p>
          <p>升級 2：公德心 ➔ civic decency 或 good manners。</p>
          <p>升級 3：動詞升級：notice ➔ ignore / overlook。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Slide 4: Blind Spot 3 -->
<section id="slide-4" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-sky-900/60 text-sky-300 text-sm font-bold rounded">盲區 3 · 感官鏡頭感</span>
      <span class="text-slate-400 text-sm">SLIDE 04 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">第一段細節空泛，缺乏畫面感</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 乾癟敘事（僅 40 字）</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-base text-rose-200">
          "In the picture, we see people in flowers. They walk into flower field and step on flowers."
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. 連續重複 flowers 三次，詞彙貧乏。</p>
          <p>2. 僅客觀陳述「走進去」，未描寫動作原因。</p>
          <p>3. 閱卷老師無法感受現場花圃被破壞的痛心。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ Show, Don't Tell 畫面升級</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-base text-emerald-200">
          "Eager for snapshots, tourists ruthlessly trampled delicate petals underfoot."
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>策略 1：補足動機（Eager for snapshots）。</p>
          <p>策略 2：強烈動詞替換（step on ➔ trample）。</p>
          <p>策略 3：感官受詞（flowers ➔ delicate petals）。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Slide 5: Summary -->
<section id="slide-5" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-emerald-900/60 text-emerald-300 text-sm font-bold rounded">實戰行動指南</span>
      <span class="text-slate-400 text-sm">SLIDE 05 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">課堂總結：學測英文作文突破 15+ 分三大鐵律</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 1：語法嚴格校對</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 寫完務必檢查句首！嚴禁 Because/Although 獨立成句。</p>
          <p>2. 動詞時態前後一致，特別是假設法。</p>
          <p>3. 連接詞與逗號不混用。</p>
        </div>
      </div>
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 2：中式直譯降噪</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 拋棄 public manners，用 good manners。</p>
          <p>2. 拋棄 Because of that，用 Therefore。</p>
          <p>3. 告示牌用 sign reading，不用 say。</p>
        </div>
      </div>
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 3：感官畫面深耕</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 描摹首段實景至少 70~80 字。</p>
          <p>2. 描寫動態動作與受害花瓣。</p>
          <p>3. 結尾昇華公德心與同理心。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Footer Nav -->
<footer class="flex items-center justify-between pt-6 border-t border-slate-800 text-sm text-slate-400">
  <div>鍵盤左右方向鍵 (← / →) 切換投影片</div>
  <div class="space-x-2">
    <button onclick="prevSlide()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded transition">上一頁</button>
    <button onclick="nextSlide()" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded transition">下一頁</button>
  </div>
</footer>

<script>
let currentSlide = 1;
const totalSlides = 5;

function showSlide(n) {
  document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(`slide-${n}`);
  if (target) target.classList.add('active');
  currentSlide = n;
}

function nextSlide() {
  if (currentSlide < totalSlides) showSlide(currentSlide + 1);
}

function prevSlide() {
  if (currentSlide > 1) showSlide(currentSlide - 1);
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
  if (e.key === 'ArrowLeft') prevSlide();
});
</script>
</body>
</html>
"""
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved Slides HTML: {out_path.name}")

# ==================== MAIN EXECUTION & ASSEMBLY ====================

def main():
    print("==================== STARTING COMPLETE MASTER V15 BUILD ====================")

    # 1. Build Page 1 & Page 2 for All 3 Essays
    essays = [
        (DATA_S01, TMP / "s01_p1.pdf", TMP / "s01_p2.pdf", "Student_01"),
        (DATA_S35, TMP / "s35_p1.pdf", TMP / "s35_p2.pdf", "Student_35"),
        (DATA_CEEC, TMP / "ceec_p1.pdf", TMP / "ceec_p2.pdf", "大考中心佳作01")
    ]

    for data, p1_path, p2_path, prefix in essays:
        render_page_1_clean(data, p1_path)
        render_page_2_zoned(data, p2_path)

        # Assemble 2-page print edition
        two_page_out = OUT_DIR / f"{prefix}_前兩頁雙面列印_雜誌風.pdf"
        writer2 = PdfWriter()
        r1 = PdfReader(p1_path)
        r2 = PdfReader(p2_path)
        writer2.add_page(r1.pages[0])
        writer2.add_page(r2.pages[0])
        with open(two_page_out, 'wb') as f:
            writer2.write(f)
        print(f"Saved 2-Page Print PDF: {two_page_out.name} ({two_page_out.stat().st_size:,} bytes)")

        # Assemble complete 7-page The Writing Edit magazine edition
        full_mag_out = OUT_DIR / f"{prefix}_雜誌風手寫批改_The_Writing_Edit.pdf"
        det_pdf = TMP / "tmp_mag_v3" / "details.pdf"
        writer7 = PdfWriter()
        writer7.add_page(r1.pages[0])
        writer7.add_page(r2.pages[0])
        if det_pdf.exists():
            r_det = PdfReader(det_pdf)
            for page in r_det.pages:
                writer7.add_page(page)
        with open(full_mag_out, 'wb') as f:
            writer7.write(f)
        print(f"Saved 7-Page Magazine PDF: {full_mag_out.name} ({full_mag_out.stat().st_size:,} bytes)")

    # 2. Build 1-Page Spot-the-Error Worksheets
    print("\n--- Building 1-Page Spot-the-Error Worksheets ---")
    ws_stud_pdf = OUT_DIR / "110學測作文_大家來找碴_挑錯微講義_學用版.pdf"
    ws_teach_pdf = OUT_DIR / "110學測作文_大家來找碴_挑錯微講義_教用解答版.pdf"
    render_worksheet_master(is_teacher=False, out_path=ws_stud_pdf)
    render_worksheet_master(is_teacher=True, out_path=ws_teach_pdf)

    # 3. Build 16:9 Slides (PDF & HTML)
    print("\n--- Building 16:9 Classroom Slides ---")
    slides_pdf = OUT_DIR / "110學測作文_全班三大集體盲區_課堂投影簡報.pdf"
    slides_html = OUT_DIR / "110學測作文_全班三大集體盲區_課堂投影簡報.html"
    render_slides_master(slides_pdf)
    render_slides_html(slides_html)

    print("\n==================== ALL 10 DELIVERABLES SUCCESSFULLY PRODUCED! ====================")

if __name__ == '__main__':
    main()
