
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from data_utils import (
    load_file,
    data_profile,
    preprocess_data,
    statistical_summary,
)

# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

DEFAULT_FILE = Path(__file__).with_name("experiment10_raw_dataset.csv")


# --------------------------------------------------
# 2. Reusable helper functions
# --------------------------------------------------

def filter_options(df, column):
    """Return sorted unique options for a filter."""
    if column not in df.columns:
        return []

    return sorted(df[column].dropna().astype(str).unique().tolist())


def money(value):
    """Format a number as currency."""
    return f"${value:,.2f}"


def render_kpis(df):
    """Calculate and display the five sales KPIs."""

    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())

    total_orders = int(
        df["Order ID"].nunique(dropna=True)
    )

    total_quantity = float(df["Quantity"].sum())

    profit_margin = (
        total_profit / total_sales * 100
        if total_sales != 0
        else 0.0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Sales", money(total_sales))
    c2.metric("Total Profit", money(total_profit))
    c3.metric("Total Orders", f"{total_orders:,}")
    c4.metric("Total Quantity Sold", f"{total_quantity:,.0f}")
    c5.metric("Profit Margin", f"{profit_margin:.2f}%")


def apply_filters(df):
    """Apply interactive filters to the dataset."""

    filtered = df.copy()

    with st.sidebar:
        st.header("2. Filter Data")

        # Date range filter
        if (
            "Order Date" in filtered.columns
            and filtered["Order Date"].notna().any()
        ):
            valid_dates = filtered["Order Date"].dropna()

            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            date_range = st.date_input(
                "Order date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="order_date_range",
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range

                date_mask = (
                    filtered["Order Date"].notna()
                    & filtered["Order Date"].dt.date.between(
                        start_date, end_date
                    )
                )

                filtered = filtered[date_mask]

        # Categorical filters
        filter_definitions = [
            ("Region", "Region"),
            ("Category", "Category"),
            ("Segment", "Customer Segment"),
            ("Ship Mode", "Shipping Mode"),
        ]

        for column, label in filter_definitions:
            if column in filtered.columns:
                options = filter_options(df, column)

                selected = st.multiselect(
                    label,
                    options,
                    default=options,
                    key=f"filter_{column}",
                )

                filtered = filtered[
                    filtered[column].astype(str).isin(selected)
                ]

    return filtered


# --------------------------------------------------
# 3. Application heading
# --------------------------------------------------

st.title("📊 Sales Analytics Dashboard")

st.caption(
    "Upload sales data, validate data quality, "
    "clean records, and explore business performance."
)


# --------------------------------------------------
# 4. Upload or load sample dataset
# --------------------------------------------------

with st.sidebar:
    st.header("1. Upload Data")

    uploaded_file = st.file_uploader(
        "Choose a CSV, Excel, or JSON file",
        type=["csv", "xlsx", "json"],
    )

    use_sample = st.checkbox(
        "Use included sample dataset",
        value=uploaded_file is None,
    )


if uploaded_file is not None:
    try:
        raw = load_file(
            uploaded_file.getvalue(),
            uploaded_file.name,
        )
    except Exception as exc:
        st.error(f"Could not read the uploaded file: {exc}")
        st.stop()

elif use_sample and DEFAULT_FILE.exists():
    try:
        raw = pd.read_csv(DEFAULT_FILE)
    except Exception as exc:
        st.error(f"Could not read the sample dataset: {exc}")
        st.stop()

else:
    st.info(
        "Upload a CSV, Excel (.xlsx), or JSON file, "
        "or select the included sample dataset."
    )
    st.stop()


# --------------------------------------------------
# 5. Basic data validation
# --------------------------------------------------

if raw.empty:
    st.warning("The selected file contains no data rows.")
    st.stop()

if len(raw.columns) == 0:
    st.error("No columns were found in the uploaded file.")
    st.stop()

st.success(
    f"Dataset loaded successfully: "
    f"{raw.shape[0]:,} rows and {raw.shape[1]:,} columns."
)

st.subheader("1. Data Validation")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Rows", f"{raw.shape[0]:,}")
col2.metric("Total Columns", f"{raw.shape[1]:,}")
col3.metric("Duplicate Records", f"{int(raw.duplicated().sum()):,}")
col4.metric("Missing Cells", f"{int(raw.isna().sum().sum()):,}")


with st.expander("Raw Data Preview"):
    st.dataframe(
        raw.head(100),
        use_container_width=True,
        hide_index=True,
    )


try:
    profile = data_profile(raw)

    with st.expander("Column Names, Data Types and Missing Values", expanded=True):
        st.dataframe(
            profile,
            use_container_width=True,
            hide_index=True,
        )

except Exception as exc:
    st.error(f"Data profiling failed: {exc}")
    st.stop()


# --------------------------------------------------
# 6. Data preprocessing
# --------------------------------------------------

st.subheader("2. Data Preprocessing")

try:
    clean, clean_stats = preprocess_data(raw)

except Exception as exc:
    st.error(f"Data preprocessing failed: {exc}")
    st.stop()


a, b, c = st.columns(3)

a.metric(
    "Rows After Cleaning",
    f"{clean_stats['output_rows']:,}",
)

b.metric(
    "Duplicate Rows Removed",
    f"{clean_stats['duplicates_removed']:,}",
)

c.metric(
    "Rows Removed",
    f"{clean_stats['rows_removed']:,}",
)

st.caption(
    "Preprocessing trims whitespace, removes exact duplicate rows, "
    "converts known numeric columns, parses dates, fills numeric "
    "missing values using the median, and fills categorical missing "
    "values using the mode or 'Unknown'. Invalid dates remain missing."
)


with st.expander("Cleaned Data Preview"):
    st.dataframe(
        clean.head(200),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download Cleaned Data as CSV",
        data=clean.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_sales_data.csv",
        mime="text/csv",
    )


with st.expander("Statistical Summary"):
    try:
        summary = statistical_summary(clean)

        if summary.empty:
            st.info("No numeric columns were detected.")
        else:
            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
            )

    except Exception as exc:
        st.error(f"Could not calculate statistical summary: {exc}")


# --------------------------------------------------
# 7. Check columns required for sales KPIs
# --------------------------------------------------

required_columns = [
    "Sales",
    "Profit",
    "Quantity",
    "Order ID",
]

missing_columns = [
    column
    for column in required_columns
    if column not in clean.columns
]

if missing_columns:
    st.warning(
        "Data quality and preprocessing are available, but the sales "
        "dashboard requires these columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


# --------------------------------------------------
# 8. Interactive filters
# --------------------------------------------------

st.divider()
st.subheader("3. Interactive Filters")

filtered = apply_filters(clean)

if filtered.empty:
    st.warning(
        "No records match the selected filters. "
        "Please adjust the filters."
    )
    st.stop()


# --------------------------------------------------
# 9. Five dynamic KPIs
# --------------------------------------------------

st.subheader("4. Key Performance Indicators")

render_kpis(filtered)


# --------------------------------------------------
# 10. Interactive charts
# --------------------------------------------------

st.subheader("5. Interactive Visualizations")

left, right = st.columns(2)


# Chart 1: Sales and Profit by Category
with left:
    if "Category" in filtered.columns:
        category_data = (
            filtered.groupby("Category", dropna=False, as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
        )

        fig = px.bar(
            category_data,
            x="Category",
            y=["Sales", "Profit"],
            barmode="group",
            title="Sales and Profit by Category",
            hover_data=["Category"],
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info("A Category column is required for this chart.")


# Chart 2: Monthly Sales and Profit Trend
with right:
    if "Order Date" in filtered.columns:
        dated = filtered.dropna(subset=["Order Date"]).copy()

        if not dated.empty:
            dated["Month"] = (
                dated["Order Date"]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

            monthly_data = (
                dated.groupby("Month", as_index=False)
                .agg(
                    Sales=("Sales", "sum"),
                    Profit=("Profit", "sum"),
                )
            )

            fig = px.line(
                monthly_data,
                x="Month",
                y=["Sales", "Profit"],
                markers=True,
                title="Monthly Sales and Profit Trend",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:
            st.info("No valid order dates are available.")

    else:
        st.info("An Order Date column is required for this chart.")


left2, right2 = st.columns(2)


# Chart 3: Sales by Region
with left2:
    if "Region" in filtered.columns:
        region_data = (
            filtered.groupby("Region", dropna=False, as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
            )
        )

        fig = px.bar(
            region_data,
            x="Region",
            y="Sales",
            color="Profit",
            title="Sales by Region",
            hover_data=["Profit"],
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info("A Region column is required for this chart.")


# Chart 4: Top Sub-Categories by Quantity
with right2:
    if "Sub-Category" in filtered.columns:
        subcategory_data = (
            filtered.groupby("Sub-Category", as_index=False)
            .agg(Quantity=("Quantity", "sum"))
            .sort_values("Quantity", ascending=False)
            .head(12)
        )

        fig = px.bar(
            subcategory_data,
            x="Quantity",
            y="Sub-Category",
            orientation="h",
            title="Top Sub-Categories by Quantity",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info(
            "A Sub-Category column is required for this chart."
        )


# --------------------------------------------------
# 11. Filtered records
# --------------------------------------------------

st.divider()
st.subheader("6. Filtered Records")

st.caption(
    f"Showing {len(filtered):,} records "
    f"out of {len(clean):,} cleaned records."
)

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

st.caption("Sales Analytics Dashboard | Built with Python, Pandas, and Streamlit")
