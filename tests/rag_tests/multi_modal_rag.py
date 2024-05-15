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

def is_base64(s):
    """Check if a string is Base64 encoded"""
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except Exception:
        return False
    
def retrieve_text(docs):
    # Split,Emdedding the document
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap = 100)
    splits = text_splitter.split_documents(docs)
    vectorstore_text = Chroma.from_documents(collection_name='vectorstore_text',documents=splits, embedding=OpenAIEmbeddings(),persist_directory="./chroma_db_text")
    return vectorstore_text

def retrieve_image(image_ls):
    # Split,Emdedding the document
    vectorstore_image=Chroma(collection_name='vectorstore_image',embedding_function=OpenCLIPEmbeddings(),persist_directory="./chroma_db_image")
    vectorstore_image.add_images(uris=image_ls)
    return vectorstore_image

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

def resize_base64_image(base64_string, size=(128, 128)):
    """
    Resize an image encoded as a Base64 string.

    Args:
    base64_string (str): Base64 string of the original image.
    size (tuple): Desired size of the image as (width, height).

    Returns:
    str: Base64 string of the resized image.
    """
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
        image=resize_base64_image(image, size=(60, 60))
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
                    "Please find the most relevant images to the User Question.\n "
                    "You can use Context to help you understand the content in questions and images.\n "
                    "You need to find all images that are relevant to the User Question and Context.\n"
                    "Your output is only the list, which includes the index of each relevant image in the image_message, "
                    "as well as the description of the image content."
                    "output format(Do not include any Spaces in the string):[[index=0,description=''],[index=1,description=''], [index=2,description='']]\n"
                    f"User Question: {data_dict['question']}\n" 
                    f"Context: {data_dict['context']}"
                )
        }
    messages.append(text_message)
    return [HumanMessage(content=messages)]

def retriever_best_images(image,text,llm,query):
    text_ls=[]
    image_ls=[]
    for i in range(len(text)):
        text_ls.append(text[i].page_content)
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
    result=chain.invoke({"images":image_ls,"context":text_ls,"question":query}) 
    return result


def qa_retrieval(llm,question,retriever,image_description,chat_history):
    qa_system_prompt="""
                    You need to answer User Questions based on Context.
                    You can also use Chat History to help you understand User Questions.
                    If there are some Image Descriptions, you should summary them at the end of your answer.
                    If you don't know the answer, just say that you don't know, don't try to make up an answer.
                    Context: '''{context}'''
                    User Questions: '''{question}'''
                    Chat History: '''{chat_history}'''
                    Image Description: '''{image_description}'''
                    """
    chain = PromptTemplate.from_template(qa_system_prompt) | llm | StrOutputParser()

    result=chain.invoke({"chat_history":chat_history ,"image_description":image_description, "question": question,"context": retriever})
    return result

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    '''init'''
    url = 'https://melbconnect.com.au/'
    image_path='src/images'
    retriever_image = True

    '''get text from url'''
    # text_document = url_to_text(url)
    

    '''get image from url'''
    # image_urls = get_image_urls(url)
    # image_ls = save_images(image_urls,image_path)
    # image_ls = load_images(image_path)

    # '''generate vectorstore'''
    # vectorstore_text=retrieve_text(text_document)
    # if retriever_image:
    #     vectorstore_image = retrieve_image(image_ls)

    # '''load from db'''
    vectorstore_text = Chroma(collection_name='vectorstore_text',persist_directory="./chroma_db_text", embedding_function=OpenAIEmbeddings())
    vectorstore_image = Chroma(collection_name='vectorstore_image',persist_directory="./chroma_db_image", embedding_function=OpenCLIPEmbeddings())


    '''run rag'''
    llm_text = ChatOpenAI(model="gpt-4o",temperature=0)
    llm_multi_modal = ChatOpenAI(model="gpt-4o",temperature=0)
    question=input("Question:")
    chat_history=[]
    while True:
        query=generate_based_history_query(question,chat_history,llm_text)
        print('query:',query)
        retriever_text=vectorstore_text.max_marginal_relevance_search(query,k=6)
        # print('retriever_text:',retriever_text)
        if retriever_image:
            retriever_image=vectorstore_image.max_marginal_relevance_search(query,k=10)
            images_result_str=retriever_best_images(retriever_image,retriever_text,llm_multi_modal,query)
            print(images_result_str)
            images_result_str.strip()
            matches = re.findall(r"\[index=(\d+),description='(.*?)']", images_result_str)
            print('matches:',matches)
            if matches:
                image_indexes = [int(match[0]) for match in matches]
                image_description = [match[1] for match in matches]
            else:
                image_indexes = []
                image_description = []
        else:
            image_indexes = []
            image_description = []
        '''show answer'''
        rag_answer=qa_retrieval(llm_text,question,retriever_text,image_description,chat_history)
        print('answer:',rag_answer)
        chat_history.extend([HumanMessage(content=question), rag_answer])
        '''show image'''
        print('image description:',image_description)
        for i in image_indexes:
            img_data = io.BytesIO(base64.b64decode(retriever_image[i].page_content))
            img = Image.open(img_data)
            img.show()
        question=input("Question:")
    




