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
multiprocessing.set_start_method('spawn', force=True)
import scrapy
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_core.model_context import BufferedChatCompletionContext
from autogen_core import CancellationToken
import json
import asyncio
import logging

# Set logging level to ERROR
logging.getLogger('scrapy').setLevel(logging.ERROR)
logging.getLogger('azure').setLevel(logging.ERROR)
logging.getLogger('autogen').setLevel(logging.ERROR)

# Replace with your Key Vault URL
key_vault_url = "https://mmgwkv.vault.azure.net/"

# Create a DefaultAzureCredential instance
credential = DefaultAzureCredential()

# Create a SecretClient instance
client = SecretClient(vault_url=key_vault_url, credential=credential)

# KEYS AND SECRETS
open_ai_endpoint = client.get_secret("mmgwoaiendpoint")
open_ai_deployment = client.get_secret("mmgwaoaideployment")
open_ai_key = client.get_secret("mmgwoaikey")
open_ai_api = client.get_secret("mmgwoaiapi")

model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=open_ai_deployment.value,
    model="gpt-3.5-turbo",
    api_version=open_ai_api.value,
    azure_endpoint=open_ai_endpoint.value,
    api_key=open_ai_key.value  # For key-based authentication.
)

# Initialize user memory
user_memory = ListMemory()

class MySocialSpider(scrapy.Spider):
    name = "socialspider"
    start_urls = ['http://localhost:3000/api/blogs']  # Use the API endpoint

    def __init__(self):
        self.scraped_titles = []

    def parse(self, response):
        data = response.json()
        for blog in data:
            self.scraped_titles.append({"title": blog['title']})

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
            titles = json.load(file)
            print("File Data Object Type =  ", type(titles))
        formatted_titles = [{"title": title['title']} for title in titles]
        return formatted_titles if formatted_titles else []
    except FileNotFoundError:
        return []

def summarize_data(data):
    summary = f"Scraped {len(data)} blog titles."
    return summary

async def update_memory():
    scraped_data = scrape_blog_titles()
    summary = summarize_data(scraped_data)
    # Update memory with the summary
    metadata_dict = {"summary": summary}
    await user_memory.add(MemoryContent(content=summary, mime_type=MemoryMimeType.TEXT, metadata=metadata_dict))
    # Create a model context
    model_context = BufferedChatCompletionContext(buffer_size=100)
    # Update a model context with memory
    await user_memory.update_context(model_context)

# Create the AssistantAgent
agent = AssistantAgent(
    name="Social_Agent",
    model_client=model_client,
    description="A helpful assistant that can scrape a website, and gain social insights into what has been scraped",
    system_message="You are a helpful AI assistant. Solve tasks using your tools.",
    memory=[user_memory]  # Pass memory as a list
)

# Function to handle user interaction
async def handle_user_interaction():
    cancellation_token = CancellationToken()  # Create a default cancellation token
    print("Blog titles have been scraped. You can now ask questions about them.")
    while True:
        question = input("Ask a question: ")
        if question.lower() in ["exit", "quit"]:
            break
        response = await agent.on_messages(
            [TextMessage(content=question, source="user")],
            cancellation_token
        )
        # Print only the content of the response
        print(response.chat_message.content)

if __name__ == "__main__":
    # Run the tool to scrape blog titles
    asyncio.run(update_memory())

    # Start user interaction
    asyncio.run(handle_user_interaction())