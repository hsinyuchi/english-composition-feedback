"""Synthetic tests; no student records are required."""
import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from essay_tools import count_words, merge_front_pages


class EssayToolsTests(unittest.TestCase):
    def test_count(self):
        result = count_words("I don't like well-known parks.\nA has 2 trees.\n\nBut B is quiet! -- ...")
        self.assertEqual([row['count'] for row in result['paragraphs']], [9, 4])
        self.assertEqual(result['total'], 13)
        self.assertEqual(count_words('')['total'], 0)
        self.assertEqual(count_words('parants + trees')['total'], 2)

    def test_merge_and_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, width, pages in [('one', 100, 3), ('two', 200, 2), ('short', 300, 1)]:
                writer = PdfWriter()
                for _ in range(pages):
                    writer.add_blank_page(width, 400)
                writer.write(root / (name + '.pdf'))
            manifest = root / 'manifest.json'
            rows = [dict(student_id='two', **{'class':'301'}, seat=2, pdf='two.pdf'),
                    dict(student_id='one', **{'class':'301'}, seat=1, pdf='one.pdf')]
            manifest.write_text(json.dumps(rows), encoding='utf-8')
            output = root / 'merged.pdf'
            result = merge_front_pages(manifest, output)
            self.assertEqual(result['order'], ['one', 'two'])
            self.assertEqual([float(page.mediabox.width) for page in PdfReader(output).pages], [100,100,200,200])
            with self.assertRaises(FileExistsError):
                merge_front_pages(manifest, output)
            manifest.write_text(json.dumps([rows[0], rows[0]]), encoding='utf-8')
            with self.assertRaises(ValueError):
                merge_front_pages(manifest, root / 'duplicate.pdf')
            rows[0]['pdf'] = 'short.pdf'
            manifest.write_text(json.dumps(rows), encoding='utf-8')
            with self.assertRaises(ValueError):
                merge_front_pages(manifest, root / 'short-output.pdf')
            self.assertFalse((root / 'short-output.pdf').exists())


if __name__ == '__main__':
    unittest.main()
