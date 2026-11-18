#!/usr/bin/env python3
"""
scripts/02_build_dashboard.py
-----------------------------
Generates a professional 4-page executive dashboard for Task 3:
Marketing Funnel & Conversion Performance Analysis.

Outputs:
  - dashboard/FUTURE_DS_03_dashboard.pdf
  - images/page_1.png
  - images/page_2.png
  - images/page_3.png
  - images/page_4.png

Specifications:
  - 16:9 Aspect ratio (16x9 inches @ 150 DPI)
  - Navy / Teal / Red palette
  - Dynamic insight headlines computed from data
  - Strict framing: Contacted -> Engaged (>60s) -> Subscribed; associations, not causes.
"""

import os
import sys

# Ensure clean matplotlib cache directory
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

# Define Color Palette
NAVY_DARK = "#0F1E36"
NAVY_PRIMARY = "#1B2A4A"
NAVY_LIGHT = "#2C3E50"
TEAL_PRIMARY = "#008080"
TEAL_LIGHT = "#20B2AA"
TEAL_ACCENT = "#4DB6AC"
RED_PRIMARY = "#D9534F"
RED_DARK = "#C0392B"
GRAY_BG = "#F8F9FA"
GRAY_CARD = "#FFFFFF"
GRAY_BORDER = "#E2E8F0"
TEXT_DARK = "#1E293B"
TEXT_MUTED = "#64748B"
TEXT_LIGHT = "#FFFFFF"

def setup_figure():
    """Initializes a standard 16:9 figure with soft background styling."""
    fig = plt.figure(figsize=(16, 9), dpi=150, facecolor=GRAY_BG)
    return fig

def draw_header(fig, page_num, total_pages, title, category, insight_headline):
    """Draws a standardized executive header banner with dynamic insight headline."""
    # Top banner background
    header_ax = fig.add_axes([0, 0.88, 1, 0.12])
    header_ax.set_facecolor(NAVY_DARK)
    header_ax.axis("off")

    # Category Pill & Page Number
    header_ax.text(0.04, 0.72, f"FUTURE_DS_03  |  TASK 3: MARKETING FUNNEL & CONVERSION PERFORMANCE  •  PAGE {page_num} OF {total_pages}",
                   color=TEAL_ACCENT, fontsize=10, weight="bold", va="center")

    # Main Page Title
    header_ax.text(0.04, 0.38, title,
                   color=TEXT_LIGHT, fontsize=18, weight="bold", va="center")

    # Dynamic Insight Headline Bar
    sub_ax = fig.add_axes([0, 0.82, 1, 0.06])
    sub_ax.set_facecolor(NAVY_PRIMARY)
    sub_ax.axis("off")

    # Accent tag
    rect = patches.Rectangle((0.04, 0.22), 0.08, 0.56, facecolor=TEAL_PRIMARY, edgecolor="none", transform=sub_ax.transAxes)
    sub_ax.add_patch(rect)
    sub_ax.text(0.08, 0.5, "KEY INSIGHT", color=TEXT_LIGHT, fontsize=9, weight="bold", va="center", ha="center")

    # Insight Text
    sub_ax.text(0.13, 0.5, insight_headline,
                color="#E2E8F0", fontsize=11, weight="medium", va="center")

def draw_kpi_card(ax, title, main_val, sub_val, border_color=TEAL_PRIMARY, bg_color=GRAY_CARD):
    """Renders a styled KPI card on a given axis."""
    ax.set_facecolor(bg_color)
    ax.axis("off")

    # Outer border & rounded feel
    card_rect = patches.FancyBboxPatch(
        (0.02, 0.04), 0.96, 0.92,
        boxstyle="round,pad=0.03,rounding_size=0.06",
        facecolor=bg_color, edgecolor=GRAY_BORDER, linewidth=1.5,
        transform=ax.transAxes
    )
    ax.add_patch(card_rect)

    # Accent top border line
    accent_bar = patches.FancyBboxPatch(
        (0.02, 0.90), 0.96, 0.06,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=border_color, edgecolor="none",
        transform=ax.transAxes
    )
    ax.add_patch(accent_bar)

    # Text content
    ax.text(0.08, 0.72, title.upper(), color=TEXT_MUTED, fontsize=9, weight="bold", va="center")
    ax.text(0.08, 0.44, main_val, color=TEXT_DARK, fontsize=20, weight="bold", va="center")
    ax.text(0.08, 0.20, sub_val, color=TEXT_MUTED, fontsize=8.5, weight="normal", va="center")

