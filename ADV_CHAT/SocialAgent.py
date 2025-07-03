# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# **************************************             Social Agent                ******************************************************* #
# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# Author: Miguel Mares
# Date: 2-17-2025
# Description: Web crawler that is pointing specifically to the GlitchyWeb API Blogs page. Can be run from the command line to scrape
#              website and output social engineering insights gleaned from scraped data
# **************************************************************************************************************************************** #


import scrapy
import multiprocessing
from Tools.RAGEvaluator import RAGEvaluator
from Tools.Connectors import AgentDataConnector
from Tools.Connectors import AzureBlobConnector
from Tools.Connectors import AzureSearchConnector
multiprocessing.set_start_method('spawn', force=True)
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from azure.identity import DefaultAzureCredential , ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.model_context import BufferedChatCompletionContext
from azure.core.credentials import AzureKeyCredential
from autogen_core.tools import FunctionTool
from autogen_core import CancellationToken
from typing import List, Dict
from pathlib import Path
import time
import json
import asyncio
import logging
import os

# Set logging level to ERROR
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('azure').setLevel(logging.ERROR)
logging.getLogger('autogen').setLevel(logging.ERROR)

# Key Vault URL
key_vault_url = os.getenv("KEY_VAULT_URL")

# VARS
# ****************************** #
user_memory = ListMemory()
override_index_name = True


# Retrieve them from environment
tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
blog_url = os.getenv("GLITCHY_WEB_BLOGS")


# SECRET CLIENT
# ****************************** #
# credential = DefaultAzureCredential()
# Use them to authenticate
credential = ClientSecretCredential(tenant_id, client_id, client_secret)
client = SecretClient(vault_url=key_vault_url, credential=credential)

# RAGEVALUATOR
# ****************************** #
evaluator = RAGEvaluator()

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

# Possibly override index name
if override_index_name:
    azure_search_index = "glitchy-web-index"
else:
    azure_search_index = client.get_secret("mmgwaisindex").value

# WEBSCRAPER
# ****************************** #
class MySocialSpider(scrapy.Spider):
    name = "socialspider"
    start_urls = blog_url  # Use the API endpoint

    def __init__(self):
        self.scraped_titles = []

    def parse(self, response):
        data = response.json()
        for blog in data:
            self.scraped_titles.append({"title": blog['title'] ,"author": blog['author'],"content": blog['content']})

    def closed(self, reason):
        with open('scraped_blogs.json', 'w') as f:
            json.dump(self.scraped_titles, f)

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

# ASSISTANT AGENT
agent = AssistantAgent(
    name="Social_Agent",
    model_client=model_client,
    # tools= search_tool,
    description="A helpful assistant that can gain social insights from scraped data.",
    system_message="You are a helpful AI assistant. When the user asks about specific topics, retrieve information from the Azure Cognitive Search knowledge base. Use the search index to find potential social engineering insights about individuals.",
    memory=[user_memory]  # Pass memory as a list
)

# SEARCH FUNCTIONS
# ****************************** #
def get_retrieval_context(query: str) -> str:
    results = search_client.search(query,top=5)
    context_strings = []
    for result in results:
        context_strings.append(f"Document: {result['content']}")
    return "\n\n".join(context_strings) if context_strings else "No results found"


async def ask_unified_rag(query: str, evaluator: RAGEvaluator):
    """
    A unified RAG function that combines both document retrieval and blog data
    based on the query.
    
    Args:
        query: The user's question
        evaluator: The RAG evaluator to measure response quality
    """
    try:
        
        cancellation_token = CancellationToken()
        # Get context from both sources
        retrieval_context = get_retrieval_context(query)

        # Augment the query with both contexts if available
        augmented_query = (
            f"Retrieved Context:\n{retrieval_context}\n\n"
            f"User Query: {query}\n\n"
            "Based ONLY on the above context, please provide the answer."
        )

        # Send the augmented query as a user message
        start_time = time.time()
        response = await agent.on_messages(
            [TextMessage(content=augmented_query, source="user")],
            cancellation_token=CancellationToken(),
        )

        processing_time = time.time() - start_time

        # Use retrieval context directly for evaluation
        combined_context = format_retrieval_context(retrieval_context)

        
        # Evaluate the response
        metrics = evaluator.evaluate_response(
            query=query,
            response=response.chat_message.content,
            context=combined_context
        )
        
        result = {
            'response': response.chat_message.content,
            'processing_time': processing_time,
            'metrics': metrics,
        }
            
        return result
    except Exception as e:
        print(f"Error processing unified query: {e}")
        return None


# HELPER FUNCTIONS
# ****************************** #
def scrape_blog_titles():
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
    
    
def format_retrieval_context(input_string: str) -> List[Dict]:
    # Split the string by "Document:" and filter out empty segments
    segments = [seg.strip() for seg in input_string.split("Document:") if seg.strip()]
    
    # Create a list of dictionaries with unique IDs and content
    formatted_context = [{"id": f"doc-{i}", "content": seg} for i, seg in enumerate(segments)]
    
    return formatted_context


async def upload_data():
    print("Scraping blog titles")
    scraped_data = scrape_blog_titles()

    # VECTOR, INDEX CLIENTS
    # ****************************** #
    az_index_client = AzureSearchConnector(search_client, azure_search_endpoint, azure_search_key, azure_search_index)
    az_index_client.upload_chunked_data(scraped_data, 600)


# # HANDLE USER INTERACTION WITH AGENT
# # ****************************** #
async def handle_user_interaction():
    print("Blog titles have been scraped. You can now ask questions.")
    while True:
        question = input("Ask a question: ")
        if question.lower() in ["exit", "quit"]:
            break

        # retrieval_context = get_retrieval_context(question)
        # # Print the RAG context for transparency
        # print("\n--- RAG Context ---")
        # print(retrieval_context)
        result = await ask_unified_rag(question, evaluator)

        if result:
            print("Response:", result['response'])
            # print("\nMetrics:", result['metrics'])
            print("\n" + "="*60 + "\n")





if __name__ == "__main__":
    # Run the tool to scrape blog titles
    asyncio.run(upload_data())

    # Start user interaction
    asyncio.run(handle_user_interaction())