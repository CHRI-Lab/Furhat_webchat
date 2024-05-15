import openai
from furhat_remote_api import FurhatRemoteAPI
import argparse

def setup_arg_parser():
    parser = argparse.ArgumentParser(description="Furhat chat based on web images")
    parser.add_argument("--openai_api_key", type=str, required=True, help="Openai API Key")
    parser.add_argument("--image_info_path", type=str, default='./image_info/melbconnect.com.au_/image_info.txt', help="Directory with image information file")
    return parser

def read_image_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        image_info =  file.read()

    return image_info

def ask_openai(user_question, image_info):
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
                            "text": f"{user_question} {image_info}"
                        },
                    ] 
                }]
            )
    
    return response.choices[0].message.content

def handle_furhat_input(user_question):
    # Simulated input capturing, replace with actual method to capture voice input
    # user_question = "What are these images about?"

    image_info = read_image_info(args.image_info_path)
    
    # Get answer from OpenAI
    answer = ask_openai(user_question, image_info)
    
    # Send the answer back to Furhat
    try:
        furhat.say(text=answer)
    except Exception as e:
        print(f"Error sending response to Furhat: {e}")

def listen_to_user():
    while True:  # Start an infinite loop
        result = furhat.listen()  # Listen for 5 seconds
        if result.message:  # Check if there was any recognized text
            print("User said:", result.message)  # Optional: print what the user said
            break  # Exit the loop if user said something
        else:
            furhat.say(text="I didn't catch that, could you please repeat?")

    return result.message

if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()
    openai.api_key = args.openai_api_key
    furhat = FurhatRemoteAPI("localhost")
    user_question = listen_to_user()
    handle_furhat_input(user_question)
