from .news_scraper import fetch_news
from .ai_service import generate_notes
from .models import CurrentAffair

url = "https://www.thehindu.com/news/national/"

article_text = fetch_news(url)

notes = generate_notes(article_text)

CurrentAffair.objects.create(
    title="Daily Current Affairs",
    content=notes,
    sector="General"
)