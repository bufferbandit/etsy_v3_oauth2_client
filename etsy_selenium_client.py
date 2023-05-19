from functools import partial

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.firefox import GeckoDriverManager
from lib.etsy_v3_oauth2_client.etsy_client import EtsyOAuth2Client
from selenium.webdriver.support import expected_conditions as EC

import os


def find_element_wait(self, locator, by=By.ID, waiting_time=3, *findElementArgs, **findElementKwargs):
    webdriver_wait = WebDriverWait(self, waiting_time)
    locator_tuple = (by, locator)
    located = EC.visibility_of_element_located(locator_tuple,
                            *findElementArgs, **findElementKwargs)
    element = webdriver_wait.until(located)
    return element

class EtsyOAuth2ClientSelenium(EtsyOAuth2Client):
    def __init__(self, api_token, email, password, host="localhost", port=5000,
                 auto_close_browser=True, auto_refresh_token=False,
                 verbose=True, auto_start_auth=True, scopes=None,
                 access_token=None, refresh_token=None, expiry=None,
                 reference_file_path="./api_reference.json",
                 driver=None):

        if not driver: driver = driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        self.driver = driver
        self.email = email
        self.password = password
        super().__init__(api_token, host, port, auto_close_browser,
                         auto_refresh_token, verbose, auto_start_auth,
                         scopes, access_token, refresh_token, expiry,
                         reference_file_path,
                         process_callback_url=self.login_to_etsy)

    def login_to_etsy(self, url):
        self.driver.get(url)

        email_input_id = "join_neu_email_field"
        password_input_id = "join_neu_password_field"
        login_button_class = "//button[@value='sign-in' and @type='submit']"

        # find_element_wait = lambda
        email_input = driver.find_element_wait(email_input_id)
        password_input = driver.find_element_wait(password_input_id)

        email_input.send_keys(self.email)
        password_input.send_keys(self.password)

        login_button = driver.find_element_wait(login_button_class, By.XPATH)
        login_button.click()


if __name__ == "__main__":
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()),
                               options=webdriver.FirefoxOptions().headless)
    driver.find_element_wait = partial(find_element_wait, driver)
    try:

        AUTO_CLOSE_BROWSER = True
        AUTO_REFRESH_TOKEN = True
        AUTO_START_AUTH = True
        VERBOSE = True
        HOST = "localhost"
        PORT = 5000

        API_TOKEN = input("ADD YOUR API TOKEN ")
        ETSY_EMAIL = input("ADD YOUR EMAIL ")
        ETSY_PASSWORD = input("ADD YOUR PASSWORD ")

        client = EtsyOAuth2ClientSelenium(
            api_token=API_TOKEN,
            email=ETSY_EMAIL, password=ETSY_PASSWORD,
            host=HOST, port=PORT,
            auto_close_browser=AUTO_CLOSE_BROWSER,
            auto_refresh_token=AUTO_REFRESH_TOKEN,
            verbose=VERBOSE, auto_start_auth=AUTO_START_AUTH,
            reference_file_path=os.path.join(
                os.path.dirname(__file__), "./", "api_reference.json"),
            driver=driver
        )
        print(client.ping())


    finally:driver.quit()
