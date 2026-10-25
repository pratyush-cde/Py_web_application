import pandas as pd
from data_utils import preprocess_data, data_profile, statistical_summary

def test_profile_reports_dimensions_and_missing_values():
    df = pd.DataFrame({"Sales": [10, None], "Region": ["East", "West"]})
    profile = data_profile(df)
    assert len(profile) == 2
    assert int(profile.loc[profile["Column"] == "Sales", "Missing Values"].iloc[0]) == 1

def test_preprocessing_parses_dates_and_removes_duplicates():
    df = pd.DataFrame({
        "Order ID": ["A", "A"],
        "Order Date": ["2025-01-01", "2025-01-01"],
        "Sales": ["10.5", "10.5"],
        "Profit": ["2", "2"],
        "Quantity": ["1", "1"],
        "Region": [" east ", " east "],
    })
    cleaned, stats = preprocess_data(df)
    assert len(cleaned) == 1
    assert pd.api.types.is_datetime64_any_dtype(cleaned["Order Date"])
    assert stats["duplicates_removed"] == 1
    assert cleaned.loc[0, "Region"] == "East"

def test_statistical_summary_returns_numeric_columns():
    result = statistical_summary(pd.DataFrame({"Sales": [1, 3], "City": ["A", "B"]}))
    assert "Sales" in result["Column"].tolist()
