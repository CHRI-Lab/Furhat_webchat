from environment import chat, url

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

import numpy as np
import re

def get_examples(all_splits, n):

    question = f"Give me {n} questions that a new visitor will ask based on the provided context, and answer each of them. Make sure that for each question the answer is not 'I don't know'. Show questions and answers separately in a list format."

    # docs = retriever.invoke(question)

    # for doc in docs:
    #     print(len(docs), len(doc.page_content))

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

    chosen_splits = list(range(len(all_splits)))
    np.random.shuffle(chosen_splits)
    chosen_splits = chosen_splits[:np.random.randint(1, 10)]
    # print(chosen_splits)
    # for i in chosen_splits:
    #     print(all_splits[i].page_content)

    results = document_chain.invoke(
        {
            "context": [all_splits[i] for i in chosen_splits],
            "messages": [
                HumanMessage(content=question)
            ],
        }
    )

    # print(results)

    results = results.split("Questions:")[1].split("Answers:")
    questions = re.sub("[0-9]\. ", "", results[0])
    answers = re.sub("[0-9]\. ", "", results[1])
    questions = [question for question in questions.split("\n") if question != ""]
    answers = [answer for answer in answers.split("\n") if answer != ""]
    for i in range(n):
        if answers[i] == "I don't know.":
            questions[i] = ""
            answers[i] = ""
    questions = [question for question in questions if question != ""]
    answers = [answer for answer in answers if answer != ""]
    # print(questions, answers)

    return questions, answers

# get_examples(url)