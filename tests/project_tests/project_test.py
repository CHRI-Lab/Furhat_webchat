import json
import time

from src.RagFramework import RAG_chain  # Import the RAG_chain class from the RagFramework module
from src.url_to_text import url_to_text  # Import the url_to_text function
import textwrap  # Import the textwrap module for text formatting


def main():
    # Load test data from a JSON file named 'input_sample.json'
    with open('input_sample.json', 'r') as file:
        test_cases = json.load(file)  # Parse the JSON file into a Python dictionary

    # Iterate over each test case in the JSON data
    for case_name, details in test_cases.items():
        # Check if the current case is either 'case5' or 'case6'
        if case_name == 'case5' or case_name == 'case6':
            details = test_cases[case_name]
            print(f"\n--- {case_name} ---")  # Print the case name

            # Print the user story from the test case, formatted to a width of 120 characters
            print(textwrap.fill("User Story: " + details['User Story'], width=120))
            url = details['Input Url']  # Get the URL from the test case details
            print(f"\nUsing URL: {url}")
            print("\nReading website...")  # Indicate that the program is reading from the website
            docs = url_to_text(url)  # Retrieve text from the URL
            rag_model = RAG_chain()  # Instantiate the RAG_chain model
            rag_model.retrieve_data(docs)  # Retrieve data using the RAG model

            # Process each question in the test case
            for question in details['Questions']:
                print(f"\nQuestion: {question}")  # Print the question
                answer = rag_model.get_answer(question)  # Retrieve the answer from the RAG model
                paragraphs = answer.split('\n')  # Split the answer into paragraphs
                # Wrap each paragraph to a width of 120 characters for better readability
                wrapped_paragraphs = [textwrap.fill(paragraph, width=120) for paragraph in paragraphs]
                print('\n'.join(wrapped_paragraphs))  # Print the formatted paragraphs
                time.sleep(1)  # Wait for 1 second between processing questions


# Check if the script is run as the main program
if __name__ == "__main__":
    main()  # Execute the main function
