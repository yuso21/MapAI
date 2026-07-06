from io import BytesIO

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src import config
from src.geocoder import fill_missing_coordinates
from src.map_generator import build_map, valid_coordinate_rows


st.set_page_config(
    page_title="MapAI",
    page_icon="M",
    layout="wide",
)


def read_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file, encoding="utf-8-sig")


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="map_data", index=False)
    return output.getvalue()


def render_summary(df: pd.DataFrame, error_count: int) -> None:
    mapped_count = len(valid_coordinate_rows(df))
    total_count = len(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("件数", f"{total_count}")
    col2.metric("地図表示", f"{mapped_count}")
    col3.metric("未取得", f"{error_count}")


def render_downloads(df: pd.DataFrame, map_html: str) -> None:
    col1, col2, col3 = st.columns(3)
    col1.download_button(
        "地図HTML",
        data=map_html.encode("utf-8"),
        file_name="map.html",
        mime="text/html",
        key="download_map_html",
        on_click="ignore",
        use_container_width=True,
    )
    col2.download_button(
        "座標入りCSV",
        data=dataframe_to_csv_bytes(df),
        file_name="map_data.csv",
        mime="text/csv",
        key="download_map_csv",
        on_click="ignore",
        use_container_width=True,
    )
    col3.download_button(
        "Excel",
        data=dataframe_to_excel_bytes(df),
        file_name="map_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_map_excel",
        on_click="ignore",
        use_container_width=True,
    )


def display_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    hidden_columns = [config.LATITUDE_COLUMN, config.LONGITUDE_COLUMN]
    return df.drop(columns=hidden_columns, errors="ignore")


def render_app() -> None:
    st.title("MapAI")
    st.caption("CSVから住所を読み取り、地図HTMLと座標入りデータを作成します。")

    uploaded_file = st.file_uploader("CSVファイル", type=["csv"])
    use_sample = st.toggle("サンプルCSVを使う", value=uploaded_file is None)

    if uploaded_file is None and not use_sample:
        st.info("CSVをアップロードしてください。")
        return

    try:
        if uploaded_file is not None:
            df = read_csv(uploaded_file)
        else:
            df = pd.read_csv(config.INPUT_CSV, encoding="utf-8-sig")
    except Exception as exc:
        st.error(f"CSVを読み込めませんでした: {exc}")
        return

    st.subheader("データ確認")
    st.dataframe(display_dataframe(df), use_container_width=True, hide_index=True)

    with st.expander("必要な列"):
        st.write(
            f"名称列: {', '.join(config.NAME_COLUMNS)} のいずれか / "
            f"住所列: {config.ADDRESS_COLUMN} / "
            f"緯度列: {config.LATITUDE_COLUMN} / "
            f"経度列: {config.LONGITUDE_COLUMN}"
        )

    if st.button("地図を作成", type="primary", use_container_width=True):
        with st.spinner("住所を確認して地図を作成しています..."):
            try:
                result_df, errors, _ = fill_missing_coordinates(df)
                folium_map = build_map(result_df)
                map_html = folium_map.get_root().render()
            except Exception as exc:
                st.error(f"地図を作成できませんでした: {exc}")
                return

        st.session_state["result_df"] = result_df
        st.session_state["errors"] = errors
        st.session_state["map_html"] = map_html

    if "map_html" not in st.session_state:
        return

    result_df = st.session_state["result_df"]
    errors = st.session_state["errors"]
    map_html = st.session_state["map_html"]

    st.subheader("地図")
    render_summary(result_df, len(errors))
    components.html(map_html, height=650, scrolling=False)
    render_downloads(result_df, map_html)

    if errors:
        st.subheader("住所を取得できなかった行")
        error_df = pd.DataFrame(errors)
        st.dataframe(error_df, use_container_width=True, hide_index=True)
        st.download_button(
            "エラー一覧CSV",
            data=dataframe_to_csv_bytes(error_df),
            file_name="error_log.csv",
            mime="text/csv",
            key="download_error_csv",
            on_click="ignore",
            use_container_width=True,
        )


if __name__ == "__main__":
    render_app()
