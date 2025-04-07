# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# **************************************             Social Agent Summary          ******************************************************* #
# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# Author: Miguel Mares
# Date: 2-17-2025
# Description: Web crawler that is pointing specifically to the GlitchyWeb API Blogs page. Can be run from the command line to scrape
#              website and output ag
# **************************************************************************************************************************************** #


import scrapy
import multiprocessing
from Tools.Connectors import RAGEvaluator
from Tools.Connectors import AgentDataConnector
from Tools.Connectors import AzureBlobConnector
multiprocessing.set_start_method('spawn', force=True)
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from azure.identity import DefaultAzureCredential
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
from pathlib import Path
# from datetime import datetime
# import subprocess
# import pyodbc
import json
import asyncio
import logging

# Set logging level to ERROR
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('azure').setLevel(logging.ERROR)
logging.getLogger('autogen').setLevel(logging.ERROR)

# Replace with your Key Vault URL
key_vault_url = "https://mmgwkv.vault.azure.net/"

# VARS
blobContainer = "scraped"
blobName =  "GlitchyWebScraped"
user_memory = ListMemory()


# CREDENTIALS AND SECRET CLIENT
# ****************************** #
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)



# KEYS, SECRETS
# ****************************** #
open_ai_endpoint = client.get_secret("mmgwoaiendpoint")
open_ai_deployment = client.get_secret("mmgwaoaideployment")
open_ai_key = client.get_secret("mmgwoaikey")
open_ai_api = client.get_secret("mmgwoaiapi")
blob_key = client.get_secret("mmgwblobkey")
blob_connection_string = client.get_secret("mmgwblobconnection")
azure_search = client.get_secret("mmgwaisname")
azure_search_index = client.get_secret("mmgwaisindex")
azure_search_key = client.get_secret("mmgwaiskey")
azure_search_config = client.get_secret("mmgwazuresearchconfig")
server_name = client.get_secret("mmgwsqlserver")
db_name = client.get_secret("mmgwsqldbname")

# WEBSCRAPER
# ****************************** #
class MySocialSpider(scrapy.Spider):
    name = "socialspider"
    start_urls = ['http://localhost:3000/api/blogs']  # Use the API endpoint

    def __init__(self):
        self.scraped_titles = []

    def parse(self, response):
        data = response.json()
        for blog in data:
            self.scraped_titles.append({"title": blog['title'] ,"author": blog['author'],"content": blog['content']})

    def closed(self, reason):
        with open('scraped_blogs.json', 'w') as f:
            json.dump(self.scraped_titles, f)

# # DB Configuration
# server = server_name.value
# db = db_name.value

# MODEL CLIENT
# ****************************** #
model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=open_ai_deployment.value,
    model="gpt-3.5-turbo",
    api_version=open_ai_api.value,
    azure_endpoint=open_ai_endpoint.value,
    api_key=open_ai_key.value  # For key-based authentication.
)

# SEARCH CLIENT
# ****************************** #
search_client = SearchClient(
    endpoint=f"https://{azure_search.value}.search.windows.net",
    index_name=azure_search_index.value,
    credential=AzureKeyCredential(azure_search_key.value)
)

# SEARCH FUNCTIONS
# ****************************** #
def query_search(query: str):
    payload = json.dumps(
        {
            "search": query,
            "vectorQueries": [{"kind": "text", "text": query, "k": 5, "fields": "vector"}],
            "queryType": "semantic",
            "semanticConfiguration": azure_search_config.value,
            "captions": "extractive",
            "answers": "extractive|count-3",
            "queryLanguage": "en-US",
        }
    )

    response = list(search_client.search(payload))

    output = []
    for result in response:
        # print(result)
        result.pop("text_vector")
        # result.pop("content")
        output.append(result)

    return output

# def get_retrieval_context(query: str) -> str:
#     results = search_client.search(query)
#     context_strings = []
#     for result in results:
#         context_strings.append(f"Document: {result['content']}")
#     return "\n\n".join(context_strings) if context_strings else "No results found"

