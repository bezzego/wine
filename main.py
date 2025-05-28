import pandas as pd
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader
import argparse


def format_years(n):
    if 11 <= n % 100 <= 14:
        return "лет"
    elif n % 10 == 1:
        return "год"
    elif 2 <= n % 10 <= 4:
        return "года"
    else:
        return "лет"


def main():
    parser = argparse.ArgumentParser(
        description="Генерация страницы и запуск HTTP-сервера"
    )
    parser.add_argument(
        "-d", "--data-path", help="Путь к Excel-файлу с данными", required=True
    )
    args = parser.parse_args()
    data_path = args.data_path

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")
    winery_age = datetime.now().year - 1920

    df = pd.read_excel(data_path, na_values=["", "NaN"], keep_default_na=False)
    df["Категория"] = df["Категория"].fillna("")
    df["Картинка"] = df["Картинка"].str.strip()

    wines_by_category = defaultdict(list)
    for _, row in df.iterrows():
        item = row.to_dict()
        item = {k: ("" if pd.isna(v) else v) for k, v in item.items()}
        wines_by_category[item["Категория"]].append(
            {
                "name": item["Название"],
                "grape": item["Сорт"],
                "price": item["Цена"],
                "image": item["Картинка"],
                "promo": item.get("Акция", ""),
            }
        )

    rendered_page = template.render(
        winery_age=winery_age,
        winery_age_suffix=format_years(winery_age),
        wines_by_category=wines_by_category,
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(rendered_page)

    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
