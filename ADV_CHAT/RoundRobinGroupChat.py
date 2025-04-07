# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# **************************************             Round Robin Group Chat        ******************************************************* #
# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# Author: Miguel Mares
# Date: 4-3-2025
# Description: Multiy Agentic System, using scraped web data to glean social engineering as well as web weaknesses.
# **************************************************************************************************************************************** #

import multiprocessing
from multiprocessing import Process
multiprocessing.set_start_method('spawn', force=True)
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from azure.keyvault.secrets import SecretClient
from Tools.RAGEvaluator import RAGEvaluator
from azure.identity import DefaultAzureCredential
from autogen_core.memory import ListMemory
from scrapy.crawler import CrawlerProcess
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage
from autogen_core.model_context import BufferedChatCompletionContext
from azure.core.credentials import AzureKeyCredential
from Tools.Connectors import AzureSearchConnector
from Agents.SocialAgent import SocialAgent
from autogen_core import CancellationToken
from typing import List, Dict
from dotenv import load_dotenv
from pathlib import Path
import scrapy
import time
import json
import asyncio
import logging
import os

# Set logging level to ERROR
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('azure').setLevel(logging.ERROR)
logging.getLogger('autogen').setLevel(logging.ERROR)

# Load environment variables from .env file
load_dotenv()


# Replace with your Key Vault URL
key_vault_url = os.getenv("KEY_VAULT_URL")

# VARS
# ****************************** #
user_memory = ListMemory()
override_index_name = True

# SECRET CLIENT
# ****************************** #
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)


# KEYS, SECRETS
# ****************************** #
open_ai_endpoint = client.get_secret("mmgwoaiendpoint").value
open_ai_deployment = client.get_secret("mmgwaoaideployment").value
open_ai_key = client.get_secret("mmgwoaikey").value
open_ai_api = client.get_secret("mmgwoaiapi").value
blob_key = client.get_secret("mmgwblobkey").value
blob_connection_string = client.get_secret("mmgwblobconnection").value
azure_search = client.get_secret("mmgwaisname").value
azure_search_endpoint = client.get_secret("mmgwaisendpoint").value
azure_search_key = client.get_secret("mmgwaiskey").value
azure_search_config = client.get_secret("mmgwazuresearchconfig").value
server_name = client.get_secret("mmgwsqlserver").value
db_name = client.get_secret("mmgwsqldbname").value

# OVERRIDE INDEX NAME
# ****************************** #
if override_index_name:
    azure_search_index = "glitchy-web-index"
else:
    azure_search_index = client.get_secret("mmgwaisindex").value

# MODEL CLIENT
# ****************************** #
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=open_ai_deployment,
    model="gpt-3.5-turbo",
    api_version=open_ai_api,
    azure_endpoint=open_ai_endpoint,
    api_key=open_ai_key  # For key-based authentication.
)
# SEARCH CLIENT
# ****************************** #
search_client = SearchClient(
    endpoint=azure_search_endpoint,
    index_name=azure_search_index,
    credential=AzureKeyCredential(azure_search_key)
)

# WEBSCRAPER
# ****************************** #
class MySocialSpider(scrapy.Spider):
    name = "socialspider"
    start_urls = [os.getenv("GLITCHY_WEB")]  # Use the API endpoint

    def __init__(self):
        self.scraped_titles = []

    def parse(self, response):
        data = response.json()
        for blog in data:
            self.scraped_titles.append({"title": blog['title'] ,"author": blog['author'],"content": blog['content']})

    def closed(self, reason):
        with open('scraped_blogs.json', 'w') as f:
            json.dump(self.scraped_titles, f)


# HELPER FUNCTIONS
# ****************************** #
def scrape_blogs():
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'ERROR',  # Enable logging for debugging
        'CONCURRENT_REQUESTS': 50,  # Increase the number of concurrent requests
        'DOWNLOAD_TIMEOUT': 240,  # Increase the download timeout
        'RETRY_TIMES': 3,  # Retry failed requests up to 3 times
        'DOWNLOAD_DELAY': 0.25,  # Set the delay between requests to match server response time
    })
    process.crawl(MySocialSpider)
    process.start()

    try:
        with open('scraped_blogs.json', 'r') as file:
            blogs = json.load(file)
        formatted_titles = [{"title": blog['title'],"author": blog['author'],"content": blog['content'] } for blog in blogs]
        return formatted_titles if formatted_titles else []
    except FileNotFoundError:
        return []
        

async def upload_blogs():
    print("Scraping blog titles")
    scraped_data = scrape_blogs()

    # VECTOR, INDEX CLIENTS
    # ****************************** #
    az_index_client = AzureSearchConnector(search_client, azure_search_endpoint, azure_search_key, azure_search_index)
    await az_index_client.initializeIndex()
    az_index_client.upload_chunked_data(scraped_data, 600)



def get_retrieval_context(query: str) -> str:
    results = search_client.search(query,top=5)
    context_strings = []
    for result in results:
        context_strings.append(f"Document: {result['content']}")
    return "\n\n".join(context_strings) if context_strings else "No results found"

async def runAgents():

    social_agent = SocialAgent(search_client, model_client).initialize_agent()
    query = "Find information on an author that could be easily socially engineered, name that author, methods, why and how to prevent"

    # Send the augmented query as a user message
    start_time = time.time()
    response = await social_agent.on_messages(
        [TextMessage(content=query, source="user")],
        cancellation_token=CancellationToken(),
    )

    print(response.inner_messages)
    print(response.chat_message)




if __name__ == "__main__":
    # Run the tool to scrape blog titles
    asyncio.run(upload_blogs())

    # Start user interaction
    asyncio.run(runAgents())