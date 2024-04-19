import os
from io import BytesIO
from PIL import Image
import openai
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import requests
from PIL import Image
from io import BytesIO
import base64
import json
import argparse

def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Images to text")
    parser.add_argument("--openai_api_key", type=str, required=True, help="Openai API Key")
    parser.add_argument("--github_token", type=str, required=True, help="Github Token")
    parser.add_argument("--image_path", type=str, default="./sc_images/Video-Thumbnail.jpg", help="Images path")
    parser.add_argument("--repo_name", type=str, default="image_warehouse", help="Github repo name")
    parser.add_argument("--github_username", type=str, default="ShaohuiWANG-1", help="Github Username")
    return parser

def compress_image(image_path, max_size_mb=20, step=5): # 20MB limit
    quality = 95
    while True:
        img = Image.open(image_path)
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=quality)
        if img_io.tell() / 1024 / 1024 < max_size_mb:
            break
        quality -= step
        if quality < 20:
            raise Exception("Cannot compress image to the desired size")
    img_io.seek(0)
    return img_io

def upload_to_github(image_io, filename, repo_name, user_name, token):
    url = f"https://api.github.com/repos/{user_name}/{repo_name}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    # First, try to retrieve the existing file to get its SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
    else:
        sha = None  # If the file does not exist, sha will be None

    # Prepare the data payload
    data = {
        "message": "upload image",
        "content": base64.b64encode(image_io.getvalue()).decode('utf-8'),
        "sha": sha  # This will be None if the file is new
    }
    if sha:
        data['sha'] = sha  # Only include the sha if updating the file

    # Attempt to upload/update the file
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200 or response.status_code == 201:
        return response.json()['content']['download_url']
    else:
        response.raise_for_status()  # This will raise an error if the upload failed

def ask_openai_about_image(image_url):
    response = openai.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0.2,
                top_p=1,
                n=1,
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": [
                        {
                            "type": "text",
                            "text": "What is in the image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ] 
                }]
            )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()
    openai.api_key = args.openai_api_key
    image_path = args.image_path
    image_name = os.path.basename(image_path)
    image_io = compress_image(image_path)
    image_url = upload_to_github(image_io, image_name, args.repo_name, args.github_username, args.github_token)
    result = ask_openai_about_image(image_url)
    print(result)
