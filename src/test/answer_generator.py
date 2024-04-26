from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from typing import Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch

# get answer from LLM, no conversation support
def get_answer(chat, question, context):


    SYSTEM_TEMPLATE = """
    Answer the user's questions based on the below context. 
    If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

    <context>
    {context}
    </context>
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


    from langchain_core.messages import HumanMessage

    results = document_chain.invoke(
        {
            "context": context,
            "messages": [
                HumanMessage(content=question)
            ],
        }
    )

    return results


# convert the query for the retriever, which means adding previous conversation contents
def get_converted_question(chat, previous_conversations, question):

    messages = []
    for conversation in previous_conversations:
        messages.append(HumanMessage(content=conversation[0]))
        messages.append(AIMessage(content=conversation[1]))
    
    messages.append(HumanMessage(content=question))
    
    query_transform_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
            ),
        ]
    )

    query_transformation_chain = query_transform_prompt | chat

    converted_question = query_transformation_chain.invoke(
        {
            "messages": messages,
        }
    )

    return converted_question.content

# get answer from LLM based on previous conversation contents
def get_answer_for_conversation(chat, retriever, previous_conversations, question):

    query_transform_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
            ),
        ]
    )

    query_transforming_retriever_chain = RunnableBranch(
        (
            lambda x: len(x.get("messages", [])) == 1,
            # If only one message, then we just pass that message's content to retriever
            (lambda x: x["messages"][-1].content) | retriever,
        ),
        # If messages, then we pass inputs to LLM chain to transform the query, then pass to retriever
        query_transform_prompt | chat | StrOutputParser() | retriever,
    ).with_config(run_name="chat_retriever_chain")

    SYSTEM_TEMPLATE = """
    Answer the user's questions based on the below context. 
    If the context doesn't contain any relevant information to the question, don't make something up and just say "I don't know":

    <context>
    {context}
    </context>
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

    conversational_retrieval_chain = RunnablePassthrough.assign(
        context=query_transforming_retriever_chain,
    ).assign(
        answer=document_chain,
    )

    messages = []
    for conversation in previous_conversations:
        messages.append(HumanMessage(content=conversation[0]))
        messages.append(AIMessage(content=conversation[1]))
    
    messages.append(HumanMessage(content=question))

    results = conversational_retrieval_chain.invoke(
        {
            "messages": messages
        }
    )

    return results['answer']
