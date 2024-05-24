# Project Source Code Files

This directory contains the source files for our project, organized into different subdirectories and modules. Each module serves a specific function within the project, as outlined below:

## How to Use
- 1.Start the remote api of furhat sdk.
- 2.Input the url and a new image_path to save image(Make sure you do that) on line 195 on `furhat_chat.py`.
- 3.Run `furhat_chat.py`
- 4.Press enter to start a chat round with the robot.

## Directory Structure

- `image_chat/`: Contains files related to handling image-based chat functionalities.(To be completed)
- `prompt/`: Includes scripts for generating and managing prompts.
- `rag_methods/`: Stores the RAG (Retrieval-Augmented Generation) related scripts for the project.
- `test`: Stores crawled image folder.

## Files in `rag_methods/`
- `furhat_chat.py`: The main function of our project
- `chatbot.py`: Implements the chatbot interface.
- `RagFramework.py`: Core library for the RAG implementation, handling the retrieval and generation logic.
- `requirements.txt`: Lists all the dependencies required to run the scripts in this directory.
- `url_to_text.py`: Contains functionality to extract text from URLs.
- `url_to_pic.py`: Contains functionality to extract image from URLs.



```bash
pip install -r requirements.txt



