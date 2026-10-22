# TFCRE College Selector

A single-page tool for exploring how a university's academic departments could be regrouped into six new colleges. The department data is built into the page, so you can start right away: rate how closely departments relate to one another, then build, score and compare college plans.

Everything runs in the browser. There is no server and no build step, and nothing leaves your machine unless you save a file.

## Running it

The hosted version is at **https://rbbass.github.io/TFCRE-College-Selector-Web/**. It is published with GitHub Pages from the `main` branch, root folder, so pushing to `main` updates the site.

You can also open `index.html` directly in a browser.

This repository started as a copy of [TFCRE-College-Selector](https://github.com/rbbass/TFCRE-College-Selector). To bring in later changes from it: `git fetch upstream && git merge upstream/main`.

## Department data

The department data comes from `Input Files/Departments and Attributes.xlsx` (first sheet, columns A to L) and is built into the page; users cannot upload their own. Columns M to O (NET and the two "Exp. per $1 Revenue" ratios) and the free-text notes in column P are left out, so they are not in the published page.

To update the data, save the new spreadsheet over `Input Files/Departments and Attributes.xlsx`, put the plan CSVs to build in into `College Plans` and list their names in `BUILT_IN` at the top of the script, and run:

```
python tools/update_data.py
```

It rewrites the `DATA` and `PLANS` arrays near the top of the script in `index.html`. Each built-in plan is named after its file (`plan - SCH Balance.csv` becomes "SCH Balance"), whatever its Plan column says. Pass a different path to read another file. It needs `openpyxl` (`pip install openpyxl`).

The spreadsheet layout the page expects:

| Column | Contents |
|---|---|
| A | Department (unit) name. Rows without a name are ignored. |
| B | Current college (optional). Detected when the header contains "college", "school" or "division", or when most values are text. |
| Remaining columns | Numbers: faculty counts, student credit hours (SCH), headcounts, research and financial figures, and so on. `$`, `,` and `%` are handled; blanks count as missing. |

Two total columns are added: **Total # FT Faculty** (headers containing "Faculty TT" and "NTTF") and **Student Headcount Total** (headers containing "UG Students" and "Grad students"). The Plans comparison dropdown leaves out # GAs and # Faculty PT.

Text in parentheses in a header is dropped from the display name.

## What it does

### Design colleges tab
- Drag departments from the unassigned pool into six colleges (or tap a department, then tap a college). Rename a college by editing its title.
- Departments are color-coded by their current college.
- A summary table shows the sum of each column for each new college, plus the affinity kept inside each college.
- **Suggest from affinity** groups the departments automatically to keep high-affinity departments together. Options: how even the college sizes must be, an optional financial balance (keep each college's total for a chosen column within a tolerance of the average), and whether to keep departments you have already placed. **Undo suggestion** restores the previous arrangement.
- **Load a stored plan** opens a plan CSV as the working arrangement.
- **Plans**: Advising Pathways, House Proposal, SCH Balance and AnH EnS are built in, marked "built-in", and cannot be deleted. Save the current arrangement, tick two or more plans to compare them on any column (balance table and side-by-side bars), and save each plan as its own CSV.

### Department affinity tab
- Pick a department, then drag every other department into one of four nested squares: little, some, moderate or high affinity (weights 0, 1, 4 and 8, used internally).
- Departments that share a current college start at moderate affinity. A checkbox turns this default off. "Apply both ways" makes a rating symmetric.
- Save and load the ratings as a CSV.

## File formats

**Affinities** (`department-affinities.csv`): one row per rated pair.

```
Department,Related department,Weight
Biology,Chemistry,8
```

Weight is 0, 1, 4 or 8. The file includes the same-college defaults and any pairs you deliberately lowered to 0, so loading it recreates your ratings exactly. Loading replaces current ratings; **Undo load** restores them.

**Plans** (one file per plan, `plan - <name>.csv`): one row per placed department, plus a row for each empty college so its name is kept.

```
Plan,Department,College number,College name
Plan A,Biology,1,Natural Sciences
Plan A,,2,College 2
```

College number is 1 to 6. Department names are matched to the department list ignoring capitalization. Files that hold several plans also load: "Add plan files" imports them all, and "Load a stored plan" uses the first.

## Where data is kept

Working state is saved in the browser's local storage, so it is private to one browser on one device: college assignments, plans you save, affinity ratings and the defaults setting. Clearing site data erases it. Use the CSV save buttons for backups and to share work with colleagues, who load your CSVs.

## Data privacy

Departmental financial and enrollment data can be sensitive. The built-in data is part of `index.html`, so anyone who can open the hosted page can see it. The `.gitignore` still excludes spreadsheets and a `data/` folder so other data files are not committed by accident.

## Development

The whole app is `index.html`: markup, styles and script in one file, with no external dependencies. Edit it and reload.

Notes for working on it:

- Suggestions use a local search (random restarts plus perturbation) that maximizes within-college affinity under size limits, with a soft penalty for college totals outside the balance tolerance.
- When the page is not hosted inside Claude, CSV saves use a normal browser download. Inside Claude's artifact viewer they go through the viewer's save prompt.
