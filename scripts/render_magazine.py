"""Single-student magazine suite. No filesystem writes on import; explicit fresh output only."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageOps
from jsonschema import Draft202012Validator

W,H=595.276,841.89
NAVY='#1E293B'; INK='#142B2B'; MUTED='#64748B'; RED='#BC1632'; GREEN='#006A4E'; BLUE='#164FB2'
LIGHT='#F6F8FA'; LINE='#CBD5E1'; PALE='#E2E8F0'

def count(s):
    return len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*|\d+",s))

def validate(d,base):
    if not isinstance(d,dict) or 'students' in d: raise ValueError('Use one student per magazine input')
    schema=Path(__file__).resolve().parents[1]/'templates/magazine.schema.json'
    Draft202012Validator(json.loads(schema.read_text(encoding='utf8'))).validate(d)
    for key in ['id','class','seat','topic','paragraphs','sentences','scores','tasks','feedback_zh','feedback_en','basic','enhanced','worksheet','slide_indices','actions','rubric']:
        if key not in d:raise ValueError('Missing '+key)
    if not re.fullmatch(r'[A-Za-z0-9_-]+',d['id']):raise ValueError('Safe single-student filename ID required')
    cls,sep,seat=d['id'].rpartition('_')
    if not sep or cls!=d['class'] or not seat.isdigit() or int(seat)!=d['seat']:raise ValueError('Student ID, class and seat do not agree')
    if len(d['scores'])!=4 or [v['label'] for v in d['scores']]!=['內容','組織','文法句構','字彙拼字']:raise ValueError('Four current rubric dimensions required')
    if any(not 0<=x['value']<=5 for x in d['scores']):raise ValueError('Score outside /5 range')
    if sum(x['value'] for x in d['scores'])-d.get('deduction',0)!=d['total']:raise ValueError('Score total mismatch')
    normalize=lambda s:re.sub(r'\s+',' ',s).strip()
    if normalize(' '.join(d['paragraphs']))!=normalize(' '.join(x['original'] for x in d['sentences'])):raise ValueError('Sentence transcription does not match original paragraphs')
    if not 4<=len(d['sentences'])<=12:raise ValueError('10-page layout supports 4-12 sentences; request a longer edition for larger input')
    if len(d['tasks'])!=3 or len(d['worksheet'])!=5 or len(d['slide_indices'])!=3 or len(d['actions'])!=3:raise ValueError('Need 3 tasks, 5 exercises, 3 slide indices, 3 actions')
    if len(set(d['slide_indices']))!=3 or any(i not in range(5) for i in d['slide_indices']):raise ValueError('Slide indices must select 3 distinct exercises')
    for mode in ['basic','enhanced']:
        if len(d[mode]['en'])!=len(d[mode]['zh']) or not d[mode]['en']:raise ValueError('Bilingual paragraphs missing')
    for i,x in enumerate(d['sentences']):
        for key in ['original','corrected','analysis','optional']:
            if not x.get(key,'').strip():raise ValueError(f'Missing sentence {i+1} {key}')
    for x in d['worksheet']:
        for key in ['title','original','corrected','analysis','rule']:
            if not x.get(key,'').strip():raise ValueError('Incomplete classroom exercise '+key)
        indices=x.get('source_sentence_ids',[])
        if not indices or any(i not in range(1,len(d['sentences'])+1) for i in indices):raise ValueError('Exercise needs valid source sentence IDs')
        source=' '.join(d['sentences'][i-1]['original'] for i in indices)
        mode=x.get('source_mode')
        if mode=='verbatim' and x['original'] not in [d['sentences'][i-1]['original'] for i in indices]:raise ValueError('Verbatim exercise differs from source')
        if mode=='excerpt' and x['original'].lstrip('.').strip() not in source:raise ValueError('Exercise excerpt is absent from its source')
        if mode=='word_list' and any(w.strip() not in source for w in x['original'].split(' / ')):raise ValueError('Exercise words absent from source')
        if mode not in ['verbatim','excerpt','adapted','word_list']:raise ValueError('Exercise source mode required')
    if not d['rubric'].get('checked') or not d['rubric'].get('url','').startswith('https://www.ceec.edu.tw/'):raise ValueError('Verified official rubric citation required')
    if d.get('first_page_pdf'):
        p=base/d['first_page_pdf']; r=PdfReader(p)
        if not r.pages:raise ValueError('First-page source is empty')
        text=(r.pages[0].extract_text() or '').replace('_','-')
        code=re.escape(d['id'].replace('_','-'))
        if not re.search(r'(?<![A-Za-z0-9-])'+code+r'(?![A-Za-z0-9-])',text):raise ValueError('Approved first page belongs to a different student ID')
        normal=lambda s:re.sub(r'[\W_]+','',s)
        if normal(d['topic']) not in normal(text):raise ValueError('Approved first page belongs to a different topic')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=d.get('first_page_sha256'):raise ValueError('Approved first page file fingerprint mismatch')
        bound=hashlib.sha256(normalize(' '.join(d['paragraphs'])).encode('utf8')).hexdigest()
        if bound!=d.get('first_page_transcription_sha256'):raise ValueError('Approved first page transcription binding mismatch')
    elif not d.get('scan') or not (base/d['scan']).is_file():
        raise ValueError('Handwriting scan required; no silent typed-text fallback')
    elif not d.get('short_zh') or not d.get('short_en'):
        raise ValueError('Short bilingual notes required for the handwriting page')
    else:
        with Image.open(base/d['scan']) as im:
            if im.height/im.width>2.2 or d.get('scan_line_count',999)>22:raise ValueError('Long manuscript requires a reviewed split/extended layout, not automatic shrinking')

def fonts():
    for n,p in [('JH','msjh.ttc'),('JHB','msjhbd.ttc'),('Georgia','georgia.ttf'),('GB','georgiab.ttf'),('GI','georgiai.ttf')]:
        fp=Path('C:/Windows/Fonts')/p
        if not fp.is_file():raise ValueError('Required font unavailable: '+str(fp))
        pdfmetrics.registerFont(TTFont(n,str(fp)))

def p(s,size=10.5,font='JH',color=INK):
    # Explicit font checks also inspect Latin text: PDF extraction cannot detect .notdef boxes.
    glyph=pdfmetrics.getFont(font).face.charToGlyph
    missing={ch for ch in str(s) if not ch.isspace() and ord(ch) not in glyph}
    if missing:raise ValueError(f'{font} lacks glyphs: '+''.join(sorted(missing)))
    return Paragraph(html.escape(str(s)).replace('\n','<br/>'),ParagraphStyle('p',fontName=font,fontSize=size,leading=size*1.32,textColor=colors.HexColor(color),wordWrap='CJK'))

def draw(c,s,x,y,width=505,size=10.5,font='JH',color=INK,floor=45):
    q=p(s,size,font,color);_,h=q.wrap(width,1000)
    if y-h<floor:raise ValueError(f'Page overflow: {s[:60]}')
    q.drawOn(c,x,y-h);return y-h

def table(c,rows,widths,x,y,styles=None):
    t=Table(rows,colWidths=widths)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('GRID',(0,0),(-1,-1),.55,colors.HexColor(LINE))]+(styles or [])))
    _,h=t.wrap(sum(widths),1000)
    if y-h<45:raise ValueError('Table exceeds page capacity; rebalance without shrinking body text')
    t.drawOn(c,x,y-h);return y-h

def header(c,d,n,title,sub=None,compact=False):
    c.setFillColor(colors.HexColor(NAVY));c.rect(0,H-7,W,7,fill=1,stroke=0)
    if compact:
        draw(c,'THE WRITING EDIT  |  LEARNING & REVISION WORKBENCH',45,824,size=9,font='GB')
        draw(c,f'{d["class"]}班 {d["seat"]}號 · 修訂與反思',365,823,width=185,size=8.5,color=MUTED)
        c.setStrokeColor(colors.HexColor(LINE));c.line(45,806,550,806)
    else:
        draw(c,title,45,792,size=19,font='JHB',floor=764)
        draw(c,sub or f'{d["class"]}班 {d["seat"]}號 | {d["topic"]}',45,758,size=9.5,color=MUTED,floor=738)
    draw(c,f'THE WRITING EDIT  /  {d["id"]}                                      {n:02d} / 10',45,30,size=8,color=MUTED,floor=12)

def band(c,label,y,width=505):
    c.setFillColor(colors.HexColor(NAVY));c.roundRect(45,y-19,width,19,3,fill=1,stroke=0)
    draw(c,label,53,y-4,width=width-16,size=9.5,font='JHB',color='#FFFFFF');return y-25

def dotted(c,y,n=1,x=52,width=491):
    c.setStrokeColor(colors.HexColor('#94A3B8'));c.setDash(1,3)
    for k in range(n):c.line(x,y-k*24,x+width,y-k*24)
    c.setDash()

def create_first(d,base,out):
    c=canvas.Canvas(str(out),pagesize=(W,H))
    c.setFillColor(colors.HexColor(GREEN));c.rect(0,H-6,W,6,fill=1,stroke=0)
    draw(c,'THE WRITING EDIT  /  '+d['id'],34,817,size=12,font='GB')
    draw(c,d['topic'],34,794,width=527,size=17,font='JHB',floor=769)
    for i,(lab,v) in enumerate([(z['label'],str(z['value'])+'/5') for z in d['scores']]+[('總分',str(d['total'])+'/20')]):
        x=34+i*106;c.setStrokeColor(colors.HexColor(LINE));c.roundRect(x,727,99,36,5,fill=0,stroke=1)
        draw(c,lab,x+7,759,width=88,size=8,color=MUTED);draw(c,v,x+7,745,width=88,size=11,font='GB')
    draw(c,'Sp 拼字 / G 文法 / P 標點 / W 用字 / + 插入 / x 刪除',34,719,width=527,size=8.5)
    im=ImageOps.autocontrast(Image.open(base/d['scan']).convert('L'),cutoff=.6)
    im=im.point(lambda v:255 if v>225 else int((v/225)**1.3*255))
    iw=527;ih=min(491,iw*im.height/im.width);iw=ih*im.width/im.height;ix=34+(527-iw)/2;iy=177+(491-ih)/2
    c.drawImage(ImageReader(im),ix,iy,width=iw,height=ih)
    annotation_boxes=[]
    for a in d.get('annotations',[]):
        # normalized x1/x2/y target coordinates and normalized text x/y on the intact scan
        x1=ix+a['x1']*iw;x2=ix+a['x2']*iw;y=iy+ih-a['y']*ih
        tx=ix+a['text_x']*iw;ty=iy+ih-a['text_y']*ih
        font='Helvetica-Bold' if all(32<=ord(ch)<=126 for ch in a['text']) else 'JHB'
        if font=='JHB':p(a['text'],9.5,font,RED)
        end=tx+28+pdfmetrics.stringWidth(a['text'],font,9.5)
        if min(x1,x2,tx)<34 or max(x1,x2,end)>561 or ty+10>668 or ty-2<177:raise ValueError('Annotation outside manuscript bounds')
        box=(tx,ty-2,end,ty+10)
        if any(box[0]<b[2] and box[2]>b[0] and box[1]<b[3] and box[3]>b[1] for b in annotation_boxes):raise ValueError('Annotation text boxes overlap')
        annotation_boxes.append(box)
        c.setStrokeColor(colors.HexColor(RED));c.setLineWidth(1.2);c.line(x1,y,x2,y)
        if a.get('operation')=='delete':c.line(x1,y+6,x2,y+6)
        if a.get('operation')=='insert':c.lines([(x1-3,y-4,x1,y),(x1,y,x1+3,y-4)])
        c.setFillColor(colors.HexColor(INK));c.roundRect(tx,ty-2,25,11,3,fill=1,stroke=0)
        c.setFont('Helvetica-Bold',6.5);c.setFillColor(colors.white);c.drawCentredString(tx+12.5,ty+1,a['label'])
        c.setFont(font,9.5);c.setFillColor(colors.HexColor(RED));c.drawString(tx+28,ty,a['text'])
    draw(c,'導師筆記｜'+d['short_zh'],34,148,width=527,size=10.5,font='JHB',floor=125)
    draw(c,d['short_en'],34,117,width=527,size=10,font='Georgia',floor=89)
    draw(c,'完整逐句解析見第4–7頁。分數為教學診斷估分，供教師核定。',34,78,width=527,size=9,color=MUTED)
    c.showPage();c.save()

def workbook(c,d):
    header(c,d,2,'',compact=True)
    y=band(c,'PART A | 大考規準評分與教師評語 (Assessment)',797)
    n=sum(count(s) for s in d['paragraphs'])
    y=table(c,[[p(f'總分 {d["total"]}/20 · {d["tier"]}',9.5),p(f'實測 {n}字 · 自填 {d.get("self_count","未填")}字 · 另扣{d.get("deduction",0)}分',9.5)]],[210,295],45,y)
    rows=[[p('評量規準',8.5,'JHB'),p('得分',8.5,'JHB'),p('給分依據與下次修訂焦點',8.5,'JHB')]]
    rows += [[p(v['label'],9,'JHB'),p(str(v['value'])+'/5',9,'GB'),p(v['brief'],9.5)] for v in d['scores']]
    y=table(c,rows,[77,45,383],45,y,[('BACKGROUND',(0,0),(-1,0),colors.HexColor(PALE))])-5
    y=table(c,[[p('導師評語｜'+d['feedback_zh']+'\nTeacher’s Note: '+d['feedback_en'],9)]],[505],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor(LIGHT))])-10
    y=band(c,'PART B | 學生自主修訂任務 (Personalized Tasks)',y)
    for i,t in enumerate(d['tasks'],1):
        y=table(c,[[p(f'任務 {i}｜'+t,9.5)]],[505],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor(LIGHT))])-17
        dotted(c,y);y-=14
    y-=3;y=band(c,'PART C | 學習歷程與後設反思 (Metacognition)',y)
    y=draw(c,'1. 圈選你的掌握程度，再留下修訂證據。',45,y,size=9.5)-10
    for lab in ['Before 修訂前','After 修訂後']:
        draw(c,lab,51,y+5,width=100,size=8.5)
        c.setStrokeColor(colors.HexColor(MUTED));c.line(182,y,540,y)
        for i in range(5):
            x=182+i*89.5;c.circle(x,y,4.4,fill=0,stroke=1);draw(c,str(i+1),x-2.4,y+3.8,width=12,size=6.4)
        y-=18
    y-=4
    cardh=(y-56-6)/2
    if cardh<69:raise ValueError('Reflection writing boxes too small')
    for i,(title,prompt) in enumerate([('原句診斷 (Before)','原句：'),('精修成果 (After)','訂正：'),('核心心法 (Why)','為什麼：'),('下篇策略 (Transfer)','下次我要：')]):
        x=45+(i%2)*259;top=y-(i//2)*(cardh+6)
        c.setFillColor(colors.HexColor(LIGHT));c.setStrokeColor(colors.HexColor(LINE));c.roundRect(x,top-cardh,246,cardh,4,fill=1,stroke=1)
        c.setFillColor(colors.HexColor(NAVY));c.roundRect(x+4,top-17,238,14,2,fill=1,stroke=0)
        draw(c,title,x+9,top-5,width=226,size=8,color='#FFFFFF')
        draw(c,prompt,x+8,top-cardh+16,width=225,size=8,color=MUTED)
    draw(c,'學生：__________ 日期：__________ 教師核閱：□達標 □再修訂',45,55,size=8.5,floor=43)
    c.showPage()

def assessment(c,d):
    header(c,d,3,'大考規準評分核算總表')
    rows=[[p(x,9,'JHB','#FFFFFF') for x in ['評量項目','得分','閱卷規準與原稿具體表現','下一步修訂策略']]]
    for v in d['scores']:rows.append([p(v['label'],10,'JHB'),p(str(v['value'])+'/5',11,'GB'),p(v['reason'],10.5),p(v['strategy'],10.5,color=GREEN)])
    y=table(c,rows,[64,45,254,142],45,732,[('BACKGROUND',(0,0),(-1,0),colors.HexColor(NAVY)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor(LIGHT)])])-18
    counts=[count(t) for t in d['paragraphs']]
    note=f'評分核算｜{d["total"]}/20（{d["tier"]}）\n四項合計 {sum(x["value"] for x in d["scores"])}，另扣 {d.get("deduction",0)} 分。實算 {sum(counts)} 字（各段：'+ ' / '.join(map(str,counts))+f'），學生自填 {d.get("self_count","未填")} 字。英文詞與數字計數，所有格算一詞；不含題目。\n\n整體評閱，再以分項檢驗；不逐錯固定扣分。本分數為教學估分，供教師覆核。\n\n核對與疑義｜'+d.get('uncertainty','無另列疑義。')
    y=table(c,[[p(note,10.5)]],[505],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#F0F4F8'))])-17
    draw(c,'規準來源｜'+d['rubric']['title']+'\n查核日期：'+d['rubric']['checked']+'\n'+d['rubric']['url'],45,y,size=8.5,color=MUTED)
    c.showPage()

def sentence_pages(c,d):
    n=len(d['sentences']);k=0
    for pg in range(4):
        num=n//4+(pg<n%4);group=d['sentences'][k:k+num];k+=num
        header(c,d,pg+4,f'逐句深度精修卡片 — Part {pg+1:02d}','每句獨立卡片：對比原句、精修、考點解析與可選升級')
        y=732
        for j,s in enumerate(group,k-num+1):
            rows=[[p(f'Sentence {j:02d}',9,'JHB','#FFFFFF'),p(s['original'],10.5,'GB',RED)],[p('精修正句',9.5,'JHB',GREEN),p(s['corrected'],10.5,'GB',GREEN)],[p('考點解析',9.5,'JHB',MUTED),p(s['analysis'],10)],[p('可選升級',9.5,'JHB',BLUE),p(s['optional'],10.5,'GI',BLUE)]]
            y=table(c,rows,[77,428],45,y,[('BACKGROUND',(0,0),(0,0),colors.HexColor(NAVY)),('BACKGROUND',(0,1),(0,-1),colors.HexColor(PALE)),('BACKGROUND',(1,0),(1,-1),colors.HexColor(LIGHT))])-11
        draw(c,'藍色升級句為可選示範，不計為原稿錯誤。',45,60,size=9,color=MUTED)
        c.showPage()

def essay(c,d,key,pg):
    title='示範改寫全文：基礎修訂版' if key=='basic' else '示範改寫全文：進階示範版'
    header(c,d,pg,title,'保留原意、修正文法與拼字。' if key=='basic' else '示範改寫，非學生原作；不保證特定學測分數。')
    col=LINE if key=='basic' else '#86DDA8'; bg=LIGHT if key=='basic' else '#F0FDF4'
    en='\n\n'.join(d[key]['en']);zh='\n\n'.join(d[key]['zh'])
    rows=[[p('英文全文 (English Revision)' if key=='basic' else '英文全文 (Enhanced Essay)',10.5,'JHB')],[p(en,11,'Georgia')],[p('繁體中文對照翻譯 (Chinese Translation)',10,'JHB',MUTED)],[p(zh,10.5,'JH',MUTED)]]
    y=table(c,rows,[505],45,732,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor(bg)),('LINEBELOW',(0,1),(-1,1),.7,colors.HexColor(col)),('BOX',(0,0),(-1,-1),.8,colors.HexColor(col))])-14
    if d[key].get('note'):draw(c,d[key]['note'],45,y,size=9.5,color=MUTED)
    c.showPage()

def action(c,d):
    header(c,d,10,'學習歷程反思與個人升級行動指南','將這次批改轉化為下次交卷前可執行的修訂習慣。')
    rows=[[p('個人修訂策略',10,'JHB','#FFFFFF'),p('具體執行步驟與檢查方法',10,'JHB','#FFFFFF')]]
    rows += [[p(a['title'],11,'JHB'),p(a['steps'],10.5)] for a in d['actions']]
    y=table(c,rows,[155,350],45,732,[('BACKGROUND',(0,0),(-1,0),colors.HexColor(NAVY)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor(LIGHT),colors.white])])-18
    summary='學習歷程成果摘要（請依你實際完成的修訂調整）\n\n作品主題：'+d['topic']+'\n本次練習：'+d['learning_summary']+'\n\n我的原句：______________________________\n我的修訂：______________________________\n我能解釋的規則：________________________\n下次交卷前要檢查：______________________'
    table(c,[[p(summary,10.5)]],[505],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#FFF5D6')),('BOX',(0,0),(-1,-1),.8,colors.HexColor('#F4B942'))])
    c.showPage()

def source_label(e):
    return '教學改寫' if e['source_mode']=='adapted' else '詞組整理' if e['source_mode']=='word_list' else '原稿摘句'

def worksheets(d,out):
    for teacher in [False,True]:
        path=out/(d['id']+'_大家來找碴_'+('教用解答版' if teacher else '學用版')+'.pdf')
        c=canvas.Canvas(str(path),pagesize=(W,H))
        c.setFillColor(colors.HexColor(GREEN));c.rect(0,H-7,W,7,fill=1,stroke=0)
        draw(c,'THE WRITING EDIT  |  CLASSROOM SPOT-THE-ERROR CHALLENGE',45,823,size=9,font='GB',color=GREEN)
        draw(c,'大家來找碴：'+('教師詳解' if teacher else '學生練習'),45,800,size=17,font='JHB')
        draw(c,'取自單一作文個案；僅含本次批改的重點，非全班錯誤頻率。',45,774,size=9,color=MUTED)
        y=745
        for i,e in enumerate(d['worksheet'],1):
            y=band(c,f'重點 {i}｜'+e['title'],y)
            y=table(c,[[p(source_label(e),8.5,'JHB',RED),p(e['original'],10,'Georgia')]],[65,440],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor(LIGHT))])-6
            if teacher:
                y=table(c,[[p('錯誤診斷｜'+e['analysis'],9.5)],[p('精修正句｜'+e['corrected'],9.5,'JHB',GREEN)],[p('修訂心法｜'+e['rule'],9,color=MUTED)]],[505],45,y,[('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#F0FDF4')),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)])-14
            else:
                y-=16;dotted(c,y,2);y-=47
        if y<45:raise ValueError('Worksheet overflow')
        draw(c,d['id']+' | 寫給你的一次修訂練習',45,30,size=8,color=MUTED,floor=12)
        c.showPage();c.save()

def slides(d,out):
    sw,sh=960,540
    c=canvas.Canvas(str(out/(d['id']+'_三大修訂重點_課堂投影簡報.pdf')),pagesize=(sw,sh))
    es=[d['worksheet'][i] for i in d['slide_indices']]
    def bg():
        c.setFillColor(colors.HexColor('#0F172A'));c.rect(0,0,sw,sh,fill=1,stroke=0)
        c.setFillColor(colors.HexColor(GREEN));c.rect(0,sh-7,sw,7,fill=1,stroke=0)
    slide_title=d.get('slide_title','作文修訂：三大重點')
    bg();draw(c,'THE WRITING EDIT / '+d['id'],60,440,width=840,size=17,font='GB',color='#6EE7B7')
    draw(c,slide_title,60,375,width=840,size=36,font='JHB',color='#FFFFFF',floor=321)
    draw(c,'從你的原句出發，先修改，再說明理由。',60,302,width=840,size=21,color='#94A3B8')
    draw(c,'單一學生個案 · 非全班統計',60,80,width=840,size=13,color='#94A3B8');c.showPage()
    for j,e in enumerate(es,1):
        bg();draw(c,f'修訂重點 {j:02d}',60,500,width=840,size=13,font='JHB',color='#6EE7B7')
        draw(c,e['title'],60,465,width=840,size=35,font='JHB',color='#FFFFFF',floor=395)
        for x,title,body,col in [(60,source_label(e),e['original'],'#FB7185'),(500,'精修正句',e['corrected'],'#6EE7B7')]:
            c.setFillColor(colors.HexColor(NAVY));c.setStrokeColor(colors.HexColor(RED if x==60 else GREEN));c.setLineWidth(1.6);c.roundRect(x,185,400,192,9,fill=1,stroke=1)
            draw(c,title,x+18,358,width=364,size=12,font='JHB',color=col)
            draw(c,body,x+18,322,width=364,size=22,font='Georgia' if x==60 else 'GB',color=col,floor=191)
        c.setFillColor(colors.HexColor('#022C22'));c.setStrokeColor(colors.HexColor(GREEN));c.roundRect(60,62,840,86,7,fill=1,stroke=1)
        draw(c,'修訂心法｜'+e['rule'],78,130,width=804,size=17,font='JHB',color='#A7F3D0',floor=78)
        c.showPage()
    bg();draw(c,'課堂總結：交卷前的三個檢查',60,485,width=840,size=35,font='JHB',color='#FFFFFF')
    for i,e in enumerate(es):
        top=405-i*111;c.setFillColor(colors.HexColor(NAVY));c.roundRect(60,top-91,840,91,7,fill=1,stroke=0)
        draw(c,f'{i+1}. '+e['title'],80,top-14,width=800,size=20,font='JHB',color='#38BDF8',floor=top-43)
        draw(c,e['rule'],80,top-49,width=800,size=15,color='#CBD5E1',floor=top-83)
    c.showPage();c.save()
    # Fixed local CSS reproduces the supplied dark-card hierarchy, without a CDN dependency.
    escape=html.escape
    sections='<section class="slide active cover"><span class="pill">THE WRITING EDIT</span><h1>'+escape(slide_title)+'</h1><p>從你的原句出發，先修改，再說明理由。</p><small>單一學生個案 · 非全班統計</small></section>'
    for j,e in enumerate(es,1):
        sections+=f'<section class="slide"><span class="pill">修訂重點 {j:02d}</span><h2>{escape(e["title"])}</h2><div class="grid"><article class="wrong"><span>{escape(source_label(e))}</span><p>{escape(e["original"])}</p></article><article class="right"><span>精修正句</span><p>{escape(e["corrected"])}</p></article></div><aside>修訂心法｜{escape(e["rule"])}</aside></section>'
    sections+='<section class="slide"><span class="pill">課堂總結</span><h2>交卷前的三個檢查</h2><div class="summary">'+''.join(f'<article><h3>{i+1}. {escape(e["title"])}</h3><p>{escape(e["rule"])}</p></article>' for i,e in enumerate(es))+'</div></section>'
    css='''*{box-sizing:border-box}body{margin:0;background:#0f172a;color:#f8fafc;font-family:"Microsoft JhengHei",sans-serif;border-top:7px solid #006a4e}header,footer{display:flex;justify-content:space-between;align-items:center;max-width:1180px;margin:auto;padding:18px 28px;border-bottom:1px solid #334155;color:#94a3b8;font-size:14px}main{max-width:1180px;margin:auto;padding:24px 28px}.slide{display:none;min-height:68vh}.slide.active{display:flex;flex-direction:column;justify-content:center;gap:20px}.pill{align-self:flex-start;background:#065f46;color:#a7f3d0;border-radius:5px;padding:7px 15px;font-size:14px}h1,h2{font-size:clamp(28px,3.7vw,48px);margin:4px 0 12px;line-height:1.3}.cover{align-items:center;text-align:center}.cover .pill{align-self:center}.cover p{color:#94a3b8;font-size:23px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{background:#1e293b;border-radius:12px;padding:25px;border:1px solid #334155}.grid article{min-height:240px}.wrong{border-color:#bc1632;color:#fb7185}.right{border-color:#006a4e;color:#6ee7b7}.grid p{font:clamp(20px,2.3vw,30px)/1.5 Georgia,serif}.right p{font-weight:bold}article span{font-size:14px;font-weight:bold}aside{background:#022c22;border:1px solid #006a4e;color:#a7f3d0;border-radius:9px;padding:20px;font-size:21px}.summary{display:grid;gap:16px}.summary h3{color:#38bdf8;margin:0 0 10px}.summary p{margin:0;color:#cbd5e1}.summary article{padding:20px}button{font:inherit;color:white;background:#1e293b;border:1px solid #475569;border-radius:6px;padding:9px 18px;cursor:pointer}button:disabled{opacity:.4}button:focus-visible{outline:3px solid #a7f3d0}footer{border-top:1px solid #334155;border-bottom:0}small{color:#94a3b8}@media(max-width:650px){.grid{grid-template-columns:1fr}.slide{min-height:65vh}.grid article{min-height:145px}.grid p{font-size:22px}aside{font-size:18px}header,footer{gap:15px;flex-wrap:wrap}}@media print{@page{size:landscape}header,footer{display:none}.slide,.slide.active{display:flex;min-height:90vh;break-after:page}.slide:last-child{break-after:auto}*{print-color-adjust:exact}}'''
    js='''const slides=[...document.querySelectorAll('.slide')];let current=0;function show(n){current=Math.min(slides.length-1,Math.max(0,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));document.getElementById('counter').textContent=`${current+1} / ${slides.length}`;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1}document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);document.getElementById('full').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen()};document.addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown'].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}});show(0);'''
    (out/(d['id']+'_三大修訂重點_課堂投影簡報.html')).write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(d['id'])+' 作文修訂</title><style>'+css+'</style><header><b>THE WRITING EDIT</b><span>16:9 課堂投影 · 單一學生個案</span></header><main>'+sections+'</main><footer><span>← → / 空白鍵切換 · <span id="counter">1 / 5</span></span><div><button id="prev">上一頁</button> <button id="next">下一頁</button> <button id="full">全螢幕</button></div></footer><script>'+js+'</script></html>',encoding='utf8')

def render(d,base,out):
    validate(d,base)
    if out.exists():raise FileExistsError('Output directory already exists; choose a new version')
    fonts();out.mkdir(parents=True)
    # Intermediates remain inside this run, never beside the original scan.
    detail=out/'_detail.pdf';c=canvas.Canvas(str(detail),pagesize=(W,H))
    workbook(c,d);assessment(c,d);sentence_pages(c,d);essay(c,d,'basic',8);essay(c,d,'enhanced',9);action(c,d);c.save()
    if d.get('first_page_pdf'):first=base/d['first_page_pdf']
    else:first=out/'_first.pdf';create_first(d,base,first)
    writer=PdfWriter();writer.add_page(PdfReader(first).pages[0]);writer.append(detail)
    full=out/(d['id']+'_完整精修電子檔_10頁雜誌版.pdf')
    with full.open('xb') as f:writer.write(f)
    writer=PdfWriter();r=PdfReader(full)
    if len(r.pages)!=10:raise ValueError('Full book must have exactly 10 pages')
    for pg in r.pages[:2]:writer.add_page(pg)
    with (out/(d['id']+'_前兩頁雙面列印_雜誌風.pdf')).open('xb') as f:writer.write(f)
    worksheets(d,out);slides(d,out)
    report={'student':d['id'],'word_counts':[count(t) for t in d['paragraphs']],'total':d['total'],'source_first_page':str(first.resolve()),'source_first_page_sha256':hashlib.sha256(first.read_bytes()).hexdigest(),'visual_qa':'pending','files':{p.name:p.stat().st_size for p in out.glob('*') if not p.name.startswith('_')}}
    (out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    d=json.loads(a.input.read_text(encoding='utf8'));print(json.dumps(render(d,a.input.parent,a.out),ensure_ascii=True,indent=2))

if __name__=='__main__':main()
