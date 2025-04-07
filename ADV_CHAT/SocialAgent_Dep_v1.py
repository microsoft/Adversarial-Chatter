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





import multiprocessing
from  Tools.Connectors import AgentDataConnector
from  Tools.Connectors import AzureBlobConnector
multiprocessing.set_start_method('spawn', force=True)
import scrapy
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
from autogen_core import CancellationToken
from datetime import datetime
import subprocess
import pyodbc
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

# Create a DefaultAzureCredential instance
credential = DefaultAzureCredential()

# Create a SecretClient instance
client = SecretClient(vault_url=key_vault_url, credential=credential)

# KEYS, SECRETS


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
# username_secret = client.get_secret("mmgwsqluser")
# password_secret = client.get_secret("mmgwsqlpwd")
server_name = client.get_secret("mmgwsqlserver")
db_name = client.get_secret("mmgwsqldbname")


# DB Configuration
# username = username_secret.value
# password = password_secret.value
server = server_name.value
db = db_name.value

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=open_ai_deployment.value,
    model="gpt-3.5-turbo",
    api_version=open_ai_api.value,
    azure_endpoint=open_ai_endpoint.value,
    api_key=open_ai_key.value  # For key-based authentication.
)

# Create a SearchClient instance
search_client = SearchClient(
    endpoint=f"https://{azure_search.value}.search.windows.net",
    index_name=azure_search_index.value,
    credential=AzureKeyCredential(azure_search_key.value)

)

# Function to query the Azure Search index
def query_search_index(query):
    results = search_client.search(query)
    return [result for result in results]

def search(query: str):
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

    response = list(client.search(payload))

    output = []
    for result in response:
        result.pop("titleVector")
        result.pop("contentVector")
        output.append(result)

    return output



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



async def update_memory_blob():
    print("Scraping blog titles")
    scraped_data = scrape_blog_titles()
    agent_blob_connector = AzureBlobConnector(blob_connection_string.value, blobContainer)
    agent_blob_connector.upload_chunked_data(scraped_data, blobName, 100)
    # agent_blob_connector.upload_data(scraped_data, blobName)

# Updating memory using SQL CONNECTION
# async def update_memory_sql():
#     print("Scraping blog titles")
#     scraped_data = scrape_blog_titles()
#     agent_data_connector = AgentDataConnector(server, db)
#     agent_data_connector.storeScrapedData(scraped_data)
#     metadata_dict = {"db_reference": "Azure SQL Database"}
#     await user_memory.add(MemoryContent(content="scraped web data stored in Azure SQL Database", mime_type=MemoryMimeType.TEXT, metadata=metadata_dict))
#     model_context = BufferedChatCompletionContext(buffer_size=100)
#     await user_memory.update_context(model_context)
#     print("made it past scraping")

# # Create the AssistantAgent
# agent = AssistantAgent(
#     name="Social_Agent",
#     model_client=model_client,
#     description="A helpful assistant that can scrape a website, and gain social insights into what has been scraped",
#     system_message="You are a helpful AI assistant. When the user asks about specific topics, retrieve information from the Azure Cognitive Search knowledge base. Use the search index to find relevant documents and provide accurate answers based on the retrieved information.",
#     memory=[user_memory]  # Pass memory as a list
# )


# Function to handle user interaction


async def handle_user_interaction():

    # Initialize user memory
    user_memory = ListMemory()

    # Create the AssistantAgent
    agent = AssistantAgent(
        name="Social_Agent",
        model_client=model_client,
        description="A helpful assistant that can scrape a website, and gain social insights into what has been scraped",
        system_message="You are a helpful AI assistant. When the user asks about specific topics, retrieve information from the Azure Cognitive Search knowledge base. Use the search index to find relevant documents and provide accurate answers based on the retrieved information.",
        memory=[user_memory]  # Pass memory as a list
    )

    cancellation_token = CancellationToken()
    
    print("Blog titles have been scraped. You can now ask questions about them.")
    while True:
        question = input("Ask a question: ")
        if question.lower() in ["exit", "quit"]:
            break
        
        # Query the Azure Search index
        search_results = query_search_index(question)
        
        if not search_results:
            print("No results found or an error occurred.")
            continue

        # Format the search results
        formatted_results = "\n".join([f"Title: {result['title']}\nAuthor: {result['author']}\nContent: {result['content']}\n" for result in search_results])

        # Get response from the agent
        response = await agent.on_messages(
            [TextMessage(content=formatted_results, source="user")],
            cancellation_token
        )
        
        # Print only the content of the response
        print(response.chat_message.content)



 

# async def handle_user_interaction():
#     cancellation_token = CancellationToken()  # Create a default cancellation token
#     print("Blog titles have been scraped. You can now ask questions about them.")
#     while True:
#         question = input("Ask a question: ")
#         if question.lower() in ["exit", "quit"]:
#             break

#         # Query the Azure Search index
#         search_results = query_search_index(question)
        
#         if not search_results:
#             print("No results found or an error occurred.")
#             continue

#         # Format the search results
#         formatted_results = "\n".join([f"Title: {result['title']}\nAuthor: {result['author']}\nContent: {result['content']}\n" for result in search_results])

#         # Add search results to user memory
#         await user_memory.add(MemoryContent(content=formatted_results, mime_type=MemoryMimeType.TEXT))

#         # Get response from the agent
#         response = await agent.on_messages(
#             [TextMessage(content=question, source="user")],
#             cancellation_token
#         )
        
#         # Print only the content of the response
#         print(response.chat_message.content)



if __name__ == "__main__":
    # Run the tool to scrape blog titles
    asyncio.run(update_memory_blob())

    # Start user interaction
    asyncio.run(handle_user_interaction())