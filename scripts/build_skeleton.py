#!/usr/bin/env python3
"""Build the municipality skeleton JSONL from an official e-Stat CSV export.

Usage:
  python scripts/build_skeleton.py path/to/estat_municipalities.csv
  python scripts/build_skeleton.py path/to/estat_municipalities.csv --expected-count 1741

The input CSV must contain columns for municipality code, municipality name,
and prefecture. Column names can be mapped with CLI options. The script does
not guess missing codes or create fabricated municipalities.
"""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv_path")
    p.add_argument("--code-column", default="全国地方公共団体コード")
    p.add_argument("--name-column", default="市区町村名")
    p.add_argument("--prefecture-column", default="都道府県名")
    p.add_argument("--expected-count", type=int, default=1741)
    p.add_argument("--output", default="data/municipalities.jsonl")
    args = p.parse_args()

    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rows = {}
    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = [args.code_column, args.name_column, args.prefecture_column]
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"CSV columns missing: {missing}; available={reader.fieldnames}")
        for line_no, row in enumerate(reader, start=2):
            code = re.sub(r"\\D", "", (row.get(args.code_column) or "").strip())
            name = (row.get(args.name_column) or "").strip()
            prefecture = (row.get(args.prefecture_column) or "").strip()
            if not code or not name or not prefecture:
                continue
            if len(code) == 5:
                code = "0" + code
            if not re.fullmatch(r"\\d{6}", code):
                raise SystemExit(f"Invalid municipality code at CSV line {line_no}: {code!r}")
            kind = "special_ward" if prefecture == "東京都" and name.endswith("区") else "city" if name.endswith("市") else "town" if name.endswith("町") else "village" if name.endswith("村") else "other"
            record = {
                "municipality_code": code,
                "name": name,
                "prefecture": prefecture,
                "municipality_type": kind,
                "official_site_url": None,
                "source_ids": ["src-estat-municipalities"],
                "research_status": "skeleton",
                "as_of_date": None,
                "created_at": now,
                "updated_at": None,
                "notes": "自治体コード・名称の基礎レコード。公式サイト等は別データとのJOINで追加する。"
            }
            if code in rows and rows[code] != record:
                raise SystemExit(f"Duplicate municipality code: {code}")
            rows[code] = record

    if len(rows) != args.expected_count:
        raise SystemExit(f"Expected {args.expected_count} unique municipalities, got {len(rows)}. Check CSV scope/date; no output written.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\\n") as f:
        for code in sorted(rows):
            f.write(json.dumps(rows[code], ensure_ascii=False) + "\\n")
    print(f"Wrote {len(rows)} municipality skeleton records to {out}")

if __name__ == "__main__":
    main()