# async def ask_unified_rag(query: str, evaluator: RAGEvaluator, location: str = None):
#     """
#     A unified RAG function that combines both document retrieval and weather data
#     based on the query and optional location parameter.
    
#     Args:
#         query: The user's question
#         evaluator: The RAG evaluator to measure response quality
#         location: Optional location for weather queries
#     """
#     try:
#         # Get context from both sources
#         retrieval_context = get_retrieval_context(query)
        
#         # If location is provided, add weather data
#         weather_context = ""
#         if location:
#             weather_context = get_weather_data(location)
#             weather_intro = f"\nWeather Information for {location}:\n"
#         else:
#             weather_intro = ""
        
#         # Augment the query with both contexts if available
#         augmented_query = (
#             f"Retrieved Context:\n{retrieval_context}\n\n"
#             f"{weather_intro}{weather_context}\n\n"
#             f"User Query: {query}\n\n"
#             "Based ONLY on the above context, please provide the answer."
#         )

#         # Send the augmented query as a user message
#         start_time = time.time()
#         response = await assistant.on_messages(
#             [TextMessage(content=augmented_query, source="user")],
#             cancellation_token=CancellationToken(),
#         )
#         processing_time = time.time() - start_time

#         # Create combined context for evaluation
#         combined_context = documents.copy()  # Start with travel documents
        
#         # Add weather as a document if it exists
#         if location and weather_context:
#             combined_context.append({"id": f"weather-{location}", "content": weather_context})
        
#         # Evaluate the response
#         metrics = evaluator.evaluate_response(
#             query=query,
#             response=response.chat_message.content,
#             context=combined_context
#         )
        
#         result = {
#             'response': response.chat_message.content,
#             'processing_time': processing_time,
#             'metrics': metrics,
#         }
        
#         # Add location to result if provided
#         if location:
#             result['location'] = location
            
#         return result
#     except Exception as e:
#         print(f"Error processing unified query: {e}")
#         return None


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


async def upload_data():
    print("Scraping blog titles")
    scraped_data = scrape_blog_titles()
    agent_blob_connector = AzureBlobConnector(blob_connection_string.value, blobContainer)
    agent_blob_connector.upload_chunked_data(scraped_data, blobName, 100)
    # agent_blob_connector.upload_data(scraped_data, blobName)


# AGENT AND TOOLS
# ****************************** #
search_tool = FunctionTool(
    query_search, description="A tool for searching the Cognitive Search index"
)

# Create the AssistantAgent
agent = AssistantAgent(
    name="Social_Agent",
    model_client=model_client,
    # tools= search_tool,
    description="A helpful assistant that can scrape a website, and gain social insights into what has been scraped",
    system_message="You are a helpful AI assistant. When the user asks about specific topics, retrieve information from the Azure Cognitive Search knowledge base. Use the search index to find relevant documents and provide accurate answers based on the retrieved information.",
    memory=[user_memory]  # Pass memory as a list
)


# HANDLE USER INTERACTION WITH AGENT
async def handle_user_interaction():

    cancellation_token = CancellationToken()
    
    print("Blog titles have been scraped. You can now ask questions about them.")
    while True:
        question = input("Ask a question: ")
        if question.lower() in ["exit", "quit"]:
            break
        
        # Query the Azure Search index
        search_results = query_search(question)
        
        if not search_results:
            print("No results found or an error occurred.")
            continue

        # # Format the search results
        # formatted_results = "\n".join([f"Title: {result.get('title', 'N/A')}\nAuthor: {result.get('author', 'N/A')}\nContent: {result.get('content', 'N/A')}\n" for result in search_results])
        for result in search_results:
            print(result['chunk'])

        # Get response from the agent
        response = await agent.on_messages(
            [TextMessage(content=formatted_results, source="user")],
            cancellation_token
        )
        
        # Print only the content of the response
        print(response.chat_message.content)


if __name__ == "__main__":
    # Run the tool to scrape blog titles
    asyncio.run(upload_data())

    # Start user interaction
    asyncio.run(handle_user_interaction())