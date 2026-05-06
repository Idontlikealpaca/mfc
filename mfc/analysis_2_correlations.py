"""
통계적 상관관계 분석
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from config import COLORS, FIGURES_DIR


def _pearson_pval_matrix(df_sub):
    cols = df_sub.columns.tolist()
    n = len(cols)
    pmat = pd.DataFrame(np.nan, index=cols, columns=cols)
    for col_x, c1 in enumerate(cols):
        for col_y, c2 in enumerate(cols):
            if col_x == col_y:
                pmat.loc[c1, c2] = 0.0
            else:
                valid = df_sub[[c1, c2]].dropna()
                if len(valid) >= 3:
                    _, p = stats.pearsonr(valid[c1], valid[c2])
                    pmat.loc[c1, c2] = p
    return pmat


def _sig_stars(p):
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def _plot_correlation_heatmap(corr_mat, pval_mat, title, fname):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, (mat, method) in zip(axes, [(corr_mat, "Pearson"), (None, "Spearman")]):
        if method == "Spearman":
            # 두 번째 축에는 이미 corr_mat이 클로저로 전달됨
            pass

    # Pearson 상관계수
    ax0 = axes[0]
    annot_p = corr_mat.copy().astype(str)
    for col_x in corr_mat.index:
        for col_y in corr_mat.columns:
            val = corr_mat.loc[col_x, col_y]
            star = _sig_stars(pval_mat.loc[col_x, col_y]) if col_x != col_y else ""
            annot_p.loc[col_x, col_y] = f"{val:.2f}{star}" if not pd.isna(val) else "N/A"

    mask_p = corr_mat.isna()
    sns.heatmap(
        corr_mat, ax=ax0, annot=annot_p, fmt="", cmap="RdYlGn", vmin=-1, vmax=1,
        linewidths=0.5, mask=mask_p, cbar_kws={"shrink": 0.8},
    )
    ax0.set_title(f"Pearson 상관행렬\n(* p<0.05, ** p<0.01, *** p<0.001)")

    return fig, axes


def analyze_correlations(df_al, df_c, df_al_clean):
    print("\n=== Analysis 2: Statistical Correlations ===")

    numeric_cols = ["voltage_mV", "current_uA", "resistance_ohm", "power_uW",
                    "ec_uS_cm", "tds_ppm", "temp_C"]
    col_labels = {
        "voltage_mV": "전압(mV)", "current_uA": "전류(μA)", "resistance_ohm": "저항(Ω)",
        "power_uW": "전력(μW)", "ec_uS_cm": "EC(μS/cm)", "tds_ppm": "TDS(ppm)", "temp_C": "온도(°C)",
    }

    results = {}

    for label, df, fname_suffix in [
        ("알루미늄 전극 (Al)", df_al, "al"),
        ("흑연 전극 (C)", df_c, "c"),
    ]:
        sub = df[numeric_cols].rename(columns=col_labels)
        sub_valid_cols = [c for c in sub.columns if sub[c].notna().sum() >= 3]
        sub = sub[sub_valid_cols]

        pearson_mat = sub.corr(method="pearson")
        spearman_mat = sub.corr(method="spearman")
        pval_mat = _pearson_pval_matrix(sub)

        # Pearson 및 Spearman 히트맵 모두 플롯
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        for ax, (mat, method) in zip(axes, [(pearson_mat, "Pearson"), (spearman_mat, "Spearman")]):
            pv = pval_mat if method == "Pearson" else pd.DataFrame(np.nan, index=mat.index, columns=mat.columns)
            annot = mat.copy().astype(str)
            for col_x in mat.index:
                for col_y in mat.columns:
                    val = mat.loc[col_x, col_y]
                    star = _sig_stars(pv.loc[col_x, col_y]) if col_X != col_y and method == "Pearson" else ""
                    annot.loc[col_X, col_y] = f"{val:.2f}{star}" if not pd.isna(val) else "N/A"

            sns.heatmap(
                mat, ax=ax, annot=annot, fmt="", cmap="RdYlGn", vmin=-1, vmax=1,
                linewidths=0.5, cbar_kws={"shrink": 0.8},
            )
            star_note = "\n(* p<0.05, ** p<0.01, *** p<0.001)" if method == "Pearson" else ""
            ax.set_title(f"{method} 상관행렬{star_note}")

        plt.suptitle(f"{label} - 상관행렬", fontsize=13, fontweight="bold")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / f"02_correlation_matrix_{fname_suffix}.png")
        plt.close()
        print(f"  → Saved: 02_correlation_matrix_{fname_suffix}.png")

        results[fname_suffix] = {
            "pearson": pearson_mat,
            "spearman": spearman_mat,
            "pval": pval_mat,
        }

    # Mann-Whitney U: voltage and power (Al clean vs graphite)
    al_v = df_al_clean["voltage_mV"].dropna().values
    c_v = df_c["voltage_mV"].dropna().values
    al_p = df_al_clean["power_uW"].dropna().values
    c_p = df_c["power_uW"].dropna().values

    u_v, p_v = stats.mannwhitneyu(al_v, c_v, alternative="two-sided")
    u_p, p_p = stats.mannwhitneyu(al_p, c_p, alternative="two-sided")
    r_v = 1 - 2 * u_v / (len(al_v) * len(c_v))
    r_p = 1 - 2 * u_p / (len(al_p) * len(c_p))

    print(f"  Mann-Whitney Voltage: U={u_v:.1f}, p={p_v:.4f}, r={r_v:.3f}")
    print(f"  Mann-Whitney Power:   U={u_p:.1f}, p={p_p:.4f}, r={r_p:.3f}")

    # 박스플롯
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (metric, al_data, c_data, unit, ylabel, ylog) in zip(
        axes,
        [
            ("전압 (Voltage)", al_v, c_v, "mV", "전압 (mV)", False),
            ("전력 (Power)", al_p, c_p, "μW", "전력 (μW)", True),
        ],
    ):
        plot_df = pd.DataFrame(
            {"값": np.concatenate([al_data, c_data]),
             "전극 재료": ["알루미늄"] * len(al_data) + ["흑연"] * len(c_data)}
        )
        palette = {"알루미늄": COLORS["aluminum"], "흑연": COLORS["graphite"]}
        sns.boxplot(data=plot_df, x="전극 재료", y="값", ax=ax, palette=palette, width=0.5)
        sns.stripplot(data=plot_df, x="전극 재료", y="값", ax=ax,
                      palette=palette, size=7, jitter=True, alpha=0.8, edgecolor="white", linewidth=0.5)
        if ylog:
            ax.set_yscale("log")
        ax.set_ylabel(ylabel)
        ax.set_title(f"{metric} 분포 비교")

    u_results = [
        ("전압", u_v, p_v, r_v, len(al_v), len(c_v)),
        ("전력", u_p, p_p, r_p, len(al_p), len(c_p)),
    ]
    stat_text = "\n".join(
        [f"{m}: U={u:.1f}, p={p:.4f} {'*' if p<0.05 else 'ns'}, r={r:.3f} (n₁={n1}, n₂={n2})"
         for m, u, p, r, n1, n2 in u_results]
    )
    plt.figtext(0.5, -0.04, f"Mann-Whitney U 검정\n{stat_text}", ha="center", fontsize=9,
                bbox=dict(boxstyle="round", facecolor="#EAF2FB", alpha=0.8))
    plt.suptitle("알루미늄 vs 흑연 전극 분포 비교 (Mann-Whitney U Test)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "03_mann_whitney_boxplot.png")
    plt.close()
    print("  → Saved: 03_mann_whitney_boxplot.png")

    results["mann_whitney"] = {
        "voltage": {"U": u_v, "p": p_v, "r": r_v},
        "power": {"U": u_p, "p": p_p, "r": r_p},
    }
    return results