import time
import gradio as gr

from src.chatbot import WebChatbot


def slow_echo(message,history):
    answer = chatbot.invoke(question=message)
    for i in range(len(answer)):
        time.sleep(0.01)
        yield answer[: i + 1]

demo = gr.ChatInterface(slow_echo).queue()

if __name__ == "__main__":
    chatbot = WebChatbot(url='https://melbconnect.com.au/')
    demo.launch()