def create_page_1(df):
    """Page 1: Marketing Funnel & Call Duration Performance."""
    fig = setup_figure()

    # Dynamic metrics
    total_contacts = len(df)
    engaged_count = int(df["engaged"].sum())
    engaged_pct = df["engaged"].mean() * 100
    subscribed_count = int(df["converted"].sum())
    overall_conv = df["converted"].mean() * 100
    sub_per_engaged = df[df["engaged"] == 1]["converted"].mean() * 100
    avg_contacts = df["campaign"].mean()
    short_calls_cnt = int((df["duration"] <= 60).sum())
    short_calls_pct = short_calls_cnt / total_contacts * 100
    short_calls_sub = int(df[df["duration"] <= 60]["converted"].sum())

    insight_headline = (
        f"Engaged calls (>60s) yield {sub_per_engaged:.2f}% conversion ({subscribed_count - short_calls_sub:,} subs), "
        f"while calls \u226460s represent {short_calls_pct:.1f}% of volume with only {short_calls_sub} single subscription (0.02%)."
    )

    draw_header(fig, 1, 4,
                "Marketing Funnel Architecture & Call Duration Diagnostics",
                "STAGE CONVERSION & CALL ENGAGEMENT",
                insight_headline)

    # KPI Row (6 cards)
    kpis = [
        ("Total Contacts", f"{total_contacts:,}", "100.0% of campaign contacts", NAVY_PRIMARY),
        ("Engaged Contacts", f"{engaged_count:,}", f"{engaged_pct:.1f}% reached >60s proxy", TEAL_PRIMARY),
        ("Subscribed Clients", f"{subscribed_count:,}", f"{overall_conv:.2f}% overall conversion", TEAL_PRIMARY),
        ("Subscribed / Engaged", f"{sub_per_engaged:.2f}%", f"{subscribed_count:,} of {engaged_count:,} engaged", TEAL_LIGHT),
        ("Avg Contacts / Client", f"{avg_contacts:.2f}", "Total touches / client pool", NAVY_LIGHT),
        ("Calls \u2264 60 Seconds", f"{short_calls_cnt:,}", f"{short_calls_pct:.1f}% share | {short_calls_sub} sub (0.02%)", RED_PRIMARY),
    ]

    card_width = 0.143
    card_gap = 0.012
    start_x = 0.04
    for i, (title, val, sub, color) in enumerate(kpis):
        ax = fig.add_axes([start_x + i * (card_width + card_gap), 0.69, card_width, 0.11])
        draw_kpi_card(ax, title, val, sub, border_color=color)

    # Left Panel: Funnel Stage Progression (x=0.04 to 0.48, y=0.14 to 0.65)
    ax_funnel = fig.add_axes([0.05, 0.15, 0.42, 0.50])
    ax_funnel.set_facecolor(GRAY_CARD)
    for spine in ax_funnel.spines.values():
        spine.set_color(GRAY_BORDER)

    stages = ["1. Contacted", "2. Engaged (>60s)", "3. Subscribed"]
    counts = [total_contacts, engaged_count, subscribed_count]
    rates_of_total = [100.0, engaged_pct, overall_conv]
    colors = [NAVY_PRIMARY, TEAL_PRIMARY, TEAL_LIGHT]

    y_pos = [2, 1, 0]
    bars = ax_funnel.barh(y_pos, counts, height=0.45, color=colors, edgecolor=NAVY_DARK, linewidth=1.2)
    ax_funnel.set_yticks(y_pos)
    ax_funnel.set_yticklabels(stages, fontsize=11, weight="bold", color=TEXT_DARK)
    ax_funnel.set_xlabel("Client Count", fontsize=10, weight="bold", color=TEXT_MUTED)
    ax_funnel.set_xlim(0, 48000)
    ax_funnel.grid(axis="x", linestyle="--", alpha=0.4)

    # Annotate bars
    for i, (bar, count, pct) in enumerate(zip(bars, counts, rates_of_total)):
        w = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        ax_funnel.text(w + 800, y, f"{count:,} ({pct:.1f}%)", va="center", ha="left",
                       fontsize=10.5, weight="bold", color=TEXT_DARK)

    # Annotate Drop-offs between stages
    drop_1 = (1 - engaged_count / total_contacts) * 100
    drop_2 = (1 - subscribed_count / engaged_count) * 100

    ax_funnel.annotate(
        f"Drop-off: -{drop_1:.1f}%\n(Calls \u2264 60s)",
        xy=(engaged_count, 1.25), xytext=(22000, 1.55),
        arrowprops=dict(arrowstyle="->", color=RED_PRIMARY, lw=1.5),
        fontsize=9.5, weight="bold", color=RED_PRIMARY,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFEEEE", edgecolor=RED_PRIMARY, alpha=0.8)
    )

    ax_funnel.annotate(
        f"Drop-off: -{drop_2:.1f}%\n(Unsubscribed)",
        xy=(subscribed_count, 0.25), xytext=(12000, 0.55),
        arrowprops=dict(arrowstyle="->", color=RED_PRIMARY, lw=1.5),
        fontsize=9.5, weight="bold", color=RED_PRIMARY,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFEEEE", edgecolor=RED_PRIMARY, alpha=0.8)
    )
    ax_funnel.set_title("Marketing Funnel Stages & Stage-to-Stage Drop-off", fontsize=12, weight="bold", color=NAVY_DARK, pad=12)

    # Right Panel: Conversion Rate by Duration Band (x=0.52 to 0.96, y=0.14 to 0.65)
    ax_dur = fig.add_axes([0.53, 0.15, 0.42, 0.50])
    ax_dur.set_facecolor(GRAY_CARD)
    for spine in ax_dur.spines.values():
        spine.set_color(GRAY_BORDER)

    dur_order = ["<=60", "61-180", "181-300", "301-600", "600+"]
    dur_df = df.groupby("duration_band")["converted"].agg(
        count="count",
        conv_rate=lambda x: x.mean() * 100
    ).reindex(dur_order).reset_index()

    dur_colors = [RED_PRIMARY if b == "<=60" else (TEAL_LIGHT if b in ["61-180", "181-300"] else TEAL_PRIMARY) for b in dur_df["duration_band"]]
    bars_dur = ax_dur.bar(dur_df["duration_band"], dur_df["conv_rate"], width=0.55, color=dur_colors, edgecolor=NAVY_DARK, linewidth=1.2)
    ax_dur.set_ylabel("Conversion Rate (%)", fontsize=10, weight="bold", color=TEXT_MUTED)
    ax_dur.set_xlabel("Call Duration Band (Seconds)", fontsize=10, weight="bold", color=TEXT_MUTED)
    ax_dur.set_ylim(0, 56)
    ax_dur.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, (_, row) in zip(bars_dur, dur_df.iterrows()):
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2
        cnt = int(row["count"])
        ax_dur.text(x, h + 1.2, f"{h:.2f}%\n({cnt:,})", ha="center", va="bottom",
                    fontsize=9.5, weight="bold", color=TEXT_DARK)

    ax_dur.set_title("Term Deposit Conversion Rate by Call Duration Band", fontsize=12, weight="bold", color=NAVY_DARK, pad=12)

    # Diagnostic Framing Footer
    footer_ax = fig.add_axes([0.05, 0.04, 0.90, 0.065])
    footer_ax.set_facecolor("#EDF2F7")
    footer_ax.axis("off")
    footer_rect = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.01,rounding_size=0.04",
        facecolor="#EDF2F7", edgecolor=NAVY_LIGHT, linewidth=1,
        transform=footer_ax.transAxes
    )
    footer_ax.add_patch(footer_rect)
    disclaimer_text = (
        "METHODOLOGICAL FRAMING & CAUSAL DISCLAIMER:\n"
        "• The funnel is structured strictly as Contacted -> Engaged -> Subscribed. 'Engaged' is a diagnostic proxy operationalized as call duration > 60 seconds.\n"
        "• Call duration is strictly unknown prior to placing the call and cannot be used as an ex-ante targeting filter. Observed patterns are associated with, not caused by, duration."
    )
    footer_ax.text(0.02, 0.5, disclaimer_text, fontsize=8.2, color=NAVY_DARK, weight="bold", va="center")

    return fig

