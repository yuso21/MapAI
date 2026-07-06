import time
from typing import Any, Optional, Tuple

import pandas as pd
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import ArcGIS, Nominatim

from src import config


def ensure_coordinate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add latitude/longitude columns when the CSV does not have them yet."""
    for column in [config.LATITUDE_COLUMN, config.LONGITUDE_COLUMN]:
        if column not in df.columns:
            df[column] = pd.NA
    return df


def has_coordinates(row: pd.Series) -> bool:
    lat = pd.to_numeric(row.get(config.LATITUDE_COLUMN), errors="coerce")
    lon = pd.to_numeric(row.get(config.LONGITUDE_COLUMN), errors="coerce")
    return pd.notna(lat) and pd.notna(lon)


def create_geocoders() -> list[tuple[str, object]]:
    geocoders: list[tuple[str, object]] = []
    for provider in config.GEOCODER_PROVIDERS:
        if provider == "nominatim":
            geocoders.append(
                (
                    provider,
                    Nominatim(
                        user_agent=config.GEOCODER_USER_AGENT,
                        timeout=config.GEOCODER_TIMEOUT,
                    ),
                )
            )
        elif provider == "arcgis":
            geocoders.append((provider, ArcGIS(timeout=config.GEOCODER_TIMEOUT)))
    return geocoders


def run_geocode(provider: str, geolocator: object, address: str):
    if provider == "nominatim":
        return geolocator.geocode(address, country_codes="jp")
    return geolocator.geocode(address)


def address_queries(address: str) -> list[str]:
    address_text = str(address).strip()
    queries = [address_text]
    if "日本" not in address_text:
        queries.append(f"{address_text}, 日本")
    return queries


def geocode_address(
    geocoders: list[tuple[str, object]],
    address: str,
) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Return latitude, longitude, and an error message if geocoding fails."""
    if not address or pd.isna(address):
        return None, None, "住所が空です"

    last_error = None
    for provider, geolocator in geocoders:
        for query in address_queries(address):
            try:
                location = run_geocode(provider, geolocator, query)
            except (GeocoderTimedOut, GeocoderServiceError) as exc:
                last_error = f"{provider}: {exc}"
                continue
            except Exception as exc:
                last_error = f"{provider}: {exc}"
                continue

            if location is not None:
                return float(location.latitude), float(location.longitude), None

    if last_error:
        return None, None, f"ジオコーディングエラー: {last_error}"
    return None, None, "住所から座標を取得できませんでした"


def find_name_column(df: pd.DataFrame) -> str:
    for column in config.NAME_COLUMNS:
        if column in df.columns:
            return column
    raise ValueError(f"施設名の列が見つかりません。候補: {', '.join(config.NAME_COLUMNS)}")


def fill_missing_coordinates(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]], bool]:
    """
    Fill missing coordinates in a dataframe.

    Existing coordinates are kept as-is so later runs do not call the geocoder
    again for already resolved rows.
    """
    df = df.copy()
    df = ensure_coordinate_columns(df)
    name_column = find_name_column(df)
    geocoders = create_geocoders()
    errors: list[dict[str, Any]] = []
    updated = False

    for index, row in df.iterrows():
        if has_coordinates(row):
            continue

        address = row.get(config.ADDRESS_COLUMN)
        latitude, longitude, error = geocode_address(geocoders, address)

        if error:
            errors.append(
                {
                    "行番号": index + 2,
                    "施設名": row.get(name_column, ""),
                    "住所": address,
                    "エラー": error,
                }
            )
            time.sleep(config.GEOCODER_DELAY_SECONDS)
            continue

        df.at[index, config.LATITUDE_COLUMN] = latitude
        df.at[index, config.LONGITUDE_COLUMN] = longitude
        updated = True
        time.sleep(config.GEOCODER_DELAY_SECONDS)

    return df, errors, updated


def update_missing_coordinates(csv_path=config.INPUT_CSV) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """
    Fill missing coordinates in the CSV and save updates back to the file.
    """
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df, errors, updated = fill_missing_coordinates(df)

    if updated:
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return df, errors
