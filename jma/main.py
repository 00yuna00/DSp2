import flet as ft
import requests

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

    # 地域リストの取得
    area_data = get_area_list()
    regions = area_data["class10s"]  # 地域データ

    # 地域選択用のドロップダウン
    selected_region = ft.Ref[ft.Dropdown]()
    weather_display = ft.Ref[ft.Column]()

    def fetch_weather(e):
        """選択した地域の天気情報を取得して表示"""
        region_code = selected_region.current.value
        if region_code:
            weather_data = get_weather_data(region_code)
            forecasts = weather_data[0]["timeSeries"][0]["areas"][0]["weathers"]

            # 画面に天気情報を表示
            weather_display.current.controls.clear()

            for i, forecast in enumerate(forecasts[:7]):  
                # 各日付の天気情報を四角に入れて表示
                weather_display.current.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"2024-11-{i + 1:02}", style="bodyMedium"),  
                                ft.Text(forecast, style="bodyMedium"),  
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

    # 地域リストをドロップダウンに変換
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

    # 天気情報表示
    weather_display = ft.Column(
        [
            ft.Row(
                [ft.Container(width=100, height=100, bgcolor="white", padding=ft.padding.all(10)) for _ in range(1)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [ft.Container(width=100, height=100, bgcolor="white", padding=ft.padding.all(10)) for _ in range(3)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                [ft.Container(width=100, height=100, bgcolor="white", padding=ft.padding.all(10)) for _ in range(3)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=20,
        expand=True,
    )

    # メインUI
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
