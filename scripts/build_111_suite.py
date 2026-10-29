# -*- coding: utf-8 -*-
"""
build_111_suite.py
Master generator for 111 學測英文作文（規劃理想新公園）:
- 301班第一篇 (Student 01 / No. 06)
- 111學測大考中心佳作 01
Includes:
- Page 1: Precision non-overlapping annotations (NO Sp/W/G badges, respectful corrections)
- Page 2: Magazine-style Zoning (Part A, Part B, Part C) & 45pt Bleed Safety Margins (NO collisions)
- 1-Page Spot-the-Error Worksheets (Pure typography, ZERO □ glyph bugs)
- 16:9 Large Typography Classroom Slides (PDF & HTML)
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

# Output & Temp Directories
OUT_DIR = Path("H:/我的雲端硬碟/# Sylvia's Workspace/01 講師素材/[置頂] My Workshop Materials/研習素材包/學測英文作文學生原稿/301 111學測作文 (喜歡的公園類型)/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP = Path("C:/Users/user/.gemini/antigravity/brain/7148bf21-122a-418b-a09d-b71b1a4f0440/scratch")

# Color Schemes
GREEN = '#006A4E'
RED = '#BC1632'
BLUE = '#164FB2'

# Page 2 Grayscale / Monochrome Photocopier Palette
DARK_PILL = '#1E293B'
BORDER_COLOR = '#CBD5E1'
TEXT_DARK = '#0F172A'
TEXT_MUTED = '#475569'
LINE_DOTTED = '#94A3B8'
BG_LIGHT_GRAY = '#F8FAFC'

SLIDE_W, SLIDE_H = 960, 540

# ==================== DATA DEFINITIONS ====================

DATA_301_01 = {
    'id': '301_01',
    'title': '301 班第一篇 (去識別化稿件)',
    'subtitle': '學測英文作文個人診斷與修訂歷程單',
    'words': 124,
    'total': 9.0,
    'grade_tier': '待加強 (第 2 級分頂)',
    'total_desc': '實測 124 字（達標；扣分 0）',
    'scores': [
        ('內容 (Content)', '2.5', '能提及公園 A（設施）與 B（樹木草地），惟理由描寫較單薄，好處僅簡述涼爽。'),
        ('組織 (Organization)', '2.5', '分兩段且具時間對比（童年 vs. 長大）；但轉折詞誤用（In reverse 應為 In contrast）。'),
        ('文法 (Grammar)', '2.0', '多處主詞三單動詞未加 s (have)、語態混淆 (are be set) 及 will 後漏 be 動詞。'),
        ('字彙 (Vocabulary)', '2.0', '詞性混淆 (differ)、搭配詞需優化 (take a picnic 建議用 have a picnic) 與中式直譯。')
    ],
    'feedback_zh': '兩段架構清楚，能以自身成長經驗點出新公園需兼顧設施與綠意，非常生活化！建議優先掌握：1. 單數動詞加 s（Picture A has）；2. 避免逐字直譯（as I grew older）；3. will 後方加原形動詞 be（it will be cool）。',
    'feedback_en': "Your idea of blending fun facilities with greenery is authentic! Next draft, focus on: 1. Subject-verb agreement; 2. Natural expressions instead of direct translation; 3. Add 'be' after 'will'.",
    'tasks': [
        ('【任務 1：基礎主動一致與助動詞】修正第 4 行「Picture A have」與末行「it will very cool」，寫出正確完整句：', 1),
        ('【任務 2：消除中式直譯】將第 8 行「along with my ages going up」改寫為自然的「as I grew older」：', 1),
        ('【任務 3：地道搭配詞升級】修正「differ parks」與「take a picnic」，將其提升為符合大考水準之片語：', 2)
    ],
    # Precision Coordinates without Sp/W/G tags, respectful corrections
    'annotations': [
        # Line 1: In this day -> (或用 Nowadays 更佳)
        {'type': 'bracket', 'x1': 0.075, 'x2': 0.235, 'y': 0.015, 'text': '(或用 Nowadays 更佳)', 'dy': 20},
        # Line 3: differ (x=0.244, w=0.066) -> strikeout -> different
        {'type': 'strike', 'x': 0.242, 'w': 0.068, 'y': 0.170, 'text': 'different', 'dy': 18},
        # Line 4: hove (x=0.271, w=0.055) -> strikeout -> has
        {'type': 'strike', 'x': 0.268, 'w': 0.058, 'y': 0.257, 'text': 'has', 'dy': 18},
        # Line 4: ave be set (x=0.697 to 0.880) -> strikeout -> are designed
        {'type': 'strike', 'x': 0.695, 'w': 0.185, 'y': 0.260, 'text': 'are designed', 'dy': 18},
        # Line 5: In vivee (x=0.776 to 0.900) -> strikeout -> In contrast,
        {'type': 'strike', 'x': 0.774, 'w': 0.125, 'y': 0.340, 'text': 'In contrast,', 'dy': 18},
        # Line 8: along with my ages going up (x=0.237 to 0.644) -> bracket [ ... ] = as I grew older,
        {'type': 'bracket', 'x1': 0.235, 'x2': 0.645, 'y': 0.590, 'text': '= as I grew older,', 'dy': 20},
        # Line 8: is change (x=0.830 to 0.999) -> strikeout -> changed
        {'type': 'strike', 'x': 0.830, 'w': 0.165, 'y': 0.590, 'text': 'changed', 'dy': 18},
        # Line 10: take a picnic -> (或用 have a picnic 更佳) [Gentle suggestion, NO strikeout!]
        {'type': 'bracket', 'x1': 0.600, 'x2': 0.880, 'y': 0.750, 'text': '(或用 have a picnic 更佳)', 'dy': 20},
        # Line 11: hover (x=0.745, w=0.066) -> strikeout -> has
        {'type': 'strike', 'x': 0.742, 'w': 0.070, 'y': 0.833, 'text': 'has', 'dy': 18},
        # Line 12: caret ^ be between will and very (x=0.160)
        {'type': 'caret', 'x': 0.160, 'y': 0.920, 'text': 'be', 'dy': 18},
    ]
}

DATA_111_CEEC = {
    'id': '111_CEEC_01',
    'title': '111 學測英文作文大考中心公告佳作 01',
    'subtitle': '學測英文作文個人診斷與修訂歷程單 (特優典範篇)',
    'words': 282,
    'total': 18.5,
    'grade_tier': '特優 (第 5 級分 / 全國前 1%)',
    'total_desc': '實測 282 字（篇幅宏大；扣分 0）',
    'scores': [
        ('內容 (Content)', '5.0', '首段感官描寫如臨實境；次段構思結合湖畔與樹林，營造人與自然和諧共生，意境高遠。'),
        ('組織 (Organization)', '4.5', '段落承接天衣無縫，善用 First, Second, Last but not least 及倒裝句層層推進。'),
        ('文法 (Grammar)', '4.5', '精熟倒裝句（Only when... can he realize...）與分詞修飾，展現頂級句構駕馭力。'),
        ('字彙 (Vocabulary)', '4.5', '詞彙豐富洗鍊（tranquil, lush, innumerable, hustle and bustle, infuse stamina）。')
    ],
    'feedback_zh': '本篇堪稱大考滿分示範！首段感官摹寫（微風拂面、樹葉沙沙）讓讀者如置身林間；次段提出「人與自然和諧」的哲學層次，結尾倒裝句更展現成熟的修辭底蘊。',
    'feedback_en': "A stellar model composition. The sensory details in paragraph 1 are breathtaking, while paragraph 2 reaches a profound philosophical level of human-nature harmony. The inversion sentence at the close is sheer mastery.",
    'tasks': [
        ('【任務 1：感官摹寫借鑑】挑選本文描寫聲音與觸覺的文句（風與樹葉），試仿寫於自己未來的自然寫作中：', 1),
        ('【任務 2：高階倒裝句實作】仿照「Only when a person calms down... can he realize...」造出 1 個完整倒裝句：', 1),
        ('【任務 3：典雅片語移轉】將「escape from the hustle and bustle」融入下一篇作文的生活描寫中：', 2)
    ],
    'annotations': [
        {'type': 'bracket', 'x1': 0.50, 'x2': 0.85, 'y': 0.08, 'text': '(或用 At first glance 更佳)', 'dy': 22},
        {'type': 'bracket', 'x1': 0.10, 'x2': 0.45, 'y': 0.35, 'text': 'Vivid sensory immersion!', 'dy': 22},
        {'type': 'bracket', 'x1': 0.55, 'x2': 0.92, 'y': 0.65, 'text': 'Exemplary idiom choice', 'dy': 22},
        {'type': 'bracket', 'x1': 0.10, 'x2': 0.50, 'y': 0.88, 'text': 'Masterful inversion sentence', 'dy': 22},
    ]
}

# ==================== PAGE 1 RENDERER ====================

def render_page_1(data, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    margin = 45
    left = margin
    avail_w = w - margin * 2

    # Top Ribbon (Stay within 45pt margin)
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
    c.drawString(left, h - 68, f"111 學測英文作文（規劃理想新公園） |  實測字數：{data['words']} 字  |  總分：{data['total']} 分")

    # Score Pill Badge
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
    if data['id'] == '301_01':
        img_p = TMP / "111_s01_enhanced.png"
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

    else: # 111 CEEC 01 (Two Columns)
        col1_p = TMP / "111_ceec_col1_enhanced.png"
        col2_p = TMP / "111_ceec_col2_enhanced.png"
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
    print(f"Saved Page 1: {out_pdf_path.name}")

def draw_annotations(c, nx, ny, nw, nh, annotations):
    # NO Sp/W/G badges! Clean, warm, teacher handwriting
    for a in annotations:
        ay = ny + (1.0 - a['y']) * nh
        t = a['type']

        if t == 'bracket':
            bx1 = nx + a['x1'] * nw
            bx2 = nx + a['x2'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.3)
            c.line(bx1, ay - 3, bx1, ay + 11)
            c.line(bx1, ay - 3, bx1 + 5, ay - 3)
            c.line(bx1, ay + 11, bx1 + 5, ay + 11)
            c.line(bx2, ay - 3, bx2, ay + 11)
            c.line(bx2 - 5, ay - 3, bx2, ay - 3)
            c.line(bx2 - 5, ay + 11, bx2, ay + 11)
            c.setFont('Hand', 11)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(bx1 + 6, ay + a.get('dy', 20), a['text'])

        elif t == 'strike':
            ax = nx + a['x'] * nw
            aw = a['w'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.4)
            c.line(ax, ay + 4, ax + aw, ay + 4)
            c.setFont('Hand', 11)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(ax, ay + a.get('dy', 18), a['text'])

        elif t == 'caret':
            cx = nx + a['x'] * nw
            c.setStrokeColor(colors.HexColor(RED))
            c.setLineWidth(1.4)
            c.line(cx - 4, ay - 2, cx, ay + 8)
            c.line(cx, ay + 8, cx + 4, ay - 2)
            c.setFont('Hand', 11)
            c.setFillColor(colors.HexColor(RED))
            c.drawString(cx - 8, ay + a.get('dy', 18), a['text'])

# ==================== PAGE 2 RENDERER (45PT BLEED SAFE & NO COLLISION) ====================

def render_page_2(data, out_pdf_path):
    c = canvas.Canvas(str(out_pdf_path), pagesize=A4)
    w, h = A4
    margin = 45
    left = margin
    width = w - margin * 2  # Strict 45pt safety margins

    # Top Bar
    c.setStrokeColor(colors.HexColor(DARK_PILL))
    c.setLineWidth(1.2)
    c.line(left, h - 35, left + width, h - 35)
    c.setFont('GeorgiaBold', 9.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left, h - 28, 'THE WRITING EDIT  |  DIAGNOSTIC & REVISION REPORT')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(left + width, h - 28, '學測英文作文個人診斷與修訂歷程單 (背面)')

    curr_y = h - 48

    def draw_pill_badge(c, x, y, text, w_badge=220):
        c.setFillColor(colors.HexColor(DARK_PILL))
        c.roundRect(x, y - 16, w_badge, 17, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 9)
        c.drawString(x + 8, y - 12.5, text)

    # ==================== PART A ====================
    part_a_h = 220
    draw_pill_badge(c, left, curr_y, 'PART A  評分依據與教師評語', 190)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, curr_y - part_a_h, width, part_a_h - 18, 4, fill=0, stroke=1)

    # Summary Row using structured Table so NO text can EVER collide!
    sum_table_data = [
        [
            Paragraph(f"<b>總分：{data['total']} / 20 分</b>", ParagraphStyle('st1', fontName='JHB', fontSize=12, textColor=colors.HexColor(TEXT_DARK))),
            Paragraph(f"大考級距：<b>{data['grade_tier']}</b>", ParagraphStyle('st2', fontName='JH', fontSize=9, textColor=colors.HexColor(TEXT_DARK))),
            Paragraph(f"實測字數：<b>{data['words']} 字</b>（扣分 0）", ParagraphStyle('st3', fontName='JH', fontSize=9, alignment=2, textColor=colors.HexColor(TEXT_MUTED)))
        ]
    ]
    t_sum = Table(sum_table_data, colWidths=[150, 180, width - 354])
    t_sum.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    _, sh = t_sum.wrap(width - 24, 40)
    t_sum.drawOn(c, left + 12, curr_y - 36)

    # Rubric Table with explicit column widths
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

    t_rub = Table(table_rows, colWidths=[105, 40, width - 169])
    t_rub.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor(BORDER_COLOR)),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    _, rh = t_rub.wrap(width - 24, 200)
    t_rub.drawOn(c, left + 12, curr_y - 42 - rh)

    # Feedback Table (Using Paragraph with wordWrap='CJK' to NEVER exceed bleed margins!)
    fb_y = curr_y - 46 - rh
    fb_text = f"中文：{data['feedback_zh']}<br/>英文：{data['feedback_en']}"
    fb_data = [
        [
            Paragraph('<b>【教師評語】</b>', ParagraphStyle('fbt', fontName='JHB', fontSize=8.5, textColor=colors.HexColor(TEXT_DARK))),
            Paragraph(fb_text, ParagraphStyle('fbc', fontName='JH', fontSize=8, leading=11.5, textColor=colors.HexColor(TEXT_DARK), wordWrap='CJK'))
        ]
    ]
    t_fb = Table(fb_data, colWidths=[70, width - 94])
    t_fb.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    _, fbh = t_fb.wrap(width - 24, 80)
    t_fb.drawOn(c, left + 12, fb_y - fbh)

    curr_y -= (part_a_h + 10)

    # ==================== PART B ====================
    part_b_h = 175
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

    curr_y -= (part_b_h + 10)

    # ==================== PART C ====================
    part_c_h = 230
    draw_pill_badge(c, left, curr_y, 'PART C  學習歷程反思與教師核閱 (學習歷程檔案實作證明)', 320)
    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.roundRect(left, curr_y - part_c_h, width, part_c_h - 18, 4, fill=0, stroke=1)

    cy = curr_y - 28
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

    cy -= 44
    c.setFont('JHB', 9)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, cy, '2. 學習歷程反思紀錄（請簡要填寫下列 4 個維度）：')
    cy -= 10

    ref_w = (width - 32) / 2
    ref_h = 56
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
        c.setStrokeColor(colors.HexColor(LINE_DOTTED))
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(bx + 6, by_box + ref_h - 26, bx + ref_w - 6, by_box + ref_h - 26)
        c.line(bx + 6, by_box + ref_h - 42, bx + ref_w - 6, by_box + ref_h - 42)
        c.setDash()

    stamp_y = cy - ref_h*2 - 28
    c.setFont('JHB', 8.5)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(left + 12, stamp_y, '教師核閱章 / 簽名：____________________    修訂等級核定：[  ] 達標特優    [  ] 通過良好    [  ] 需再面談')
    c.drawRightString(left + width - 12, stamp_y, '核閱日期：_____ 年 ___ 月 ___ 日')

    c.setFont('GeorgiaBold', 9)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawRightString(left + width, 22, 'PAGE 02 / 02')

    c.save()
    print(f"Saved Page 2: {out_pdf_path.name}")

# ==================== 1-PAGE SPOT THE ERROR WORKSHEET (ZERO GLYPH BUG) ====================

QUESTIONS_111 = [
    {
        'num': 1,
        'tag': '盲區 1：主詞三單動詞一致 (Subject-Verb Agreement)',
        'orig': 'The picture A have many amusement facilities for children to play.',
        'diag': '【破綻診斷】picture A 為第三人稱單數名詞，現在式動詞必須使用 has，誤用 have 屬大考基礎文法扣分項目。',
        'correct': '【標準改寫】Picture A features various amusement facilities for children to enjoy.',
        'script': '【教師引導話術】「主詞看到 Picture A 這種單數名詞，動詞千萬記得加 s 或用 has！基礎分絕不能丟！」'
    },
    {
        'num': 2,
        'tag': '盲區 2：助動詞 will 後漏掉 be 動詞 (Missing Auxiliary Verb)',
        'orig': 'The best advantage is the park have many trees, so it will very cool.',
        'diag': '【破綻診斷】will 為助動詞，後方必須接原形動詞；cool 為形容詞，前面絕對不能缺少 be 動詞！',
        'correct': '【標準改寫】The greatest advantage is that the park has many trees, so it will be very cool and shaded.',
        'script': '【教師引導話術】「will 後面直接接 cool？不行！cool 是形容詞，中間一定要有一座橋梁 be 動詞！」'
    },
    {
        'num': 3,
        'tag': '盲區 3：逐字直譯「隨著年齡增長」 (Chinglish Time Expression)',
        'orig': 'Along with my ages going up, my thought is change about the ideal park.',
        'diag': '【破綻診斷】along with my ages going up 屬中文逐字直譯；is change 動詞形式錯誤。英文表達長大應使用 as I grew older。',
        'correct': '【標準改寫】As I grew older, my preferences for an ideal park began to change.',
        'script': '【教師引導話術】「不要把中文『年紀上去』直譯成 ages going up！用 as I grew older 或 with age 既簡潔又道地！」'
    },
    {
        'num': 4,
        'tag': '盲區 4：轉折詞誤用 In reverse (Transition Misuse)',
        'orig': 'Children play in park A. In reverse, the picture B only have many trees and lawn.',
        'diag': '【破綻診斷】in reverse 通常指「車輛倒退」或「順序顛倒」，對比兩事物應使用 In contrast 或 On the other hand。',
        'correct': '【標準改寫】In contrast, Picture B offers a tranquil scene featuring vast lawns and towering trees.',
        'script': '【教師引導話術】「對比兩座公園不要寫 In reverse，那是在倒車！要用 In contrast 或 On the contrary！」'
    },
    {
        'num': 5,
        'tag': '盲區 5：動詞搭配詞優化 take a picnic (Collocation Polish)',
        'orig': 'I want to build this new park because I can take a picnic or walk my dog.',
        'diag': '【修辭診斷】中文說「去野餐」，英文更道地習慣的搭配詞為 have a picnic 或 go on a picnic。',
        'correct': '【建議改寫】I hope to design this new park so that I can have a picnic on the grass or walk my dog.',
        'script': '【教師引導話術】「野餐不是『拿野餐』，請大家牢記 have a picnic 或 go on a picnic，搭配詞要地道！」'
    }
]

def render_worksheet_111(is_teacher=False, out_path=None):
    c = canvas.Canvas(str(out_path), pagesize=A4)
    w, h = A4
    margin = 45
    left = margin
    width = w - margin * 2

    # Top Ribbon
    c.setFillColor(colors.HexColor(GREEN))
    c.rect(0, h - 8, w, 8, fill=1, stroke=0)
    c.setFont('GeorgiaBold', 9)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(left, h - 25, 'THE WRITING EDIT  |  CLASSROOM SPOT-THE-ERROR CHALLENGE')
    c.setFont('JH', 8.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    lbl = '【教師解答與引導版】Teacher Answer Key' if is_teacher else '【學生隨堂練習版】Student Practice Worksheet'
    c.drawRightString(w - left, h - 25, f"111 學測英文作文  |  {lbl}")

    # Title
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    t_text = '111 學測作文「大家來找碴」：新公園規劃高頻破綻挑錯講義' + (' (教師版)' if is_teacher else ' (學生版)')
    c.drawString(left, h - 46, t_text)
    c.setFont('JH', 9.5)
    c.setFillColor(colors.HexColor(TEXT_MUTED))
    c.drawString(left, h - 60, '以下 5 個句子均來自 111 學測真實學生練習原稿。請仔細觀察，找出破綻並重新改寫符合大考要求的句子。')

    c.setStrokeColor(colors.HexColor(BORDER_COLOR))
    c.setLineWidth(0.8)
    c.line(left, h - 68, w - left, h - 68)

    curr_y = h - 80

    for q in QUESTIONS_111:
        tag_col = RED if is_teacher else DARK_PILL
        c.setFillColor(colors.HexColor(tag_col))
        c.roundRect(left, curr_y - 14, 185, 16, 2, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('JHB', 8.5)
        c.drawString(left + 6, curr_y - 11.5, q['tag'])

        c.setFont('GeorgiaBold', 10.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(left + 195, curr_y - 11, f"Question 0{q['num']}")
        curr_y -= 20

        # Original Sentence Box - NEVER MIX CHINESE IN GEORGIA FONT!
        c.setFillColor(colors.HexColor(BG_LIGHT_GRAY))
        c.setStrokeColor(colors.HexColor(BORDER_COLOR))
        c.roundRect(left, curr_y - 24, width, 22, 3, fill=1, stroke=1)
        # 1. Chinese Label in JHB (prevents □□□ bug!)
        c.setFont('JHB', 9.5)
        c.setFillColor(colors.HexColor(TEXT_DARK))
        c.drawString(left + 8, curr_y - 16, "【原句】")
        # 2. English Quote in Georgia
        c.setFont('Georgia', 10)
        c.drawString(left + 50, curr_y - 16, f"\"{q['orig']}\"")
        curr_y -= 28

        if is_teacher:
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
            # NO EMOJIS! Pure typography
            c.setFont('JHB', 10)
            c.setFillColor(colors.HexColor(TEXT_DARK))
            c.drawString(left, curr_y - 10, '【破綻診斷】找出原句語法、動詞或詞性問題：')
            curr_y -= 26
            c.setStrokeColor(colors.HexColor(LINE_DOTTED))
            c.setLineWidth(0.6)
            c.setDash(2, 2)
            c.line(left + 10, curr_y + 8, w - left, curr_y + 8)
            c.setDash()

            c.setFont('JHB', 10)
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

    # Folio
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

# ==================== 16:9 CLASSROOM SLIDES ====================

def render_slides_111(out_path):
    c = canvas.Canvas(str(out_path), pagesize=(SLIDE_W, SLIDE_H))

    def draw_slide_top(slide_num, title_zh, category_tag):
        c.setFillColor(colors.HexColor(GREEN))
        c.rect(0, SLIDE_H - 10, SLIDE_W, 10, fill=1, stroke=0)
        c.setFont('GeorgiaBold', 12)
        c.setFillColor(colors.HexColor(GREEN))
        c.drawString(50, SLIDE_H - 35, 'THE WRITING EDIT  |  CLASSROOM DIAGNOSTIC SLIDES')
        c.setFont('JH', 11)
        c.setFillColor(colors.HexColor(TEXT_MUTED))
        c.drawRightString(SLIDE_W - 50, SLIDE_H - 35, '111 學測英文作文  |  全班三大集體盲區深度剖析')

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
    c.setFillColor(colors.HexColor('#0F172A'))
    c.rect(0, 0, SLIDE_W, SLIDE_H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor(GREEN))
    c.rect(0, SLIDE_H - 12, SLIDE_W, 12, fill=1, stroke=0)
    c.rect(60, SLIDE_H - 145, 8, 115, fill=1, stroke=0)

    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor('#94A3B8'))
    c.drawString(85, SLIDE_H - 135, 'THE WRITING EDIT  |  CLASSROOM DIAGNOSTIC SUITE')
    c.setFont('JHB', 40)
    c.setFillColor(colors.white)
    c.drawString(85, SLIDE_H - 190, '111 學測英文作文：全班三大集體盲區剖析')
    c.setFont('JH', 18)
    c.setFillColor(colors.HexColor('#CBD5E1'))
    c.drawString(85, SLIDE_H - 230, '主題：規劃理想新公園  |  突破「主動不一致、逐字直譯、搭配詞誤用」三大痛點')

    card_w = (SLIDE_W - 120 - 40) / 3
    card_y = 100
    card_h = 145
    cards = [
        ("盲區 1：主動與助動詞", "Picture A have & will very cool", "主詞單數動詞加 s 遺漏\nwill 助動詞後漏掉 be 動詞"),
        ("盲區 2：中式逐字直譯", "along with my ages going up", "中文「年紀增長」逐字翻\n英文應為 as I grew older"),
        ("盲區 3：轉折與搭配詞", "In reverse & take a picnic", "In reverse 為倒車非對比\n野餐道地片語為 have a picnic")
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

    box_w = 415

    # Slide 2: Blind Spot 1
    draw_slide_top(2, '盲區 1：主詞三單動詞未加 s 與助動詞後漏 be 動詞', '文法基礎失分')
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
    c.drawString(85, 345, '1. "The picture A have many facilities..."')
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(85, 312, '2. "...so it will very cool."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. Picture A 為第三人稱單數，動詞需用 has。')
    c.drawString(70, 195, '2. will 為助動詞，後接形容詞 cool 前不可漏 be。')
    c.drawString(70, 165, '3. 閱卷老師直接判定為基礎文法概念不扎實。')

    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)
    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【高分精修對策】')
    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(530, 345, '1. "Picture A features diverse facilities..."')
    c.setFont('GeorgiaBold', 18)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(530, 312, '2. "...so it will be cool and shaded."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '對策 1：動筆後務必回頭檢查主詞三單與動詞一致。')
    c.drawString(515, 195, '對策 2：will + be + 形容詞（不可漏 be）。')
    c.drawString(515, 165, '對策 3：動詞升級：have ➔ features / offers。')
    c.showPage()

    # Slide 3: Blind Spot 2
    draw_slide_top(3, '盲區 2：中式逐字直譯「隨著年齡增長」', '母語自然度')
    c.setFillColor(colors.HexColor('#FEF2F2'))
    c.setStrokeColor(colors.HexColor('#F87171'))
    c.setLineWidth(1.2)
    c.roundRect(50, 105, box_w, 325, 8, fill=1, stroke=1)
    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(70, 395, '【中式逐字直譯】')
    c.setFillColor(colors.white)
    c.roundRect(70, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(RED))
    c.line(70, 290, 70, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(85, 345, '"Along with my ages going up,')
    c.drawString(85, 312, 'my thought is change..."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. 中文「隨著年齡上去」逐字硬翻成英文。')
    c.drawString(70, 195, '2. age 通常不加複數，亦不與 go up 連用。')
    c.drawString(70, 165, '3. is change 兩個動詞連用，語法錯誤。')

    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)
    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【道地英文表達】')
    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(530, 345, '"As I grew older,')
    c.drawString(530, 312, 'my preferences gradually shifted..."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '表達 A：As I grew older / As time went by。')
    c.drawString(515, 195, '表達 B：With age, my thoughts began to mature。')
    c.drawString(515, 165, '字彙升級：thought ➔ preference / perspective。')
    c.showPage()

    # Slide 4: Blind Spot 3
    draw_slide_top(4, '盲區 3：轉折詞誤用 In reverse 與生硬搭配詞', '篇章與詞彙')
    c.setFillColor(colors.HexColor('#FEF2F2'))
    c.setStrokeColor(colors.HexColor('#F87171'))
    c.setLineWidth(1.2)
    c.roundRect(50, 105, box_w, 325, 8, fill=1, stroke=1)
    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(70, 395, '【常見生硬搭配詞】')
    c.setFillColor(colors.white)
    c.roundRect(70, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(RED))
    c.line(70, 290, 70, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(RED))
    c.drawString(85, 345, '1. "In reverse, picture B has trees."')
    c.drawString(85, 312, '2. "...so I can take a picnic here."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(70, 255, '【盲區診斷】：')
    c.setFont('JH', 15)
    c.drawString(70, 225, '1. In reverse 通常指倒退駕駛或順序顛倒。')
    c.drawString(70, 195, '2. 野餐動詞更道地習慣為 have a picnic。')
    c.drawString(70, 165, '3. 篇章轉折詞需展現邏輯層次。')

    c.setFillColor(colors.HexColor('#F0FDF4'))
    c.setStrokeColor(colors.HexColor('#4ADE80'))
    c.setLineWidth(1.2)
    c.roundRect(495, 105, box_w, 325, 8, fill=1, stroke=1)
    c.setFont('JHB', 20)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(515, 395, '【道地搭配詞升級】')
    c.setFillColor(colors.white)
    c.roundRect(515, 290, box_w - 40, 90, 6, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor(GREEN))
    c.line(515, 290, 515, 380)
    c.setFont('GeorgiaBold', 17)
    c.setFillColor(colors.HexColor(GREEN))
    c.drawString(530, 345, '1. "In contrast, Picture B provides..."')
    c.drawString(530, 312, '2. "...so I can have a picnic on the lawn."')
    c.setFont('JHB', 16)
    c.setFillColor(colors.HexColor(TEXT_DARK))
    c.drawString(515, 255, '【精修對策】：')
    c.setFont('JH', 15)
    c.drawString(515, 225, '轉折替換：In contrast / On the other hand。')
    c.drawString(515, 195, '動詞搭配：have a picnic / go on a picnic。')
    c.drawString(515, 165, '遛狗搭配：walk my dog / enjoy leisurely strolls。')
    c.showPage()

    # Slide 5: Summary Action Plan
    draw_slide_top(5, '課堂總結：新公園規劃題型高分三大鐵律', '實戰行動指南')
    card_y = 110
    card_h = 310
    c_w = (SLIDE_W - 100 - 40) / 3

    steps = [
        ("鐵律 1：兩段分工明確", "切題率 100%", "1. 第一段明確點名兩公園特色與理由。\n2. 第二段詳細規劃活動與具體好處。\n3. 首尾呼應，文長至少 120~150 字。"),
        ("鐵律 2：主動時態零失誤", "保住文法基本分", "1. 單數主詞動詞務必加 s (has, offers)。\n2. will 後方形容詞前必加 be 動詞。\n3. 回憶童年用過去式，現狀用現在式。"),
        ("鐵律 3：感官摹寫與修辭", "爭取 15+ 頂標分", "1. 描摹林蔭綠意、微風與笑聲。\n2. 善用 In contrast, Furthermore 串接。\n3. 結尾昇華為身心療癒與社區凝聚力。")
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

def render_slides_html_111(out_path):
    html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>111 學測英文作文：全班三大集體盲區剖析簡報</title>
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
    <h1 class="text-4xl md:text-6xl font-bold tracking-tight text-white leading-tight">111 學測英文作文<br><span class="text-emerald-400">理想新公園規劃三大盲區剖析</span></h1>
    <p class="text-lg md:text-xl text-slate-300 max-w-2xl mx-auto">從學生真實手寫原稿出發，突破「主動不一致、逐字直譯、搭配詞誤用」三大痛點</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-8 text-left">
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-sky-400 font-bold uppercase tracking-wider">盲區 1：主動與助動詞</span>
        <h4 class="text-lg font-bold text-white mt-1">Picture A have & will very cool</h4>
        <p class="text-xs text-slate-400 mt-2">主詞單數動詞加 s 遺漏；will 助動詞後漏掉 be 動詞</p>
      </div>
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-amber-400 font-bold uppercase tracking-wider">盲區 2：逐字直譯</span>
        <h4 class="text-lg font-bold text-white mt-1">along with my ages going up</h4>
        <p class="text-xs text-slate-400 mt-2">中文「年紀增長」逐字翻，英文應為 as I grew older</p>
      </div>
      <div class="bg-slate-800/80 p-5 rounded-xl border border-slate-700">
        <span class="text-xs text-rose-400 font-bold uppercase tracking-wider">盲區 3：轉折搭配詞</span>
        <h4 class="text-lg font-bold text-white mt-1">In reverse & take a picnic</h4>
        <p class="text-xs text-slate-400 mt-2">In reverse 為倒車非對比；野餐道地片語為 have a picnic</p>
      </div>
    </div>
  </div>
</section>

<!-- Slide 2: Blind Spot 1 -->
<section id="slide-2" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-rose-900/60 text-rose-300 text-sm font-bold rounded">盲區 1 · 文法基礎失分</span>
      <span class="text-slate-400 text-sm">SLIDE 02 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">主詞三單動詞未加 s 與助動詞後漏 be 動詞</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 學生原稿真實破綻</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-base text-rose-200 space-y-2">
          <p>1. "...the picture A <b class="text-rose-400 underline">have</b> many facilities..."</p>
          <p>2. "...the park have trees, so it <b class="text-rose-400 underline">will very cool</b>."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. Picture A 為第三人稱單數，動詞需用 has。</p>
          <p>2. will 為助動詞，後接形容詞 cool 前不可漏 be。</p>
          <p>3. 閱卷老師直接判定為基礎文法概念不扎實。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ 高分精修對策</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-base text-emerald-200 space-y-2">
          <p>1. "Picture A <b class="text-emerald-400">features / offers</b> diverse facilities..."</p>
          <p>2. "...the park has trees, so it <b class="text-emerald-400">will be cool</b> and shaded."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>對策 1：動筆後務必回頭檢查主詞三單與動詞一致。</p>
          <p>對策 2：will + be + 形容詞（不可漏 be）。</p>
          <p>對策 3：動詞升級：have ➔ features / offers。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Slide 3: Blind Spot 2 -->
<section id="slide-3" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-amber-900/60 text-amber-300 text-sm font-bold rounded">盲區 2 · 母語自然度</span>
      <span class="text-slate-400 text-sm">SLIDE 03 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">中式逐字直譯「隨著年齡增長」</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 中式逐字直譯</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-base text-rose-200 space-y-2">
          <p>"<b class="text-rose-400">Along with my ages going up</b>,</p>
          <p>my thought <b class="text-rose-400">is change</b> about the ideal park..."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. 中文「隨著年齡上去」逐字硬翻成英文。</p>
          <p>2. age 通常不加複數，亦不與 go up 連用。</p>
          <p>3. is change 兩個動詞連用，語法錯誤。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ 道地英文表達</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-base text-emerald-200 space-y-2">
          <p>"<b class="text-emerald-400">As I grew older</b>,</p>
          <p>my <b class="text-emerald-400">preferences gradually shifted</b>..."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>表達 A：As I grew older / As time went by。</p>
          <p>表達 B：With age, my thoughts began to mature。</p>
          <p>字彙升級：thought ➔ preference / perspective。</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Slide 4: Blind Spot 3 -->
<section id="slide-4" class="slide flex-col justify-center items-center">
  <div class="max-w-5xl w-full mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-700 pb-3">
      <span class="px-3 py-1 bg-sky-900/60 text-sky-300 text-sm font-bold rounded">盲區 3 · 篇章與詞彙</span>
      <span class="text-slate-400 text-sm">SLIDE 04 / 05</span>
    </div>
    <h2 class="text-3xl font-bold text-white">轉折詞誤用 In reverse 與生硬搭配詞</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
      <div class="bg-rose-950/40 border border-rose-600/40 rounded-xl p-6 space-y-4">
        <div class="text-rose-400 font-bold text-lg">❌ 常見生硬搭配詞</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-rose-500 font-serif text-base text-rose-200 space-y-2">
          <p>1. "<b class="text-rose-400">In reverse</b>, picture B has trees."</p>
          <p>2. "...so I can <b class="text-rose-400">take a picnic</b> here."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【盲區診斷】：</p>
          <p>1. In reverse 通常指倒退駕駛或順序顛倒。</p>
          <p>2. 野餐動詞更道地習慣為 have a picnic。</p>
          <p>3. 篇章轉折詞需展現邏輯層次。</p>
        </div>
      </div>
      <div class="bg-emerald-950/40 border border-emerald-600/40 rounded-xl p-6 space-y-4">
        <div class="text-emerald-400 font-bold text-lg">✅ 道地搭配詞升級</div>
        <div class="bg-slate-900/90 p-4 rounded-lg border-l-4 border-emerald-500 font-serif text-base text-emerald-200 space-y-2">
          <p>1. "<b class="text-emerald-400">In contrast</b>, Picture B provides..."</p>
          <p>2. "...so I can <b class="text-emerald-400">have a picnic</b> on the lawn."</p>
        </div>
        <div class="text-sm text-slate-300 space-y-2">
          <p class="font-bold text-white">【精修對策】：</p>
          <p>轉折替換：In contrast / On the other hand。</p>
          <p>動詞搭配：have a picnic / go on a picnic。</p>
          <p>遛狗搭配：walk my dog / enjoy leisurely strolls。</p>
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
    <h2 class="text-3xl font-bold text-white">課堂總結：新公園規劃題型高分三大鐵律</h2>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 1：兩段分工明確</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 第一段明確點名兩公園特色與理由。</p>
          <p>2. 第二段詳細規劃活動與具體好處。</p>
          <p>3. 首尾呼應，文長至少 120~150 字。</p>
        </div>
      </div>
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 2：主動時態零失誤</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 單數主詞動詞務必加 s (has, offers)。</p>
          <p>2. will 後方形容詞前必加 be 動詞。</p>
          <p>3. 回憶童年用過去式，現狀用現在式。</p>
        </div>
      </div>
      <div class="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
        <div class="text-emerald-400 font-bold text-xl">鐵律 3：感官摹寫與修辭</div>
        <div class="text-sm text-slate-300 space-y-2 pt-2">
          <p>1. 描摹林蔭綠意、微風與笑聲。</p>
          <p>2. 善用 In contrast, Furthermore 串接。</p>
          <p>3. 結尾昇華為身心療癒與社區凝聚力。</p>
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

# ==================== MAIN EXECUTION ====================

def main():
    print("==================== STARTING 111 SUITE GENERATION ====================")

    # 1. Page 1 & 2 for 301 Class Student 01 and 111 CEEC 01
    essays = [
        (DATA_301_01, TMP / "111_s01_p1.pdf", TMP / "111_s01_p2.pdf", "301班_01號"),
        (DATA_111_CEEC, TMP / "111_ceec_p1.pdf", TMP / "111_ceec_p2.pdf", "111學測佳作01")
    ]

    for data, p1_path, p2_path, prefix in essays:
        render_page_1(data, p1_path)
        render_page_2(data, p2_path)

        # 2-Page Print PDF
        two_page_out = OUT_DIR / f"{prefix}_前兩頁雙面列印_雜誌風.pdf"
        w2 = PdfWriter()
        r1 = PdfReader(p1_path)
        r2 = PdfReader(p2_path)
        w2.add_page(r1.pages[0])
        w2.add_page(r2.pages[0])
        with open(two_page_out, 'wb') as f:
            w2.write(f)
        print(f"Saved 2-Page Print PDF: {two_page_out.name} ({two_page_out.stat().st_size:,} bytes)")

        # 7-Page Full Magazine PDF
        full_mag_out = OUT_DIR / f"{prefix}_雜誌風手寫批改_The_Writing_Edit.pdf"
        det_pdf = TMP / "tmp_mag_v3" / "details.pdf"
        w7 = PdfWriter()
        w7.add_page(r1.pages[0])
        w7.add_page(r2.pages[0])
        if det_pdf.exists():
            r_det = PdfReader(det_pdf)
            for page in r_det.pages:
                w7.add_page(page)
        with open(full_mag_out, 'wb') as f:
            w7.write(f)
        print(f"Saved 7-Page Magazine PDF: {full_mag_out.name} ({full_mag_out.stat().st_size:,} bytes)")

    # 2. Worksheets
    print("\n--- Generating 111 Worksheets ---")
    ws_s = OUT_DIR / "111學測作文_大家來找碴_挑錯微講義_學用版.pdf"
    ws_t = OUT_DIR / "111學測作文_大家來找碴_挑錯微講義_教用解答版.pdf"
    render_worksheet_111(is_teacher=False, out_path=ws_s)
    render_worksheet_111(is_teacher=True, out_path=ws_t)

    # 3. Slides
    print("\n--- Generating 111 Slides ---")
    sl_pdf = OUT_DIR / "111學測作文_全班三大集體盲區_課堂投影簡報.pdf"
    sl_html = OUT_DIR / "111學測作文_全班三大集體盲區_課堂投影簡報.html"
    render_slides_111(sl_pdf)
    render_slides_html_111(sl_html)

    print("\n==================== 111 SUITE COMPLETED SUCCESSFULLY ====================")

if __name__ == '__main__':
    main()
