import os
from langchain.retrievers import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import openai
from langchain_core.messages import HumanMessage
from langchain.docstore.document import Document
from test.rag_methods.multiquery import get_multiquery_retriever
from test.rag_methods.parent_document import get_parent_retriever
from test.url_to_text import url_to_text
from test.RagFramework import RAG_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict
from langchain_core.runnables import RunnablePassthrough

# key = os.getenv('OPENAI_API_KEY')
# openai.api_key = key
# os.environ["OPENAI_API_KEY"] = key

# Loader
# loader = WebBaseLoader("https://melbconnect.com.au/about")
# data = loader.load()

# 1.Basic Spliter
def basic_spliter_search(data, question):
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    all_splits = text_splitter.split_documents(data)
    # Embedding and store the data into vector db
    vector_store = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    # k is the number of chunks to retrieve
    retriever = vector_store.as_retriever(k=3)
    docs = retriever.invoke(question)
    return docs, retriever
#2.Parent Spliter
def parent_splitter_search(data, question):
    parent_retriever = get_parent_retriever(docs=data, parent_document_size=2000, child_document_size=300)
    #retriever = parent_retriever.as_retriever(k=3)
    docs = parent_retriever.invoke(question)
    return docs, parent_retriever
#3.Multi_query_search
def multi_query_search(data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
    all_splits = text_splitter.split_documents(data)
    vector_store = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    multi_query_retriever = get_multiquery_retriever(vector_store)
    unique_docs = multi_query_retriever.get_relevant_documents(query=question)
    return unique_docs, multi_query_retriever

# def parse_retriever_input(params: Dict):
#     return params["messages"][-1].content

# def format_docs(docs):
#     res = "\n\n".join(doc.page_content for doc in docs)
#     return res


class WebChatbot():
    def __init__(self, url, rag_model=RAG_chain()):
        self.rag_model = rag_model
        # Before we get key from client, we could use our own key and use 3.5 for testing.
        self.rag_model.llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)
        # get the text from the url
        self.data = url_to_text(url=url)
        self.rag_model.retriever = get_parent_retriever(docs=self.data, parent_document_size=2000, child_document_size=300)



    def invoke(self, question):
        #self._init_retriever(parent_retriever)
        # print(docs)
        result = self.rag_model.get_answer(question)
        return result


if __name__ == '__main__':
    chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)
    url = 'https://melbconnect.com.au/'
    question = "Tell me about the latest news"
    data = url_to_text(url=url)
    docs, retriever = parent_splitter_search(data, question=question)
    rag_model = RAG_chain()
    rag_model.retriever = retriever
    result = rag_model.get_answer(question)
    print(result)



    