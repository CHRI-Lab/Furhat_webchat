from operator import itemgetter
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from PIL import Image
from dotenv import find_dotenv, load_dotenv
from url_to_pic import get_image_urls
import requests
import os
from langchain_community.vectorstores import Chroma
from url_to_text import url_to_text
import base64
import io
from io import BytesIO
from PIL import Image
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from furhat_remote_api import FurhatRemoteAPI
import time

def judge_type(question):
    judge_type_prompt="""
                    You need to determine the type of question based on the user question. 
                    You can also use Chat History to help you understand User Questions.
                    If this is a question about images or location, please answer: 'image chat'. 
                    If this is a text question, please answer: 'text chat'. 
                    Don't have any extra answers.
                    User Question: '''{question}'''
                    Chat History: '''{chat_history}'''
                    """
    rag_chain = PromptTemplate.from_template(judge_type_prompt) | llm | StrOutputParser()
    result=rag_chain.invoke(
        {
            "chat_history":chat_history, 
            "question": question
        }
    )
    return result

def save_images(image_urls, path):
    image_ls=[]
    if not os.path.exists(path):
        os.makedirs(path)
    for url in image_urls:
        filename = url.split("/")[-1]
        filepath = os.path.join(path, filename)
        response = requests.get(url)
        if response.status_code == 200 and filename.endswith((".jpg", ".png", ".jpeg")):
            with open(filepath, "wb") as f:
                f.write(response.content)
            image_ls.append(filepath)
        else:
            print(f"Cannot download the {filename}.")
    return image_ls

def load_images(path):
    image_ls = []
    for filename in os.listdir(path):
        if filename.endswith((".jpg", ".png", ".jpeg")):
            image_ls.append(os.path.join(path, filename))
    return image_ls

def retrieve_text(docs):
    # Split,Emdedding the document
    text_splitter = RecursiveCharacterTextSplitter()
    splits = text_splitter.split_documents(docs)
    vectorstore_text = Chroma.from_documents(collection_name='vectorstore_text',documents=splits, embedding=OpenAIEmbeddings(),persist_directory="./chroma_db_text")
    return vectorstore_text

def retrieve_image(image_ls):
    # Split,Emdedding the document
    vectorstore_image=Chroma(collection_name='vectorstore_image',embedding_function=OpenCLIPEmbeddings(),persist_directory="./chroma_db_image")
    vectorstore_image.add_images(uris=image_ls)
    return vectorstore_image

def generate_based_history_query(question,chat_history,llm):
    based_history_prompt="""
        Use the following latest User Question to formulate a standalone query.
        The query can be understood without the Chat History.
        The output should just be the sentence sutiable for query. 
        If you feel confused, just output the latest User Question.
        Do not provide any answer.
        User Question: '''{question}'''
        Chat History: '''{chat_history}'''
        query:
    """
    rag_chain = PromptTemplate.from_template(based_history_prompt) | llm | StrOutputParser()
    result=rag_chain.invoke(
        {
            "chat_history":chat_history , 
            "question": question
        }
    )
    return result

def qa_retrieval(llm,question,retriever,chat_history):
    qa_system_prompt="""
                    You need to answer User Questions based on Context.
                    You can also use Chat History to help you understand User Questions.
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    Context: '''{context}'''
                    User Questions: '''{question}'''
                    Chat History: '''{chat_history}'''
                    """
    chain = PromptTemplate.from_template(qa_system_prompt) | llm | StrOutputParser()

    result=chain.invoke({"chat_history":chat_history , "question": question,"context": retriever})
    return result

def resize_base64_image(base64_string, size=(128, 128)):
    # Decode the Base64 string
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))
    # Resize the image
    resized_img = img.resize(size, Image.LANCZOS)
    # Save the resized image to a bytes buffer
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)
    # Encode the resized image to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
