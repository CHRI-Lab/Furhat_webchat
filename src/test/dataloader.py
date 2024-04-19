from environment import chat, url
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_all_links(url):
    if "http" not in url:
        return []
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Finding all 'a' tags which typically contain href attribute for links
    links = [
        urljoin(url, a["href"]) for a in soup.find_all("a", href=True) if a["href"]
    ]

    return links

def recursive_loader(url, depth):
    if depth > 0:
        links = get_all_links(url)
        depth -= 1
        if depth > 0:
            for url in links:
                links += recursive_loader(url, depth)
        return links
    return []

# links = recursive_loader(url, 1)
# print(links)

from langchain_community.document_loaders import WebBaseLoader
import re

def get_data(url):

    links = recursive_loader(url, 1)
    print(len(links))

    # load the data from a website
    loader = WebBaseLoader(links)
    data = loader.load()
    for doc in data:
        doc.page_content = re.sub("\\n|\\t", " ", doc.page_content)
    #     doc.page_content = re.sub("[^a-zA-Z' ,\.?!-]", " ", doc.page_content)
    # print(data[0])

    return data