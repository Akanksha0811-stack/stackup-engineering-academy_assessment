# Power BI Setup

For **Task 2.4 — Dashboard Design**.

The assessment asks for a one-page executive dashboard. Power BI Desktop is the preferred tool, but we accept several alternatives if Power BI isn't available to you.

---

## Option A — Power BI Desktop (Windows only)

### Install

1. Download Power BI Desktop (free) from:
   https://powerbi.microsoft.com/desktop/

2. Choose the **64-bit installer** (most systems)

3. Run the installer with default options:
   - ✅ Accept license terms
   - ✅ Create desktop shortcut

4. Launch Power BI Desktop — **no Microsoft account is required** for local report building

### Sign in (optional)

You only need to sign in if you want to publish reports to the Power BI Service. For the assessment, local development is fine — you can skip sign-in.

### First-time configuration

1. **File → Options → Global → Preview features**
2. Tick: ☑ **Modern visual tooltips** (better hover info)
3. **File → Options → Current file → Regional settings**
4. Set locale to your region (e.g. English (United Arab Emirates))

---

### Connect to assessment data

Power BI loads data via connectors.

1. Open Power BI Desktop
2. Home tab → **Get Data → Text/CSV**
3. Navigate to `outputs/transactions_clean.csv`
4. Preview window opens — verify columns look correct → **Load**
5. Repeat for:
   - `outputs/projects_clean.csv`
   - `outputs/employees_clean.csv`

> Tip: If your ETL pipeline (Task 2.2) hasn't been run yet, you can load the raw datasets from `datasets/` to start designing. Re-import the cleaned data later.

### Define relationships

1. Click **Model view** (left sidebar, third icon)
2. Drag `transactions.project_id` onto `projects.project_id` to create a relationship
3. Drag `transactions.approved_by` onto `employees.employee_id`
4. Click each relationship line to confirm:
   - Cardinality: **Many to one (*:1)**
   - Cross filter direction: **Single**

### Build the required visuals

Per Task 2.4, your dashboard needs:

| Visual | What to use | Data |
|---|---|---|
| KPI cards | Card visual | Total budget, total actual spend, % over budget projects |
| Bar chart | Clustered bar chart | Actual spend vs budget by department |
| Line chart | Line chart | Monthly transaction spend trend |
| Table | Table visual | Top 5 projects by budget variance |
| Filters | Slicer | Region, project status |

### Recommended measures (DAX)

Create these in the **Modeling** tab → **New measure**:

```dax
Total Budget = SUM(projects[budget])

Total Actual Cost = SUM(projects[actual_cost])

Budget Utilisation % =
DIVIDE([Total Actual Cost], [Total Budget], 0) * 100

Over Budget Projects =
CALCULATE(
    COUNTROWS(projects),
    projects[actual_cost] > projects[budget]
)

Total Transactions = SUM(transactions[amount])
```

### Format and theme

1. **View tab → Themes** → pick a professional theme (Sunset, Tidal, or Executive work well)
2. Add a title text box at the top: "Presight — Project Spend Dashboard"
3. Add your name and the date in small text in the corner

### Save and export

1. **File → Save As → `presight_dashboard.pbix`**
2. Move the file to your repo's `outputs/` folder
3. Commit and push as part of your PR

> File size note: `.pbix` files can be 5–50 MB depending on data. Use Git LFS if it exceeds 100 MB (unlikely for this dataset).

---

## Option B — Power BI Service (web — Mac / Linux friendly)

For Mac and Linux users who can't install Desktop.

### Sign up

1. Go to https://app.powerbi.com
2. Sign up with a **work or school email** (personal Gmail/Outlook won't work)
3. If you don't have a work email, use **Power BI Service free trial** with a Microsoft 365 developer account: https://developer.microsoft.com/microsoft-365/dev-program

### Upload data

1. My workspace → **+ New → Upload a file**
2. **Local File** → upload your cleaned CSVs

### Build visuals in web

The web report builder has fewer features than Desktop but covers the basics for this assessment.

### Export as PDF

1. Open your finished report
2. **File → Export → Export to PDF**
3. Save as `outputs/presight_dashboard.pdf`

---

## Option C — Tableau Public (free, all platforms)

### Install

1. Download Tableau Public (free) from: https://public.tableau.com/en-us/s/download
2. Available for Windows and Mac (no Linux version)
3. Run installer with defaults

### Sign up for an account

Free account required to save and share workbooks.

### Build the dashboard

Tableau's drag-and-drop interface is more visual than Power BI. Same data, same visuals required.

### Export

- **File → Export Packaged Workbook → `presight_dashboard.twbx`**
- Place in `outputs/`

---

## Option D — Looker Studio (free, web, all platforms)

Google's free data visualization tool. Works in any browser.

### Set up

1. Go to https://lookerstudio.google.com
2. Sign in with any Google account
3. **Create → Data source → File Upload** → upload CSVs

### Build and share

1. Build your visuals
2. **Share → Get link** → set to "Anyone with the link can view"
3. Add the link to your PR description

---

## Option E — Mockup (any design tool)

If none of the above work for you, a high-quality mockup is acceptable.

### Tools

| Tool | Format |
|---|---|
| Figma (free, web) | PDF export |
| Microsoft PowerPoint | PDF export |
| Excalidraw (free, web) | PNG / SVG |
| Hand-drawn on paper | Photo → PDF |

### Requirements for a mockup submission

Your mockup must:

1. **Show the full dashboard layout** with all five required visual types
2. **Use realistic numbers** — pull actual figures from your dataset analysis
3. **Annotate each visual** with:
   - What data it shows
   - Why you chose that chart type
   - What insight it gives the executive viewer

### Save

- Export as PDF
- Place in `outputs/dashboard_mockup.pdf`

---

## Grading considerations

| Approach | Grading impact |
|---|---|
| Power BI Desktop (.pbix) | Full marks possible |
| Power BI Service (PDF) | Full marks possible |
| Tableau (.twbx) | Full marks possible |
| Looker Studio (link) | Full marks possible |
| Mockup PDF (annotated) | Full marks possible IF annotations explain design choices |
| Mockup without annotations | Partial marks only |

**Reviewers care about:**
- Did you pick the right chart types for each question?
- Is the layout logical and easy to scan?
- Are the visuals connected to the data and the business problem?
- Did you make smart design decisions (colours, hierarchy, what to leave out)?

**They don't care:**
- Which tool you used
- Whether the file is interactive or static
- Polish vs. functional design — clarity beats prettiness

---

## Troubleshooting Power BI Desktop

### "Cannot install — Windows version not supported"

Power BI Desktop requires Windows 10 (build 14393+) or 11. Older versions need to upgrade Windows or use an alternative tool.

### "CSV file fails to load"

In the import preview, change:
- **File Origin:** 65001 Unicode (UTF-8)
- **Delimiter:** Comma
- **Data Type Detection:** Based on first 200 rows

### "Relationships aren't auto-detecting"

Power BI doesn't always find foreign keys. Manually create them in Model view by dragging between columns.

### "DAX measure shows incorrect totals"

Common issue with averages and percentages. Use `DIVIDE()` instead of `/` to handle nulls:
```dax
Bad:  [Total Cost] / [Total Budget]
Good: DIVIDE([Total Cost], [Total Budget], 0)
```

### File too large to commit

If `.pbix` exceeds GitHub's 100 MB limit:
1. Remove unused tables from the data model
2. Reduce columns loaded — only load what the dashboard needs
3. Or use Git LFS: `git lfs track "*.pbix"`
