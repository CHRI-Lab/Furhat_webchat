from environment import chat, url

def get_retriever(vectorstore):
    retriever = vectorstore.as_retriever(search_type="mmr")
    return retriever

def get_context(retriever, question):
    docs = retriever.invoke(question)
    return docs


# question = 'what courses are provided?'

# docs = retriever.invoke(question)

# for doc in docs:
#     print()
#     print(doc.page_content)



