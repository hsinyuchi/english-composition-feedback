"""Render validated, agent-neutral JSON using fixed PDF and XLSX templates."""
import argparse
from copy import deepcopy
from html import escape
from io import BytesIO
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from jsonschema import Draft202012Validator
from PIL import Image, ImageFilter, ImageMath
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether

from essay_tools import count_words

ROOT = Path(__file__).resolve().parents[1]
THEME = json.loads((ROOT / 'templates/theme.json').read_text(encoding='utf-8'))
W, H = A4
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
ET.register_namespace('', NS)


def validate(data, base):
    schema = json.loads((ROOT / 'templates/feedback.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(data)
    ids, seats, filenames = set(), set(), set()
    for s in data['students']:
        if s.get('reflections_en') and len(s['reflections_en'])!=len(s['reflections']):
            raise ValueError('English and Chinese reflection counts must match')
        filename=s.get('pdf_filename',s['id']+'_full.pdf').casefold()
        if filename in filenames or filename in {'front.pdf','detail.pdf','class_print.pdf'}:
            raise ValueError('Duplicate or reserved PDF filename')
        filenames.add(filename)
        if [(x['label'],x['max']) for x in s['scores']] != [('內容',5),('組織',5),('文法句構',5),('字彙拼字',5)]:
            raise ValueError('Use current CEEC GSAT four-dimension rubric, each /5')
        key = (s['class'], s['seat'])
        if s['id'] in ids or key in seats:
            raise ValueError('Duplicate student ID or class/seat')
        ids.add(s['id']); seats.add(key)
        if any(x['value'] > x['max'] for x in s['scores']):
            raise ValueError('Score exceeds maximum')
        if s['deduction'] > sum(x['value'] for x in s['scores']):
            raise ValueError('Deduction exceeds earned score')
        sentence_ids = [x['id'] for x in s['sentences']]
        if sentence_ids != list(range(1, len(sentence_ids)+1)):
            raise ValueError('Sentence IDs must be consecutive from 1')
        normalize = lambda t: re.sub(r'\s+', ' ', t).strip()
        if normalize(' '.join(s['paragraphs'])) != normalize(' '.join(x['original'] for x in s['sentences'])):
            raise ValueError('Original sentences do not match transcription')
        if any(e['sentence_id'] not in sentence_ids for e in s['errors']):
            raise ValueError('Error references missing sentence')
        if any(x['sentence_id'] not in sentence_ids for x in s['optional_rewrites']):
            raise ValueError('Optional rewrite references missing sentence')
        if s.get('scan') and not (base / s['scan']).is_file():
            raise ValueError('Missing scan image')
        if s.get('annotations') and not s.get('scan'):
            raise ValueError('Annotations require a scan image')
        for a in s.get('annotations', []):
            if a['operation']!='delete' and not a['text'].strip():
                raise ValueError('Replacement and insertion need correction text')
            if a['x'] + a['width'] > 1:
                raise ValueError('Annotation extends beyond scan width')
            if a['target'][0]+a['target'][2]>1:
                raise ValueError('Target extends beyond scan width')
            if a['operation']=='insert' and a['target'][2]!=0:
                raise ValueError('Insertion target must be one precise point (width 0)')
    if len({tuple((x['label'], x['max']) for x in s['scores']) for s in data['students']}) != 1:
        raise ValueError('A batch must use one consistent rubric')


def register_fonts(regular, bold, hand):
    for name, path in [('Body', regular), ('Bold', bold), ('Hand', hand)]:
        if not path or not Path(path).is_file():
            raise ValueError(f'Provide an existing font file for {name}')
        pdfmetrics.registerFont(TTFont(name, str(path)))


def para(text, size=11, font='Body', color=None):
    glyphs=pdfmetrics.getFont(font).face.charToGlyph
    missing={ch for ch in str(text) if not ch.isspace() and ord(ch) not in glyphs}
    if missing:raise ValueError(f'Font {font} is missing characters: {"".join(sorted(missing))}')
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), ParagraphStyle(
        'p', fontName=font, fontSize=size, leading=size*1.38,
        textColor=colors.HexColor(color or THEME['ink']), wordWrap='CJK', spaceAfter=7, keepWithNext=size>=13))


