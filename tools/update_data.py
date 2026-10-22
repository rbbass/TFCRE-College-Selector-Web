"""Rebuild the built-in DATA and PLANS arrays in index.html.

DATA comes from the departments spreadsheet; PLANS holds the BUILT_IN plan files in "College Plans",
each named after its file ("plan - SCH Balance.csv" becomes "SCH Balance").

Usage: python tools/update_data.py ["Input Files/Departments and Attributes.xlsx"]
Requires openpyxl (pip install openpyxl).
"""
import csv
import io
import json
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Input Files" / "Departments and Attributes.xlsx"
PLANS = ROOT / "College Plans"
PAGE = ROOT / "index.html"
BUILT_IN = ["Advising Pathways", "House Proposal", "SCH Balance", "AnH EnS"]


def cell(c):
    if c is None:
        return ""
    if isinstance(c, float):
        v = round(c, 6)
        return int(v) if v.is_integer() else v
    if isinstance(c, str):
        return " ".join(c.replace("\xa0", " ").split())
    return c


def put(page, name, end, body):
    page, n = re.subn(rf"const {name}=\[\r?\n.*?{end};\r?\n", lambda m: body, page, flags=re.S)
    if n != 1:
        sys.exit(f"Could not find the {name} array in index.html")
    return page


ws = openpyxl.load_workbook(SRC, data_only=True).worksheets[0]
rows = [[cell(c) for c in r]
        # Columns A-L only: M-O (NET and the two "Exp. per $1 Revenue" ratios) are not published, and P holds notes
        for r in ws.iter_rows(values_only=True, max_col=12)
        if any(c is not None and str(c).strip() for c in r)]



def plan_csv(name):
    rows = list(csv.reader(io.StringIO((PLANS / f"plan - {name}.csv").read_text(encoding="utf-8-sig"))))
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows([rows[0]] + [[name] + r[1:] for r in rows[1:] if any(r)])
    return out.getvalue()


csvs = [plan_csv(n) for n in BUILT_IN]

page = PAGE.read_text(encoding="utf-8")
page = put(page, "DATA", r"\]\]", "const DATA=[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "];\n")
page = put(page, "PLANS", r"\]", "const PLANS=[\n" + ",\n".join(json.dumps(t, ensure_ascii=False) for t in csvs) + "];\n")
PAGE.write_text(page, encoding="utf-8")
print(f"Wrote {len(rows) - 1} units from {SRC.name} and {len(csvs)} plans into index.html")
