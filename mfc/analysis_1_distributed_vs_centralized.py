"""
분석 1: 분산형 vs 중앙집중식 시스템 비교 모듈
Analysis 1: Distributed vs Centralized System Comparison Module

이 모듈은 MFC 기반 분산형 폐수 처리 시스템과
기존 중앙집중식 활성슬러지 공법을 에너지·비용 측면에서 비교합니다.
This module compares distributed MFC-based wastewater treatment systems
with conventional centralized activated sludge processes in terms of energy and cost.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import COLORS, FIGURES_DIR


def analyze_distributed_vs_centralized(df_c):
    """
    분산형 vs 중앙집중식 시스템 비교 분석 메인 함수
    Main function for distributed vs centralized system comparison analysis

    Parameters:
    df_c (DataFrame): 흑연 데이터 / Graphite data

    Returns:
    dict: 비교 분석 결과 / Comparison analysis results
    """
    print("\n=== Analysis 1: Distributed vs Centralized System ===")

    peak_power_uW = df_c["power_uW"].max()  # 셀당 최대 전력
    peak_voltage_mV = df_c["voltage_mV"].max()
    mean_power_uW = df_c["power_uW"].mean()

    # 스케일업 가정
    cell_volume_L = 0.5  # 셀당 유효 부피
    household_wastewater_L_per_day = 200.0
    cells_per_unit = household_wastewater_L_per_day / cell_volume_L  # 400개 셀

    # 가구당 일별 에너지 회수 (평균 전력 기준)
    energy_recovery_uWh = mean_power_uW * 24  # μWh/셀/일
    total_energy_Wh_per_day = energy_recovery_uWh * cells_per_unit / 1e6  # μWh를 Wh로 변환
    total_energy_kWh_per_day = total_energy_Wh_per_day / 1000

    # 중앙집중식 기준 (문헌: 활성슬러지 0.3–0.6 kWh/m³)
    centralized_energy_kWh_per_m3 = 0.45  # 중간값
    household_volume_m3 = household_wastewater_L_per_day / 1000
    centralized_energy_kWh = centralized_energy_kWh_per_m3 * household_volume_m3

    # MFC 에너지 투입 (펌핑만, 폭기 없음) 약 0.05 kWh/m³
    mfc_energy_input_kWh_per_m3 = 0.05
    mfc_energy_input_kWh = mfc_energy_input_kWh_per_m3 * household_volume_m3

    net_energy_balance = total_energy_kWh_per_day - mfc_energy_input_kWh

    print(f"  Peak power per cell:      {peak_power_uW:.1f} μW")
    print(f"  Mean power per cell:      {mean_power_uW:.1f} μW")
    print(f"  Cells per household unit: {cells_per_unit:.0f}")
    print(f"  Est. energy recovery:     {total_energy_kWh_per_day*1000:.4f} Wh/day")
    print(f"  Centralized energy need:  {centralized_energy_kWh*1000:.1f} Wh/day")
    print(f"  Net energy balance (MFC): {net_energy_balance*1000:.4f} Wh/day")

    comparison_data = {
        "항목 (Parameter)": [
            "에너지 투입량 (kWh/m³)",
            "에너지 회수 가능량 (kWh/m³)",
            "순 에너지 수지 (kWh/m³)",
            "인프라 규모",
            "초기 설치 비용",
            "유지보수 복잡성",
            "확장성",
            "CO₂ 발자국",
            "원격 지역 적용성",
            "슬러지 처리 부담",
        ],
        "분산형 MFC": [
            f"{mfc_energy_input_kWh_per_m3:.2f}",
            f"{total_energy_kWh_per_day/household_volume_m3*1000:.4f} (현재 실험 규모)",
            "현재 소규모 단계",
            "소형 모듈형",
            "낮음 (모듈 단위)",
            "낮음 (단순 구조)",
            "높음 (점진적 확장)",
            "낮음",
            "매우 높음",
            "낮음 (자체 분해)",
        ],
        "중앙집중식 (활성슬러지)": [
            f"{centralized_energy_kWh_per_m3:.2f}",
            "0 (에너지 소비만)",
            f"-{centralized_energy_kWh_per_m3:.2f}",
            "대형 고정 시설",
            "매우 높음",
            "높음 (전문 인력)",
            "낮음 (대규모 투자)",
            "높음",
            "낮음",
            "높음 (별도 처리 필요)",
        ],
    }
    df_comp = pd.DataFrame(comparison_data)

    # 그림
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 왼쪽: 에너지 막대 차트
    ax = axes[0]
    categories = ["에너지 투입\n(kWh/m³)", "에너지 회수\n(Wh/m³, 실험 기준)"]
    mfc_vals = [mfc_energy_input_kWh_per_m3, total_energy_kWh_per_day / household_volume_m3 * 1000]
    cent_vals = [centralized_energy_kWh_per_m3, 0]

    x = np.arange(len(categories))
    w = 0.35
    b1 = ax.bar(x - w / 2, mfc_vals, w, label="분산형 MFC", color=COLORS["graphite"], alpha=0.85)
    b2 = ax.bar(x + w / 2, cent_vals, w, label="중앙집중식", color=COLORS["aluminum"], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("에너지 (단위별 상이)")
    ax.set_title("에너지 투입·회수 비교\n(Distributed vs Centralized)")
    ax.legend()
    ax.bar_label(b1, fmt="%.3f", padding=3, fontsize=9)
    ax.bar_label(b2, fmt="%.2f", padding=3, fontsize=9)

    # 오른쪽: 정성 비교 표
    ax2 = axes[1]
    ax2.axis("off")
    qual_items = [
        ("인프라 규모", "소형 모듈형", "대형 고정 시설"),
        ("초기 설치 비용", "낮음", "매우 높음"),
        ("확장성", "높음 (점진적)", "낮음 (대규모 투자)"),
        ("CO₂ 발자국", "낮음", "높음"),
        ("원격 지역 적용성", "매우 높음", "낮음"),
        ("에너지 회수", "가능", "불가능"),
        ("슬러지 처리 부담", "낮음", "높음"),
    ]
    col_labels = ["항목", "분산형 MFC", "중앙집중식"]
    cell_text = [[r[0], r[1], r[2]] for r in qual_items]
    table = ax2.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.6)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#2C3E50")
            cell.set_text_props(color="white", fontweight="bold")
        elif col == 1:
            cell.set_facecolor("#D5E8D4")
        elif col == 2:
            cell.set_facecolor("#F8CECC")
    ax2.set_title("정성적 비교 (Qualitative Comparison)", pad=20)

    plt.suptitle("분산형 MFC vs 중앙집중식 폐수 처리 시스템 비교", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_distributed_vs_centralized.png")
    plt.close()
    print("  → Saved: 01_distributed_vs_centralized.png")

    return {
        "peak_power_uW": peak_power_uW,
        "mean_power_uW": mean_power_uW,
        "centralized_energy_kWh_per_m3": centralized_energy_kWh_per_m3,
        "mfc_energy_input_kWh_per_m3": mfc_energy_input_kWh_per_m3,
        "cells_per_unit": cells_per_unit,
        "total_energy_kWh_per_day": total_energy_kWh_per_day,
    }
