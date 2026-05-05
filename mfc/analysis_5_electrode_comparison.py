"""
분석 5: 전극 효율성 비교 모듈
Analysis 5: Electrode Efficiency Comparison Module

이 모듈은 알루미늄과 흑연 전극의 효율성을 통계적으로 비교하고,
막대 차트와 산점도를 통해 시각화합니다.
This module statistically compares the efficiency of aluminum and graphite electrodes,
and visualizes them through bar charts and scatter plots.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import COLORS, FIGURES_DIR


def analyze_electrode_comparison(df_al, df_c, df_al_clean, energy_results):
    """
    전극 효율성 비교 분석 메인 함수
    Main function for electrode efficiency comparison analysis

    Parameters:
    df_al (DataFrame): 알루미늄 데이터 / Aluminum data
    df_c (DataFrame): 흑연 데이터 / Graphite data
    df_al_clean (DataFrame): 정제된 알루미늄 데이터 / Cleaned aluminum data
    energy_results (dict): 에너지 분석 결과 / Energy analysis results

    Returns:
    dict: 비교 분석 결과 / Comparison analysis results
    """
    print("\n=== Analysis 5: Electrode Efficiency Comparison ===")

    def stats_summary(df):
        """
        데이터프레임의 통계 요약 계산
        Calculate statistical summary of dataframe
        """
        v = df["voltage_mV"].dropna()
        p = df["power_uW"].dropna()
        r = df["resistance_ohm"].dropna()
        return {
            "mean_v": v.mean(), "max_v": v.max(), "min_v": v.min(), "std_v": v.std(),
            "mean_p": p.mean(), "max_p": p.max(), "std_p": p.std(),
            "mean_r": r.mean(), "max_r": r.max(),
        }

    al_stats = stats_summary(df_al_clean)
    c_stats = stats_summary(df_c)

    voltage_ratio = c_stats["max_v"] / al_stats["max_v"] if al_stats["max_v"] > 0 else np.nan
    power_ratio = c_stats["max_p"] / al_stats["max_p"] if al_stats["max_p"] > 0 else np.nan
    energy_ratio = (energy_results["graphite"]["energy_Wh"] /
                    energy_results["aluminum"]["energy_Wh"]) if energy_results["aluminum"]["energy_Wh"] > 0 else np.nan

    print(f"  Al  – mean V={al_stats['mean_v']:.1f} mV, max V={al_stats['max_v']:.1f} mV, "
          f"max P={al_stats['max_p']:.2f} μW")
    print(f"  C   – mean V={c_stats['mean_v']:.1f} mV, max V={c_stats['max_v']:.1f} mV, "
          f"max P={c_stats['max_p']:.2f} μW")
    print(f"  Ratios – V: {voltage_ratio:.2f}x, P: {power_ratio:.2f}x, Energy: {energy_ratio:.2f}x")

    # 2×2 막대차트 / 2×2 bar charts
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    metrics = [
        ("평균 전압 (mV)", al_stats["mean_v"], c_stats["mean_v"], None, axes[0, 0]),
        ("최대 전압 (mV)", al_stats["max_v"], c_stats["max_v"], None, axes[0, 1]),
        ("평균 전력 (μW)", al_stats["mean_p"], c_stats["mean_p"], "log", axes[1, 0]),
        ("최대 전력 (μW)", al_stats["max_p"], c_stats["max_p"], "log", axes[1, 1]),
    ]
    for title, al_val, c_val, scale, ax in metrics:
        bars = ax.bar(["알루미늄", "흑연"], [al_val, c_val],
                      color=[COLORS["aluminum"], COLORS["graphite"]], alpha=0.85, width=0.5)
        if scale == "log":
            ax.set_yscale("log")
        ax.set_title(title)
        ax.set_ylabel(title.split("(")[1].rstrip(")"))
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
        ratio = c_val / al_val if al_val > 0 else np.nan
        if not np.isnan(ratio):
            ax.text(0.98, 0.95, f"흑연/알루미늄 = {ratio:.1f}x",
                    transform=ax.transAxes, ha="right", va="top", fontsize=9,
                    bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.suptitle("알루미늄 vs 흑연 전극 효율성 비교", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "09_electrode_comparison_bars.png")
    plt.close()
    print("  → Saved: 09_electrode_comparison_bars.png")

    # 저항 vs 전압 산점도 / Resistance vs voltage scatter plot
    fig, ax = plt.subplots(figsize=(9, 6))
    for df, label, marker, color in [
        (df_al_clean, "알루미늄 전극", "o", COLORS["aluminum"]),
        (df_c, "흑연 전극", "s", COLORS["graphite"]),
    ]:
        sub = df.dropna(subset=["resistance_ohm", "voltage_mV"])
        ax.scatter(sub["resistance_ohm"], sub["voltage_mV"], color=color, marker=marker,
                   s=90, zorder=5, edgecolors="white", linewidths=0.8, label=label)
        if len(sub) >= 2:
            m, b = np.polyfit(sub["resistance_ohm"], sub["voltage_mV"], 1)
            x_lr = np.linspace(sub["resistance_ohm"].min(), sub["resistance_ohm"].max(), 100)
            ax.plot(x_lr, m * x_lr + b, color=color, linewidth=1.5, linestyle="--", alpha=0.7)

    ax.set_xlabel("내부저항 (Ω)")
    ax.set_ylabel("전압 (mV)")
    ax.set_title("내부저항 vs 전압 관계 (Resistance – Voltage)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "10_resistance_voltage_scatter.png")
    plt.close()
    print("  → Saved: 10_resistance_voltage_scatter.png")

    return {
        "al": al_stats, "c": c_stats,
        "voltage_ratio": voltage_ratio,
        "power_ratio": power_ratio,
        "energy_ratio": energy_ratio,
    }