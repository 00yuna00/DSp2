import sqlite3
import flet as ft
import requests

# SQLite DBの初期化
def initialize_db():
    conn = sqlite3.connect("jma.db")
    cursor = conn.cursor()

    # 地域情報のテーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT
        )
    """)

    # 天気情報のテーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT,
            date TEXT,
            weather TEXT,
            FOREIGN KEY (area_code) REFERENCES areas(area_code)
        )
    """)
    conn.commit()
    conn.close()

# 地域リストをDBに格納
def store_areas_to_db(area_data):
    areas = area_data["class10s"]

    conn = sqlite3.connect("jma.db")
    cursor = conn.cursor()

    for area_code, area in areas.items():
        cursor.execute(
            "INSERT OR IGNORE INTO areas (area_code, area_name) VALUES (?, ?)",
            (area_code, area["name"])
        )

    conn.commit()
    conn.close()

# 天気データをDBに格納
def store_forecasts_to_db(area_code, weather_data):
    forecasts = weather_data[0]["timeSeries"][0]["areas"][0]["weathers"]

    conn = sqlite3.connect("jma.db")
    cursor = conn.cursor()

    for i, forecast in enumerate(forecasts[:7]):
        date = f"2024-11-{i + 1:02}"
        cursor.execute(
            "INSERT INTO forecasts (area_code, date, weather) VALUES (?, ?, ?)",
            (area_code, date, forecast)
        )

    conn.commit()
    conn.close()

# DBから天気データを取得
def get_forecasts_from_db(area_code):
    conn = sqlite3.connect("jma.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, weather FROM forecasts WHERE area_code = ? ORDER BY date ASC",
        (area_code,)
    )
    forecasts = cursor.fetchall()
    conn.close()
    return forecasts


def get_area_list():
    """気象庁のAPIから地域リストを取得"""
    url = "http://www.jma.go.jp/bosai/common/const/area.json"
    response = requests.get(url)
    return response.json()

def get_weather_data(area_code):
    """指定された地域コードの天気予報を取得"""
    url = f"http://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    response = requests.get(url)
    return response.json()

def main(page: ft.Page):
    initialize_db()

    # 地域リストの取得とDB格納
    area_data = get_area_list()
    store_areas_to_db(area_data)

    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    ft.Text("☀️", style="titleLarge", color="white"),
                    ft.Text("天気予報", style="titleMedium", color="white"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            alignment=ft.alignment.center_left,
            height=60,
            bgcolor=ft.colors.BLUE_700,  
        )
    )

    regions = area_data["class10s"]
    
    # 地域選択用のドロップダウン
    selected_region = ft.Ref[ft.Dropdown]()
    weather_display = ft.Ref[ft.Column]()

    def fetch_weather(e):
        region_code = selected_region.current.value
        if region_code:
            # 天気情報を取得してDBに格納
            weather_data = get_weather_data(region_code)
            store_forecasts_to_db(region_code, weather_data)

            # DBから天気情報を取得して表示
            forecasts = get_forecasts_from_db(region_code)

            weather_display.current.controls.clear()
            for date, weather in forecasts:
                weather_display.current.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(date, style="bodyMedium"),
                                ft.Text(weather, style="bodyMedium"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=5,
                        ),
                        width=120,
                        height=120,
                        bgcolor="white",  
                        padding=ft.padding.all(10),
                        border_radius=10,
                    )
                )
            page.update()

    dropdown_items = [
        ft.dropdown.Option(region_code, region["name"])
        for region_code, region in regions.items()
    ]
    region_dropdown = ft.Dropdown(
        options=dropdown_items,
        ref=selected_region,
        label="地域を選択",
        on_change=fetch_weather,
        bgcolor=ft.colors.BLUE_500,  
    )

    weather_display = ft.Column(
        [],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True,
    )

    page.add(
        ft.Row(
            [
                ft.NavigationRail(
                    selected_index=0,
                    min_width=100,
                    min_extended_width=200,
                    bgcolor=ft.colors.BLUE_300,
                    destinations=[
                        ft.NavigationRailDestination(
                            icon=ft.icons.LIST, label="地域選択"
                        ),
                    ],
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column([region_dropdown, weather_display], expand=True),
                    bgcolor=ft.colors.BLUE_100, 
                    expand=True,
                ),
            ],
            expand=True,
        )
    )

ft.app(main)
