import os
import openai
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# 设置API密钥
openai.api_key = ""
os.environ["OPENAI_API_KEY"] = openai.api_key

# 数据加载
loader = WebBaseLoader("https://melbconnect.com.au/")
data = loader.load()

# print(data)

# 数据过滤
def filter_data(data, conditions):
    filtered_data = [d for d in data if all(condition(d) for condition in conditions)]
    return filtered_data

# # 示例过滤条件：长度大于100字符
# conditions = [lambda d: len(d) > 100]
# filtered_data = filter_data(data, conditions)

# 文本分割
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
# all_splits = text_splitter.split_documents(filtered_data)
all_splits = text_splitter.split_documents(data)

# 嵌入并存储数据
vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())

# 检索
retriever = vectorstore.as_retriever(k=4)
retrieved_docs = retriever.invoke("Tell me about the latest news")

# 转换检索到的文档为字符串，作为GPT模型的上下文
context = "\n".join([doc.page_content for doc in retrieved_docs])

# 激活ChatOpenAI实例
# chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)


# 使用检索到的上下文生成回答
# response = chat.complete(prompt="Tell me about the latest news", context=context)

# print(context)

response = openai.chat.completions.create(
                model='gpt-3.5-turbo-1106',
                temperature=0.2,
                top_p=1,
                messages=[
                    {"role": "system", "content": "You need to answer the user with this information: " + context},
                    {"role": "user", "content": "Tell me about the latest news about Melbourne Connect"}]
            )

print(response.choices[0].message.content)
