# Sales Analytics Dashboard

A Streamlit application for uploading, validating, cleaning, and analyzing sales data. It supports CSV, Excel (`.xlsx`), and JSON inputs.

## Features
- Upload CSV, XLSX, and JSON files; an included CSV is available as a sample.
- Data dimensions, column names, inferred data types, missing values, unique counts, and duplicate-record checks.
- Reusable preprocessing and statistical-summary functions.
- Exact duplicate removal, whitespace cleanup, numeric/date parsing, median numeric imputation, and mode categorical imputation.
- Interactive filters for date range, region, category, segment, and shipping mode (when columns exist).
- Five live KPIs: Total Sales, Total Profit, unique Total Orders, Total Quantity Sold, and Profit Margin.
- Interactive Plotly charts for category performance, monthly trends, regional sales, and sub-category quantities.
- Friendly errors for unreadable/empty files and missing required KPI columns.

## Run locally
Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Deploy to Streamlit Community Cloud
1. Create a public GitHub repository and upload `app.py`, `data_utils.py`, `requirements.txt`, `README.md`, `test_app.py`, and the sample CSV.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py`.
4. Deploy, then open the app URL and verify upload, filters, KPI updates, and charts.

## Data notes
- The sample file is a small sales dataset, not a production-grade source of truth.
- Numeric columns named Sales, Profit, Quantity, and Discount are parsed when present.
- Order Date and Ship Date are parsed when present; invalid dates remain missing rather than being fabricated.
- Numeric nulls are filled with the column median. Text nulls are filled with the mode, or `Unknown` when no mode exists. Exact duplicate rows are removed.
- Profit Margin is calculated as `Total Profit / Total Sales * 100`; when sales total zero, it displays 0%.

## Test checklist
- Upload valid CSV, XLSX, and JSON files.
- Upload an empty file and a malformed file; confirm an actionable error is shown.
- Confirm raw profile values match the uploaded data before cleaning.
- Confirm duplicate removal and missing-value handling in the preprocessing summary.
- Change each filter and verify all five KPI values and charts update.
- Test a dataset without required sales columns; confirm the app explains which columns are missing.
- Open the deployed URL in a private/incognito window to verify public accessibility.
