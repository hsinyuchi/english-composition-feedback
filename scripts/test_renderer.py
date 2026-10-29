"""Behavioral tests using synthetic records only."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from jsonschema import ValidationError
from pypdf import PdfReader
from PIL import Image, ImageDraw, ImageFont
from render_feedback import ROOT, NS, validate, build


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'examples/demo.json').read_text(encoding='utf-8'))

    def test_teacher_band_above_three_tasks(self):
        import pdfplumber
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'layout.json'
            source.write_text(json.dumps(self.data),encoding='utf-8')
            build(source,root/'result','C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/comicbd.ttf')
            with pdfplumber.open(root/'result/demo-01_full.pdf') as doc:
                words=doc.pages[1].extract_words()
                scores=[w for w in words if w['text']=='Scores']
                tasks=[w for w in words if w['text']=='Task']
                reflections=[w for w in words if w['text']=='Reflection' and w['top']>400]
                self.assertEqual(len(scores),1,'English score heading missing')
                self.assertEqual(len(tasks),3,'Exactly three visible task headings required')
                self.assertEqual(len(reflections),1)
                self.assertGreater(min(w['top'] for w in tasks),scores[0]['bottom']+100)
                self.assertLess(max(w['x0'] for w in tasks)-min(w['x0'] for w in tasks),1)
                self.assertGreater(tasks[1]['top']-tasks[0]['top'],70)
                self.assertGreater(tasks[2]['top']-tasks[1]['top'],70)
                self.assertGreater(reflections[0]['top'],max(w['bottom'] for w in tasks))
                stars=[p for p in doc.pages[1].curves if len(p['pts'])==11]
                self.assertEqual(len(stars),10,'Two rows of five outline stars required')
                self.assertTrue(all(p['stroke'] and not p['fill'] for p in stars))
                self.assertEqual(len({round(p['top']) for p in stars}),2)
                writing=[p for p in doc.pages[1].lines if p['x1']-p['x0']>490 and p['top']>tasks[0]['top']]
                self.assertGreaterEqual(len(writing),11,'Nine task lines plus two reflection lines')
                text=doc.pages[1].extract_text()
                self.assertNotIn('<font',text)
                self.assertNotIn('<br',text)
                for q in self.data['students'][0]['reflections']:
                    self.assertIn(q,text.replace('\n',''))

    def test_invalid_records(self):
        for mutation in ['translation','score','duplicate','transcription','annotation','six_rewrites','reserved_filename','reflection_language_count']:
            d=copy.deepcopy(self.data);s=d['students'][0]
            if mutation=='translation':del s['models']['basic'][0]['zh']
            elif mutation=='score':s['scores'][0]['value']=6
            elif mutation=='duplicate':d['students'].append(copy.deepcopy(s))
            elif mutation=='transcription':s['sentences'][0]['original']='Different.'
            elif mutation=='six_rewrites':s['optional_rewrites']=[s['optional_rewrites'][0]]*6
            elif mutation=='reserved_filename':s['pdf_filename']='class_print.pdf'
            elif mutation=='reflection_language_count':s['reflections_en']=['one','two','three']
            else:s['annotations']=[{'x':.9,'y':.1,'width':.5,'label':'G','text':'has'}]
            with self.subTest(mutation=mutation),self.assertRaises((ValidationError,ValueError)):
                validate(d,ROOT/'examples')

    def test_long_batch_and_excel(self):
        d=copy.deepcopy(self.data);short=d['students'][0];long=copy.deepcopy(short)
        long['id']='demo-long';long['seat']=2;long['reported_count']=None
        long['sentences']=[{'id':i,'original':f'I visit the park on day {i}.','basic':f'I visit the park on day {i}.','notes':['原句可保留。'],'advanced':f'I enjoy visiting the park on day {i}.'} for i in range(1,121)]
        long['paragraphs']=[' '.join(x['original'] for x in long['sentences'][:35]),' '.join(x['original'] for x in long['sentences'][35:])]
        long['errors']=[]
        d['students']=[long,short]
        short['optional_rewrites']=[copy.deepcopy(short['optional_rewrites'][0]) for _ in range(5)]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'batch.json';source.write_text(json.dumps(d),encoding='utf-8')
            output=root/'result'
            audit=build(source,output,'C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/comicbd.ttf')
            self.assertEqual([a['id'] for a in audit],['demo-01','demo-long'])
            self.assertEqual(len(PdfReader(output/'class_print.pdf').pages),4)
            first=PdfReader(output/'demo-01_full.pdf').pages[0].extract_text()
            self.assertNotIn(short['short_comment']['en'],first)
            self.assertIn('完整英中評語見第2頁',first)
            self.assertNotIn('原寫法可保留',first)
            self.assertNotIn('也可以這樣寫',first)
            detail_text='\n'.join(p.extract_text() for p in PdfReader(output/'demo-01_full.pdf').pages[2:])
            self.assertEqual(detail_text.count('可選潤飾｜原寫法可保留'),5)
            second=PdfReader(output/'demo-01_full.pdf').pages[1].extract_text()
            for label in ['My Revision Tasks','任務1','任務2','任務3','My Reflection','回溯自評','修訂日期','教師核閱']:
                self.assertIn(label,second)
            for task in short['tasks']:
                self.assertIn(task['instruction'],second.replace('\n',''))
            self.assertNotIn('另附',second);self.assertNotIn('不是學生',second)
            self.assertGreater(audit[1]['pages'],audit[0]['pages'])
            text='\n'.join(p.extract_text() for p in PdfReader(output/'demo-long_full.pdf').pages)
            self.assertIn('原稿節錄',text);self.assertIn('day 120',text);self.assertIn('SENTENCE 120',text)
            with ZipFile(output/'classroom.xlsx') as z:
                main=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
                summary=ET.fromstring(z.read('xl/worksheets/sheet6.xml'))
                cells={c.attrib['r']:c for c in main.iter(f'{{{NS}}}c')}
                self.assertEqual(cells['J2'].find(f'{{{NS}}}v').text,'11')
                self.assertEqual(cells['M3'].find(f'{{{NS}}}v').text,None)
                reflection=ET.fromstring(z.read('xl/worksheets/sheet5.xml'))
                rc={c.attrib['r']:c for c in reflection.iter(f'{{{NS}}}c')}
                self.assertIn(short['reflections_en'][0],''.join(rc['B2'].itertext()))
                task_sheet=ET.fromstring(z.read('xl/worksheets/sheet3.xml'))
                tc={c.attrib['r']:c for c in task_sheet.iter(f'{{{NS}}}c')}
                self.assertIn(short['tasks'][0]['instruction_en'],''.join(tc['C2'].itertext()))
                self.assertEqual(''.join(rc['D2'].itertext()),'')
                self.assertEqual(''.join(rc['E2'].itertext()),'')
                sc={c.attrib['r']:c for c in summary.iter(f'{{{NS}}}c')}
                self.assertEqual(sc['B5'].find(f'{{{NS}}}v').text,'1')
            with self.assertRaises(FileExistsError):
                build(source,output,'unused','unused','unused')

    def test_scan_annotations(self):
        d=copy.deepcopy(self.data)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            image=Image.new('RGB',(1100,800),'white');draw=ImageDraw.Draw(image)
            font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',30)
            draw.text((60,180),'The park have many trees.',font=font,fill='black')
            draw.text((60,330),'I enjoy walk there.',font=font,fill='black')
            draw.text((60,480),'It is quiet, so I can relax after school.',font=font,fill='black')
            image.save(root/'scan.png')
            s=d['students'][0];s['scan']='scan.png'
            s['annotations']=[{'x':.23,'y':.17,'width':.22,'label':'G','text':'has','operation':'replace','target':[.23,.27,.06]}, {'x':.17,'y':.36,'width':.25,'label':'G','text':'walking','operation':'replace','target':[.17,.46,.07]}]
            s['annotations'].append({'x':0,'y':0,'width':.1,'label':'G','text':'del.','operation':'delete','target':[.1,.65,.05]})
            source=root/'scan.json';source.write_text(json.dumps(d),encoding='utf-8')
            build(source,root/'result','C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/comicbd.ttf')
            page=PdfReader(root/'result/demo-01_full.pdf').pages[0]
            self.assertIn('walking',page.extract_text());self.assertGreater(len(page.images),0)
            self.assertNotIn('del.',page.extract_text())

    def test_three_reflections_compatibility(self):
        d=copy.deepcopy(self.data)
        d['students'][0]['reflections'].append('下一篇先檢查什麼？')
        d['students'][0]['reflections_en'].append('What will I check next?')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'three.json'
            source.write_text(json.dumps(d),encoding='utf-8')
            build(source,root/'result','C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/comicbd.ttf')
            second=PdfReader(root/'result/demo-01_full.pdf').pages[1].extract_text()
            self.assertIn('下一篇先檢查什麼',second)
        for n in [1,4]:
            bad=copy.deepcopy(d);bad['students'][0]['reflections']=['測試']*n
            with self.assertRaises(ValidationError):validate(bad,ROOT/'examples')

    def test_capacity_failure_is_explicit_and_leaves_no_partial_result(self):
        d=copy.deepcopy(self.data)
        d['students'][0]['full_comment']['en']='Detailed feedback. '*1500
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'too-long.json'
            source.write_text(json.dumps(d),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Page 2 capacity.*demo-01'):
                build(source,root/'result','C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/comicbd.ttf')
            self.assertFalse((root/'result').exists())


if __name__=='__main__':unittest.main()
