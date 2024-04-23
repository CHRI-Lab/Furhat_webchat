# set environment variable
import os
os.environ['OPENAI_API_KEY'] = ''

# https://github.com/COMP90082-2024-SM1/QA-Koala

from langchain_openai import ChatOpenAI

chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)

url="https://www.unimelb.edu.au/"
# url = "https://python.langchain.com/docs/modules/"
# url = "https://library.unimelb.edu.au/library-locations-and-opening-hours"


