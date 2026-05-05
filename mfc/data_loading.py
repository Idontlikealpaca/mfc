"""
Data Loading Module
데이터 로딩 및 전처리 함수들
"""

import pandas as pd
from config import DATA_DIR


def load_and_preprocess():
    """데이터 로딩 및 기본 전처리"""
    df_al = pd.read_csv(DATA_DIR / "al_mfc_data.csv")
    df_c = pd.read_csv(DATA_DIR / "c_mfc_data.csv")

    for df, label in [(df_al, "aluminum"), (df_c, "graphite")]:
        df["electrode_type"] = label
        df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])

    df_all = pd.concat([df_al, df_c], ignore_index=True).sort_values("datetime")

    # 각 그룹의 첫 측정에서 경과한 시간 계산
    for label, df in [("aluminum", df_al), ("graphite", df_c)]:
        t0 = df["datetime"].min()
        df["elapsed_hours"] = (df["datetime"] - t0).dt.total_seconds() / 3600

    df_al_clean = df_al[~df_al["is_anomaly"]].copy()

    return df_al, df_c, df_all, df_al_clean