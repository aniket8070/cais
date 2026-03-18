import re

def split_articles(text):

    articles = re.split(r'\n\n+', text)

    clean_articles = []

    for article in articles:

        if len(article) > 200:
            clean_articles.append(article)

    return clean_articles