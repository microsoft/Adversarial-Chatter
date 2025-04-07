# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# **************************************             Helper class to connect to Azure Blob Storage and Azure Search  ********************* #
# **************************************************************************************************************************************** #
# **************************************************************************************************************************************** #
# Author: Miguel Mares
# Date: 3-17-2025
# Description: Azure Blob Storage and Azure Search helper class 
# **************************************************************************************************************************************** #


import asyncio
import time
import math
import uuid
import json
import pyodbc
import subprocess
from datetime import datetime
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient,ContentSettings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch
)
from azure.core.exceptions import ResourceNotFoundError

class AzureBlobConnector:
    """
    Description: Azure Blob Storage connector class, initilization of BlobServiceClient, uploading files to Blob Storage.
    """
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload_file(self, file_path, blob_name, overwrite=True):
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=overwrite, content_settings=ContentSettings(content_type="application/json"))
            print(f"File {file_path} uploaded to blob {blob_name} successfully.")
        except Exception as e:
            print(f"Error uploading file: {e}")

    def upload_chunked_data(self, data, blob_name, limit, chunkSize ,overwrite=True):
        try:
            blogSplitter = BlogContentSplitter(chunkSize)

            if isinstance(data, list):
                total_items = len(data)
                num_files = math.ceil(total_items / limit)

                print("Iterating over new files")
                for i in range(num_files):
                    blob_client = self.container_client.get_blob_client(blob_name + "_" + str(i))
                    start_index = i * limit
                    end_index = ((i + 1) * limit) - 1 
                    chunk_items = data[start_index:end_index]
                    temp_chunk_items = []
                    for item in chunk_items:
                        temp_items = blogSplitter.split_blog_content(item)
                        temp_chunk_items.extend(temp_items)
                    data_chunk = json.dumps(temp_chunk_items)  # Convert list to JSON string
                    blob_client.upload_blob(data_chunk, overwrite=overwrite, content_settings=ContentSettings(content_type="application/json"))
                    # print(f"Data uploaded to blob {blob_name} successfully.")
        except Exception as e:
            print(f"Error uploading data: {e}")

    def upload_data(self, data, blob_name, overwrite=True):
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            if isinstance(data, list):
                for item in data:
                    item["id"] = str(uuid.uuid4())  # Generate a unique id for each document
                data = json.dumps(data)  # Convert list to JSON string
            blob_client.upload_blob(data, overwrite=overwrite, content_settings=ContentSettings(content_type="application/json"))
            print(f"Data uploaded to blob {blob_name} successfully.")
        except Exception as e:
            print(f"Error uploading data: {e}")


class AzureSearchConnector:
    """
    Description: Azure Search connector class, initialization of Index, uploading documents to Index.
    """
    def __init__(self, search_client, search_service_endpoint, search_api_key, index_name):
        self.search_client = search_client
        self.search_service_endpoint = search_service_endpoint
        self.search_api_key = search_api_key
        self.index_name = index_name
        self.initializeIndex()

    async def initializeIndex(self):
        index_client = SearchIndexClient(
            endpoint=self.search_service_endpoint,
            credential=AzureKeyCredential(self.search_api_key)
        )
        
        # Check if the index exists
        try:
            index_client.get_index(self.index_name)
            # If the index exists, delete it
            index_client.delete_index(self.index_name)
            print(f"Index '{self.index_name}' deleted.")
        except ResourceNotFoundError:
            print(f"Index '{self.index_name}' does not exist. Creating a new index.")

        # Define the index schema
        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="title", type=SearchFieldDataType.String, searchable=True, sortable=True),
            SearchField(name="author", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True)
        ]

        # Define the semantic configuration
        semantic_configuration = SemanticConfiguration(
            name="glitchy-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keyword_fields=[SemanticField(field_name="author")],
                content_fields=[SemanticField(field_name="content")]
            )
        )


        # Create the semantic settings with the configuration
        semantic_search = SemanticSearch(configurations=[semantic_configuration])

        # Create the new index with the semantic configuration
        index = SearchIndex(
            name=self.index_name,
            fields=fields
        )

        # Create the index
        index_client.create_or_update_index(index)

        await asyncio.sleep(10)


    def upload_chunked_data(self, data, chunkSize):
        try:
            blogSplitter = BlogContentSplitter(chunkSize)

            print("Iterating over new index documents")
            temp_chunk_items = []
            for doc in data:
                temp_items = blogSplitter.split_blog_content(doc)
                temp_chunk_items.extend(temp_items)
            documents = temp_chunk_items 
            self.search_client.upload_documents(documents)
        except Exception as e:
            print(f"Error uploading document data: {e}")