def put(c, text, x, y, width, size=11, font='Body', color=None, floor=50):
    p = para(text, size, font, color)
    _, height = p.wrap(width, H)
    if y-height < floor:
        raise ValueError(f'Layout overflow; shorten content, never shrink text: {text[:60]}')
    p.drawOn(c, x, y-height)
    return y-height-7


def heading(c, text, x, y, width):
    return put(c, text, x, y, width, 13, 'Bold', THEME['accent'])


def frame(c, data, s, page):
    c.setFillColor(colors.HexColor(THEME['accent'])); c.rect(0,H-7,W,7,fill=1,stroke=0)
    c.setFont('Bold',9); c.drawString(36,H-26,'THE WRITING EDIT')
    c.setFillColor(colors.HexColor(THEME['muted'])); c.setFont('Body',9)
    c.drawRightString(W-36,H-26,f"{s['class']} / {s['seat']:02d} / {s['name']}")
    c.setStrokeColor(colors.HexColor('#BAC8C0')); c.line(36,35,W-36,35)
    c.drawString(36,21,'原稿 → 訂正 → 理解 → 自己修訂')
    c.drawRightString(W-36,21,str(page).zfill(2))


def table(c, rows, widths, x, y, floor=50):
    content = [[para(v,11,'Bold' if i==0 else 'Body','#FFFFFF' if i==0 else None) for v in row] for i,row in enumerate(rows)]
    t = Table(content, colWidths=widths)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(THEME['ink'])),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EEF4F0')]),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
    _, height = t.wrap(sum(widths),H)
    if y-height < floor: raise ValueError('Table overflow')
    t.drawOn(c,x,y-height)
    return y-height-10


def lines(c,x,y,width,n):
    c.setStrokeColor(colors.HexColor('#B8C4BD'))
    for _ in range(n):
        y -= 21
        if y < 64: raise ValueError('Insufficient writing space on page 2')
        c.line(x,y,x+width,y)
    return y-12


def total(s): return sum(x['value'] for x in s['scores'])-s['deduction']
def counts(s): return count_words('\n\n'.join(s['paragraphs']))


def section(c,en,zh,x,y,width):
    ew=pdfmetrics.stringWidth(en,'Bold',13)
    zw=pdfmetrics.stringWidth('（'+zh+'）','Body',11)
    c.setFillColor(colors.HexColor(THEME['accent']))
    if ew+zw+9<=width:
        c.setFont('Bold',13);c.drawString(x,y-17,en)
        c.setFont('Body',11);c.drawString(x+ew+9,y-17,'（'+zh+'）')
        return y-25
    yy=put(c,en,x,y,width,13,'Bold',THEME['accent'])
    return put(c,'（'+zh+'）',x,yy,width,11,'Body',THEME['accent'])


def compact(c,text,x,y,width,size=11,font='Body',gap=3):
    p=para(text,size,font)
    p.style.leading=size*1.3
    _,height=p.wrap(width,H)
    if y-height<50:raise ValueError('Page 2 text exceeds available space')
    p.drawOn(c,x,y-height)
    return y-height-gap


def draw_scale_bar(c,x,y,width,label):
    """Horizontal scale bar with 1 to 5 nodes for student self-determined rating."""
    c.setFont('Body',11);c.setFillColor(colors.HexColor(THEME['ink']))
    c.drawString(x,y-4,label)
    bar_x=x+155;bar_w=width-165
    c.setStrokeColor(colors.HexColor('#BAC8C0'));c.setLineWidth(2)
    c.line(bar_x,y,bar_x+bar_w,y)
    for index in range(5):
        cx=bar_x+(bar_w/4)*index;path=c.beginPath()
        for point in range(10):
            angle=math.pi/2+point*math.pi/5
            radius=8 if point%2==0 else 3.5
            px,py=cx+radius*math.cos(angle),y+radius*math.sin(angle)
            if point==0:path.moveTo(px,py)
            else:path.lineTo(px,py)
        path.close();c.setStrokeColor(colors.HexColor(THEME['accent']));c.setLineWidth(1.1)
        c.drawPath(path,stroke=1,fill=0)
        c.setFillColor(colors.HexColor(THEME['ink']));c.setFont('Bold',9)
        c.drawCentredString(cx,y-13,str(index+1))


