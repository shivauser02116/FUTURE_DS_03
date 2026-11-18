# Data Cleaning & Transformation Log

**Project:** FUTURE_DS_03 - Marketing Funnel & Conversion Performance Analysis  
**Dataset Source:** UCI Bank Marketing (`bank-additional-full.csv`, Moro et al., 2014, CC BY 4.0)  
**Clean Dataset Output:** `data/bank_clean.csv`  

## 1. Funnel Framing & Analytical Principles

- **Funnel Structure:** The dataset contains records of telemarketing campaign contacts. It has **no website visitor, impression, or inbound lead stages**. The funnel is structured strictly as:
  $$\text{Contacted} \longrightarrow \text{Engaged} \longrightarrow \text{Subscribed}$$
- **Engaged Proxy Definition:** An 'engaged' contact is operationalized as a telephone interaction lasting **longer than 60 seconds** (`duration > 60`). Crucially, call duration is only known **after the call is concluded**; therefore, engagement is a post-hoc diagnostic proxy rather than a predictive pre-call filter.
- **Causal Disclaimer:** All statistical observations represent relationships that are **associated with**, never **caused by**, the respective features.

## 2. Raw File Audit

- **Raw File Dimensions:** 41,188 rows, 21 columns.
- **Delimiter:** Semicolon (`;`), quoted string fields.
- **Missing Values Policy:** The dataset encodes missing categorical values explicitly as `'unknown'`. Per protocol, `'unknown'` values are strictly preserved as a valid category rather than dropped or synthetically imputed.

### Unknown Counts in Raw File

| Column Name | 'unknown' Count | Share of Total (%) |
|:---|---:|---:|
| `job` | 330 | 0.80% |
| `marital` | 80 | 0.19% |
| `education` | 1,731 | 4.20% |
| `default` | 8,597 | 20.87% |
| `housing` | 990 | 2.40% |
| `loan` | 990 | 2.40% |

## 3. Duplicate Handling

- **Exact Duplicates Identified:** 12 rows.
- **Action:** Removed exact duplicate rows using first-occurrence retention (`keep='first'`).
- **Row Count Post-Deduplication:** 41,176 rows (exact expected: 41,176 rows).

### Sample of Removed Duplicate Records

| Row Index | Age | Job | Marital | Education | Day/Month | Duration | Campaign | y |
|---:|---:|:---|:---|:---|:---|---:|---:|:---|
| 1266 | 39 | blue-collar | married | basic.6y | thu/may | 124 | 1 | no |
| 12261 | 36 | retired | married | unknown | thu/jul | 88 | 1 | no |
| 14234 | 27 | technician | single | professional.course | mon/jul | 331 | 2 | no |
| 16956 | 47 | technician | divorced | high.school | thu/jul | 43 | 3 | no |
| 18465 | 32 | technician | single | professional.course | thu/jul | 128 | 1 | no |
| 20216 | 55 | services | married | high.school | mon/aug | 33 | 1 | no |
| 20534 | 41 | technician | married | professional.course | tue/aug | 127 | 1 | no |
| 25217 | 39 | admin. | married | university.degree | tue/nov | 123 | 2 | no |
| 28477 | 24 | services | single | high.school | tue/apr | 114 | 1 | no |
| 32516 | 35 | admin. | married | university.degree | fri/may | 348 | 4 | no |
| 36951 | 45 | admin. | married | university.degree | thu/jul | 252 | 1 | yes |
| 38281 | 71 | retired | single | university.degree | tue/oct | 120 | 1 | no |

## 4. Column Renaming (snake_case)

All column names were converted from dot-notation to standardized lowercase `snake_case`:

| Original Column Name | New snake_case Name |
|:---|:---|
| `age` | `age` |
| `job` | `job` |
| `marital` | `marital` |
| `education` | `education` |
| `default` | `default` |
| `housing` | `housing` |
| `loan` | `loan` |
| `contact` | `contact` |
| `month` | `month` |
| `day_of_week` | `day_of_week` |
| `duration` | `duration` |
| `campaign` | `campaign` |
| `pdays` | `pdays` |
| `previous` | `previous` |
| `poutcome` | `poutcome` |
| `emp.var.rate` | `emp_var_rate` |
| `cons.price.idx` | `cons_price_idx` |
| `cons.conf.idx` | `cons_conf_idx` |
| `euribor3m` | `euribor3m` |
| `nr.employed` | `nr_employed` |
| `y` | `y` |