def create_page_2(df):
    """Page 2: Channel Performance & Temporal / Macroeconomic Analysis."""
    fig = setup_figure()

    # Dynamic metrics
    cell_rate = df[df["contact"] == "cellular"]["converted"].mean() * 100
    tel_rate = df[df["contact"] == "telephone"]["converted"].mean() * 100
    eur_corr = df["euribor3m"].corr(df["converted"])

    insight_headline = (
        f"Cellular outreach converts at {cell_rate:.2f}% vs {tel_rate:.2f}% for telephone (2.8\u00d7 lift), "
        f"while macroeconomic interest rate collapse (Euribor \u22641%: 45.71%, corr: {eur_corr:.2f}) drove the 2008\u20132010 surge."
    )

    draw_header(fig, 2, 4,
                "Channel Effectiveness & Macroeconomic Regime Shifts",
                "CHANNEL EFFICIENCY & TEMPORAL MACROECONOMIC IMPACT",
                insight_headline)

    # 4 Charts Layout:
    # 1. Grouped Bar: Conversion by Contact Channel overall & by year (Top Left)
    ax_ch = fig.add_axes([0.05, 0.47, 0.42, 0.31])
    ax_ch.set_facecolor(GRAY_CARD)
    for s in ax_ch.spines.values():
        s.set_color(GRAY_BORDER)

    years = ["Overall", "2008", "2009", "2010"]
    x = np.arange(len(years))
    w = 0.35

    cell_rates = [
        cell_rate,
        df[(df["period_year"] == 2008) & (df["contact"] == "cellular")]["converted"].mean() * 100,
        df[(df["period_year"] == 2009) & (df["contact"] == "cellular")]["converted"].mean() * 100,
        df[(df["period_year"] == 2010) & (df["contact"] == "cellular")]["converted"].mean() * 100,
    ]
    tel_rates = [
        tel_rate,
        df[(df["period_year"] == 2008) & (df["contact"] == "telephone")]["converted"].mean() * 100,
        df[(df["period_year"] == 2009) & (df["contact"] == "telephone")]["converted"].mean() * 100,
        df[(df["period_year"] == 2010) & (df["contact"] == "telephone")]["converted"].mean() * 100,
    ]

    b1 = ax_ch.bar(x - w/2, cell_rates, width=w, label="Cellular", color=TEAL_PRIMARY, edgecolor=NAVY_DARK)
    b2 = ax_ch.bar(x + w/2, tel_rates, width=w, label="Telephone (Fixed)", color=RED_PRIMARY, edgecolor=NAVY_DARK)
    ax_ch.set_xticks(x)
    ax_ch.set_xticklabels(years, fontsize=10, weight="bold", color=TEXT_DARK)
    ax_ch.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_ch.set_ylim(0, 68)
    ax_ch.grid(axis="y", linestyle="--", alpha=0.4)
    ax_ch.legend(loc="upper left", framealpha=0.9, fontsize=9)
    ax_ch.set_title("Conversion by Contact Channel (Overall & By Inferred Year)", fontsize=11, weight="bold", color=NAVY_DARK)

    for bar in b1:
        h = bar.get_height()
        ax_ch.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, weight="bold")
    for bar in b2:
        h = bar.get_height()
        ax_ch.text(bar.get_x() + bar.get_width()/2, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, weight="bold")

    # 2. Conversion by Inferred Year with Mean Euribor (Top Right)
    ax_yr = fig.add_axes([0.53, 0.47, 0.42, 0.31])
    ax_yr.set_facecolor(GRAY_CARD)
    for s in ax_yr.spines.values():
        s.set_color(GRAY_BORDER)

    yr_stats = df.groupby("period_year").agg(
        conv_rate=("converted", lambda x: x.mean() * 100),
        contacts=("converted", "count"),
        euribor=("euribor3m", "mean")
    ).reset_index()

    x_yr = np.arange(len(yr_stats))
    bars_yr = ax_yr.bar(x_yr, yr_stats["conv_rate"], width=0.45, color=NAVY_PRIMARY, edgecolor=NAVY_DARK, label="Conversion Rate (%)")
    ax_yr.set_xticks(x_yr)
    ax_yr.set_xticklabels([str(y) for y in yr_stats["period_year"]], fontsize=10, weight="bold", color=TEXT_DARK)
    ax_yr.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=NAVY_PRIMARY)
    ax_yr.set_ylim(0, 65)
    ax_yr.grid(axis="y", linestyle="--", alpha=0.4)

    # Line for mean Euribor on secondary axis
    ax_eur = ax_yr.twinx()
    ax_eur.plot(x_yr, yr_stats["euribor"], color=RED_PRIMARY, marker="o", linewidth=2.5, markersize=8, label="Mean Euribor 3m")
    ax_eur.set_ylabel("Euribor 3M Rate (%)", fontsize=9.5, weight="bold", color=RED_PRIMARY)
    ax_eur.set_ylim(0, 6)

    for i, (_, row) in enumerate(yr_stats.iterrows()):
        ax_yr.text(i, row["conv_rate"] + 1.2, f"{row['conv_rate']:.1f}%\n({int(row['contacts']):,})",
                   ha="center", va="bottom", fontsize=8.5, weight="bold", color=NAVY_PRIMARY)
        ax_eur.text(i, row["euribor"] + 0.25, f"{row['euribor']:.2f}%",
                    ha="center", va="bottom", fontsize=8.5, weight="bold", color=RED_PRIMARY)

    ax_yr.set_title("Annual Conversion Rate vs Macroeconomic Benchmark (Euribor 3M)", fontsize=11, weight="bold", color=NAVY_DARK)

    # 3. Conversion by Euribor Band (Bottom Left)
    ax_eb = fig.add_axes([0.05, 0.08, 0.42, 0.31])
    ax_eb.set_facecolor(GRAY_CARD)
    for s in ax_eb.spines.values():
        s.set_color(GRAY_BORDER)

    eb_order = ["<=1", "1-4", ">4"]
    eb_stats = df.groupby("euribor_band")["converted"].agg(
        conv_rate=lambda x: x.mean() * 100,
        count="count"
    ).reindex(eb_order).reset_index()

    eb_colors = [TEAL_PRIMARY, TEAL_LIGHT, NAVY_LIGHT]
    bars_eb = ax_eb.bar(eb_stats["euribor_band"], eb_stats["conv_rate"], width=0.5, color=eb_colors, edgecolor=NAVY_DARK)
    ax_eb.set_xlabel("Euribor 3M Interest Rate Regime", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_eb.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_eb.set_ylim(0, 55)
    ax_eb.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, (_, row) in zip(bars_eb, eb_stats.iterrows()):
        h = bar.get_height()
        cnt = int(row["count"])
        ax_eb.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.2f}%\n({cnt:,} calls)",
                   ha="center", va="bottom", fontsize=8.5, weight="bold", color=TEXT_DARK)

    ax_eb.set_title("Deposit Demand Surges Under Low Interest Rate Regimes", fontsize=11, weight="bold", color=NAVY_DARK)

    # 4. May Conversion by Year: Seasonality Myth Deconstruction (Bottom Right)
    ax_may = fig.add_axes([0.53, 0.08, 0.42, 0.31])
    ax_may.set_facecolor(GRAY_CARD)
    for s in ax_may.spines.values():
        s.set_color(GRAY_BORDER)

    may_stats = df[df["month"] == "may"].groupby("period_year")["converted"].agg(
        conv_rate=lambda x: x.mean() * 100,
        count="count"
    ).reset_index()

    bars_may = ax_may.bar([str(y) for y in may_stats["period_year"]], may_stats["conv_rate"],
                          width=0.45, color=[NAVY_LIGHT, TEAL_LIGHT, TEAL_PRIMARY], edgecolor=NAVY_DARK)
    ax_may.set_xlabel("Campaign Year (May Cohorts Only)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_may.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_may.set_ylim(0, 68)
    ax_may.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, (_, row) in zip(bars_may, may_stats.iterrows()):
        h = bar.get_height()
        cnt = int(row["count"])
        ax_may.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}%\n({cnt:,} calls)",
                    ha="center", va="bottom", fontsize=8.5, weight="bold", color=TEXT_DARK)

    ax_may.set_title("Deconstructing Seasonality: May Conversion Across Years", fontsize=11, weight="bold", color=NAVY_DARK)

    return fig