def writing_lines(c,y,count):
    c.setStrokeColor(colors.HexColor('#909A94'));c.setLineWidth(.55)
    for _ in range(count):
        y-=20
        if y<48:raise ValueError('Insufficient writing space on page 2')
        c.line(36,y,W-36,y)
    return y-3


def compact_section(c,en,zh,y):
    return section(c,en,zh,36,y,W-72)+5


def second_page(c,data,s):
    # Preflight on a disposable canvas before drawing any student work region.
    probe=canvas.Canvas(BytesIO(),pagesize=A4)
    try:_draw_second_page(probe,data,s)
    except ValueError as exc:
        raise ValueError(f"Page 2 capacity exceeded for {s['id']} (task lines {[t['lines'] for t in s['tasks']]}, {len(s['reflections'])} reflections). Keep all feedback and writing lines; shorten repeated instructions or agree an extended-page arrangement. No partial deliverable is exported.") from exc
    _draw_second_page(c,data,s)


def _draw_second_page(c,data,s):
    """Teacher feedback above a full-width student work band."""
    frame(c,data,s,2)
    title='My Writing: Revision & Reflection'
    c.setFont('Bold',18);c.setFillColor(colors.HexColor(THEME['ink']))
    c.drawString(36,H-58,title)
    offset=pdfmetrics.stringWidth(title,'Bold',18)+7
    c.setFont('Body',11);c.drawString(36+offset,H-58,'（作文修訂與反思）')
    y=H-66
    ct=counts(s);reported=s['reported_count']
    delta=ct['total']-reported if reported is not None else 'n/a'
    y=compact(c,f"Word Count（原稿）{ct['total']} / Self-count（自填）{reported if reported is not None else '未填'} / Difference（差異）{delta}",36,y,W-72)
    width=W-72
    yl=compact_section(c,'Scores & Rationale','評分依據',y)
    c.setFont('Body',9);c.drawRightString(W-36,y-17,'CEEC '+data['rubric_checked'])
    c.linkURL(data['rubric_url'],(W-145,y-19,W-36,y-7),relative=0)
    labels=['Content（內容）','Organization（組織）','Grammar（文法句構）','Vocabulary（字彙拼字）']
    rows=[labels,[f"{item['value']:g} / 5" for item in s['scores']],[item['reason'] for item in s['scores']]]
    content=[[para(v,11,'Bold' if i==0 else 'Body','#FFFFFF' if i==0 else None) for v in row] for i,row in enumerate(rows)]
    for row in content:
        for p in row:p.style.leading=14.3
    t=Table(content,colWidths=[width/4]*4)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(THEME['ink'])),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#EEF4F0')]),
        ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2)]))
    _,th=t.wrap(width,H);t.drawOn(c,36,yl-th);yl-=th+4
    yl=compact(c,f"Total（總分）{total(s):g}/20；扣分 {s['deduction']:g}。"+s['deduction_reason'],36,yl,width)
    yr=compact_section(c,'Teacher Feedback','教師評語',yl)
    yr=compact(c,s['full_comment']['en'],36,yr,width)
    yr=compact(c,'（'+s['full_comment']['zh']+'）',36,yr,width)
    divider=yr-4
    c.setStrokeColor(colors.HexColor(THEME['accent']));c.setLineWidth(.8);c.line(36,divider,W-36,divider)
    yy=compact_section(c,'My Revision Tasks','我的修訂任務',divider-1)
    for i,task in enumerate(s['tasks']):
        c.setStrokeColor(colors.HexColor(THEME['ink']));c.setLineWidth(.8)
        c.rect(36,yy-12,9,9,fill=0,stroke=1)
        label=f'Task {i+1}（任務{i+1}）'
        text=label+' '+task.get('instruction_en','')+'（'+task['instruction']+'）'
        yy=compact(c,text,51,yy,W-87,gap=0)
        yy=writing_lines(c,yy,task['lines'])
    yy=compact_section(c,'My Reflection','我的反思',yy-1)
    for i,question in enumerate(s['reflections']):
        text=f'{i+1}. '+(s['reflections_en'][i]+' ' if s.get('reflections_en') else '')+'（'+question+'）'
        yy=compact(c,text,36,yy,W-72,gap=1)
        if i==0:
            c.setFont('Body',9.5);c.setFillColor(colors.HexColor(THEME['muted']))
            c.drawRightString(W-36,yy-8,'回溯自評：1 到 5 刻度軸')
            for row,label in enumerate(['Before（修訂前起點）：','After （修訂後落點）：']):
                baseline=yy-10-row*20
                draw_scale_bar(c,36,baseline,W-72,label)
            yy-=48
        else:yy=writing_lines(c,yy,2)
    compact(c,'Date（修訂日期）：____________    Teacher Review（教師核閱）：□ 精熟卓越  □ 良好達標  □ 需再修訂    簽章：____________',36,yy,W-72)


