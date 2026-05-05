"""
분석 3: 전압 상승 곡선 분석 모듈
Analysis 3: Voltage Rise Curve Analysis Module

이 모듈은 알루미늄과 흑연 전극의 전압 상승 곡선을 분석합니다.
This module analyzes voltage rise curves for aluminum and graphite electrodes.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path

from config import COLORS, FIGURES_DIR


def _aic(n, rss, k):
    """
    Akaike Information Criterion 계산
    Calculate Akaike Information Criterion

    Parameters:
    n (int): 데이터 포인트 수 / Number of data points
    rss (float): 잔차 제곱합 / Residual sum of squares
    k (int): 파라미터 수 / Number of parameters

    Returns:
    float: AIC 값 / AIC value
    """
    if rss <= 0:
        return np.inf
    return n * np.log(rss / n) + 2 * k


def _r_squared(y, y_fit):
    """
    결정계수 R² 계산
    Calculate coefficient of determination R²

    Parameters:
    y (array): 실제 값 / Actual values
    y_fit (array): 예측 값 / Predicted values

    Returns:
    float: R² 값 / R² value
    """
    ss_res = np.sum((y - y_fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0


def _fit_models(x, y):
    """
    다양한 모델을 데이터에 적합시키고 평가
    Fit various models to data and evaluate them

    Parameters:
    x (array): x 값들 / x values
    y (array): y 값들 / y values

    Returns:
    dict: 모델 결과들 / Model results
    """
    models = {}

    # 2차 다항식 / Quadratic polynomial
    try:
        coeffs2 = np.polyfit(x, y, 2)
        y_fit2 = np.polyval(coeffs2, x)
        rss2 = np.sum((y - y_fit2) ** 2)
        models["poly2"] = {
            "label": "2차 다항식 (Quadratic)",
            "params": coeffs2,
            "y_fit": y_fit2,
            "r2": _r_squared(y, y_fit2),
            "aic": _aic(len(y), rss2, 3),
            "predict": lambda xp, c=coeffs2: np.polyval(c, xp),
        }
    except Exception:
        pass

    # 3차 다항식 / Cubic polynomial
    if len(x) >= 5:
        try:
            coeffs3 = np.polyfit(x, y, 3)
            y_fit3 = np.polyval(coeffs3, x)
            rss3 = np.sum((y - y_fit3) ** 2)
            models["poly3"] = {
                "label": "3차 다항식 (Cubic)",
                "params": coeffs3,
                "y_fit": y_fit3,
                "r2": _r_squared(y, y_fit3),
                "aic": _aic(len(y), rss3, 4),
                "predict": lambda xp, c=coeffs3: np.polyval(c, xp),
            }
        except Exception:
            pass

    # 지수 성장 함수: a*(1-exp(-b*x))+c / Exponential growth function: a*(1-exp(-b*x))+c
    if len(x) >= 4:
        def exp_growth(xv, a, b, c):
            return a * (1 - np.exp(-b * xv)) + c

        try:
            p0 = [max(y) - min(y), 0.05, min(y)]
            popt, _ = curve_fit(exp_growth, x, y, p0=p0, maxfev=10000)
            y_fit_exp = exp_growth(x, *popt)
            rss_exp = np.sum((y - y_fit_exp) ** 2)
            models["exp_growth"] = {
                "label": "지수 성장 (Exponential Growth)",
                "params": popt,
                "y_fit": y_fit_exp,
                "r2": _r_squared(y, y_fit_exp),
                "aic": _aic(len(y), rss_exp, 3),
                "predict": lambda xp, p=popt: exp_growth(xp, *p),
            }
        except Exception:
            pass

    return models


def _plot_voltage_curve(df, df_anomaly, electrode_label, color, fname):
    """
    전압 곡선 플롯팅 및 모델 적합
    Plot voltage curve and fit models

    Parameters:
    df (DataFrame): 정상 데이터 / Normal data
    df_anomaly (DataFrame): 이상치 데이터 / Anomaly data
    electrode_label (str): 전극 라벨 / Electrode label
    color (str): 색상 / Color
    fname (str): 파일명 / Filename

    Returns:
    dict: 모델 결과들 / Model results
    """
    x_normal = df["elapsed_hours"].values
    y_normal = df["voltage_mV"].values

    models = _fit_models(x_normal, y_normal)
    if not models:
        return {}

    best_key = min(models, key=lambda k: models[k]["aic"])
    best = models[best_key]

    fig, ax = plt.subplots(figsize=(10, 6))

    # 적합 곡선 + 신뢰 구간 / Fitted curve + confidence interval
    x_fine = np.linspace(x_normal.min(), x_normal.max(), 300)
    y_fine = best["predict"](x_fine)
    ax.plot(x_fine, y_fine, color=color, linewidth=2,
            label=f"최적 모델: {best['label']}\nR²={best['r2']:.3f}, AIC={best['aic']:.2f}")

    # 정상 데이터 점 / Normal data points
    ax.scatter(x_normal, y_normal, color=color, s=80, zorder=5, edgecolors="white", linewidths=1, label="측정값")

    # 이상치 점 / Anomaly points
    if df_anomaly is not None and len(df_anomaly) > 0:
        ax.scatter(df_anomaly["elapsed_hours"], df_anomaly["voltage_mV"],
                   color=COLORS["anomaly"], s=100, zorder=6, marker="X",
                   edgecolors="white", linewidths=1, label="이상치 (Anomaly)")

    # 각 점에 레이블 추가 / Add labels to each point
    all_pts = df if df_anomaly is None else pd.concat([df, df_anomaly])
    for _, row in all_pts.iterrows():
        exp_short = row["experiment_id"].split("_")[-1] + f"-{int(row['replicate'])}"
        c = COLORS["anomaly"] if row.get("is_anomaly", False) else "black"
        ax.annotate(exp_short, (row["elapsed_hours"], row["voltage_mV"]),
                    textcoords="offset points", xytext=(5, 5), fontsize=8, color=c)

    ax.set_xlabel("경과 시간 (시간, Hours)")
    ax.set_ylabel("전압 (mV)")
    ax.set_title(f"{electrode_label} 전극 전압 상승 곡선 분석\n(Voltage Rise Curve Analysis)")
    ax.legend(loc="upper right")

    # Model comparison table
    model_rows = [(v["label"], f"{v['r2']:.3f}", f"{v['aic']:.2f}") for v in models.values()]
    model_rows.sort(key=lambda r: float(r[2]))
    best_flag = ["★ 최적" if r[0] == best["label"] else "" for r in model_rows]
    table_text = "\n".join([f"  {r[0]}: R²={r[1]}, AIC={r[2]} {f}" for r, f in zip(model_rows, best_flag)])
    ax.text(0.02, 0.98, f"모델 비교:\n{table_text}", transform=ax.transAxes,
            verticalalignment="top", fontsize=8,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / fname)
    plt.close()
    print(f"  → Saved: {fname}")

    return {k: {"label": v["label"], "r2": v["r2"], "aic": v["aic"]} for k, v in models.items()}


def analyze_voltage_curves(df_al, df_c, df_al_clean):
    """
    전압 상승 곡선 분석 메인 함수
    Main function for voltage rise curve analysis

    Parameters:
    df_al (DataFrame): 알루미늄 데이터 / Aluminum data
    df_c (DataFrame): 흑연 데이터 / Graphite data
    df_al_clean (DataFrame): 정제된 알루미늄 데이터 / Cleaned aluminum data

    Returns:
    dict: 모델 결과들 / Model results
    """
    print("\n=== Analysis 3: Voltage Rise Curve Analysis ===")

    df_al_anomaly = df_al[df_al["is_anomaly"]].copy()

    al_models = _plot_voltage_curve(df_al_clean, df_al_anomaly, "알루미늄 (Aluminum)",
                                    COLORS["aluminum"], "04_voltage_curve_al.png")
    c_models = _plot_voltage_curve(df_c, None, "흑연 (Graphite)",
                                   COLORS["graphite"], "05_voltage_curve_c.png")

    # Combined time-series
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot Al (with anomaly distinction)
    ax.plot(df_al_clean["elapsed_hours"], df_al_clean["voltage_mV"],
            "o-", color=COLORS["aluminum"], linewidth=2, markersize=7, label="알루미늄 전극")
    if len(df_al_anomaly) > 0:
        ax.scatter(df_al_anomaly["elapsed_hours"], df_al_anomaly["voltage_mV"],
                   color=COLORS["anomaly"], s=100, marker="X", zorder=6, label="이상치 (Al)")

    # 보조 x축에 흑연 플롯: offset이 있는 트윈 축 사용 / Twin axis for graphite plot
    ax2 = ax.twiny()
    ax2.plot(df_c["elapsed_hours"], df_c["voltage_mV"],
             "s-", color=COLORS["graphite"], linewidth=2, markersize=7, label="흑연 전극")
    ax2.set_xlabel("흑연 전극 경과 시간 (시간)", color=COLORS["graphite"])
    ax2.tick_params(axis="x", labelcolor=COLORS["graphite"])

    ax.set_xlabel("알루미늄 전극 경과 시간 (시간)", color=COLORS["aluminum"])
    ax.set_ylabel("전압 (mV)")
    ax.set_title("알루미늄 vs 흑연 전극 전압 시계열 비교\n(Voltage Time-Series)")
    ax.tick_params(axis="x", labelcolor=COLORS["aluminum"])

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "06_voltage_timeseries_combined.png")
    plt.close()
    print("  → Saved: 06_voltage_timeseries_combined.png")

    return {"aluminum": al_models, "graphite": c_models}