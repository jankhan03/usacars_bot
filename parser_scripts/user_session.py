from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

user_sessions = {}

class UserSession:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1280,800")

        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')

        self.driver = webdriver.Chrome(options=chrome_options, service=service)

    # def __init__(self):
    #     chrome_options = webdriver.ChromeOptions()
    #
    #     chrome_options.add_argument("--headless")
    #     chrome_options.add_argument("--window-size=1280,800")
    #     # chrome_options.add_argument('--ignore-certificate-errors')
    #     # chrome_options.add_argument('--allow-running-insecure-content')
    #     # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    #     # chrome_options.add_argument(f'user-agent={user_agent}')
    #
    #     self.driver = webdriver.Chrome(options=chrome_options)

    def close(self):
        self.driver.quit()


def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    return user_sessions[user_id]

