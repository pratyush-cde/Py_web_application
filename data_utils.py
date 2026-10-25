from pathlib import Path
import pandas as pd

NUMERIC_COLUMNS = ["Sales", "Profit", "Quantity", "Discount"]
DATE_COLUMNS = ["Order Date", "Ship Date"]

def load_file(file_bytes, filename):
    """Load CSV, Excel, or JSON data into a DataFrame."""
    from io import BytesIO
    buffer = BytesIO(file_bytes)
    suffix = Path(filename).suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(buffer)
    if suffix == ".xlsx":
        return pd.read_excel(buffer)
    if suffix == ".json":
        try:
            return pd.read_json(buffer)
        except ValueError:
            buffer.seek(0)
            return pd.read_json(buffer, lines=True)
    raise ValueError("Unsupported file type. Upload CSV, XLSX, or JSON.")

def normalize_column_names(df):
    result = df.copy()
    result.columns = [str(c).strip() for c in result.columns]
    for col in result.select_dtypes(include=["object", "string"]).columns:
        result[col] = result[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    return result

def data_profile(df):
    return pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": [str(dtype) for dtype in df.dtypes],
        "Missing Values": [int(v) for v in df.isna().sum().values],
        "Missing (%)": [round(float(v), 2) for v in (df.isna().mean() * 100).values],
        "Unique Values": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })

def preprocess_data(raw_df):
    df = normalize_column_names(raw_df)
    original_rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            cleaned = df[col].astype("string").str.replace(r"[$,]", "", regex=True).str.strip()
            df[col] = pd.to_numeric(cleaned, errors="coerce")
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
        df[col] = df[col].replace("", pd.NA)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isna().any():
                median = df[col].median()
                df[col] = df[col].fillna(median if pd.notna(median) else 0)
        elif col not in DATE_COLUMNS and (pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col])):
            if df[col].isna().any():
                modes = df[col].mode(dropna=True)
                df[col] = df[col].fillna(modes.iloc[0] if not modes.empty else "Unknown")
    for col in ["Region", "Category", "Segment", "Ship Mode"]:
        if col in df.columns:
            df[col] = df[col].map(lambda x: x.title() if isinstance(x, str) else x)
    return df, {
        "input_rows": original_rows,
        "duplicates_removed": duplicate_count,
        "output_rows": len(df),
        "rows_removed": original_rows - len(df),
    }

def statistical_summary(df):
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    return numeric.describe().T.reset_index(names="Column")
