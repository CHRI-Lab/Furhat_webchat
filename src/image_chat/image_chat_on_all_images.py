import os
from io import BytesIO
from PIL import Image
import openai
from langchain_openai import ChatOpenAI
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
    parser.add_argument("--image_folder_path", type=str, default="./scraped_images/melbconnect.com.au_", help="Directory with images")
    parser.add_argument("--repo_name", type=str, default="image_warehouse", help="Github repo name")
    parser.add_argument("--github_username", type=str, default="ShaohuiWANG-1", help="Github username")
    parser.add_argument("--use_image_name_as_tag", type=bool, default=False, help="Image tag name")
    parser.add_argument("--save_dir", type=str, default="image_info/melbconnect.com.au_", help="Save path")
    
    return parser

from PIL import Image
from io import BytesIO

def compress_image(image_path, max_size_mb=20, step=5):
    quality = 95
    img = Image.open(image_path)

    # if it's RGBA，convert it to RGB
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    while True:
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=quality)
        # Check if the image size meets the requirements
        if img_io.tell() / 1024 / 1024 < max_size_mb:
            break
        quality -= step
        if quality < 20:
            raise Exception("Cannot compress image to the desired size")
    img_io.seek(0)
    return img_io


def upload_to_github(image_io, filename, repo_name, user_name, token):
    url = f"https://api.github.com/repos/{user_name}/{repo_name}/contents/{filename}"
    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    sha = response.json().get('sha', None) if response.status_code == 200 else None

    data = {"message": "upload image", "content": base64.b64encode(image_io.getvalue()).decode('utf-8'), "sha": sha}
    response = requests.put(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()['content']['download_url']

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
                            "text": "What is this image about?"
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

    answers_text = []

    for image_file in os.listdir(args.image_folder_path):
        image_path = os.path.join(args.image_folder_path, image_file)
        if os.path.isfile(image_path):
            image_io = compress_image(image_path)
            image_url = upload_to_github(image_io, image_file, args.repo_name, args.github_username, args.github_token)
            answer = ask_openai_about_image(image_url)
            if args.use_image_name_as_tag:
                answers_text.append(f"<image_info: {image_file}>{answer}</image_info: {image_file}>")
            else:
                answers_text.append(f"<image_info>{answer}</image_info>")

    os.makedirs(args.save_dir, exist_ok=True)

    with open(os.path.join(args.save_dir, 'image_info.txt'), "w", encoding="utf-8") as f:
        f.write("\n".join(answers_text))
