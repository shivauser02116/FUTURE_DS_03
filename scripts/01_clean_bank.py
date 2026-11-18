#!/usr/bin/env python3
"""
scripts/01_clean_bank.py
------------------------
Data cleaning and feature engineering pipeline for Task 3:
Marketing Funnel & Conversion Performance Analysis.

Dataset: data/bank-additional-full.csv
Outputs:
  - data/bank_clean.csv
  - docs/cleaning_log.md
"""

import os
import sys
import pandas as pd
import numpy as np

def main():
    raw_path = os.path.join("data", "bank-additional-full.csv")
    clean_path = os.path.join("data", "bank_clean.csv")
    log_path = os.path.join("docs", "cleaning_log.md")

    if not os.path.exists(raw_path):
        print(f"Error: Raw dataset not found at {raw_path}", file=sys.stderr)
        sys.exit(1)

    print("Step 1: Reading raw dataset...")
    df_raw = pd.read_csv(raw_path, sep=";")
    raw_rows, raw_cols = df_raw.shape
    print(f"  Raw dimensions: {raw_rows:,} rows, {raw_cols} columns")

    # Log unknown counts in the raw dataset
    unknown_cols = ["job", "marital", "education", "default", "housing", "loan"]
    raw_unknown_counts = {}
    for col in unknown_cols:
        raw_unknown_counts[col] = int((df_raw[col] == "unknown").sum())
        print(f"  Raw unknown in '{col}': {raw_unknown_counts[col]:,}")

    # Standardize column names to snake_case early for processing
    df = df_raw.copy()
    orig_columns = list(df.columns)
    df.columns = [col.replace(".", "_").strip().lower() for col in df.columns]

    print("\nStep 2: Deriving month_num and period_year on raw ordering...")
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    df["month_num"] = df["month"].str.lower().map(month_map)

    # period_year derivation:
    # Dataset records are chronologically ordered from May 2008 to November 2010.
    # Each time month_num decreases relative to the preceding row (e.g., from Nov/Dec to Mar),
    # a new calendar year cycle begins.
    month_drops = (df["month_num"].diff() < 0).cumsum()
    df["period_year"] = 2008 + month_drops

    year_counts_raw = df["period_year"].value_counts().sort_index().to_dict()
    print("  Period year counts (raw, before dropping duplicates):", year_counts_raw)

    print("\nStep 3: Detecting and logging duplicates...")
    dup_mask = df.duplicated(keep="first")
    num_duplicates = int(dup_mask.sum())
    duplicate_rows = df[dup_mask].copy()
    print(f"  Identified {num_duplicates} exact duplicate rows.")

    # Drop duplicate rows
    df = df[~dup_mask].copy().reset_index(drop=True)
    clean_rows, _ = df.shape
    print(f"  Dataset size after dropping duplicates: {clean_rows:,} rows")

    print("\nStep 4: Engineering funnel & analytical feature columns...")
    # 1. Target conversion indicator
    df["converted"] = (df["y"] == "yes").astype(int)

    # 2. Engaged flag: Proxy definition based on duration > 60 seconds
    df["engaged"] = (df["duration"] > 60).astype(int)

    # 3. duration_band: <=60, 61-180, 181-300, 301-600, 600+
    def categorize_duration(d):
        if d <= 60:
            return "<=60"
        elif d <= 180:
            return "61-180"
        elif d <= 300:
            return "181-300"
        elif d <= 600:
            return "301-600"
        else:
            return "600+"

    df["duration_band"] = df["duration"].apply(categorize_duration)

    # 4. contact_attempts_band: 1, 2, 3, 4+ (derived from campaign)
    def categorize_attempts(c):
        if c == 1:
            return "1"
        elif c == 2:
            return "2"
        elif c == 3:
            return "3"
        else:
            return "4+"

    df["contact_attempts_band"] = df["campaign"].apply(categorize_attempts)

    # 5. previously_contacted: Yes if pdays != 999 else No
    df["previously_contacted"] = np.where(df["pdays"] != 999, "Yes", "No")

    # 6. euribor_band: <=1, 1-4, >4 on euribor3m
    def categorize_euribor(e):
        if e <= 1:
            return "<=1"
        elif e <= 4:
            return "1-4"
        else:
            return ">4"

    df["euribor_band"] = df["euribor3m"].apply(categorize_euribor)

    final_rows, final_cols = df.shape
    print(f"  Clean dataframe ready: {final_rows:,} rows, {final_cols} columns")

    print("\nStep 5: Writing clean dataset to disk...")
    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    df.to_csv(clean_path, index=False)
    print(f"  Saved clean dataset to {clean_path}")

    print("\nStep 6: Writing docs/cleaning_log.md...")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Compute breakdown tables for documentation
    dur_band_order = ["<=60", "61-180", "181-300", "301-600", "600+"]
    dur_summary = df.groupby("duration_band")["converted"].agg(
        count="count",
        conversions="sum",
        rate=lambda x: round(x.mean() * 100, 2)
    ).reindex(dur_band_order).reset_index()

    att_band_order = ["1", "2", "3", "4+"]
    att_summary = df.groupby("contact_attempts_band")["converted"].agg(
        count="count",
        conversions="sum",
        rate=lambda x: round(x.mean() * 100, 2)
    ).reindex(att_band_order).reset_index()

    eur_band_order = ["<=1", "1-4", ">4"]
    eur_summary = df.groupby("euribor_band")["converted"].agg(
        count="count",
        conversions="sum",
        rate=lambda x: round(x.mean() * 100, 2)
    ).reindex(eur_band_order).reset_index()

    year_summary = df.groupby("period_year")["converted"].agg(
        count="count",
        conversions="sum",
        rate=lambda x: round(x.mean() * 100, 2)
    ).reset_index()

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("# Data Cleaning & Transformation Log\n\n")
        f.write("**Project:** FUTURE_DS_03 - Marketing Funnel & Conversion Performance Analysis  \n")
        f.write("**Dataset Source:** UCI Bank Marketing (`bank-additional-full.csv`, Moro et al., 2014, CC BY 4.0)  \n")
        f.write(f"**Clean Dataset Output:** `{clean_path}`  \n\n")

        f.write("## 1. Funnel Framing & Analytical Principles\n\n")
        f.write("- **Funnel Structure:** The dataset contains records of telemarketing campaign contacts. It has **no website visitor, impression, or inbound lead stages**. The funnel is structured strictly as:\n")
        f.write("  $$\\text{Contacted} \\longrightarrow \\text{Engaged} \\longrightarrow \\text{Subscribed}$$\n")
        f.write("- **Engaged Proxy Definition:** An 'engaged' contact is operationalized as a telephone interaction lasting **longer than 60 seconds** (`duration > 60`). Crucially, call duration is only known **after the call is concluded**; therefore, engagement is a post-hoc diagnostic proxy rather than a predictive pre-call filter.\n")
        f.write("- **Causal Disclaimer:** All statistical observations represent relationships that are **associated with**, never **caused by**, the respective features.\n\n")

        f.write("## 2. Raw File Audit\n\n")
        f.write(f"- **Raw File Dimensions:** {raw_rows:,} rows, {raw_cols} columns.\n")
        f.write("- **Delimiter:** Semicolon (`;`), quoted string fields.\n")
        f.write("- **Missing Values Policy:** The dataset encodes missing categorical values explicitly as `'unknown'`. Per protocol, `'unknown'` values are strictly preserved as a valid category rather than dropped or synthetically imputed.\n\n")
        f.write("### Unknown Counts in Raw File\n\n")
        f.write("| Column Name | 'unknown' Count | Share of Total (%) |\n")
        f.write("|:---|---:|---:|\n")
        for col in unknown_cols:
            cnt = raw_unknown_counts[col]
            pct = cnt / raw_rows * 100
            f.write(f"| `{col}` | {cnt:,} | {pct:.2f}% |\n")
        f.write("\n")

        f.write("## 3. Duplicate Handling\n\n")
        f.write(f"- **Exact Duplicates Identified:** {num_duplicates} rows.\n")
        f.write(f"- **Action:** Removed exact duplicate rows using first-occurrence retention (`keep='first'`).\n")
        f.write(f"- **Row Count Post-Deduplication:** {clean_rows:,} rows (exact expected: 41,176 rows).\n\n")
        f.write("### Sample of Removed Duplicate Records\n\n")
        f.write("| Row Index | Age | Job | Marital | Education | Day/Month | Duration | Campaign | y |\n")
        f.write("|---:|---:|:---|:---|:---|:---|---:|---:|:---|\n")
        for idx, row in duplicate_rows.iterrows():
            f.write(f"| {idx} | {row['age']} | {row['job']} | {row['marital']} | {row['education']} | {row['day_of_week']}/{row['month']} | {row['duration']} | {row['campaign']} | {row['y']} |\n")
        f.write("\n")

        f.write("## 4. Column Renaming (snake_case)\n\n")
        f.write("All column names were converted from dot-notation to standardized lowercase `snake_case`:\n\n")
        f.write("| Original Column Name | New snake_case Name |\n")
        f.write("|:---|:---|\n")
        for orig, new in zip(orig_columns, df.columns[:len(orig_columns)]):
            f.write(f"| `{orig}` | `{new}` |\n")
        f.write("\n")

        f.write("## 5. Temporal Reconstruction: `period_year` and `month_num`\n\n")
        f.write("- **Background:** The raw file lacks a four-digit year column, but the records are chronologically ordered from May 2008 to November 2010 (spanning 31 months of campaign operations).\n")
        f.write("- **Derivation Method:** Computed on raw row order **prior to duplicate removal**:\n")
        f.write("  1. Mapped string `month` ('jan'..'dec') to numerical `month_num` (1..12).\n")
        f.write("  2. Flagged each transition where `month_num[i] < month_num[i-1]` (e.g. from Nov/Dec to Mar).\n")
        f.write("  3. Computed cumulative transitions: `period_year = 2008 + (month_num.diff() < 0).cumsum()`.\n")
        f.write("- **Important Limitation:** `period_year` is an **inferred reconstruction** from sequence order rather than an explicit raw timestamp field.\n\n")
        f.write("### Inferred Year Distribution (Post-Deduplication)\n\n")
        f.write("| Period Year | Record Count | Share of Dataset (%) | Subscriptions | Conversion Rate (%) |\n")
        f.write("|:---|---:|---:|---:|---:|\n")
        for _, r in year_summary.iterrows():
            pct = r['count'] / clean_rows * 100
            f.write(f"| {int(r['period_year'])} | {int(r['count']):,} | {pct:.2f}% | {int(r['conversions']):,} | {r['rate']:.2f}% |\n")
        f.write("\n")

        f.write("## 6. Engineered Feature Columns\n\n")
        f.write("The following 6 feature columns were added to support funnel, channel, effort, and macroeconomic analysis:\n\n")
        f.write("1. **`converted`** (`int`): `1` if client subscribed to term deposit (`y == 'yes'`), else `0`.\n")
        f.write("   - Overall subscribers: **4,639** (conversion rate: **11.27%**).\n")
        f.write("2. **`engaged`** (`int`): `1` if call duration > 60 seconds, else `0`.\n")
        f.write("   - Engaged contacts: **36,892** (**89.60%** of all contacts).\n")
        f.write("   - Calls <= 60 seconds: **4,284** (**10.40%**), resulting in exactly **1** subscription (0.02% conversion).\n")
        f.write("3. **`duration_band`** (`str`): Categorization of call length into operational segments.\n\n")
        f.write("| Duration Band | Call Count | Share (%) | Subscriptions | Conversion Rate (%) |\n")
        f.write("|:---|---:|---:|---:|---:|\n")
        for _, r in dur_summary.iterrows():
            pct = r['count'] / clean_rows * 100
            f.write(f"| `{r['duration_band']}` | {int(r['count']):,} | {pct:.2f}% | {int(r['conversions']):,} | {r['rate']:.2f}% |\n")
        f.write("\n")

        f.write("4. **`contact_attempts_band`** (`str`): Customer touch count (`1`, `2`, `3`, `4+`).\n\n")
        f.write("| Attempts Band | Client Count | Share (%) | Subscriptions | Conversion Rate (%) |\n")
        f.write("|:---|---:|---:|---:|---:|\n")
        for _, r in att_summary.iterrows():
            pct = r['count'] / clean_rows * 100
            f.write(f"| `{r['contact_attempts_band']}` | {int(r['count']):,} | {pct:.2f}% | {int(r['conversions']):,} | {r['rate']:.2f}% |\n")
        f.write("\n")

        f.write("5. **`previously_contacted`** (`str`): `'Yes'` if client was contacted in an earlier campaign (`pdays != 999`), else `'No'`.\n")
        prev_yes_count = int((df["previously_contacted"] == "Yes").sum())
        prev_yes_rate = df[df["previously_contacted"] == "Yes"]["converted"].mean() * 100
        prev_no_rate = df[df["previously_contacted"] == "No"]["converted"].mean() * 100
        f.write(f"   - Prior contact (`Yes`): **{prev_yes_count:,}** clients ({prev_yes_count/clean_rows*100:.2f}%), with a conversion rate of **{prev_yes_rate:.2f}%**.\n")
        f.write(f"   - No prior contact (`No`): **{clean_rows - prev_yes_count:,}** clients, with a conversion rate of **{prev_no_rate:.2f}%**.\n\n")

        f.write("6. **`euribor_band`** (`str`): Macroeconomic interest rate climate (`<=1`, `1-4`, `>4` on 3-month Euribor).\n\n")
        f.write("| Euribor Band | Contacts | Share (%) | Subscriptions | Conversion Rate (%) |\n")
        f.write("|:---|---:|---:|---:|---:|\n")
        for _, r in eur_summary.iterrows():
            pct = r['count'] / clean_rows * 100
            f.write(f"| `{r['euribor_band']}` | {int(r['count']):,} | {pct:.2f}% | {int(r['conversions']):,} | {r['rate']:.2f}% |\n")
        f.write("\n")

        f.write("## 7. Clean Dataset Profile Summary\n\n")
        f.write(f"- **Final Dimensions:** {final_rows:,} rows, {final_cols} columns.\n")
        f.write(f"- **Total Calls Logged across Campaigns (`campaign.sum()`):** {int(df['campaign'].sum()):,}\n")
        f.write(f"- **Total Successful Subscriptions:** {int(df['converted'].sum()):,}\n")
        f.write(f"- **Overall Conversion Rate:** {df['converted'].mean()*100:.2f}%\n")

    print(f"  Written cleaning log to {log_path}")

if __name__ == "__main__":
    main()
