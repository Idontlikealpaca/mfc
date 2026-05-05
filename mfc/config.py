"""
MFC Analysis Configuration
공통 설정 및 상수들
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 디렉토리 설정
FIGURES_DIR = Path("figures")
DATA_DIR = Path("data")
FIGURES_DIR.mkdir(exist_ok=True)

# 색상 설정
COLORS = {
    "aluminum": "#4472C4",
    "graphite": "#404040",
    "anomaly": "#E74C3C",
    "highlight": "#F39C12",
}

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트를 설정하고 matplotlib에 적용"""
    # 시스템에 설치된 한글 폰트 찾기
    korean_fonts = [
        'NanumGothic', 'NanumGothic-Regular', 'Nanum Gothic',
        'Malgun Gothic', 'Gulim', 'Dotum', 'Batang',
        'AppleGothic', 'AppleMyungjo',
        'DejaVu Sans'  # fallback
    ]

    # NanumGothic.ttf 직접 경로 확인
    nanum_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic-Regular.ttf",
        "/usr/share/fonts/TTF/NanumGothic.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
        "/Library/Fonts/NanumGothic.ttf"  # macOS alternative
    ]

    selected_font = 'DejaVu Sans'  # 기본 fallback

    # 직접 경로에서 폰트 찾기
    for font_path in nanum_paths:
        if Path(font_path).exists():
            try:
                # 폰트 매니저에 추가
                fm.fontManager.addfont(font_path)
                # 폰트 이름 추출 (경로에서)
                font_name = Path(font_path).stem
                if 'Nanum' in font_name:
                    selected_font = 'NanumGothic'
                    break
            except Exception:
                continue

    # 설치된 폰트 중에서 한글 폰트 찾기
    if selected_font == 'DejaVu Sans':
        for font_name in korean_fonts[:-1]:  # 마지막은 DejaVu Sans (fallback)
            try:
                # matplotlib의 폰트 매니저에서 찾기
                if font_name in [f.name for f in fm.fontManager.ttflist]:
                    selected_font = font_name
                    break
            except Exception:
                continue

    return selected_font

# 한글 폰트 설정 적용
_korean_font = setup_korean_font()

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