import os
import shutil
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import argparse

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def delete_unwanted_files(directory, valid_extensions=('.jpg', '.jpeg', '.png')):
    for filename in os.listdir(directory):
        if not filename.lower().endswith(valid_extensions):
            os.remove(os.path.join(directory, filename))
            print(f"Deleted: {filename}")

def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Web scraper for images and text")
    parser.add_argument("--url", type=str, default="https://melbconnect.com.au/", help="URL of the website to scrape")
    parser.add_argument("--text_dir", type=str, default="scraped_text", help="Directory to save text")
    parser.add_argument("--image_dir", type=str, default="scraped_images", help="Directory to save images")
    return parser

if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()

    response = requests.get(args.url)
    web_content = response.text
    soup = BeautifulSoup(web_content, 'html.parser')

    parsed_url = urlparse(args.url)
    sanitized_filename = sanitize_filename(parsed_url.netloc + parsed_url.path)  # use url as folder name
    image_folder_path = os.path.join(args.image_dir, sanitized_filename)
    os.makedirs(image_folder_path, exist_ok=True)

    text_folder_path = os.path.join(args.text_dir, sanitized_filename)
    os.makedirs(text_folder_path, exist_ok=True)

    with open(os.path.join(text_folder_path, 'saved_text.txt'), 'w', encoding='utf-8') as file:
        paragraphs = soup.find_all('p')
        for paragraph in paragraphs:
            file.write(paragraph.text + '\n')

    images = soup.find_all('img')
    for image in images:
        try:
            image_url = urljoin(args.url, image['src'])
            if image_url.lower().endswith('.gif'):
                continue

            response = requests.get(image_url)
            if response.status_code == 200:
                image_name = sanitize_filename(image_url.split('/')[-1])
                with open(os.path.join(image_folder_path, image_name), 'wb') as file:
                    file.write(response.content)
        except Exception as e:
            print(f"Failed to process {image_url}: {str(e)}")

    delete_unwanted_files(image_folder_path)
