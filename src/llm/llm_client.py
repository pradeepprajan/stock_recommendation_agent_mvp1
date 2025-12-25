from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

openai_endpoint = os.getenv("OPENAI_API_ENDPOINT")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_deployment = os.getenv("OPENAI_API_DEPLOYMENT")
openai_version = os.getenv("OPENAI_API_VERSION")

def llm_client():
    llm = AzureChatOpenAI(
    openai_api_version=openai_version,
    azure_endpoint=openai_endpoint,
    openai_api_key=openai_api_key
    )
    return llm

