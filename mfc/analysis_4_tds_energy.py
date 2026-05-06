"""
분석 4: TDS-전압 상관관계 및 총 에너지 분석 모듈

이 모듈은 TDS와 전압 사이의 상관관계를 분석하고,
사다리꼴 적분법을 사용하여 총 발전량을 계산한다
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from config import COLORS, FIGURES_DIR


def analyze_tds_voltage_and_energy(df_al, df_c):
    """
    TDS-전압 상관관계 및 총 에너지 분석 메인 함수

    Parameters:
    df_al (DataFrame): 알루미늄 데이터 
    df_c (DataFrame): 흑연 데이터 

    Returns:
    tuple: (상관관계 결과, 에너지 결과) / (correlation results, energy results)
    """
    print("\n분석 4: TDS-전압 상관관계 + 총 전력")

    # ── TDS-전압 상관관계 ── 
    # 흑연: TDS와 전압이 모두 있는 행 
    c_tds = df_c.dropna(subset=["tds_ppm", "voltage_mV"])[["tds_ppm", "voltage_mV", "elapsed_hours"]].copy()
    # 알루미늄: 유효 행 (이상치 제외) 
    al_tds = df_al[~df_al["is_anomaly"]].dropna(subset=["tds_ppm", "voltage_mV"])[
        ["tds_ppm", "voltage_mV", "elapsed_hours"]].copy()

    corr_results = {}
    for label, sub in [("graphite", c_tds), ("aluminum", al_tds)]:
        if len(sub) >= 3:
            r_p, p_p = stats.pearsonr(sub["tds_ppm"], sub["voltage_mV"])
            r_s, p_s = stats.spearmanr(sub["tds_ppm"], sub["voltage_mV"])
        elif len(sub) == 2:
            r_p, p_p = stats.pearsonr(sub["tds_ppm"], sub["voltage_mV"])
            r_s, p_s = r_p, p_p
        else:
            r_p = p_p = r_s = p_s = np.nan
        corr_results[label] = {"pearson_r": r_p, "pearson_p": p_p,
                               "spearman_r": r_s, "spearman_p": p_s, "n": len(sub)}
        print(f"  TDS-Voltage [{label}] n={len(sub)}: "
              f"Pearson r={r_p:.3f} (p={p_p:.4f}), Spearman r={r_s:.3f} (p={p_s:.4f})")

    # TDS-전압 산점도 
    fig, ax = plt.subplots(figsize=(9, 6))
    for color, label, sub, marker in [
        (COLORS["graphite"], "흑연 전극", c_tds, "s"),
        (COLORS["aluminum"], "알루미늄 전극", al_tds, "o"),
    ]:
        if len(sub) == 0:
            continue
        ax.scatter(sub["tds_ppm"], sub["voltage_mV"], color=color, marker=marker,
                   s=90, zorder=5, edgecolors="white", linewidths=0.8, label=label)
        if len(sub) >= 2:
            m, b = np.polyfit(sub["tds_ppm"], sub["voltage_mV"], 1)
            x_lr = np.linspace(sub["tds_ppm"].min(), sub["tds_ppm"].max(), 100)
            ax.plot(x_lr, m * x_lr + b, color=color, linewidth=1.5, linestyle="--", alpha=0.7)
        cr = corr_results.get(label.split()[0].lower(), {})
        if label == "흑연 전극" and corr_results["graphite"]["n"] >= 2:
            cr = corr_results["graphite"]
            ax.annotate(
                f"Pearson r={cr['pearson_r']:.3f} (n={cr['n']})",
                xy=(0.62, 0.12), xycoords="axes fraction", fontsize=10,
                color=COLORS["graphite"],
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

    ax.set_xlabel("TDS (ppm)")
    ax.set_ylabel("전압 (mV)")
    ax.set_title("TDS vs 전압 산점도\n(TDS – Voltage Scatter Plot)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "07_tds_voltage_scatter.png")
    plt.close()
    print("  → Saved: 07_tds_voltage_scatter.png")

    # 사다리꼴 적분법을 이용한 총 에너지 
    def total_energy(df, group_label):
        # df를 elapsed_hours 기준으로 정렬 
        df_sorted = df.sort_values("elapsed_hours").copy()
        t_h = df_sorted["elapsed_hours"].values
        p_uW = df_sorted["power_uW"].fillna(0).values
        p_W = p_uW * 1e-6
        # trapz: t가 초인 경우 ∫P dt = J, 이후 /3600 → Wh
        energy_J = np.trapezoid(p_W, t_h * 3600)
        energy_Wh = energy_J / 3600
        duration_h = t_h[-1] - t_h[0]
        mean_p_uW = np.trapezoid(p_uW, t_h) / duration_h if duration_h > 0 else np.mean(p_uW)
        print(f"  Total energy [{group_label}]: {energy_Wh*1000:.4f} mWh "
              f"({energy_Wh*1e6:.2f} μWh) over {duration_h:.1f} h "
              f"| mean power {mean_p_uW:.1f} μW")
        return energy_Wh, duration_h, t_h, p_uW

    e_c, dur_c, t_c, p_c = total_energy(df_c, "graphite")
    e_al, dur_al, t_al, p_al = total_energy(df_al[~df_al["is_anomaly"]], "aluminum")

    # 전력 적분 그림 
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 흑연: 전력 대 시간 
    axes[0, 0].fill_between(t_c, p_c, alpha=0.3, color=COLORS["graphite"])
    axes[0, 0].plot(t_c, p_c, "s-", color=COLORS["graphite"], linewidth=2, markersize=7)
    axes[0, 0].set_xlabel("경과 시간 (h)")
    axes[0, 0].set_ylabel("전력 (μW)")
    axes[0, 0].set_title("흑연 전극 전력 시계열")

    # 흑연: 누적 발전량 
    cumulative_c = np.array([
        np.trapezoid(p_c[:i+1] * 1e-6, t_c[:i+1] * 3600) / 3600 * 1e6
        for i in range(len(t_c))
    ])
    axes[0, 1].plot(t_c, cumulative_c, "s-", color=COLORS["graphite"], linewidth=2, markersize=7)
    axes[0, 1].fill_between(t_c, cumulative_c, alpha=0.2, color=COLORS["graphite"])
    axes[0, 1].set_xlabel("경과 시간 (h)")
    axes[0, 1].set_ylabel("누적 발전량 (μWh)")
    axes[0, 1].set_title(f"흑연 전극 누적 발전량\n총 {e_c*1e6:.1f} μWh ({e_c*1000:.4f} mWh)")

    # 알루미늄: 전력 대 시간 
    axes[1, 0].fill_between(t_al, p_al, alpha=0.3, color=COLORS["aluminum"])
    axes[1, 0].plot(t_al, p_al, "o-", color=COLORS["aluminum"], linewidth=2, markersize=7)
    axes[1, 0].set_xlabel("경과 시간 (h)")
    axes[1, 0].set_ylabel("전력 (μW)")
    axes[1, 0].set_title("알루미늄 전극 전력 시계열")

    # 알루미늄: 누적 발전량 
    cumulative_al = np.array([
        np.trapezoid(p_al[:i+1] * 1e-6, t_al[:i+1] * 3600) / 3600 * 1e6
        for i in range(len(t_al))
    ])
    axes[1, 1].plot(t_al, cumulative_al, "o-", color=COLORS["aluminum"], linewidth=2, markersize=7)
    axes[1, 1].fill_between(t_al, cumulative_al, alpha=0.2, color=COLORS["aluminum"])
    axes[1, 1].set_xlabel("경과 시간 (h)")
    axes[1, 1].set_ylabel("누적 발전량 (μWh)")
    axes[1, 1].set_title(f"알루미늄 전극 누적 발전량\n총 {e_al*1e6:.2f} μWh ({e_al*1000:.4f} mWh)")

    plt.suptitle("전력 시계열 및 누적 발전량 (사다리꼴 적분법)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "08_power_integration.png")
    plt.close()
    print("  → Saved: 08_power_integration.png")

    energy_results = {
        "graphite": {"energy_Wh": e_c, "duration_h": dur_c},
        "aluminum": {"energy_Wh": e_al, "duration_h": dur_al},
    }
    return corr_results, energy_results