def reflection_column(c,s,x,y,width):
    y=put(c,'修訂日期：________________',x,y,width)
    y=heading(c,'本篇個別化修訂任務',x,y,width)
    for number,task in enumerate(s['tasks'],1):
        y=put(c,f"任務{number}｜{task['instruction']}",x,y,width)
        y=lines(c,x,y,width,task['lines'])
    y=heading(c,'學習歷程反思',x,y,width)
    for number,question in enumerate(s['reflections'],1):
        y=put(c,f'{number}｜{question}',x,y,width)
        if number==1:
            y=put(c,'回溯自評：前____ /5；後____ /5\n1需協助，5可獨立完成。',x,y,width)
        else:y=lines(c,x,y,width,2)
    put(c,'教師回饋／核閱：________________',x,y,width)


def front(path, data, s, base):
    c = canvas.Canvas(str(path),pagesize=A4)
    frame(c,data,s,1)
    y = put(c,data.get('assignment_en','My Writing'),36,H-49,W-72,21,'Bold')
    y = put(c,data['assignment'],36,y,W-72,11)
    y = put(c,f"原稿 {counts(s)['total']} 字 | 教學估分 {total(s):g} / {sum(x['max'] for x in s['scores']):g}",36,y,W-72,12,'Bold')
    top, bottom = y-4, 196
    if top-bottom<100:raise ValueError('Too little space for original')
    if s.get('scan'):
        scan_file = base / s['scan']
        deskew_deg = s.get('deskew_angle', 0.0)
        whiten_bg = s.get('whiten', False)
        if deskew_deg or whiten_bg:
            with Image.open(scan_file) as im:
                img = im.convert('RGB')
            if deskew_deg:
                img = img.rotate(deskew_deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(255,255,255))
            if whiten_bg:
                gray = img.convert('L')
                bg = gray.filter(ImageFilter.BoxBlur(25))
                diff = ImageMath.eval('convert(min(255, max(0, (float(a) / (float(b) + 0.001)) * 255)), "L")', a=gray, b=bg)
                lut = [255 if i > 200 else int((i / 200) * 255) for i in range(256)]
                gray_clean = diff.point(lut)
                img = Image.merge('RGB', (gray_clean, gray_clean, gray_clean))
            clean_path = scan_file.parent / f'_conditioned_{scan_file.name}'
            img.save(clean_path)
            scan_file = clean_path
        with Image.open(scan_file) as image:
            image_width,image_height=image.size
        if image_height / image_width > 1.8:
            raise ValueError('Long scan: split into readable pages before annotation; do not shrink handwriting')
        scale = min((W-72)/image_width, (top-bottom)/image_height)
        iw,ih = image_width*scale,image_height*scale
        ix,iy = (W-iw)/2, top-ih
        c.drawImage(str(scan_file),ix,iy,iw,ih)
        boxes = []
        number=0
        for a in s.get('annotations',[]):
            tx=ix+a['target'][0]*iw;ty=top-a['target'][1]*ih;tw=a['target'][2]*iw
            if a['operation']=='delete':
                c.setStrokeColor(colors.HexColor(THEME['red']));c.setLineWidth(1.5)
                c.line(tx,ty+4,tx+tw,ty+10)
                continue
            number+=1
            ax, ay, aw = ix+a['x']*iw, top-a['y']*ih, a['width']*iw
            if aw < 42: raise ValueError('Annotation width too small')
            p = para(a['text'],THEME['annotation_size'],'Hand',THEME['red'])
            _,ph = p.wrap(aw-25,H)
            box = (ax,ay-ph,ax+aw,ay)
            if box[1] < iy: raise ValueError('Annotation below scan boundary')
            if any(box[0]<b[2] and box[2]>b[0] and box[1]<b[3] and box[3]>b[1] for b in boxes):
                raise ValueError('Annotations overlap; adjust normalized coordinates')
            boxes.append(box)
            c.setFillColor(colors.HexColor('#F2F2F2'));c.rect(ax+24,ay-ph,aw-24,ph,fill=1,stroke=0)
            c.setFillColor(colors.black);c.rect(ax,ay-13,23,13,fill=1,stroke=0)
            c.setFillColor(colors.white);c.setFont('Helvetica-Bold',7);c.drawString(ax+2,ay-10,f"{number}{a['label']}")
            p.drawOn(c,ax+25,ay-ph)
            tx=ix+a['target'][0]*iw;ty=top-a['target'][1]*ih;tw=a['target'][2]*iw
            c.setStrokeColor(colors.HexColor(THEME['red']));c.setLineWidth(1.5)
            if a['operation']=='insert':
                c.line(tx-4,ty-7,tx,ty);c.line(tx,ty,tx+4,ty-7)
            elif a['operation']=='delete':
                c.line(tx,ty+4,tx+tw,ty+10)
            else:
                c.line(tx,ty,tx+tw,ty);c.line(tx,ty,tx,ty+4);c.line(tx+tw,ty,tx+tw,ty+4)
            c.setStrokeColor(colors.black);c.setLineWidth(.6)
            c.line(ax+aw/2,ay-ph-1,tx+(tw/2),ty+3)
    else:
        yy = heading(c,'原稿逐字稿（未提供手寫影像）',36,top,W-72)
        original='\n\n'.join(s['paragraphs'])
        preview=original
        while para(preview,12).wrap(W-72,H)[1] > yy-bottom-32:
            preview=preview[:-30]
            if not preview: raise ValueError('No room for original preview')
        if preview != original:
            preview += '\n（原稿節錄；完整原文見第3頁起。）'
        put(c,preview,36,yy,W-72,12,floor=bottom)
    score_labels=['Content\n內容','Organization\n組織','Grammar\n文法句構','Vocabulary\n字彙拼字']
    y = table(c,[score_labels, [f"{x['value']:g} / {x['max']:g}" for x in s['scores']]],[(W-72)/4]*4,36,175)
    put(c,'紅字為必要修正；^ 插字、斜線刪除、粗線定位。完整英中評語見第2頁。',36,y,W-72)
    c.showPage();second_page(c,data,s)
    c.save()


