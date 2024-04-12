import os

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import openai
from langchain_core.messages import HumanMessage


openai.api_key = "sk-xxx"
os.environ["OPENAI_API_KEY"] = openai.api_key
# Before we get key from client, we could use our own key and use 3.5 for testing.
chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)

# Loader
loader = WebBaseLoader("https://melbconnect.com.au/about")
data = loader.load()

# TODO: Filter the data
# TODO: Choose the best split method and the best chunk_size

# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
all_splits = text_splitter.split_documents(data)

# Embedding and store the data into vector db
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# k is the number of chunks to retrieve
retriever = vectorstore.as_retriever(k=4)
question = "Tell me about the team in melbourne connect"
docs = retriever.invoke(question)

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_TEMPLATE = """
Answer the user's questions based on the below web page information. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

<web info>
{context}
</web info>
"""

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

from typing import Dict

from langchain_core.runnables import RunnablePassthrough


def parse_retriever_input(params: Dict):
    return params["messages"][-1].content

def format_docs(docs):
    res = "\n\n".join(doc.page_content for doc in docs)
    return res

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