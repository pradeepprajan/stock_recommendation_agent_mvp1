import os
from dotenv import load_dotenv
from eventregistry import *
from langchain_core.tools import tool
load_dotenv()

@tool
def financial_news_tool(stock_name):

    """Function to fetch financial news from NewsAPI"""

    newsapi_api_key = os.getenv("NEWSAPI_API_KEY")
    try:
        er = EventRegistry(apiKey = newsapi_api_key)
        query = {
          "$query": {
            "$and": [
              {
                "keyword": stock_name,
                "keywordLoc": "title"
              },
              {
                "locationUri": "http://en.wikipedia.org/wiki/India"
              },
              {
                "lang": "eng"
              }
            ]
          },
          "$filter": {
            "forceMaxDataTimeWindow": "31"
          }
        }
        q = QueryArticlesIter.initWithComplexQuery(query)
        article_list = []
        # change maxItems to get the number of results that you want
        for i,article in enumerate(q.execQuery(er, maxItems=5)):
            title = article['title']
            body = article['body']
            article = '\n\n'.join([title,body])
            article_list.append(article)
    
        article_string = '\n\n\n'.join([f"**Article {i+1}**:\n\n{article}" for i,article in enumerate(article_list)])
    
        return article_string
    except Exception as e:
        print(f"NewsAPI API Error occurred: \n {e}")