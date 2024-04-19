from environment import chat, url

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI

def get_retriever(vectordb):
    llm = ChatOpenAI(temperature=0)
    retriever_from_llm = MultiQueryRetriever.from_llm(
        retriever=vectordb.as_retriever(), llm=llm
    )
    return retriever_from_llm

def get_context(retriever_from_llm, question):
    unique_docs = retriever_from_llm.get_relevant_documents(query=question)
    return unique_docs


# Set logging for the queries
# import logging

# logging.basicConfig()
# logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)


# for doc in unique_docs:
#     print()
#     print(doc.page_content)

# import conversation
# print(conversation.get_answer(chat, retriever_from_llm, [], question))