def retriever_image_prompt_func(data_dict):
    '''{
            "images": ["image1","image2"],
            "context": ["text1","text2"],
            "question": "question"
        }'''
    messages = []
    #Adding images to the messages
    for image in data_dict["images"]:
        image=resize_base64_image(image, size=(120, 120))
        image_message = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            },
        }
        messages.append(image_message)
    # Adding the text message for analysis
    text_message = {
        "type": "text",
        "text": (
                    "You are an image-based Q&A bot. You need to answer the question based on the user question.\n "
                    "If necessary, you can use chat history to help you understand the question.\n "
                    "You need to use parsing the image content to answer the question.\n"
                    "Users can get answers to their questions without having to scroll through the images.\n"
                    "But please don't make up any answers "
                    f"User Question: {data_dict['question']}\n" 
                    f"Context: {data_dict['context']}"
                )
        }
    messages.append(text_message)
    return [HumanMessage(content=messages)]

def qa_based_image_retrieval(llm,question,image,chat_history):
    image_ls=[]
    for i in range(len(image)):
        image_ls.append(image[i].page_content)
    chain = (
        {
            "images": itemgetter("images"),
            "context": itemgetter("context"),
            "question": itemgetter("question"),
        }
        | RunnableLambda(retriever_image_prompt_func)
        | llm
        | StrOutputParser()
    )
    result=chain.invoke({"images":image_ls,"context":chat_history,"question":question}) 
    return result

def listen_to_user():
    while True:  # Start an infinite loop
        result = furhat.listen()  # Listen for 5 seconds
        if result.message and result.success:  # Check if there was any recognized text
            print("User said:", result.message)  # Optional: print what the user said
            break  # Exit the loop if user said something
        else:
            time.sleep(5)
            furhat.say(text="I didn't catch that, could you please repeat?")

    return result.message

if __name__ == '__main__':
    '''furhat remote api'''
    furhat = FurhatRemoteAPI("localhost")

    '''init'''
    load_dotenv(find_dotenv())
    llm = ChatOpenAI(model="gpt-4o",temperature=0)

    url = 'https://melbconnect.com.au' # website url
    image_path = 'test/images' #path to save the image extracted, it will automatically created if not exist.

    # '''get text from url'''
    text_document = url_to_text(url)
    # '''get image from url'''
    image_urls = get_image_urls(url)
    image_ls = save_images(image_urls,image_path)
    image_ls = load_images(image_path)
    

    vectorstore_text=retrieve_text(text_document)
    vectorstore_image = retrieve_image(image_ls)

    # '''load from db'''
    # vectorstore_text = Chroma(collection_name='vectorstore_text',persist_directory="./chroma_db_text", embedding_function=OpenAIEmbeddings())
    # vectorstore_image = Chroma(collection_name='vectorstore_image',persist_directory="./chroma_db_image", embedding_function=OpenCLIPEmbeddings())
    print("Chat started")
    '''chat'''
    chat_history=[]
    while True:
        user_input = input("Press the space bar to start a conversation (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            print("Exit chat.")
            break
        print("Furhat is listening")
        question = listen_to_user()
        judge_type_result=judge_type(question)
        query=generate_based_history_query(question,chat_history,llm)
        if 'text chat'in judge_type_result:
            retriever_text=vectorstore_text.max_marginal_relevance_search(query,k=6)
            result=qa_retrieval(llm,question,retriever_text,chat_history)
            chat_history.extend([HumanMessage(content=question), result])
            # print(result)
        else:
            retriever_image=vectorstore_image.max_marginal_relevance_search(query,k=15)
            result=qa_based_image_retrieval(llm,question,retriever_image,chat_history)
            chat_history.extend([HumanMessage(content=question), result])
            # print(result)
            # for i in range(len(retriever_image)):
            #     img_data = io.BytesIO(base64.b64decode(retriever_image[i].page_content))
            #     img = Image.open(img_data)
            #     img.show()


        print(result)
        print("result len:", len(result))
        print("wait time for the robot speaking:", len(result) * 0.05)

        furhat.say(text=result)

        # Wait for the robot to finish speaking.
        time.sleep(len(result) * 0.05)