## 5. Temporal Reconstruction: `period_year` and `month_num`

- **Background:** The raw file lacks a four-digit year column, but the records are chronologically ordered from May 2008 to November 2010 (spanning 31 months of campaign operations).
- **Derivation Method:** Computed on raw row order **prior to duplicate removal**:
  1. Mapped string `month` ('jan'..'dec') to numerical `month_num` (1..12).
  2. Flagged each transition where `month_num[i] < month_num[i-1]` (e.g. from Nov/Dec to Mar).
  3. Computed cumulative transitions: `period_year = 2008 + (month_num.diff() < 0).cumsum()`.
- **Important Limitation:** `period_year` is an **inferred reconstruction** from sequence order rather than an explicit raw timestamp field.

### Inferred Year Distribution (Post-Deduplication)

| Period Year | Record Count | Share of Dataset (%) | Subscriptions | Conversion Rate (%) |
|:---|---:|---:|---:|---:|
| 2008 | 27,682 | 67.23% | 1,339 | 4.84% |
| 2009 | 11,436 | 27.77% | 2,227 | 19.47% |
| 2010 | 2,058 | 5.00% | 1,073 | 52.14% |

## 6. Engineered Feature Columns

The following 6 feature columns were added to support funnel, channel, effort, and macroeconomic analysis:

1. **`converted`** (`int`): `1` if client subscribed to term deposit (`y == 'yes'`), else `0`.
   - Overall subscribers: **4,639** (conversion rate: **11.27%**).
2. **`engaged`** (`int`): `1` if call duration > 60 seconds, else `0`.
   - Engaged contacts: **36,892** (**89.60%** of all contacts).
   - Calls <= 60 seconds: **4,284** (**10.40%**), resulting in exactly **1** subscription (0.02% conversion).
3. **`duration_band`** (`str`): Categorization of call length into operational segments.

| Duration Band | Call Count | Share (%) | Subscriptions | Conversion Rate (%) |
|:---|---:|---:|---:|---:|
| `<=60` | 4,284 | 10.40% | 1 | 0.02% |
| `61-180` | 16,412 | 39.86% | 563 | 3.43% |
| `181-300` | 9,278 | 22.53% | 953 | 10.27% |
| `301-600` | 7,738 | 18.79% | 1,438 | 18.58% |
| `600+` | 3,464 | 8.41% | 1,684 | 48.61% |

4. **`contact_attempts_band`** (`str`): Customer touch count (`1`, `2`, `3`, `4+`).

| Attempts Band | Client Count | Share (%) | Subscriptions | Conversion Rate (%) |
|:---|---:|---:|---:|---:|
| `1` | 17,634 | 42.83% | 2,299 | 13.04% |
| `2` | 10,568 | 25.67% | 1,211 | 11.46% |
| `3` | 5,340 | 12.97% | 574 | 10.75% |
| `4+` | 7,634 | 18.54% | 555 | 7.27% |

5. **`previously_contacted`** (`str`): `'Yes'` if client was contacted in an earlier campaign (`pdays != 999`), else `'No'`.
   - Prior contact (`Yes`): **1,515** clients (3.68%), with a conversion rate of **63.83%**.
   - No prior contact (`No`): **39,661** clients, with a conversion rate of **9.26%**.

6. **`euribor_band`** (`str`): Macroeconomic interest rate climate (`<=1`, `1-4`, `>4` on 3-month Euribor).

| Euribor Band | Contacts | Share (%) | Subscriptions | Conversion Rate (%) |
|:---|---:|---:|---:|---:|
| `<=1` | 3,907 | 9.49% | 1,786 | 45.71% |
| `1-4` | 9,601 | 23.32% | 1,515 | 15.78% |
| `>4` | 27,668 | 67.19% | 1,338 | 4.84% |

## 7. Clean Dataset Profile Summary

- **Final Dimensions:** 41,176 rows, 29 columns.
- **Total Calls Logged across Campaigns (`campaign.sum()`):** 105,735
- **Total Successful Subscriptions:** 4,639
- **Overall Conversion Rate:** 11.27%
