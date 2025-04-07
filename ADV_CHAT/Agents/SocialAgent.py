# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# **************************************             Social Agent                  ******************************************************* #
# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# Author: Miguel Mares
# Date: 2-17-2025
# Description: Web crawler that is pointing specifically to the GlitchyWeb API Blogs page. Can be run from the command line to scrape
#              website and output social engineering insights gleaned from scraped data
# **************************************************************************************************************************************** #

import scrapy
import multiprocessing
from Tools.Connectors import AzureSearchConnector
from autogen_agentchat.agents import AssistantAgent
from azure.search.documents.models import QueryType
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
from pathlib import Path
import time
import json
import asyncio
import logging
import os



class SocialAgent:
    """
    Description: Agentic Social Agent, used for gaining social insights from scraped web data.
    """
    def __init__(self,search_client,model_client):
        self.name = "Social Agent"
        self.description = "A helpful assistant that can gain social insights from scraped data."
        self.search_client = search_client
        self.model_client = model_client
        self.user_memory = ListMemory()

    # SEARCH FUNCTIONS
    # ****************************** #
    def get_retrieval_context(self, query: str) -> str:
        results = self.search_client.search(query,top=5)
        context_strings = []
        for result in results:
            context_strings.append(f"Document: {result['content']}")
        return "\n\n".join(context_strings) if context_strings else "No results found"


    def get_social_results(self, query: str) -> str:

        retrieval_context = self.get_retrieval_context(query)

        augmented_query = (
        f"Retrieved Context:\n{retrieval_context}\n\n"
        f"User Query: {query}\n\n"
        "Based ONLY on the above context, please provide the answer."
        )
        
        results = self.search_client.search(augmented_query,top=10)
        social_results = []
        for result in results:
            social_results.append({"Document": result['content']})
        return social_results


    def initialize_agent(self):
        
        social_search_tool = FunctionTool(
            self.get_social_results, description="Using Azure Search, to gain insights from scraped web data."
        )

        # SOCIAL AGENT
        agent = AssistantAgent(
            name="Social_Agent",
            model_client=self.model_client,
            tools= [social_search_tool],
            description="A helpful assistant that can gain social insights from scraped data.",
            system_message="You are a helpful AI assistant. When the user asks about gathering insights or social engineering" \
            "vulneabilities, retrieve information from the Azure Cognitive Search knowledge base. Use the search index to find potential social engineering insights about individuals. Point out the most relevant information and provide a summary, " \
            "with methods and threat attack areas and possible mitigation strategies.",
            memory=[self.user_memory]  # Pass memory as a list
        )

        return agent

