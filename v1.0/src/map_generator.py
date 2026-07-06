import html

import folium
import pandas as pd
from geopy.geocoders import ArcGIS, Nominatim

from src import config
from src.geocoder import find_name_column


def get_map_center() -> list[float]:
    """Use Nishikawaguchi Station as the initial map center."""
    geolocator = Nominatim(
        user_agent=f"{config.GEOCODER_USER_AGENT}-center",
        timeout=config.GEOCODER_TIMEOUT,
    )
    try:
        location = geolocator.geocode(config.MAP_CENTER_QUERY, country_codes="jp")
    except Exception:
        location = None

    if location is None:
        try:
            location = ArcGIS(timeout=config.GEOCODER_TIMEOUT).geocode(config.MAP_CENTER_QUERY)
        except Exception:
            location = None

    if location is None:
        return config.DEFAULT_CENTER

    return [float(location.latitude), float(location.longitude)]


def marker_color(category: str) -> str:
    return config.CATEGORY_COLORS.get(str(category), config.DEFAULT_MARKER_COLOR)


def build_popup(row: pd.Series, name_column: str) -> folium.Popup:
    value = row.get(config.VALUE_COLUMN, "")
    popup_html = f"""
    <strong>{html.escape(str(row.get(name_column, "")))}</strong><br>
    区分: {html.escape(str(row.get(config.CATEGORY_COLUMN, "")))}<br>
    偏差値: {html.escape(str(value))}<br>
    住所: {html.escape(str(row.get(config.ADDRESS_COLUMN, "")))}
    """
    return folium.Popup(popup_html, max_width=320)


def valid_coordinate_rows(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result[config.LATITUDE_COLUMN] = pd.to_numeric(result[config.LATITUDE_COLUMN], errors="coerce")
    result[config.LONGITUDE_COLUMN] = pd.to_numeric(result[config.LONGITUDE_COLUMN], errors="coerce")
    return result.dropna(subset=[config.LATITUDE_COLUMN, config.LONGITUDE_COLUMN])


def build_map(df: pd.DataFrame) -> folium.Map:
    name_column = find_name_column(df)
    m = folium.Map(
        location=get_map_center(),
        zoom_start=config.DEFAULT_ZOOM,
        tiles="OpenStreetMap",
    )

    marker_rows = valid_coordinate_rows(df)
    bounds: list[list[float]] = []

    for _, row in marker_rows.iterrows():
        latitude = float(row[config.LATITUDE_COLUMN])
        longitude = float(row[config.LONGITUDE_COLUMN])
        bounds.append([latitude, longitude])

        folium.Marker(
            location=[latitude, longitude],
            popup=build_popup(row, name_column),
            tooltip=str(row.get(name_column, "")),
            icon=folium.Icon(
                color=marker_color(row.get(config.CATEGORY_COLUMN, "")),
                icon="info-sign",
            ),
        ).add_to(m)

    if bounds:
        m.fit_bounds(bounds, padding=(30, 30))

    return m


def create_map(df: pd.DataFrame, output_path=config.MAP_OUTPUT_HTML) -> None:
    m = build_map(df)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    m.save(output_path)
