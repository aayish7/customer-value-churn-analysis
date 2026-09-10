from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CANCELLATION_PREFIX = "C"
CHURN_LOW_RISK_MAX_DAYS = 90
CHURN_MEDIUM_RISK_MAX_DAYS = 180
HIGH_VALUE_SEGMENTS = ["Champions", "Loyal Customers", "Potential Loyalists", "Big Spenders"]
LOW_VALUE_SEGMENTS = ["Hibernating", "At Risk", "Needs Attention"]
NON_PRODUCT_STOCK_CODES = ["POST", "C2", "M", "BANK CHARGES", "DOT"]
DATA_PATH = Path(__file__).with_name("Online Retail.xlsx")
CANCEL = "Cancellation"
SALE = "Sale"


def load_raw(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load the repository Excel file and coerce the transaction columns to the expected types."""
    df = pd.read_excel(path)
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    return df


def shape(df: pd.DataFrame) -> dict[str, int]:
    """Row and column counts."""
    return {"rows": int(df.shape[0]), "columns": int(df.shape[1])}


def uniqueness(df: pd.DataFrame) -> dict[str, int]:
    """Distinct invoices/customers, and full-row duplicates."""
    return {
        "unique_invoices": int(df["InvoiceNo"].nunique()),
        "unique_customers": int(df["CustomerID"].nunique(dropna=True)),
        "unique_stock_codes": int(df["StockCode"].nunique()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def missingness(df: pd.DataFrame) -> dict[str, int]:
    """Null count per column, restricted to columns that have any."""
    counts = df.isna().sum()
    return {column: int(count) for column, count in counts.items() if count > 0}


def customerid_missingness_impact(df: pd.DataFrame) -> dict[str, float | int]:
    """How much revenue is lost by dropping rows with missing customer IDs."""
    valid_txn = (df["Quantity"] > 0) & (df["UnitPrice"] > 0)
    revenue = df["Quantity"] * df["UnitPrice"]
    missing = df["CustomerID"].isna()
    total_valid_revenue = float(revenue[valid_txn].sum())
    lost_revenue = float(revenue[valid_txn & missing].sum())
    return {
        "rows_missing_customerid": int(missing.sum()),
        "pct_rows_missing_customerid": round(float(missing.mean() * 100), 2),
        "valid_txn_revenue_total": round(total_valid_revenue, 2),
        "valid_txn_revenue_unattributable": round(lost_revenue, 2),
        "pct_revenue_unattributable": round(
            lost_revenue / total_valid_revenue * 100 if total_valid_revenue else 0.0, 2
        ),
    }


def country_concentration(df: pd.DataFrame) -> dict[str, float | int | str]:
    """How concentrated sales are by country."""
    shares = df["Country"].value_counts(normalize=True) * 100
    return {
        "countries": int(df["Country"].nunique()),
        "top_country": str(shares.index[0]),
        "top_country_pct": round(float(shares.iloc[0]), 2),
        "countries_under_1pct": int((shares < 1.0).sum()),
    }


def cancellation_coherence(df: pd.DataFrame) -> dict[str, int | bool]:
    """Check whether cancellation invoice flags align with negative quantity entries."""
    is_cancel = df["InvoiceNo"].astype(str).str.startswith(CANCELLATION_PREFIX)
    negative_qty = df["Quantity"] < 0
    return {
        "cancellation_rows": int(is_cancel.sum()),
        "cancellation_rows_with_negative_qty": int((is_cancel & negative_qty).sum()),
        "negative_qty_rows_not_flagged_cancel": int((negative_qty & ~is_cancel).sum()),
        "cancel_prefix_implies_negative_qty": bool(is_cancel.sum() == (is_cancel & negative_qty).sum()),
    }


def non_product_rows(df: pd.DataFrame) -> dict[str, int | float]:
    """Rows whose stock code is a non-product category (postage, fees, etc.)."""
    codes = df["StockCode"].astype(str).str.upper()
    flagged = codes.isin([c.upper() for c in NON_PRODUCT_STOCK_CODES])
    revenue = df["Quantity"] * df["UnitPrice"]
    return {
        "non_product_rows": int(flagged.sum()),
        "pct_rows": round(float(flagged.mean() * 100), 3),
        "revenue_in_non_product_rows": round(float(revenue[flagged].sum()), 2),
        "distinct_non_product_codes_seen": int(codes[flagged].nunique()),
    }


def value_sanity(df: pd.DataFrame) -> dict[str, int | float]:
    """Range checks for quantity, unit price, and revenue extremes."""
    revenue = df["Quantity"] * df["UnitPrice"]
    return {
        "non_positive_quantity_rows": int((df["Quantity"] <= 0).sum()),
        "non_positive_unitprice_rows": int((df["UnitPrice"] <= 0).sum()),
        "zero_revenue_rows": int((revenue == 0).sum()),
        "quantity_p99": float(df["Quantity"].quantile(0.99)),
        "quantity_max": int(df["Quantity"].max()),
        "revenue_p99": round(float(revenue.quantile(0.99)), 2),
        "revenue_max": round(float(revenue.max()), 2),
    }


def rfm_binning_feasibility(df: pd.DataFrame) -> dict[str, int | bool]:
    """Check whether Recency quantile bins can cleanly form five groups."""
    valid = df.dropna(subset=["CustomerID", "InvoiceDate"]).copy()
    analysis_date = valid["InvoiceDate"].max() + pd.Timedelta(days=1)
    recency = valid.groupby("CustomerID")["InvoiceDate"].apply(
        lambda s: (analysis_date - s.max()).days
    )
    distinct_edges = recency.quantile([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]).nunique()
    bins_with_drop = pd.qcut(recency, q=5, duplicates="drop").nunique()
    return {
        "customers": int(len(recency)),
        "distinct_recency_values": int(recency.nunique()),
        "distinct_quantile_edges": int(distinct_edges),
        "bins_actually_formed": int(bins_with_drop),
        "five_clean_bins": bool(bins_with_drop == 5),
    }


def churn_threshold_split(df: pd.DataFrame) -> dict[str, int | float]:
    """Customer counts across 90/180-day churn-risk thresholds."""
    valid = df.dropna(subset=["CustomerID", "InvoiceDate"]).copy()
    analysis_date = valid["InvoiceDate"].max() + pd.Timedelta(days=1)
    recency = valid.groupby("CustomerID")["InvoiceDate"].apply(
        lambda s: (analysis_date - s.max()).days
    )
    low = recency < CHURN_LOW_RISK_MAX_DAYS
    medium = (~low) & (recency < CHURN_MEDIUM_RISK_MAX_DAYS)
    high = recency >= CHURN_MEDIUM_RISK_MAX_DAYS
    return {
        "customers": int(len(recency)),
        "low_risk_pct": round(float(low.mean() * 100), 2),
        "medium_risk_pct": round(float(medium.mean() * 100), 2),
        "high_risk_pct": round(float(high.mean() * 100), 2),
    }


def revenue_concentration(df: pd.DataFrame) -> dict[str, float]:
    """Share of revenue held by the top decile and top quintile of customers."""
    valid = df.dropna(subset=["CustomerID"]).copy()
    valid = valid[(valid["Quantity"] > 0) & (valid["UnitPrice"] > 0)]
    monetary = (valid["Quantity"] * valid["UnitPrice"]).groupby(valid["CustomerID"]).sum()
    monetary = monetary.sort_values(ascending=False)
    total = float(monetary.sum())
    n = len(monetary)
    top10 = monetary.iloc[: max(1, n // 10)].sum()
    top20 = monetary.iloc[: max(1, n // 5)].sum()
    return {
        "customers": n,
        "top_10pct_customers_share_of_revenue_pct": round(float(top10 / total * 100), 2),
        "top_20pct_customers_share_of_revenue_pct": round(float(top20 / total * 100), 2),
    }


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """Create a customer-level RFM table from the transaction data."""
    clean = df.dropna(subset=["CustomerID", "InvoiceDate", "Quantity", "UnitPrice"]).copy()
    clean = clean[(clean["Quantity"] > 0) & (clean["UnitPrice"] > 0)].copy()
    clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]
    analysis_date = clean["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = clean.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda s: (analysis_date - s.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    ).reset_index()

    rfm["R_Score"] = pd.qcut(
        rfm["Recency"],
        q=5,
        labels=[5, 4, 3, 2, 1],
        duplicates="drop",
    ).astype(int)
    rfm["F_Score"] = pd.qcut(
        rfm["Frequency"].rank(method="first"),
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates="drop",
    ).astype(int)
    rfm["M_Score"] = pd.qcut(
        rfm["Monetary"].rank(method="first"),
        q=5,
        labels=[1, 2, 3, 4, 5],
        duplicates="drop",
    ).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    rfm["RFM_Total"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)
    rfm["Churn_Risk"] = rfm["Recency"].apply(churn_risk)
    rfm["Churn_Probability"] = np.where(
        rfm["Recency"] >= 180,
        0.90,
        np.where(rfm["Recency"] >= 90, 0.60, 0.20),
    ) * 100
    return rfm


def assign_segment(row: pd.Series) -> str:
    """Map an RFM customer to a value segment."""
    r_score = row["R_Score"]
    f_score = row["F_Score"]
    m_score = row["M_Score"]

    if r_score >= 4 and f_score >= 4 and m_score >= 4:
        return "Champions"
    if r_score >= 3 and f_score >= 4:
        return "Loyal Customers"
    if r_score >= 4 and f_score >= 2:
        return "Potential Loyalists"
    if m_score >= 4:
        return "Big Spenders"
    if r_score >= 4 and f_score <= 2:
        return "New Customers"
    if r_score <= 2 and f_score >= 3:
        return "At Risk"
    if r_score <= 2 and f_score >= 4 and m_score >= 4:
        return "Cannot Lose Them"
    if r_score <= 2 and f_score <= 2:
        return "Hibernating"
    return "Needs Attention"


def churn_risk(recency_days: int) -> str:
    """Assign a simple churn-risk label based on customer recency."""
    if recency_days >= CHURN_MEDIUM_RISK_MAX_DAYS:
        return "High Risk"
    if recency_days >= CHURN_LOW_RISK_MAX_DAYS:
        return "Medium Risk"
    return "Low Risk"


def segment_coherence(rfm: pd.DataFrame, segment_col: str = "Segment") -> dict[str, float | int]:
    """Check that the segment names align with the score ranges they are expected to represent."""
    result: dict[str, float | int] = {}
    for segment in HIGH_VALUE_SEGMENTS:
        rows = rfm.loc[rfm[segment_col] == segment]
        result[f"{segment}_rows"] = int(len(rows))
        if len(rows):
            result[f"{segment}_min_R_score"] = int(rows["R_Score"].min())
            result[f"{segment}_min_F_score"] = int(rows["F_Score"].min())
            result[f"{segment}_min_M_score"] = int(rows["M_Score"].min())
    for segment in LOW_VALUE_SEGMENTS:
        rows = rfm.loc[rfm[segment_col] == segment]
        result[f"{segment}_rows"] = int(len(rows))
        if len(rows):
            result[f"{segment}_max_R_score"] = int(rows["R_Score"].max())
            result[f"{segment}_max_F_score"] = int(rows["F_Score"].max())
    return result


def run_all(df: pd.DataFrame | None = None, rfm: pd.DataFrame | None = None) -> dict[str, object]:
    """Run the transaction and RFM checks over the repository workbook."""
    data = df if df is not None else load_raw()
    checks: dict[str, object] = {
        "shape": shape(data),
        "uniqueness": uniqueness(data),
        "missingness": missingness(data),
        "customerid_missingness_impact": customerid_missingness_impact(data),
        "country_concentration": country_concentration(data),
        "cancellation_coherence": cancellation_coherence(data),
        "non_product_rows": non_product_rows(data),
        "value_sanity": value_sanity(data),
        "rfm_binning_feasibility": rfm_binning_feasibility(data),
        "churn_threshold_split": churn_threshold_split(data),
        "revenue_concentration": revenue_concentration(data),
    }
    if rfm is not None:
        checks["segment_coherence"] = segment_coherence(rfm)
    return checks


def print_summary(df: pd.DataFrame) -> None:
    """Print a concise business summary for the workbook."""
    clean = df.dropna(subset=["CustomerID", "InvoiceDate", "Quantity", "UnitPrice"]).copy()
    clean = clean[(clean["Quantity"] > 0) & (clean["UnitPrice"] > 0)].copy()
    clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]

    total_revenue = clean["Revenue"].sum()
    total_customers = clean["CustomerID"].nunique()
    total_orders = clean["InvoiceNo"].nunique()

    print("Dataset shape:", clean.shape)
    print(f"Total revenue: ${total_revenue:,.2f}")
    print(f"Customers: {total_customers:,}")
    print(f"Orders: {total_orders:,}")
    print(f"Average order value: ${total_revenue / total_orders:,.2f}")

    rfm = build_rfm(clean)
    print("\nSegment counts:")
    print(rfm["Segment"].value_counts().to_string())
    print("\nChurn risk counts:")
    print(rfm["Churn_Risk"].value_counts().to_string())


if __name__ == "__main__":
    df = load_raw(DATA_PATH)
    print_summary(df)
    print("\nData quality checks:")
    print(run_all(df))
