from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_CSV = DATA_DIR / "omiya_high_school_tennis_mapai_with_tuition.csv"
MAP_OUTPUT_HTML = OUTPUT_DIR / "school_map.html"
ERROR_LOG_CSV = OUTPUT_DIR / "error_log.csv"

# Columns can be changed when reusing this project for shops, hospitals,
# sales targets, or other facilities.
NAME_COLUMNS = [
    "学校名",
    "ラーメン屋",
    "店舗名",
    "店名",
    "飲食店名",
    "施設名",
    "名称",
    "名前",
    "表示名",
    "正式名称",
    "会社名",
    "法人名",
    "顧客名",
    "取引先名",
    "拠点名",
]
CATEGORY_COLUMN = "区分"
VALUE_COLUMN = "偏差値"
ADDRESS_COLUMN = "住所"
LATITUDE_COLUMN = "緯度"
LONGITUDE_COLUMN = "経度"

CATEGORY_COLORS = {
    "公立": "blue",
    "私立": "red",
}
DEFAULT_MARKER_COLOR = "green"

MAP_CENTER_QUERY = "大宮駅, 埼玉県さいたま市, 日本"
DEFAULT_CENTER = [35.9063, 139.6239]
DEFAULT_ZOOM = 12

GEOCODER_USER_AGENT = "map-generator-csv-openstreetmap"
GEOCODER_TIMEOUT = 10
GEOCODER_DELAY_SECONDS = 1.1
GEOCODER_PROVIDERS = ["nominatim", "arcgis"]
