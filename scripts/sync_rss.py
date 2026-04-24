import feedparser
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

RSS_URL = os.environ.get("RSS_URL")
OUTPUT_FILE = "assets/data/news.json"
MAX_ITEMS = 15  # сколько последних новостей хранить

def parse_feed():
    if not RSS_URL:
        raise ValueError("Переменная окружения RSS_URL не задана")
    
    logging.info(f"Загрузка {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    if feed.bozo:
        logging.warning(f"Возможные ошибки парсинга: {feed.bozo_exception}")

    items = []
    for entry in feed.entries:
        # Безопасное извлечение даты
        pub_date = entry.get("published") or entry.get("updated", "")
        try:
            # feedparser возвращает struct_time, приводим к ISO8601 для сортировки
            dt = datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None
            iso_date = dt.isoformat() if dt else ""
        except Exception:
            iso_date = ""

        items.append({
            "title": entry.get("title", "Без заголовка"),
            "link": entry.get("link", "#"),
            "published": pub_date,
            "published_iso": iso_date,
            "summary": entry.get("summary", "")[:300] + "..."  # обрезаем длинные описания
        })

    # Сортируем по дате (если есть), берем последние
    items.sort(key=lambda x: x["published_iso"] or "0000-01-01T00:00:00", reverse=True)
    return items[:MAX_ITEMS]

def save_json(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Сохранено {len(data)} записей в {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        news = parse_feed()
        save_json(news)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        exit(1)