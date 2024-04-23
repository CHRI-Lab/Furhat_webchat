from environment import chat, url

from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.vectorstores import FAISS
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_text_splitters import CharacterTextSplitter
from langchain.retrievers.document_compressors import EmbeddingsFilter


def get_retriever(vectorstore):

    retriever = vectorstore.as_retriever(search_type="mmr")
    # retriever = FAISS.from_documents(all_splits, OpenAIEmbeddings()).as_retriever()

    llm = OpenAI(temperature=0)
    compressor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )

    return compression_retriever

def get_retriever_transformer(all_splits, chunk_size):

    embeddings  = OpenAIEmbeddings()
    retriever = FAISS.from_documents(all_splits, OpenAIEmbeddings()).as_retriever()

    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0, separator=". ")
    redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
    relevant_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.76)
    pipeline_compressor = DocumentCompressorPipeline(
        transformers=[splitter, redundant_filter, relevant_filter]
    )
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=pipeline_compressor, base_retriever=retriever
    )

    return compression_retriever

def get_context(compression_retriever, question):
    compressed_docs = compression_retriever.get_relevant_documents(query=question)
    return compressed_docs