class AgentDataConnector():
    """
    Description: Azure SQL connector class, initilization of SQL connection, uploading documents to SQL.
    """
    def __init__(self, server, db):
        self.server = server
        self.db = db

    # azd login function to not have to run a powershell CMDLT.
    def azd_auth_login(self):
        try:
            # Run the azd auth login command
            result = subprocess.run(['azd', 'auth', 'login'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr.decode()}")

    # Connect to SQL Server using Entra ID
    def connectToSql(self):
        try:
            conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};'
                                  f'SERVER={self.server};'
                                  f'DATABASE={self.db};'
                                  'Authentication=ActiveDirectoryMsi')
            return conn
        except pyodbc.OperationalError as e:
            print(f"OperationalError: {e}")

    # Store scraped data in SQL Server
    def storeScrapedData(self, data):

        try:

            self.azd_auth_login()
            print("Connecting to Azure...")
            conn = self.connectToSql()
            print("Connecting to SQL...")
            cursor = conn.cursor()

            # Create the table if it does not exist
            print("Creating table if it does not exist...")
            cursor.execute('''
                        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'Analytics' AND TABLE_NAME = 'Blogs')
                        CREATE TABLE Analytics.Blogs (id INT PRIMARY KEY IDENTITY(1,1), title NVARCHAR(MAX), author NVARCHAR(MAX), content Text)''')

            # Insert data into the table
            print("Inserting data into the table...")
            for entry in data:
                cursor.execute('''INSERT INTO Analytics.Blogs (title, author, content) VALUES (?,?,?)''', (entry['title'], entry['author'], entry['content']))

            # Commit the transaction
            conn.commit()
            cursor.close()
            conn.close()
            print("Data inserted successfully.")

            print(datetime.now())
        except pyodbc.OperationalError as e:
            print(f"OperationalError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def query_azure_sql(self, query):

        try:
            conn = self.connectToSql()

            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()

            return results
        except pyodbc.OperationalError as e:
            print(f"OperationalError: {e}")


class BlogContentSplitter:
    """
    Description: Blog content splitter class, split blog content into chunks of specified size.
    """
    def __init__(self, chunk_size=600):
        self.chunk_size = chunk_size 

    def is_content_within_limit(self, content):
        """
        Check if the content size is within the specified limit.

        Parameters:
        content (str): The content to be checked.
        limit (int): The maximum allowed size in bytes. Default is 32766 bytes.

        Returns:
        bool: True if the content size is within the limit, False otherwise.
        """
        content_bytes = content.encode('utf-8')
        content_size = len(content_bytes)
        # print("content size: ", content_size)
        return content_size <= self.chunk_size

    def split_content_into_chunks(self, content):
        """
        Split the content into chunks of specified size.

        Parameters:
        content (str): The content to be split.
        chunk_size (int): The maximum allowed size in bytes. Default is 32000 bytes.

        Returns:
        list: A list of content chunks.
        """
        chunks = []
        current_chunk_bytes = b""
        
        for char in content:
            char_bytes = char.encode('utf-8')
            if len(current_chunk_bytes + char_bytes) <= self.chunk_size:
                current_chunk_bytes += char_bytes
            else:
                chunks.append(current_chunk_bytes.decode('utf-8'))
                current_chunk_bytes = char_bytes
        
        # Append the last chunk
        if current_chunk_bytes:
            chunks.append(current_chunk_bytes.decode('utf-8'))
        
        return chunks

    def split_blog_content(self, blog):
        """
        Split the blog content into multiple chunks if it exceeds the size limit.

        Parameters:
        blog (dict): The blog entry with 'title', 'author', and 'content' fields.
        chunk_size (int): The maximum allowed size in bytes. Default is 32000 bytes.

        Returns:
        list: A list of blog entries with split content.
        """
        title = blog['title']
        author = blog['author']
        content = blog['content']
        
        # Check if content needs to be split into chunks
        if self.is_content_within_limit(content):
            blog['id'] = str(uuid.uuid4()) 
            return [blog]
        
        # Split content into chunks
        chunks = self.split_content_into_chunks(content)
        
        # Create new blog entries with split content
        split_blogs = []
        for chunk in chunks:
            new_blog = {
                'title': title,
                'author': author,
                'content': chunk,
                'id': str(uuid.uuid4())
            }
            split_blogs.append(new_blog)
            # print("split blogs", split_blogs)
        
        return split_blogs






