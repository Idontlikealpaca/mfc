"""
메인 실행 파일

이 파일은 모든 분석 모듈을 임포트하고 순차적으로 실행한다
"""

from pathlib import Path

from config import FIGURES_DIR
from data_loading import load_and_preprocess
from analysis_1_distributed_vs_centralized import analyze_distributed_vs_centralized
from analysis_2_correlations import analyze_correlations
from analysis_3_voltage_curves import analyze_voltage_curves
from analysis_4_tds_energy import analyze_tds_voltage_and_energy
from analysis_5_electrode_comparison import analyze_electrode_comparison
from report_generation import generate_report


def main():
    """
    메인 분석 실행 함수
    Main analysis execution function
    """
    print("MFC Wastewater Treatment Analysis")
    print("=" * 50)

    df_al, df_c, df_all, df_al_clean = load_and_preprocess()
    print(f"  Loaded Al: {len(df_al)} rows, C: {len(df_c)} rows")

    logistics = analyze_distributed_vs_centralized(df_c)
    corr_results = analyze_correlations(df_al, df_c, df_al_clean)
    fit_results = analyze_voltage_curves(df_al, df_c, df_al_clean)
    tds_corr, energy_results = analyze_tds_voltage_and_energy(df_al, df_c)
    comparison = analyze_electrode_comparison(df_al, df_c, df_al_clean, energy_results)

    all_results = {
        "logistics": logistics,
        "correlations": corr_results,
        "fitting": fit_results,
        "tds_corr": tds_corr,
        "energy": energy_results,
        "comparison": comparison,
    }
    generate_report(all_results)

    print("\n" + "=" * 50)
    print("Analysis complete.")
    print(f"  Figures: {FIGURES_DIR}/ ({len(list(FIGURES_DIR.glob('*.png')))} PNG files)")
    print("  Report:  report.md")


if __name__ == "__main__":
    main()