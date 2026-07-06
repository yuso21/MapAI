import pandas as pd

from src import config
from src.geocoder import update_missing_coordinates
from src.map_generator import create_map


def save_error_log(errors: list[dict]) -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if errors:
        pd.DataFrame(errors).to_csv(config.ERROR_LOG_CSV, index=False, encoding="utf-8-sig")
    elif config.ERROR_LOG_CSV.exists():
        config.ERROR_LOG_CSV.unlink()


def main() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df, errors = update_missing_coordinates(config.INPUT_CSV)
    save_error_log(errors)
    create_map(df, config.MAP_OUTPUT_HTML)

    print(f"地図を作成しました: {config.MAP_OUTPUT_HTML}")
    if errors:
        print(f"取得できない住所がありました: {config.ERROR_LOG_CSV}")


if __name__ == "__main__":
    main()
