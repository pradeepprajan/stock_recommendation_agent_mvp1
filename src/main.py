from llm.llm_client import llm_client as llm
from eventregistry import *
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools.stock_prices_tool import stock_prices_tool
from tools.financial_news_tool import financial_news_tool
from email.send_email import send_email
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import ast

def stock_recommendation_agent_mvp1():


    # Getting a random list of blue chip stocks in BSE
    messages = [
    {"role": "system", "content": """You are a financial advisor capable of recommending stocks to buy or sell."""},
    {"role": "user", "content": """Can you recommend some good blue chip stocks in BSE? Return the output as a JSON object with the expected format below.
    **Expected format**: 
    {
    "blue_chip_stocks": ['Tata Motors','Axis Bank','ICICI Bank']
    }"""}
    ]

    blue_chip_stock_list = []
    try:
        output = llm.invoke(messages)
    
        start_index = output.content.index('{')
        end_index = output.content.index('}')
        
        blue_chip_stock_list = ast.literal_eval(output.content[start_index:end_index+1])['blue_chip_stocks']
    except Exception as e:
        raise TypeError(f"Error occured while fetching list of blue chip stocks: {e}")

    ai_msg_content = "Here are some stock trading recommendations for today: \n\n"
    for stock_name in blue_chip_stock_list:
        print(f"Stock name: {stock_name}")
    
        messages = [
        {"role": "system", "content": """You are a financial advisor capable of recommending stocks to buy or sell."""},
        {"role": "user", "content" : """Your task is to fetch five articles and last 100 days stock prices regarding {stock_name} using the tools 
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
    try:
        stock_recommendation_agent_mvp1()
    except Exception as e:
        print(f"Error occured during execution: {e}")




