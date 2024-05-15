# Web Image and Text Scraper, Analyzer, and Furhat Skill Integration

This repository contains a comprehensive toolkit designed for scraping web content (text and images), analyzing images using OpenAI's API, and integrating the results into a Furhat robot skill for interactive voice response.

## Overview

The toolkit includes three main components:

1. **image_sc.py**: Scrapes text and images from specified websites.
2. **image_chat_on_all_images.py**: Analyzes images using OpenAI's API, uploads images to GitHub, and saves generated text and answers.
3. **furhat_image_chat_*.py**: Integrates with Furhat robots to enable interactive voice responses based on the analyzed images.

## Dependencies

- Python 3.x
- `requests`
- `beautifulsoup4`
- `Pillow`
- `openai`
- `langchain_openai`
- `furhat_remote_api`

## Installation

Install the necessary Python packages:

```bash
pip install requests beautifulsoup4 Pillow openai langchain_openai furhat_remote_api
```

## Configuration

Each script accepts command-line arguments for configuration such as URLs, API keys, GitHub tokens, and directory paths.

### Scripts Usage

#### 1. **image_sc.py**

Scrapes a given URL for text and images, saving them in specified directories. Filters out unwanted file types and handles download exceptions.

```bash
python image_sc.py --url [URL] --text_dir [TEXT DIRECTORY] --image_dir [IMAGE DIRECTORY]
```

#### 2. **image_chat_on_all_images.py**

Processes images through OpenAI's API to generate descriptive text and answers related to the images. It compresses images, uploads them to GitHub, and saves the AI-generated text and answers locally.

Usage:
```bash
python image_chat_on_all_images.py --openai_api_key [API KEY] --github_token [TOKEN] --image_folder_path [IMAGE PATH] --repo_name [REPO NAME] --github_username [USERNAME]
```

#### 3. **furhat_image_chat_without_voice_input.py** & **furhat_image_chat_voice_input.py**

These scripts integrate with a Furhat robot, using the generated image information to interact with users. The version with voice input listens actively to user questions.

Usage:
```bash
python furhat_image_chat_without_voice_input.py --openai_api_key [API KEY] --image_info_path [INFO PATH]
```

```bash
python furhat_image_chat_voice_input.py --openai_api_key [API KEY] --image_info_path [INFO PATH]
```

## Usage

Each script is designed to be run independently, provided the necessary parameters are supplied. Ensure the output from one script is correctly utilized as input for subsequent scripts, especially in a deployment environment.

## Deployment

These scripts can be deployed on any standard Python environment. For Furhat integration, ensure the Furhat SDK and remote API are correctly configured on the network.