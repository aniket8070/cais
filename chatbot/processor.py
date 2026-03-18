from .article_splitter import split_articles
from .sector_detector import detect_sector
from .ai_service import generate_sector_notes

def process_newspaper(text):

    articles = split_articles(text)

    results = []

    for article in articles:

        sector = detect_sector(article)

        notes = generate_sector_notes(article)

        results.append({
            "sector": sector,
            "notes": notes
        })

    return results