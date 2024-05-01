from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_parent_retriever(docs, parent_document_size, child_document_size):
    # This text splitter is used to create the parent documents
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_document_size)
    # This text splitter is used to create the child documents
    # It should create documents smaller than the parent
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_document_size)
    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(
        collection_name="split_parents", embedding_function=OpenAIEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    retriever.add_documents(docs)
    return vectorstore

def get_context(retriever, question):
    docs = retriever.get_relevant_documents(question)
    return docs


