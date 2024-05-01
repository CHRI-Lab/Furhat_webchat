from environment import chat, url

# create a summary for each document
from langchain.retrievers.multi_vector import MultiVectorRetriever

from langchain.storage import InMemoryByteStore
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

import uuid

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_summary_retriever(all_splits):

    chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("Summarize the following document:\n\n{doc}")
        | ChatOpenAI(max_retries=0)
        | StrOutputParser()
    )
    
    summaries = chain.batch(all_splits, {"max_concurrency": 5})

    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(collection_name="summaries", embedding_function=OpenAIEmbeddings())
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=store,
        id_key=id_key,
    )
    doc_ids = [str(uuid.uuid4()) for _ in all_splits]

    summary_docs = [
        Document(page_content=s, metadata={id_key: doc_ids[i]})
        for i, s in enumerate(summaries)
    ]

    retriever.vectorstore.add_documents(summary_docs)
    retriever.docstore.mset(list(zip(doc_ids, all_splits)))

    # for i, doc in enumerate(all_splits):
    #     doc.metadata[id_key] = doc_ids[i]
    # retriever.vectorstore.add_documents(all_splits)

    return retriever

def get_context(retriever, question):
    docs = retriever.get_relevant_documents(question)
    return docs


# create hypothetical questions for each document
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

def get_hypothetical_retriever(all_splits):

    functions = [
        {
            "name": "hypothetical_questions",
            "description": "Generate hypothetical questions",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["questions"],
            },
        }
    ]

    chain = (
        {"doc": lambda x: x.page_content}
        # Only asking for 3 hypothetical questions, but this could be adjusted
        | ChatPromptTemplate.from_template(
            "Generate a list of exactly 3 hypothetical questions that the below document could be used to answer and answer them:\n\n{doc}"
        )
        | chat.bind(
            functions=functions, function_call={"name": "hypothetical_questions"}
        )
        | JsonKeyOutputFunctionsParser(key_name="questions")
    )

    hypothetical_questions = chain.batch(all_splits, {"max_concurrency": 5})
    
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="hypo-questions", embedding_function=OpenAIEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        byte_store=store,
        id_key=id_key,
    )
    doc_ids = [str(uuid.uuid4()) for _ in all_splits]

    question_docs = []
    for i, question_list in enumerate(hypothetical_questions):
        question_docs.extend(
            [Document(page_content=s, metadata={id_key: doc_ids[i]}) for s in question_list]
        )
    
    retriever.vectorstore.add_documents(question_docs)
    retriever.docstore.mset(list(zip(doc_ids, all_splits)))

    return retriever