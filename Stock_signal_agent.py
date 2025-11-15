#!/usr/bin/env python
# coding: utf-8

# # MVP 1 - User Interface using Pythonic code


from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
import pandas as pd
import requests
from eventregistry import *
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import smtplib
from email.message import EmailMessage
import ast
from datetime import date



load_dotenv()


@tool
def stock_prices_tool(stock_name):

    """Function to fetch stock prices from Alpha Vantage"""

    alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')

    #url = "https://" + f"www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name.re}&apikey={alpha_vantage_api_key}"
    #print(url) 

    try:
        #url_stock_name = stock_name.replace(" ","%20")
        url = "https://" + f"www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name.replace(' ','%20')}&apikey={alpha_vantage_api_key}"
        print(url) 
        r = requests.get(url)
        data = r.json()
    except Exception as e:
        print(f"Alpha Vantage API Error occurred: \n {e}")
        
    try:
        stock_ticker = ''
        for match in data['bestMatches']:
            if 'BSE' in match['1. symbol']:
               stock_ticker = match['1. symbol']
        
        if stock_ticker == '':
            raise ValueError('Stock not found in BSE')
    except Exception as e:
        raise TypeError(data)

    try:
        url = "https://" + f"www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock_ticker}&apikey={alpha_vantage_api_key}"
        r = requests.get(url)
        data = r.json()
    except Exception as e:
        print(f"Alpha Vantage API Error occurred: \n {e}")
    
    #print(len(data['Time Series (Daily)']))
    
    stock_prices_json = data['Time Series (Daily)']

    stock_prices_df = pd.DataFrame(stock_prices_json).T
    stock_prices_df.rename(columns={'1. open':'open','2. high':'high','3. low':'low','4. close':'close','5. volume':'volume'},inplace=True)
    stock_prices_df.reset_index(inplace=True)
    stock_prices_df.rename(columns={'index':'date'},inplace=True)

    stock_prices_mkd = stock_prices_df.to_markdown(index=False)

    return stock_prices_mkd


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
            #print(f'Article {i+1}')
            #print(article['title'])
            #print(article['body'])
            title = article['title']
            body = article['body']
            article = '\n\n'.join([title,body])
            article_list.append(article)
    
        article_string = '\n\n\n'.join([f"**Article {i+1}**:\n\n{article}" for i,article in enumerate(article_list)])
    
        return article_string
    except Exception as e:
        print(f"NewsAPI API Error occurred: \n {e}")


def send_email(output):
    try:
        with smtplib.SMTP('smtp.hostinger.com', 587) as s:
            s.starttls()
            email_password = os.getenv("EMAIL_PASSWORD")
            s.login("pradeep@agileai.in",email_password)
            today = date.today()
            formatted_date = today.strftime("%d-%b-%Y")
            message = EmailMessage()
            message['Subject'] = f'BSE Stock trading signals on {formatted_date}'
            message['From'] = "pradeep@agileai.in"
            message['To'] = "pradeepprajan@agileapps.in"
            message.set_content(output)
            s.send_message(message)
            s.quit()
    except Exception as e:
        print(f"An error occurred while sending email: {e}")


def stock_recommendation_agent_mvp1():
    #stock_name = input("Enter the stock that you want to get buy or sell recommendation")
    
    #alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    #newsapi_api_key = os.getenv("NEWSAPI_API_KEY")
    openai_endpoint = os.getenv("OPENAI_API_ENDPOINT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_deployment = os.getenv("OPENAI_API_DEPLOYMENT")
    openai_version = os.getenv("OPENAI_API_VERSION")

    llm = AzureChatOpenAI(
            openai_api_version='2025-01-01-preview',
            azure_endpoint='https://agileapps-azure-openai.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview',
            openai_api_key=openai_api_key
    )

    # Getting a random list of blue chip stocks in BSE
    messages = [
    {"role": "system", "content": """Can you recommend some good blue chip stocks in BSE? Return the output as a JSON object with the expected format below.
    **Expected format**: 
    {
    "blue_chip_stocks": ['Tata Motors','Axis Bank','ICICI Bank']
    }"""}
    ]

    #stock_name = "Axis Bank"
    #alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    #url = "https://" + f"www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={alpha_vantage_api_key}"
    #print(url)

    blue_chip_stock_list = []
    try:
        output = llm.invoke(messages)
    
        start_index = output.content.index('{')
        end_index = output.content.index('}')
        
        blue_chip_stock_list = ast.literal_eval(output.content[start_index:end_index+1])['blue_chip_stocks']
    except Exception as e:
        raise TypeError(f"Error occured while fetching list of blue chip stocks: {e}")

    ai_msg_content = "Here are some stock trading recommendations for today: \n\n"
    for stock_name in blue_chip_stock_list[:1]:
        print(f"Stock name: {stock_name}")
    
        messages = [
        {"role": "system", "content": """You are a financial advisor capable to 
        recommending stocks to buy or sell. Your task is to fetch five articles and last 100 days stock prices regarding {stock_name} using the tools 
        and analyze the articles to predict whether the stock prices of {stock_name} will move in a bullish or 
        bearish manner and give recommendation on whether to buy or sell stock."""},
        MessagesPlaceholder("agent_scratchpad")
        ]
        
        prompt = ChatPromptTemplate.from_messages(messages)
    
        tools = [stock_prices_tool,financial_news_tool]
    
        llm_with_tools = llm.bind_tools(tools)
        
        agent = create_tool_calling_agent(llm_with_tools, tools, prompt)
    
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        ai_msg = agent_executor.invoke({"stock_name":stock_name})

        ai_msg_content_article = ai_msg['output']

        ai_msg_content_article = stock_name + ":" + "\n\n" + ai_msg_content_article

        ai_msg_content += ai_msg_content_article
        ai_msg_content += "\n\n\n"
        
    send_email(ai_msg_content)
    

if __name__ == "__main__":
    print("Running stock recommender agent")
    alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    stock_recommendation_agent_mvp1()




