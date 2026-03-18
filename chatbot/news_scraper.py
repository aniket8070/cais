from newspaper import Article

def fetch_news(url):

    article = Article(url)

    article.download()

    article.parse()

    return article.text