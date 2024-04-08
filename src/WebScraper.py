import os

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import openai

openai.api_key = "PUT YOUR OPENAI KEY HERE"
os.environ["OPENAI_API_KEY"] = openai.api_key
#chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)

# Loader
loader = WebBaseLoader("https://melbconnect.com.au/")
data = loader.load()

# TODO: Filter the data
# TODO: Choose the best split method and the best chunk_size

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Embedding and store the data into vector db
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# k is the number of chunks to retrieve
retriever = vectorstore.as_retriever(k=4)

docs = retriever.invoke("Tell me about the latest news")

print("docs")