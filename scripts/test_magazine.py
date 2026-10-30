"""Behavioral checks for single-student safety, completeness and approved first-page reuse."""
import copy,json,sys,tempfile,unittest,hashlib,re
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_magazine as m
from pypdf import PdfReader

class MagazineChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[1]
        cls.input=root/'examples/magazine_demo.json'
        cls.data=json.loads(cls.input.read_text(encoding='utf8'))
        cls.base=cls.input.parent
    def test_bad_total_is_rejected(self):
        d=copy.deepcopy(self.data);d['total']=17
        with self.assertRaisesRegex(ValueError,'total mismatch'):m.validate(d,self.base)
    def test_adapted_material_is_labelled_in_both_slide_formats(self):
        d=copy.deepcopy(self.data);d['worksheet'][0]['source_mode']='adapted'
        out=Path(tempfile.mkdtemp(prefix='essay-adapted-slides-'));m.fonts();m.slides(d,out)
        self.assertIn('教學改寫',PdfReader(next(out.glob('*.pdf'))).pages[1].extract_text())
        self.assertIn('<span>教學改寫</span>',next(out.glob('*.html')).read_text(encoding='utf8'))
    def test_omitted_sentence_is_rejected(self):
        d=copy.deepcopy(self.data);d['sentences'].pop()
        with self.assertRaisesRegex(ValueError,'transcription'):m.validate(d,self.base)
    def test_missing_scan_does_not_downgrade_to_typed_text(self):
        d=copy.deepcopy(self.data);d['scan']='missing-file.png'
        with self.assertRaisesRegex(ValueError,'scan required'):m.validate(d,self.base)
    def test_existing_output_is_untouched(self):
        out=Path(tempfile.mkdtemp(prefix='essay-v13-existing-'));sentinel=out/'keep.txt';sentinel.write_text('keep')
        with self.assertRaises(FileExistsError):m.render(self.data,self.base,out)
        self.assertEqual(sentinel.read_text(),'keep');self.assertEqual(len(list(out.iterdir())),1)
    def test_single_student_only(self):
        with self.assertRaisesRegex(ValueError,'one student'):m.validate({'students':[self.data]},self.base)
    def test_end_to_end_and_first_page_reuse(self):
        root=Path(tempfile.mkdtemp(prefix='essay-v13-complete-'));out=root/'first'
        m.render(self.data,self.base,out)
        files=list(out.glob('*.pdf'));full=next(out.glob('*10頁*.pdf'));r=PdfReader(full)
        self.assertEqual(len(r.pages),10)
        self.assertEqual(len(PdfReader(next(out.glob('*前兩*.pdf'))).pages),2)
        self.assertEqual(len(PdfReader(next(out.glob('*投影*.pdf'))).pages),5)
        self.assertEqual(len(PdfReader(next(out.glob('*學用*.pdf'))).pages),1)
        self.assertEqual(len(PdfReader(next(out.glob('*教用*.pdf'))).pages),1)
        body=' '.join(pg.extract_text() for pg in r.pages)
        for s in self.data['sentences']:self.assertIn(s['original'],' '.join(body.split()))
        d=copy.deepcopy(self.data);d['first_page_pdf']=str(full)
        d['first_page_sha256']=hashlib.sha256(full.read_bytes()).hexdigest()
        d['first_page_transcription_sha256']=hashlib.sha256(re.sub(r'\s+',' ',' '.join(d['paragraphs'])).strip().encode('utf8')).hexdigest()
        out2=root/'second';m.render(d,self.base,out2)
        a=PdfReader(full).pages[0];b=PdfReader(next(out2.glob('*10頁*.pdf'))).pages[0]
        self.assertEqual(a.get_contents().get_data(),b.get_contents().get_data())
        stale=copy.deepcopy(d);stale['topic']='Different topic'
        with self.assertRaisesRegex(ValueError,'different topic'):m.validate(stale,self.base)
        stale=copy.deepcopy(d);stale['first_page_transcription_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'transcription binding'):m.validate(stale,self.base)
        d['id']='OTHER_99';d['class']='OTHER';d['seat']=99
        with self.assertRaisesRegex(ValueError,'different student'):m.validate(d,self.base)
        self.assertEqual(len(list(out.glob('*.html'))),1)
        print('Synthetic integration artifacts:',root)
    def test_class_seat_identity_must_agree(self):
        d=copy.deepcopy(self.data);d['seat']=16
        with self.assertRaisesRegex(ValueError,'do not agree'):m.validate(d,self.base)
    def test_exercise_must_match_its_quoted_source(self):
        d=copy.deepcopy(self.data);d['worksheet'][0]['original']='A different student wrote this.'
        with self.assertRaisesRegex(ValueError,'Verbatim exercise differs'):m.validate(d,self.base)
    def test_long_scan_is_not_silently_shrunk(self):
        d=copy.deepcopy(self.data);d['scan_line_count']=40
        with self.assertRaisesRegex(ValueError,'Long manuscript'):m.validate(d,self.base)
    def test_similar_seat_cannot_supply_the_first_page(self):
        root=Path(tempfile.mkdtemp(prefix='essay-id-check-'));fake=root/'wrong.pdf'
        c=m.canvas.Canvas(str(fake));c.drawString(45,700,'THE WRITING EDIT SAMPLE_010');c.showPage();c.save()
        d=copy.deepcopy(self.data);d['first_page_pdf']=str(fake)
        d['first_page_sha256']=hashlib.sha256(fake.read_bytes()).hexdigest()
        d['first_page_transcription_sha256']=hashlib.sha256(re.sub(r'\s+',' ',' '.join(d['paragraphs'])).strip().encode('utf8')).hexdigest()
        with self.assertRaisesRegex(ValueError,'different student'):m.validate(d,self.base)
    def test_annotation_long_text_cannot_run_off_page(self):
        root=Path(tempfile.mkdtemp(prefix='essay-annotation-'));d=copy.deepcopy(self.data)
        d['annotations']=[{'label':'[G]','text':'A correction that is much too long','x1':.1,'x2':.2,'y':.3,'text_x':.85,'text_y':.1}]
        m.fonts()
        with self.assertRaisesRegex(ValueError,'outside manuscript'):m.create_first(d,self.base,root/'long.pdf')
    def test_unsupported_annotation_glyph_is_rejected(self):
        root=Path(tempfile.mkdtemp(prefix='essay-glyph-'));d=copy.deepcopy(self.data)
        d['annotations']=[{'label':'[W]','text':'𓀀','x1':.1,'x2':.2,'y':.3,'text_x':.2,'text_y':.1}]
        m.fonts()
        with self.assertRaisesRegex(ValueError,'lacks glyphs'):m.create_first(d,self.base,root/'missing.pdf')

if __name__=='__main__':unittest.main(verbosity=2)
