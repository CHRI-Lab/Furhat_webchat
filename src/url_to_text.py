import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time

from webdriver_manager.chrome import ChromeDriverManager


def url_to_text(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920x1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    # time.sleep(2)  # Delay to ensure all dynamic content has loaded

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text_content = soup.get_text()

    dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")

    for i in range(len(dynamic_divs)):
        try:
            text_content += dynamic_divs[i].text
        except StaleElementReferenceException:
            # If element is stale, refetch elements and try to access it again
            dynamic_divs = driver.find_elements(By.CSS_SELECTOR, "div")
            text_content += dynamic_divs[i].text

    driver.quit()
    return format_text(text_content)


def format_text(text):
    # Replace all occurrences of two or more consecutive tab characters with a single tab
    text = re.sub(r'\t{2,}', '\t', text)
    # Replace all occurrences of three or more consecutive newline characters with exactly two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Return the formatted text
    return text

if __name__ == '__main__':
    text = url_to_text('https://melbconnect.com.au/')
    print(len(text))
    print(text)
