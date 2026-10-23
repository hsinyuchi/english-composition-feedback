"""Auditable word counts and two-page-per-student print bundles."""
import argparse
import json
import re
from pathlib import Path


def count_words(text):
    paragraphs = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
    records = []
    for index, paragraph in enumerate(paragraphs, 1):
        tokens = [token for token in paragraph.split() if re.search(r"[A-Za-z0-9]", token)]
        records.append({"paragraph": index, "count": len(tokens), "tokens": tokens})
    return {"method": "whitespace tokens containing ASCII letters or digits; punctuation-only excluded",
            "total": sum(row["count"] for row in records), "paragraphs": records}


def merge_front_pages(manifest, output):
    from pypdf import PdfReader, PdfWriter
    manifest, output = Path(manifest), Path(output)
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}")
    entries = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest must be a nonempty list")
    ids, seats = set(), set()
    for row in entries:
        student_id = row["student_id"]
        if not isinstance(student_id, str) or not student_id.strip():
            raise ValueError("student_id must be a nonempty string")
        if not isinstance(row["class"], str) or not row["class"].strip():
            raise ValueError("class must be a nonempty string")
        if type(row["seat"]) is not int or row["seat"] < 1:
            raise ValueError("seat must be a positive integer")
        key = (row["class"], row["seat"])
        if student_id in ids or key in seats:
            raise ValueError("Duplicate student_id or class/seat")
        ids.add(student_id)
        seats.add(key)
    entries.sort(key=lambda row: (row["class"], row["seat"]))
    writer = PdfWriter()
    for row in entries:
        source = Path(row["pdf"])
        if not source.is_absolute():
            source = manifest.parent / source
        reader = PdfReader(source)
        if len(reader.pages) < 2:
            raise ValueError(f"Fewer than two pages: {source}")
        writer.add_page(reader.pages[0])
        writer.add_page(reader.pages[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        writer.write(handle)
    if len(PdfReader(output).pages) != 2 * len(entries):
        raise ValueError("Unexpected output page count")
    return {"students": len(entries), "pages": len(entries) * 2,
            "order": [row["student_id"] for row in entries], "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    count = commands.add_parser("count")
    count.add_argument("text", type=Path)
    merge = commands.add_parser("merge")
    merge.add_argument("manifest", type=Path)
    merge.add_argument("output", type=Path)
    args = parser.parse_args()
    result = count_words(args.text.read_text(encoding="utf-8-sig")) if args.command == "count" else merge_front_pages(args.manifest, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
