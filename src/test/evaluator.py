from environment import chat, url

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, answer_correctness, context_precision, context_recall, answer_similarity

import answer_generator

def evaluate_retriever(questions, ground_truth, retriever, get_context, conversation_support):
    answers = []
    contexts = []

    if not conversation_support:
        # no conversation
        for question in questions:
            docs = get_context(retriever, question)
            contexts.append([doc.page_content for doc in docs])
            answer = answer_generator.get_answer(chat, question, docs)
            answers.append(answer)
    else:
        # support conversation
        previous_conversations = []
        for question in questions:
            converted_question = answer_generator.get_converted_question(chat, previous_conversations, question)
            docs = get_context(retriever, converted_question)
            contexts.append([doc.page_content for doc in docs])
            answer = answer_generator.get_answer(chat, question, docs)
            answers.append(answer)
            previous_conversations.append((question, answer))
    # print(answers)

    data = {"question":questions, "contexts": contexts, "answer": answers, "ground_truth": ground_truth}
    dataset = Dataset.from_dict(data)
    results = evaluate(dataset, metrics=[answer_relevancy, answer_correctness, context_precision, context_recall, answer_similarity])
    print(results)

import qa_example_generator
import dataloader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import vectorstore_retriever
import multiquery
import context_compression
import parent_document


data = dataloader.get_data(url)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# 20 examples
# questions = []
# ground_truth = []
# for i in range(4):
#     question, answer = qa_example_generator.get_examples(all_splits, 5)
#     questions += question
#     ground_truth += answer
questions, ground_truth = qa_example_generator.get_examples(all_splits, 4)
evaluate_retriever(questions, ground_truth, vectorstore_retriever.get_retriever(vectorstore),  vectorstore_retriever.get_context, True)
evaluate_retriever(questions, ground_truth, multiquery.get_retriever(vectorstore), multiquery.get_context, True)
evaluate_retriever(questions, ground_truth, context_compression.get_retriever(vectorstore), context_compression.get_context, True)
evaluate_retriever(questions, ground_truth, parent_document.get_retriever(data, 500, 300), parent_document.get_context, True)