def detail(path,data,s):
    story=[para('Original Draft | 原稿完整逐字稿',16,'Bold',THEME['accent'])]+[para(x,12) for x in s['paragraphs']]+[Spacer(1,15)]
    if s['uncertainties']:
        story += [para('To Verify | 待核對事項',16,'Bold')]+[para(x) for x in s['uncertainties']]
    for sent in s['sentences']:
        block=[para(f"SENTENCE {sent['id']:02d} | 逐句精修",16,'Bold',THEME['accent']),para('Original | 原句：'+sent['original']),para('Basic Revision | 基本修正：'+sent['basic'])]
        block += [para('Note | 說明：'+note) for note in sent['notes']]
        for item in s['optional_rewrites']:
            if item['sentence_id']==sent['id']:
                block += [para('Optional Refinement | 可選潤飾｜'+item['note'],12,'Bold'),
                          para('Keep | 保留表達：'+item['original']),
                          para('Alternative | 替代寫法：'+item['alternative'])]
        block += [para('Advanced Expression | 進階表達：'+sent['advanced']),Spacer(1,15)]
        story.append(KeepTogether(block))
    from reportlab.platypus import PageBreak
    for key,title in [('basic','Basic Revision | 基礎修訂版'),('advanced','Enhanced Version | 進階示範版')]:
        story += [PageBreak(),para(title,20,'Bold'),para('Full Model Essay | 完整文章英中對照',13,'Bold'),para('教師示範；進階版新增內容需與原稿區分。')]
        for i,pair in enumerate(s['models'][key],1):
            story += [para(f'Paragraph {i} | 第 {i} 段',13,'Bold',THEME['accent']),para(pair['en'],12),para(pair['zh'],12),Spacer(1,10)]
    doc=SimpleDocTemplate(str(path),pagesize=A4,leftMargin=36,rightMargin=36,topMargin=52,bottomMargin=50)
    doc.build(story,onFirstPage=lambda c,d:frame(c,data,s,d.page+2),onLaterPages=lambda c,d:frame(c,data,s,d.page+2))


