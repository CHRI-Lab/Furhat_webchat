# Prompt used for generate url chat.
SYSTEM_TEMPLATE = """
Answer the user's questions based on the below web page information. 
If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

<web info>
{context}
</web info> 
"""