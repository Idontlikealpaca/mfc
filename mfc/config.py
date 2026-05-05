"""
공통 설정 및 상수들
"""

from pathlib import Path
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"
FIGURES_DIR = BASE_DIR / "figures"
DATA_DIR = BASE_DIR / "data"
FONT_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 색상 설정
COLORS = {
    "aluminum": "#4472C4",
    "graphite": "#404040",
    "anomaly": "#E74C3C",
    "highlight": "#F39C12",
}

# 한글 폰트 설정

NANUM_GOTHIC_PATH = Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf")
_korean_font = "DejaVu Sans"
if NANUM_GOTHIC_PATH.exists():
    try:
        fm.fontManager.addfont(str(NANUM_GOTHIC_PATH))
        _korean_font = "NanumGothic"
    except Exception:
        _korean_font = "DejaVu Sans"

plt.rcParams["font.family"] = _korean_font
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# Matplotlib 기본 설정
plt.rcParams.update(
    {
        "font.family": [_korean_font, 'DejaVu Sans'],  # 폰트 fallback 설정
        "axes.unicode_minus": False,  # 마이너스 기호 제대로 표시
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "legend.fontsize": 10,
        "mathtext.fontset": "dejavusans",  # 수식 폰트
        "font.sans-serif": [_korean_font, 'DejaVu Sans', 'Arial'],
    }
)

# 폰트 캐시 강제 리프레시 (선택사항)
try:
    fm._load_fontmanager(try_read_cache=False)
except Exception:
    pass