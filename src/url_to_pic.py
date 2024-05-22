import re
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def extract_url(style):
    # Use regex to find URLs within a style string
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
    if match:
        return match.group(1)
    return None

def get_image_urls(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--disable-gpu')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.find_all(lambda tag: tag.name in ['img', 'div', 'a'] and any(tag.get(attr) for attr in ['src', 'href', 'data-src', 'style']))

    image_urls = []
    for element in elements:
        image_src = None
        # Check for image links in various attributes
        for attr in ['src', 'href', 'data-src', 'style']:
            if element.get(attr):
                if attr == 'style':
                    image_src = extract_url(element[attr])
                else:
                    image_src = element[attr]

                # Match against image file extensions
                if image_src and re.search(r'\.(jpg|jpeg|png|svg)$', image_src, re.IGNORECASE):
                    if not image_src.startswith(('http', 'https')):
                        image_src = urlparse(url).scheme + '://' + urlparse(url).netloc + image_src

                    image_urls.append(image_src)

    driver.quit()
    return image_urls
if __name__ == '__main__':
    # Call the function and print the results
    image_urls = get_image_urls('https://cis.unimelb.edu.au/')
    print(image_urls)
