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

from src.prompt.prompt_config import SYSTEM_TEMPLATE
from src.rag_methods.multiquery import get_multiquery_retriever
from src.rag_methods.parent_document import get_parent_retriever
from src.url_to_text import url_to_text
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict
from langchain_core.runnables import RunnablePassthrough

key = os.getenv('OPENAI_API_KEY')
openai.api_key = key
os.environ["OPENAI_API_KEY"] = openai.api_key
# Before we get key from client, we could use our own key and use 3.5 for testing.
chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)
url = 'https://melbconnect.com.au/'
question = "Tell me about the latest news"
# Loader
# loader = WebBaseLoader("https://melbconnect.com.au/about")
# data = loader.load()

# TODO: Choose the best split method and the best chunk_size

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

def parse_retriever_input(params: Dict):
    return params["messages"][-1].content

def format_docs(docs):
    res = "\n\n".join(doc.page_content for doc in docs)
    return res

def get_chatbot_answer(question):
    # MAIN API FUNCTION for front end or chatbot
    text = url_to_text(url=url)
    data = [Document(page_content=text)]
    # Can change different rag method.
    docs, retriever = parent_splitter_search(data, question=question)

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_TEMPLATE,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

    retrieval_chain = RunnablePassthrough.assign(
        context=parse_retriever_input | retriever,
    ).assign(
        answer=document_chain,
    )

    ans = retrieval_chain.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ],
        }
    )
    return ans['answer']

class WebChatbot():
    # Init the chatbot with a url-base vector store. This could make the qa more efficient.
    def __init__(self, url, model_name='gpt-4-turbo',rag_method=None):
        self.url = url
        self.rag_method = rag_method
        self.chatbot = ChatOpenAI(model=model_name, temperature=0.1)

        # Initialize web_info base vector store.
        text = url_to_text(url=url)
        data = [Document(page_content=text)]
        docs, retriever = parent_splitter_search(data, question=question)

        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    SYSTEM_TEMPLATE,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        document_chain = create_stuff_documents_chain(self.chatbot, question_answering_prompt)

        self.retrieval_chain = RunnablePassthrough.assign(
            context=parse_retriever_input | retriever,
        ).assign(
            answer=document_chain,
        )

    def invoke(self, question):
        ans = self.retrieval_chain.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ],
            }
        )
        return ans['answer']

if __name__ == '__main__':
    text = url_to_text(url=url)
    data = [Document(page_content=text)]
    docs, retriever = parent_splitter_search()

    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_TEMPLATE,
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

    retrieval_chain = RunnablePassthrough.assign(
        context=parse_retriever_input | retriever,
    ).assign(
        answer=document_chain,
    )

    ans = retrieval_chain.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ],
        }
    )
    print(ans["answer"])