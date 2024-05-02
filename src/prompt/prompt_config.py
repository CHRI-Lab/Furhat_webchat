# Prompt used for generate url chat.
qa_system_prompt = """
Answer the user's questions based on the below web page information. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":
You might got information tells you that the scraper was blocked by the website. If this happens, tell the user that the scraper was blocked.
<web info>
{context}
</web info>
You must answer the question based on the given <web info> and do not answer any irrelevant question.
Answer user's question based on the web info: 
"""
contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

# qa_system_prompt = """You are an assistant for question-answering tasks. \
# Use the following pieces of retrieved context to answer the question. \
# If you don't know the answer, just say that you don't know. \
# Use three sentences maximum and keep the answer concise.\
# {context}"""