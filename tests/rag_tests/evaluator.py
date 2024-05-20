from environment import chat, url

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_precision, context_recall

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
    results = evaluate(dataset, metrics=[answer_relevancy, faithfulness, context_precision, context_recall])
    return results



import qa_example_generator
import dataloader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import vectorstore_retriever as vr
import multiquery as mq
import context_compression as ct
import parent_document as pd
import multivector as mv


# data = dataloader.get_data(url)

from src.url_to_text import url_to_text
data = url_to_text(url)
print(len(data), len(data[0].page_content))

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

questions = []
ground_truth = []
test_length = 20

while len(questions) < test_length:
    question = []
    answer = []
    try:
        question, answer = qa_example_generator.generate_examples(all_splits, 4)
    except:
        continue
    if len(question) != len(answer):
        continue
    questions += question
    ground_truth += answer

# questions, ground_truth = qa_example_generator.generate_examples(all_splits, 4)
retrievers = [vr.get_retriever(vectorstore), mq.get_retriever(vectorstore), ct.get_retriever(vectorstore), pd.get_parent_retriever(data, 500, 300), mv.get_summary_retriever(all_splits), mv.get_hypothetical_retriever(all_splits)]
get_contexts = [vr.get_context, mq.get_context, ct.get_context, pd.get_context, mv.get_context, mv.get_context]
results = []
for i in range(len(retrievers)):
    results.append(evaluate_retriever(questions, ground_truth, retrievers[i],  get_contexts[i], True))
print(results)

# evaluate_retriever(questions, ground_truth, vectorstore_retriever.get_retriever(vectorstore),  vectorstore_retriever.get_context, True)
# evaluate_retriever(questions, ground_truth, multiquery.get_retriever(vectorstore), multiquery.get_context, True)
# evaluate_retriever(questions, ground_truth, context_compression.get_retriever(vectorstore), context_compression.get_context, True)
# evaluate_retriever(questions, ground_truth, parent_document.get_retriever(data, 500, 300), parent_document.get_context, True)
# evaluate_retriever(questions, ground_truth, multivector.get_summary_retriever(all_splits), multivector.get_context, True)
# evaluate_retriever(questions, ground_truth, multivector.get_hypothetical_retriever(all_splits), multivector.get_context, True)