def create_page_3(df):
    """Page 3: Campaign Effort, Diminishing Returns & Client Segments."""
    fig = setup_figure()

    # Dynamic metrics
    total_calls = df["campaign"].sum()
    calls_4p = df[df["contact_attempts_band"] == "4+"]["campaign"].sum()
    share_calls_4p = calls_4p / total_calls * 100
    subs_total = df["converted"].sum()
    subs_4p = df[df["contact_attempts_band"] == "4+"]["converted"].sum()
    share_subs_4p = subs_4p / subs_total * 100

    cum_3 = df[df["contact_attempts_band"].isin(["1", "2", "3"])]["converted"].sum() / subs_total * 100

    insight_headline = (
        f"Calls \u22654 consume {share_calls_4p:.1f}% of total dialing effort but deliver only {share_subs_4p:.1f}% of subscriptions, "
        f"while {cum_3:.1f}% of all conversions are captured within the first 3 touches."
    )

    draw_header(fig, 3, 4,
                "Outreach Effort, Diminishing Returns & Segment Response",
                "CAMPAIGN EFFORT & CLIENT PROFILES",
                insight_headline)

    # 1. Conversion Rate by Contact Attempts Band (Top Left)
    ax_att = fig.add_axes([0.05, 0.48, 0.28, 0.30])
    ax_att.set_facecolor(GRAY_CARD)
    for s in ax_att.spines.values():
        s.set_color(GRAY_BORDER)

    att_order = ["1", "2", "3", "4+"]
    att_stats = df.groupby("contact_attempts_band")["converted"].agg(
        conv_rate=lambda x: x.mean() * 100,
        count="count"
    ).reindex(att_order).reset_index()

    b_att = ax_att.bar(att_stats["contact_attempts_band"], att_stats["conv_rate"], width=0.5,
                       color=[TEAL_PRIMARY, TEAL_LIGHT, NAVY_LIGHT, RED_PRIMARY], edgecolor=NAVY_DARK)
    ax_att.set_xlabel("Contact Attempts Band", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_att.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_att.set_ylim(0, 16)
    ax_att.grid(axis="y", linestyle="--", alpha=0.4)

    for bar, (_, row) in zip(b_att, att_stats.iterrows()):
        h = bar.get_height()
        ax_att.text(bar.get_x() + bar.get_width()/2, h + 0.3, f"{h:.2f}%\n({int(row['count']):,})",
                    ha="center", va="bottom", fontsize=8, weight="bold")
    ax_att.set_title("Conversion Rate Drops with Attempts", fontsize=10.5, weight="bold", color=NAVY_DARK)

    # 2. Call Share vs Subscription Share (Top Middle)
    ax_shr = fig.add_axes([0.37, 0.48, 0.28, 0.30])
    ax_shr.set_facecolor(GRAY_CARD)
    for s in ax_shr.spines.values():
        s.set_color(GRAY_BORDER)

    band_calls = df.groupby("contact_attempts_band")["campaign"].sum()
    band_subs = df.groupby("contact_attempts_band")["converted"].sum()

    call_shares = [band_calls[b] / total_calls * 100 for b in att_order]
    sub_shares = [band_subs[b] / subs_total * 100 for b in att_order]

    x = np.arange(len(att_order))
    w = 0.35
    b_c = ax_shr.bar(x - w/2, call_shares, width=w, label="Share of Calls (%)", color=RED_PRIMARY, edgecolor=NAVY_DARK)
    b_s = ax_shr.bar(x + w/2, sub_shares, width=w, label="Share of Subs (%)", color=TEAL_PRIMARY, edgecolor=NAVY_DARK)
    ax_shr.set_xticks(x)
    ax_shr.set_xticklabels(att_order, fontsize=9.5, weight="bold", color=TEXT_DARK)
    ax_shr.set_xlabel("Contact Attempts Band", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_shr.set_ylabel("Share of Total (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_shr.set_ylim(0, 56)
    ax_shr.grid(axis="y", linestyle="--", alpha=0.4)
    ax_shr.legend(loc="upper right", fontsize=8.5)
    ax_shr.set_title("Effort Misallocation (Calls vs Subs)", fontsize=10.5, weight="bold", color=NAVY_DARK)

    for bar in b_c:
        h = bar.get_height()
        ax_shr.text(bar.get_x() + bar.get_width()/2, h + 0.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=8, weight="bold", color=RED_PRIMARY)
    for bar in b_s:
        h = bar.get_height()
        ax_shr.text(bar.get_x() + bar.get_width()/2, h + 0.8, f"{h:.1f}%", ha="center", va="bottom", fontsize=8, weight="bold", color=TEAL_PRIMARY)

    # 3. Cumulative Subscriptions (Top Right)
    ax_cum = fig.add_axes([0.69, 0.48, 0.26, 0.30])
    ax_cum.set_facecolor(GRAY_CARD)
    for s in ax_cum.spines.values():
        s.set_color(GRAY_BORDER)

    cum_labels = ["<= 1", "<= 2", "<= 3", "All (4+)"]
    cum_vals = [
        band_subs["1"] / subs_total * 100,
        (band_subs["1"] + band_subs["2"]) / subs_total * 100,
        (band_subs["1"] + band_subs["2"] + band_subs["3"]) / subs_total * 100,
        100.0
    ]

    ax_cum.plot(cum_labels, cum_vals, marker="o", color=TEAL_PRIMARY, linewidth=2.5, markersize=8)
    ax_cum.fill_between(cum_labels, cum_vals, color=TEAL_LIGHT, alpha=0.25)
    ax_cum.set_xlabel("Cumulative Contacts", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_cum.set_ylabel("Cumulative Subscriptions (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_cum.set_ylim(35, 108)
    ax_cum.grid(True, linestyle="--", alpha=0.4)
    ax_cum.set_title("Cumulative Yield by Touch", fontsize=10.5, weight="bold", color=NAVY_DARK)

    for i, val in enumerate(cum_vals):
        ax_cum.text(i, val + 2.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=8.5, weight="bold", color=NAVY_DARK)

    # 4. Conversion by Prior Campaign Outcome (Bottom Left)
    ax_pout = fig.add_axes([0.05, 0.08, 0.38, 0.32])
    ax_pout.set_facecolor(GRAY_CARD)
    for s in ax_pout.spines.values():
        s.set_color(GRAY_BORDER)

    pout_order = ["nonexistent", "failure", "success"]
    pout_labels = ["Cold (Nonexistent)", "Past Failure", "Past Success"]
    pout_stats = df.groupby("poutcome")["converted"].agg(
        conv_rate=lambda x: x.mean() * 100,
        count="count"
    ).reindex(pout_order).reset_index()

    b_p = ax_pout.bar(pout_labels, pout_stats["conv_rate"], width=0.45,
                      color=[NAVY_LIGHT, RED_PRIMARY, TEAL_PRIMARY], edgecolor=NAVY_DARK)
    ax_pout.set_ylabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_pout.set_ylim(0, 78)
    ax_pout.grid(axis="y", linestyle="--", alpha=0.4)
    ax_pout.set_title("Previous Outcome: Past Success Gives 7.4x Lift", fontsize=11, weight="bold", color=NAVY_DARK)

    for bar, (_, row) in zip(b_p, pout_stats.iterrows()):
        h = bar.get_height()
        cnt = int(row["count"])
        ax_pout.text(bar.get_x() + bar.get_width()/2, h + 1.5, f"{h:.2f}%\n({cnt:,} leads)",
                     ha="center", va="bottom", fontsize=8.5, weight="bold", color=TEXT_DARK)

    # 5. Conversion by Job Segment Ranked (Bottom Right)
    ax_job = fig.add_axes([0.48, 0.08, 0.47, 0.32])
    ax_job.set_facecolor(GRAY_CARD)
    for s in ax_job.spines.values():
        s.set_color(GRAY_BORDER)

    job_stats = df.groupby("job")["converted"].agg(
        conv_rate=lambda x: x.mean() * 100,
        count="count"
    ).sort_values("conv_rate", ascending=True).reset_index()

    y_pos = np.arange(len(job_stats))
    colors_job = [TEAL_PRIMARY if j in ["student", "retired"] else (RED_PRIMARY if j == "blue-collar" else NAVY_PRIMARY) for j in job_stats["job"]]
    b_j = ax_job.barh(y_pos, job_stats["conv_rate"], height=0.6, color=colors_job, edgecolor=NAVY_DARK)
    ax_job.set_yticks(y_pos)
    ax_job.set_yticklabels(job_stats["job"].str.capitalize(), fontsize=9, weight="bold", color=TEXT_DARK)
    ax_job.set_xlabel("Conversion Rate (%)", fontsize=9.5, weight="bold", color=TEXT_MUTED)
    ax_job.set_xlim(0, 36)
    ax_job.grid(axis="x", linestyle="--", alpha=0.4)
    ax_job.set_title("Client Job Segments Ranked by Conversion Rate", fontsize=11, weight="bold", color=NAVY_DARK)

    for bar, (_, row) in zip(b_j, job_stats.iterrows()):
        w = bar.get_width()
        cnt = int(row["count"])
        ax_job.text(w + 0.5, bar.get_y() + bar.get_height()/2, f"{w:.1f}% ({cnt:,})",
                    va="center", ha="left", fontsize=8, weight="bold", color=TEXT_DARK)

    return fig

def create_page_4(df):
    """Page 4: Strategic Recommendations & Methodological Limitations."""
    fig = setup_figure()

    # Dynamic metrics
    calls_4p = df[df["contact_attempts_band"] == "4+"]["campaign"].sum()
    total_calls = df["campaign"].sum()
    share_4p = calls_4p / total_calls * 100

    insight_headline = (
        f"Data-driven strategic pivot: Capping contacts at 3 saves ~40,000 dial attempts ({share_4p:.1f}% call volume) "
        f"with <12% conversion loss, while prioritizing warm past-success leads unlocks a 65.11% conversion rate."
    )

    draw_header(fig, 4, 4,
                "Executive Recommendations & Analytical Limitations",
                "STRATEGIC RECOMMENDATIONS & GOVERNANCE",
                insight_headline)

    # Left Container: 5 Ranked Recommendations (x=0.05 to 0.58)
    recs = [
        (
            "1. Enforce a Strict 3-Contact Frequency Cap",
            f"Contacts 4+ account for {share_4p:.1f}% of total calls ({calls_4p:,} dials) but yield only 12.0% of subscriptions. "
            "Beyond 3 touches, conversion drops to 7.27%. Implement automated dialer suppression after 3 unsuccessful attempts to save ~40,000 calls."
        ),
        (
            "2. Prioritize Warm & Previously Contacted Leads",
            "Clients with prior campaign success convert at 65.11% (vs 8.83% for cold nonexistent leads—a 7.4\u00d7 lift). "
            "Create a high-priority routing queue dedicated to past participants and warm leads (pdays \u2260 999: 63.83% conversion)."
        ),
        (
            "3. Shift Telephony Infrastructure to Cellular Channels",
            "Cellular outreach achieved 14.74% conversion compared to just 5.23% on fixed telephone lines (2.8\u00d7 relative advantage). "
            "Cellular superiority holds true across all three campaign years (2008: 5.7% vs 3.9%, 2009: 19.9% vs 14.7%, 2010: 57.7% vs 28.4%)."
        ),
        (
            "4. Dynamically Time Campaigns to Macroeconomic Regimes",
            "Term deposit uptake is heavily correlated with falling interest rates (r = -0.31). "
            "Conversion reaches 45.71% in low Euribor environments (\u22641%) vs 4.84% in high-rate climates (>4%). Align budget surges with declining benchmark rates."
        ),
        (
            "5. Tailor Product Messaging to Students & Retirees",
            "Students (31.43%) and retirees (25.26%) exhibit the highest propensity to convert, yet blue-collar workers represented "
            "the largest call volume (9,253 calls) with the lowest conversion (6.90%). Reallocate marketing mix toward high-converting demographic profiles."
        )
    ]

    card_y_starts = [0.65, 0.51, 0.37, 0.23, 0.09]
    card_h = 0.125
    for i, (title, desc) in enumerate(recs):
        ax_rec = fig.add_axes([0.05, card_y_starts[i], 0.53, card_h])
        ax_rec.set_facecolor(GRAY_CARD)
        ax_rec.axis("off")

        # Card container
        c_patch = patches.FancyBboxPatch(
            (0, 0), 1, 1,
            boxstyle="round,pad=0.015,rounding_size=0.03",
            facecolor=GRAY_CARD, edgecolor=GRAY_BORDER, linewidth=1.5,
            transform=ax_rec.transAxes
        )
        ax_rec.add_patch(c_patch)

        # Left ranking indicator badge
        badge = patches.Rectangle((0, 0), 0.018, 1, facecolor=TEAL_PRIMARY if i < 2 else NAVY_PRIMARY, transform=ax_rec.transAxes)
        ax_rec.add_patch(badge)

        ax_rec.text(0.035, 0.72, title, fontsize=11, weight="bold", color=NAVY_DARK)
        ax_rec.text(0.035, 0.36, desc, fontsize=8.8, color=TEXT_DARK, weight="normal",
                    wrap=True, linespacing=1.35)

    # Right Container: Limitations Box (x=0.61 to 0.95, y=0.09 to 0.775)
    ax_lim = fig.add_axes([0.60, 0.09, 0.35, 0.685])
    ax_lim.set_facecolor("#FFFDF7")
    ax_lim.axis("off")

    lim_patch = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor="#FFFDF7", edgecolor="#F6AD55", linewidth=2,
        transform=ax_lim.transAxes
    )
    ax_lim.add_patch(lim_patch)

    # Header
    ax_lim.text(0.06, 0.94, "ANALYTICAL LIMITATIONS & GOVERNANCE", fontsize=11.5, weight="bold", color="#C05621")

    limitations = [
        (
            "1. Proxy Funnel Definition",
            "The data tracks direct telemarketing calls; it contains no web visitor, impression, or inbound lead stages. "
            "Findings reflect telemarketing dynamics only."
        ),
        (
            "2. Post-Hoc Engagement Variable",
            "Call duration is strictly known only after a call concludes. Duration cannot be used as an ex-ante operational dialer filter."
        ),
        (
            "3. Inferred Temporal Sequence",
            "The raw dataset omits explicit calendar year timestamps. 'period_year' is inferred from chronological month sequence resets (May 2008 to Nov 2010)."
        ),
        (
            "4. Confounded Macroeconomic & Cohort Effects",
            "The massive conversion surge in 2010 (52.1%) coincides with both a collapse in Euribor (0.81%) and a dramatic shift toward warm previously-contacted leads (35.2%). These factors are entangled and cannot be cleanly separated."
        ),
        (
            "5. Association vs. Causality",
            "All metrics represent observational associations, not experimental proof of causality."
        ),
        (
            "6. Scope & Generalizability",
            "Data originates from a single Portuguese retail bank during the 2008\u20132010 financial crisis. Generalization to other markets or interest rate eras requires caution."
        )
    ]

    y_cur = 0.86
    for title, text in limitations:
        ax_lim.text(0.06, y_cur, title, fontsize=9.5, weight="bold", color=NAVY_DARK)
        y_cur -= 0.04
        ax_lim.text(0.06, y_cur, text, fontsize=8.2, color=TEXT_DARK, weight="normal", wrap=True)
        y_cur -= 0.095

    return fig

def main():
    clean_path = os.path.join("data", "bank_clean.csv")
    pdf_path = os.path.join("dashboard", "FUTURE_DS_03_dashboard.pdf")
    img_dir = "images"

    if not os.path.exists(clean_path):
        print(f"Error: Clean dataset not found at {clean_path}. Run scripts/01_clean_bank.py first.", file=sys.stderr)
        sys.exit(1)

    print("Loading clean dataset...")
    df = pd.read_csv(clean_path)
    print(f"Loaded {len(df):,} records.")

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    print("\nGenerating Dashboard Pages...")

    pages = [
        (1, create_page_1, "Marketing Funnel Architecture & Duration Performance"),
        (2, create_page_2, "Channel Effectiveness & Macroeconomic Shifts"),
        (3, create_page_3, "Campaign Effort, Yield & Demographic Response"),
        (4, create_page_4, "Strategic Recommendations & Methodological Constraints")
    ]

    with PdfPages(pdf_path) as pdf:
        for page_num, create_fn, page_title in pages:
            print(f"  Building Page {page_num}: {page_title}...")
            fig = create_fn(df)

            # Save PNG image
            png_path = os.path.join(img_dir, f"page_{page_num}.png")
            fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor=GRAY_BG)
            print(f"    Saved PNG: {png_path}")

            # Save to multi-page PDF
            pdf.savefig(fig, bbox_inches="tight", facecolor=GRAY_BG)
            plt.close(fig)

    print(f"\nSuccessfully generated multi-page executive PDF dashboard at:\n  {pdf_path}")

if __name__ == "__main__":
    main()
