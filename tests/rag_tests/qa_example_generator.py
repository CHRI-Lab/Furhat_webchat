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


from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser

# known problems: key errors cause by llm not returning data according to the given format
# randomly choosing splits may not be good to generate a reasonable question since the real qeustion may need splits which are semantically connected
def generate_examples(all_splits, n):

    functions = [
        {
            "name": "hypothetical_questions",
            "description": "Generate hypothetical questions and answers",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "answers": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["questions", "answers"],
            },
        }
    ]

    chain = (
        {"doc": lambda x: " ".join([doc.page_content for doc in x])}
        # Only asking for 3 hypothetical questions, but this could be adjusted
        | ChatPromptTemplate.from_template(
            f"Generate a list of exactly {n} hypothetical questions that the below document could be used to answer" + " and answer them:\n\n{doc}" +
            """
            Make sure each question is relevant to the answer of the previous question.
            You could follow the following example:
            ### Example
            1. Question: Hi, I would like to know how many libraries does the university have?
            Answer: There are total 13 libraries in the university.
            2. Question: Ok, then which of them is the closet one to me?
            Answer: It depends on your current location, if you are in Carlton, it will be Brownless Biomedical Library.
            3. Question: Thanks, so about Brownless Biomedical Library, what is opening hours of it?
            Answer: It's 9am-8pm on work day.
            """
            
        )
        | chat.bind(
            functions=functions, function_call={"name": "hypothetical_questions"}
        )
    )
# f"Generate a conversation content which has exactly {n} hypothetical questions and answers" + " based on the below document:\n\n{doc}"

    question_parser = JsonKeyOutputFunctionsParser(key_name="questions")
    answer_parser = JsonKeyOutputFunctionsParser(key_name="answers")

    chosen_splits = list(range(len(all_splits)))
    np.random.shuffle(chosen_splits)
    chosen_splits = chosen_splits[:np.random.randint(6, 10)]

    # results = chain.batch([all_splits[i] for i in chosen_splits], {"max_concurrency": 5})
    results = chain.invoke([all_splits[i] for i in chosen_splits])
    hypothetical_questions = question_parser.invoke(results)
    hypothetical_answers = answer_parser.invoke(results)

    return hypothetical_questions, hypothetical_answers


# import dataloader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from src.url_to_text import url_to_text
# from langchain.docstore.document import Document
# data = url_to_text(url)

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
# all_splits = text_splitter.split_documents(data)

# hypothetical_questions, hypothetical_answers = generate_examples(all_splits, 4)
# print(hypothetical_questions)
# print(hypothetical_answers)