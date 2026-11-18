#!/usr/bin/env python3
"""
scripts/03_check_results.py
---------------------------
Automated test suite verifying data cleaning, metrics, and funnel calculations.
Tolerances: rates +/- 0.2 percentage points, counts exact.
Each check is isolated in its own try/except block.
Prints [PASS] / [FAIL] with actual values, reports totals, exits with code 1 if any fail.
"""

import sys
import os
import pandas as pd
import numpy as np

def approx_equal(actual, expected, tol=0.2):
    return abs(actual - expected) <= tol

def main():
    raw_path = os.path.join("data", "bank-additional-full.csv")
    clean_path = os.path.join("data", "bank_clean.csv")

    if not os.path.exists(raw_path):
        print(f"[FAIL] Raw data file missing: {raw_path}")
        sys.exit(1)
    if not os.path.exists(clean_path):
        print(f"[FAIL] Clean data file missing: {clean_path}")
        sys.exit(1)

    df_raw = pd.read_csv(raw_path, sep=";")
    df_clean = pd.read_csv(clean_path)

    total_checks = 0
    passed_checks = 0
    failed_checks = 0

    def record_result(check_name, passed, actual_val, expected_val):
        nonlocal total_checks, passed_checks, failed_checks
        total_checks += 1
        if passed:
            passed_checks += 1
            print(f"[PASS] {check_name}: actual={actual_val}")
        else:
            failed_checks += 1
            print(f"[FAIL] {check_name}: actual={actual_val} | expected={expected_val}")

    print("================================================================================")
    print("RUNNING VERIFICATION SUITE: FUTURE_DS_03 TASK 3")
    print("================================================================================\n")

    # 1. Raw counts, duplicates, clean counts, conversions
    try:
        raw_rows = len(df_raw)
        record_result("Raw rows count", raw_rows == 41188, raw_rows, 41188)
    except Exception as e:
        record_result("Raw rows count", False, str(e), 41188)

    try:
        dup_count = int(df_raw.duplicated().sum())
        record_result("Duplicate rows count", dup_count == 12, dup_count, 12)
    except Exception as e:
        record_result("Duplicate rows count", False, str(e), 12)

    try:
        clean_rows = len(df_clean)
        record_result("Clean rows count", clean_rows == 41176, clean_rows, 41176)
    except Exception as e:
        record_result("Clean rows count", False, str(e), 41176)

    try:
        subs_count = int(df_clean["converted"].sum())
        record_result("Subscribed count", subs_count == 4639, subs_count, 4639)
    except Exception as e:
        record_result("Subscribed count", False, str(e), 4639)

    try:
        conv_rate = float(df_clean["converted"].mean() * 100)
        record_result("Overall conversion rate", approx_equal(conv_rate, 11.27), f"{conv_rate:.2f}%", "11.27%")
    except Exception as e:
        record_result("Overall conversion rate", False, str(e), "11.27%")

    # 2. Funnel metrics
    try:
        engaged_count = int(df_clean["engaged"].sum())
        record_result("Engaged contacts count", engaged_count == 36892, engaged_count, 36892)
    except Exception as e:
        record_result("Engaged contacts count", False, str(e), 36892)

    try:
        engaged_pct = float(df_clean["engaged"].mean() * 100)
        record_result("Engaged share of contacts", approx_equal(engaged_pct, 89.60), f"{engaged_pct:.2f}%", "89.60%")
    except Exception as e:
        record_result("Engaged share of contacts", False, str(e), "89.60%")

    try:
        sub_engaged_pct = float(df_clean[df_clean["engaged"] == 1]["converted"].mean() * 100)
        record_result("Subscribed / engaged rate", approx_equal(sub_engaged_pct, 12.57), f"{sub_engaged_pct:.2f}%", "12.57%")
    except Exception as e:
        record_result("Subscribed / engaged rate", False, str(e), "12.57%")

    try:
        short_calls_count = int((df_clean["duration"] <= 60).sum())
        record_result("Calls <= 60s count", short_calls_count == 4284, short_calls_count, 4284)
    except Exception as e:
        record_result("Calls <= 60s count", False, str(e), 4284)

    try:
        short_calls_pct = float(short_calls_count / len(df_clean) * 100)
        record_result("Calls <= 60s share", approx_equal(short_calls_pct, 10.40), f"{short_calls_pct:.2f}%", "10.40%")
    except Exception as e:
        record_result("Calls <= 60s share", False, str(e), "10.40%")

    try:
        short_subs_count = int(df_clean[df_clean["duration"] <= 60]["converted"].sum())
        record_result("Calls <= 60s subscription count", short_subs_count == 1, short_subs_count, 1)
    except Exception as e:
        record_result("Calls <= 60s subscription count", False, str(e), 1)

    # 3. Contact channel
    try:
        cell_count = int((df_clean["contact"] == "cellular").sum())
        record_result("Cellular rows count", cell_count == 26135, cell_count, 26135)
    except Exception as e:
        record_result("Cellular rows count", False, str(e), 26135)

    try:
        cell_rate = float(df_clean[df_clean["contact"] == "cellular"]["converted"].mean() * 100)
        record_result("Cellular conversion rate", approx_equal(cell_rate, 14.74), f"{cell_rate:.2f}%", "14.74%")
    except Exception as e:
        record_result("Cellular conversion rate", False, str(e), "14.74%")

    try:
        tel_count = int((df_clean["contact"] == "telephone").sum())
        record_result("Telephone rows count", tel_count == 15041, tel_count, 15041)
    except Exception as e:
        record_result("Telephone rows count", False, str(e), 15041)

    try:
        tel_rate = float(df_clean[df_clean["contact"] == "telephone"]["converted"].mean() * 100)
        record_result("Telephone conversion rate", approx_equal(tel_rate, 5.23), f"{tel_rate:.2f}%", "5.23%")
    except Exception as e:
        record_result("Telephone conversion rate", False, str(e), "5.23%")

    # 4. Period year
    try:
        y08_count = int((df_clean["period_year"] == 2008).sum())
        record_result("2008 rows count", y08_count == 27682, y08_count, 27682)
    except Exception as e:
        record_result("2008 rows count", False, str(e), 27682)

    try:
        y08_rate = float(df_clean[df_clean["period_year"] == 2008]["converted"].mean() * 100)
        record_result("2008 conversion rate", approx_equal(y08_rate, 4.84), f"{y08_rate:.2f}%", "4.84%")
    except Exception as e:
        record_result("2008 conversion rate", False, str(e), "4.84%")

    try:
        y09_count = int((df_clean["period_year"] == 2009).sum())
        record_result("2009 rows count", y09_count == 11436, y09_count, 11436)
    except Exception as e:
        record_result("2009 rows count", False, str(e), 11436)

    try:
        y09_rate = float(df_clean[df_clean["period_year"] == 2009]["converted"].mean() * 100)
        record_result("2009 conversion rate", approx_equal(y09_rate, 19.47), f"{y09_rate:.2f}%", "19.47%")
    except Exception as e:
        record_result("2009 conversion rate", False, str(e), "19.47%")

    try:
        y10_count = int((df_clean["period_year"] == 2010).sum())
        record_result("2010 rows count", y10_count == 2058, y10_count, 2058)
    except Exception as e:
        record_result("2010 rows count", False, str(e), 2058)

    try:
        y10_rate = float(df_clean[df_clean["period_year"] == 2010]["converted"].mean() * 100)
        record_result("2010 conversion rate", approx_equal(y10_rate, 52.14), f"{y10_rate:.2f}%", "52.14%")
    except Exception as e:
        record_result("2010 conversion rate", False, str(e), "52.14%")

    # 5. Contact x period_year
    try:
        y08_cell = float(df_clean[(df_clean["period_year"] == 2008) & (df_clean["contact"] == "cellular")]["converted"].mean() * 100)
        record_result("2008 cellular conversion", approx_equal(y08_cell, 5.73), f"{y08_cell:.2f}%", "5.73%")
    except Exception as e:
        record_result("2008 cellular conversion", False, str(e), "5.73%")

    try:
        y08_tel = float(df_clean[(df_clean["period_year"] == 2008) & (df_clean["contact"] == "telephone")]["converted"].mean() * 100)
        record_result("2008 telephone conversion", approx_equal(y08_tel, 3.93), f"{y08_tel:.2f}%", "3.93%")
    except Exception as e:
        record_result("2008 telephone conversion", False, str(e), "3.93%")

    try:
        y09_cell = float(df_clean[(df_clean["period_year"] == 2009) & (df_clean["contact"] == "cellular")]["converted"].mean() * 100)
        record_result("2009 cellular conversion", approx_equal(y09_cell, 19.90), f"{y09_cell:.2f}%", "19.90%")
    except Exception as e:
        record_result("2009 cellular conversion", False, str(e), "19.90%")

    try:
        y09_tel = float(df_clean[(df_clean["period_year"] == 2009) & (df_clean["contact"] == "telephone")]["converted"].mean() * 100)
        record_result("2009 telephone conversion", approx_equal(y09_tel, 14.67), f"{y09_tel:.2f}%", "14.67%")
    except Exception as e:
        record_result("2009 telephone conversion", False, str(e), "14.67%")

    try:
        y10_cell = float(df_clean[(df_clean["period_year"] == 2010) & (df_clean["contact"] == "cellular")]["converted"].mean() * 100)
        record_result("2010 cellular conversion", approx_equal(y10_cell, 57.66), f"{y10_cell:.2f}%", "57.66%")
    except Exception as e:
        record_result("2010 cellular conversion", False, str(e), "57.66%")

    try:
        y10_tel = float(df_clean[(df_clean["period_year"] == 2010) & (df_clean["contact"] == "telephone")]["converted"].mean() * 100)
        record_result("2010 telephone conversion", approx_equal(y10_tel, 28.35), f"{y10_tel:.2f}%", "28.35%")
    except Exception as e:
        record_result("2010 telephone conversion", False, str(e), "28.35%")

    # 6. May conversion by year
    try:
        may_08_df = df_clean[(df_clean["month"] == "may") & (df_clean["period_year"] == 2008)]
        m08_rows = len(may_08_df)
        m08_rate = float(may_08_df["converted"].mean() * 100)
        record_result("May 2008 rows count", m08_rows == 7762, m08_rows, 7762)
        record_result("May 2008 conversion rate", approx_equal(m08_rate, 3.1), f"{m08_rate:.2f}%", "3.1%")
    except Exception as e:
        record_result("May 2008 checks", False, str(e), "7762 rows / 3.1%")

    try:
        may_09_df = df_clean[(df_clean["month"] == "may") & (df_clean["period_year"] == 2009)]
        m09_rows = len(may_09_df)
        m09_rate = float(may_09_df["converted"].mean() * 100)
        record_result("May 2009 rows count", m09_rows == 5793, m09_rows, 5793)
        record_result("May 2009 conversion rate", approx_equal(m09_rate, 9.0), f"{m09_rate:.2f}%", "9.0%")
    except Exception as e:
        record_result("May 2009 checks", False, str(e), "5793 rows / 9.0%")

    try:
        may_10_df = df_clean[(df_clean["month"] == "may") & (df_clean["period_year"] == 2010)]
        m10_rows = len(may_10_df)
        m10_rate = float(may_10_df["converted"].mean() * 100)
        record_result("May 2010 rows count", m10_rows == 212, m10_rows, 212)
        record_result("May 2010 conversion rate", approx_equal(m10_rate, 57.5), f"{m10_rate:.2f}%", "57.5%")
    except Exception as e:
        record_result("May 2010 checks", False, str(e), "212 rows / 57.5%")

    # 7. Euribor bands and correlation
    eur_expected = {
        "<=1": {"rows": 3907, "conv": 45.71},
        "1-4": {"rows": 9601, "conv": 15.78},
        ">4": {"rows": 27668, "conv": 4.84}
    }
    for band, exp in eur_expected.items():
        try:
            b_df = df_clean[df_clean["euribor_band"] == band]
            b_rows = len(b_df)
            b_rate = float(b_df["converted"].mean() * 100)
            record_result(f"Euribor band {band} rows", b_rows == exp["rows"], b_rows, exp["rows"])
            record_result(f"Euribor band {band} conversion", approx_equal(b_rate, exp["conv"]), f"{b_rate:.2f}%", f"{exp['conv']}%")
        except Exception as e:
            record_result(f"Euribor band {band} check", False, str(e), exp)

    try:
        corr_euribor = float(df_clean["euribor3m"].corr(df_clean["converted"]))
        record_result("Correlation euribor3m with converted", approx_equal(corr_euribor, -0.31, tol=0.01), f"{corr_euribor:.4f}", "-0.31 (+/-0.01)")
    except Exception as e:
        record_result("Correlation euribor3m with converted", False, str(e), "-0.31 (+/-0.01)")

    # 8. Contact attempts band
    att_expected = {
        "1": {"rows": 17634, "conv": 13.04},
        "2": {"rows": 10568, "conv": 11.46},
        "3": {"rows": 5340, "conv": 10.75},
        "4+": {"rows": 7634, "conv": 7.27}
    }
    for band, exp in att_expected.items():
        try:
            a_df = df_clean[df_clean["contact_attempts_band"] == band]
            a_rows = len(a_df)
            a_rate = float(a_df["converted"].mean() * 100)
            record_result(f"Attempts band {band} rows", a_rows == exp["rows"], a_rows, exp["rows"])
            record_result(f"Attempts band {band} conversion", approx_equal(a_rate, exp["conv"]), f"{a_rate:.2f}%", f"{exp['conv']}%")
        except Exception as e:
            record_result(f"Attempts band {band} check", False, str(e), exp)

    # 9. Total calls, calls from 4+, cumulative subscriptions
    try:
        total_calls = int(df_clean["campaign"].sum())
        record_result("Total calls (sum of campaign)", total_calls == 105735, total_calls, 105735)
    except Exception as e:
        record_result("Total calls", False, str(e), 105735)

    try:
        calls_4plus = int(df_clean[df_clean["contact_attempts_band"] == "4+"]["campaign"].sum())
        record_result("Calls from clients with 4+ attempts", calls_4plus == 50945, calls_4plus, 50945)
    except Exception as e:
        record_result("Calls from 4+", False, str(e), 50945)

    try:
        share_calls_4plus = float(calls_4plus / total_calls * 100)
        record_result("Share of calls from 4+ attempts", approx_equal(share_calls_4plus, 48.2), f"{share_calls_4plus:.1f}%", "48.2%")
    except Exception as e:
        record_result("Share of calls from 4+", False, str(e), "48.2%")

    try:
        subs_4plus = int(df_clean[df_clean["contact_attempts_band"] == "4+"]["converted"].sum())
        share_subs_4plus = float(subs_4plus / subs_count * 100)
        record_result("Share of subscriptions from 4+ attempts", approx_equal(share_subs_4plus, 12.0), f"{share_subs_4plus:.1f}%", "12.0%")
    except Exception as e:
        record_result("Share of subscriptions from 4+", False, str(e), "12.0%")

    try:
        subs_att_1 = int(df_clean[df_clean["contact_attempts_band"] == "1"]["converted"].sum())
        subs_att_2 = int(df_clean[df_clean["contact_attempts_band"] == "2"]["converted"].sum())
        subs_att_3 = int(df_clean[df_clean["contact_attempts_band"] == "3"]["converted"].sum())

        cum_1 = float(subs_att_1 / subs_count * 100)
        cum_2 = float((subs_att_1 + subs_att_2) / subs_count * 100)
        cum_3 = float((subs_att_1 + subs_att_2 + subs_att_3) / subs_count * 100)

        record_result("Cumulative subs within <=1 contact", approx_equal(cum_1, 49.6), f"{cum_1:.1f}%", "49.6%")
        record_result("Cumulative subs within <=2 contacts", approx_equal(cum_2, 75.7), f"{cum_2:.1f}%", "75.7%")
        record_result("Cumulative subs within <=3 contacts", approx_equal(cum_3, 88.0), f"{cum_3:.1f}%", "88.0%")
    except Exception as e:
        record_result("Cumulative subs checks", False, str(e), "49.6 / 75.7 / 88.0 %")

    # 10. Previous campaign outcome (poutcome)
    pout_expected = {
        "failure": {"rows": 4252, "conv": 14.23},
        "nonexistent": {"rows": 35551, "conv": 8.83},
        "success": {"rows": 1373, "conv": 65.11}
    }
    for pout, exp in pout_expected.items():
        try:
            p_df = df_clean[df_clean["poutcome"] == pout]
            p_rows = len(p_df)
            p_rate = float(p_df["converted"].mean() * 100)
            record_result(f"poutcome '{pout}' rows", p_rows == exp["rows"], p_rows, exp["rows"])
            record_result(f"poutcome '{pout}' conversion", approx_equal(p_rate, exp["conv"]), f"{p_rate:.2f}%", f"{exp['conv']}%")
        except Exception as e:
            record_result(f"poutcome '{pout}' check", False, str(e), exp)

    # 11. Previously contacted clients
    try:
        prev_yes_df = df_clean[df_clean["previously_contacted"] == "Yes"]
        prev_yes_rows = len(prev_yes_df)
        prev_yes_rate = float(prev_yes_df["converted"].mean() * 100)
        record_result("Previously contacted Yes rows", prev_yes_rows == 1515, prev_yes_rows, 1515)
        record_result("Previously contacted Yes conversion", approx_equal(prev_yes_rate, 63.83), f"{prev_yes_rate:.2f}%", "63.83%")
    except Exception as e:
        record_result("Previously contacted Yes check", False, str(e), "1,515 / 63.83%")

    try:
        prev_by_year = df_clean.groupby("period_year")["previously_contacted"].apply(lambda s: float((s == "Yes").mean() * 100))
        record_result("Previously contacted share 2008", approx_equal(prev_by_year[2008], 0.1), f"{prev_by_year[2008]:.1f}%", "0.1%")
        record_result("Previously contacted share 2009", approx_equal(prev_by_year[2009], 6.6), f"{prev_by_year[2009]:.1f}%", "6.6%")
        record_result("Previously contacted share 2010", approx_equal(prev_by_year[2010], 35.2), f"{prev_by_year[2010]:.1f}%", "35.2%")
    except Exception as e:
        record_result("Previously contacted by year check", False, str(e), "0.1 / 6.6 / 35.2 %")

    # 12. Selected Job categories
    job_expected = {
        "student": {"rows": 875, "conv": 31.43},
        "retired": {"rows": 1718, "conv": 25.26},
        "blue-collar": {"rows": 9253, "conv": 6.90}
    }
    for job_name, exp in job_expected.items():
        try:
            j_df = df_clean[df_clean["job"] == job_name]
            j_rows = len(j_df)
            j_rate = float(j_df["converted"].mean() * 100)
            record_result(f"Job '{job_name}' rows", j_rows == exp["rows"], j_rows, exp["rows"])
            record_result(f"Job '{job_name}' conversion", approx_equal(j_rate, exp["conv"]), f"{j_rate:.2f}%", f"{exp['conv']}%")
        except Exception as e:
            record_result(f"Job '{job_name}' check", False, str(e), exp)

    # 13. Duration bands
    dur_expected = {
        "<=60": {"rows": 4284, "conv": 0.02},
        "61-180": {"rows": 16412, "conv": 3.43},
        "181-300": {"rows": 9278, "conv": 10.27},
        "301-600": {"rows": 7738, "conv": 18.58},
        "600+": {"rows": 3464, "conv": 48.61}
    }
    for band, exp in dur_expected.items():
        try:
            d_df = df_clean[df_clean["duration_band"] == band]
            d_rows = len(d_df)
            d_rate = float(d_df["converted"].mean() * 100)
            record_result(f"Duration band '{band}' rows", d_rows == exp["rows"], d_rows, exp["rows"])
            record_result(f"Duration band '{band}' conversion", approx_equal(d_rate, exp["conv"]), f"{d_rate:.2f}%", f"{exp['conv']}%")
        except Exception as e:
            record_result(f"Duration band '{band}' check", False, str(e), exp)

    # 14. Day of week conversion rates
    dow_expected = {
        "mon": 9.95,
        "tue": 11.79,
        "wed": 11.67,
        "thu": 12.11,
        "fri": 10.81
    }
    for dow, exp_rate in dow_expected.items():
        try:
            dow_df = df_clean[df_clean["day_of_week"] == dow]
            dow_rate = float(dow_df["converted"].mean() * 100)
            record_result(f"Day of week '{dow}' conversion", approx_equal(dow_rate, exp_rate), f"{dow_rate:.2f}%", f"{exp_rate}%")
        except Exception as e:
            record_result(f"Day of week '{dow}' check", False, str(e), f"{exp_rate}%")

    print("\n================================================================================")
    print("TEST SUITE SUMMARY")
    print(f"Total Checks:  {total_checks}")
    print(f"Passed Checks: {passed_checks}")
    print(f"Failed Checks: {failed_checks}")
    print("================================================================================")

    if failed_checks > 0:
        print("\nResult: [OVERALL FAIL] Some checks failed.")
        sys.exit(1)
    else:
        print("\nResult: [OVERALL PASS] All checks passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