def column(n):
    result=''
    while n:n,r=divmod(n-1,26);result=chr(65+r)+result
    return result


def workbook(data, path):
    """Populate an artifact-tool-authored workbook using portable OOXML APIs."""
    students=data['students']; n=len(students)
    rows=[[],[],[],[],[],[]]
    for i,s in enumerate(students,2):
        ct=counts(s)
        source_label=(data['rubric_source']+' '+data['rubric_checked']).replace('"','""')
        source_link=(f'HYPERLINK("{data["rubric_url"]}","{source_label}")',data['rubric_source']+' '+data['rubric_checked'])
        rows[0].append([s['id'],s['class'],s['seat'],s['name'],*[x['value'] for x in s['scores']],s['deduction'],('SUM(E%d:H%d)-I%d'%(i,i,i),total(s)),ct['total'],s['reported_count'],(f'IF(L{i}="","",K{i}-L{i})',ct['total']-s['reported_count'] if s['reported_count'] is not None else ''),s.get('pdf_filename',f"{s['id']}_full.pdf"),source_link])
        rows[1].append([s['id'],s.get('short_comment',{}).get('en'),s.get('short_comment',{}).get('zh'),s['full_comment']['en'],s['full_comment']['zh']])
        for j,t in enumerate(s['tasks'],1):
            instruction=(t['instruction_en']+'\n' if t.get('instruction_en') else '')+t['instruction']
            rows[2].append([s['id'],j,instruction,'未開始',None,None])
        for e in s['errors']:rows[3].append([s['id'],e['sentence_id'],e['category'],e['original'],e['correction'],e['reason']])
        questions=[(s['reflections_en'][i]+'\n' if s.get('reflections_en') else '')+q for i,q in enumerate(s['reflections'])]
        questions += [None]*(3-len(questions))
        rows[4].append([s['id'],*questions,None,None,None,None])
    rows[5]=[['已批人數',(f"COUNTA('成績總表'!A2:A{n+1})",n)],['平均總分',(f"AVERAGE('成績總表'!J2:J{n+1})",sum(total(s) for s in students)/n)]]
    # One indicator per student makes repeated errors count as one affected student.
    er=max(2,len(rows[3])+1)
    for cat in ['Sp','G','W','P']:
        affected=sum(any(e['category']==cat for e in s['errors']) for s in students)
        formula='+'.join(f"IF(COUNTIFS('錯誤紀錄'!A2:A{er},'成績總表'!A{i},'錯誤紀錄'!C2:C{er},\"{cat}\")>0,1,0)" for i in range(2,n+2))
        rows[5].append([cat+' 涉及學生數',(formula,affected)])
    with ZipFile(ROOT/'templates/classroom.xlsx') as src, ZipFile(path,'w',ZIP_DEFLATED) as dest:
        for item in src.infolist():
            raw=src.read(item.filename)
            match=re.fullmatch(r'xl/worksheets/sheet(\d+)\.xml',item.filename)
            if match:
                index=int(match.group(1))-1; tree=ET.fromstring(raw); sd=tree.find(f'{{{NS}}}sheetData')
                head=deepcopy(sd.find(f'{{{NS}}}row')); template=sd.findall(f'{{{NS}}}row')[1]
                if index==0:
                    for j,score in enumerate(students[0]['scores'],4):
                        cell=list(head)[j]
                        style=cell.attrib.get('s','0'); ref=cell.attrib['r']
                        cell.clear();cell.attrib.update({'r':ref,'s':style,'t':'inlineStr'})
                        inline=ET.SubElement(cell,f'{{{NS}}}is');ET.SubElement(inline,f'{{{NS}}}t').text=f"{score['label']} /{score['max']:g}"
                styles={re.sub(r'\d','',c.attrib['r']):c.attrib.get('s','0') for c in template}
                sd.clear();sd.append(head)
                for ri,values in enumerate(rows[index],2):
                    row=ET.SubElement(sd,f'{{{NS}}}row',{'r':str(ri),'ht':str(115 if index in [1,2,3,4] else 40),'customHeight':'1'})
                    for ci,val in enumerate(values,1):
                        cell=ET.SubElement(row,f'{{{NS}}}c',{'r':column(ci)+str(ri),'s':styles.get(column(ci),'0')})
                        if val is None:continue
                        if isinstance(val,tuple):
                            ET.SubElement(cell,f'{{{NS}}}f').text=val[0]
                            if isinstance(val[1],str):cell.set('t','str')
                            ET.SubElement(cell,f'{{{NS}}}v').text=str(val[1])
                        elif isinstance(val,(float,int)):ET.SubElement(cell,f'{{{NS}}}v').text=str(val)
                        else:
                            cell.set('t','inlineStr');inline=ET.SubElement(cell,f'{{{NS}}}is');ET.SubElement(inline,f'{{{NS}}}t').text=str(val)
                width=len(head);end=max(2,len(rows[index])+1)
                dim=tree.find(f'{{{NS}}}dimension')
                if dim is not None:dim.set('ref',f'A1:{column(width)}{end}')
                af=tree.find(f'{{{NS}}}autoFilter')
                if af is not None:af.set('ref',f'A1:{column(width)}{end}')
                raw=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            elif item.filename=='xl/workbook.xml':
                tree=ET.fromstring(raw); calc=tree.find(f'{{{NS}}}calcPr')
                if calc is None:calc=ET.SubElement(tree,f'{{{NS}}}calcPr')
                calc.attrib.update({'calcMode':'auto','fullCalcOnLoad':'1'})
                raw=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
            dest.writestr(item,raw)


