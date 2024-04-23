import re
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub
import requests

class RAG_chain:
    def __init__(self):
        load_dotenv(find_dotenv())  # Load the .env file. This is where the openai-API key is stored.
        self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        self.retriever=None
        self.chat_history = []
        self.history_aware_retriever=None
        self.rag_chain=None

    def retrieve_data(self,docs):
        # Split,Emdedding the document
        text_splitter = RecursiveCharacterTextSplitter()
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        self.retriever = vectorstore.as_retriever()
    
    def historical_messages_chain(self):
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        self.history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        ) 

    def full_qa_chain(self):
        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\
        {context}"""

        # prompt = hub.pull("rlm/rag-prompt")
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain) # Combine the two chains

    
    def get_answer(self,question):
        self.historical_messages_chain() # Create the chain for historical messages
        self.full_qa_chain()  # Create the chain for full question and answer
        result=self.rag_chain.invoke({"input": question, "chat_history": self.chat_history})
        self.chat_history.extend([HumanMessage(content=question), result["answer"]])
        return result["answer"]
        

def parse_data(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs

def request_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # If the response status code is not 200, an exception is thrown
        return response.text
    except requests.RequestException as e:
        return None

# The WebBaseLoader() only accepts the URL that starts with http
def validate_url(url):
    pattern = r"^http"  # Begin with http
    if re.match(pattern, url):
        return True
    else:
        return False
    
def main():
    url_response=None
    while not url_response:
        url=input('Input the URL you want to search:')
        if validate_url(url):
            url_response=request_website(url)
        else:
            print('URL should start with http or https')
    else:
        docs=parse_data(url)
        rag_model=RAG_chain()
        rag_model.retrieve_data(docs)
        while True:
            question=input('Input the question:')
            result=rag_model.get_answer(question)
            print('Answer:',result)
            # if input a new url:
            #     rag_model.chat_history.clear()
            #     # cleanup
            #     vectorstore.delete_collection()


if __name__ == "__main__":
    main()