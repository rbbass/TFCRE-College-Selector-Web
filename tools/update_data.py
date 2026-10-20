"""Rebuild the built-in DATA array in index.html from the departments spreadsheet.

Usage: python tools/update_data.py ["Input Files/Departments and Attributes.xlsx"]
Requires openpyxl (pip install openpyxl).
"""
import json
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Input Files" / "Departments and Attributes.xlsx"
PAGE = ROOT / "index.html"


def cell(c):
    if c is None:
        return ""
    if isinstance(c, float):
        v = round(c, 6)
        return int(v) if v.is_integer() else v
    if isinstance(c, str):
        return " ".join(c.replace("\xa0", " ").split())
    return c


ws = openpyxl.load_workbook(SRC, data_only=True).worksheets[0]
rows = [[cell(c) for c in r]
        for r in ws.iter_rows(values_only=True, max_col=15)  # column P holds free-text notes, not data
        if any(c is not None and str(c).strip() for c in r)]

data = "const DATA=[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "];\n"
page = PAGE.read_text(encoding="utf-8")
page, n = re.subn(r"const DATA=\[\r?\n.*?\]\];\r?\n", lambda m: data, page, flags=re.S)
if n != 1:
    sys.exit("Could not find the DATA array in index.html")
PAGE.write_text(page, encoding="utf-8")
print(f"Wrote {len(rows) - 1} units from {SRC.name} into index.html")