def build(source,output,font,bold,hand):
    source,output=Path(source).resolve(),Path(output).resolve()
    if output.exists():raise FileExistsError('Choose a new output directory; originals are preserved')
    data=json.loads(source.read_text(encoding='utf-8-sig'));validate(data,source.parent)
    data['students'].sort(key=lambda s:(s['class'],s['seat']))
    register_fonts(font,bold,hand)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        work=Path(temp); merged=PdfWriter(); audit=[]
        for s in data['students']:
            a,b=work/'front.pdf',work/'detail.pdf'
            front(a,data,s,source.parent);detail(b,data,s)
            full=PdfWriter();full.append(a);full.append(b)
            full.write(work/s.get('pdf_filename',s['id']+'_full.pdf'))
            read=PdfReader(a)
            if len(read.pages)!=2:raise ValueError('Print section must be exactly two pages')
            for page in read.pages:merged.add_page(page)
            audit.append({'id':s['id'],'score':total(s),'word_count':counts(s),'pages':len(full.pages)})
        merged.write(work/'class_print.pdf');workbook(data,work/'classroom.xlsx')
        (work/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
        output.mkdir()
        for file in work.iterdir():
            if file.name not in ['front.pdf','detail.pdf']:shutil.copy2(file,output/file.name)
    return audit


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input');parser.add_argument('--out',required=True)
    parser.add_argument('--font',required=True,help='CJK regular TTF/TTC')
    parser.add_argument('--bold',required=True,help='CJK bold TTF/TTC')
    parser.add_argument('--hand',required=True,help='Legible handwriting-style TTF')
    args=parser.parse_args()
    print(json.dumps(build(args.input,args.out,args.font,args.bold,args.hand),ensure_ascii=False,indent=2))
