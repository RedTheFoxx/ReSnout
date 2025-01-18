from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class ChromeRetriever:
    @staticmethod
    def setup_driver():
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    @staticmethod
    async def get_driver(url):
        driver = ChromeRetriever.setup_driver()
        driver.get(url)
        return driver
