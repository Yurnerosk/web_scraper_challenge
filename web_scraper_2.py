from RPA.Browser.Selenium import Selenium
from selenium.webdriver.chrome.options import Options
from typing import Tuple
from configurations_class import ConfigManager
from excel_class import ExcelManager
from RPA.FileSystem import FileSystem
import os
import requests
import re
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
import time

class CustomSelenium:

    excel = ExcelManager()

    def __init__(self) -> None:
        self._browser = Selenium()
        self._options = None
        self._file = FileSystem()
        self._picture_link_list = []
        self._news_list = {
            "title": [],
            "date": [],
            "description": [],
            "picture_filename": [],
            "phrase_count": [],
            "contains_money": [],
        }
        self.set_chrome_options()
        self.set_webdriver()

    def set_chrome_options(self):
        if self._options is None:
            self._options = Options()
            self._options.binary_location = "/usr/bin/chromium"
            self._options.add_argument('--disable-dev-shm-usage')
            # self._options.add_argument('--headless')
            self._options.add_argument('--no-sandbox')
            self._options.add_argument("--disable-extensions")
            self._options.add_argument("--disable-gpu")
            self._options.add_argument('--disable-web-security')
            self._options.add_argument("--start-maximized")
            self._options.add_argument('--remote-debugging-port=9222')
            self._options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return self._options

    def set_webdriver(self):
        self._browser.open_chrome_browser(options=self._options)

    def open_url(self, url: str, screenshot: str = None):
        """Opens the browser and navigates to the input URL."""
        self._browser.go_to(url)

    def kill_popup(self):
        ''' Closes the popup asking if I want to pay for scraping news
        '''
        shadow_host_selector = 'modality-custom-element'
        close_pop_locator = '.met-flyout-close'
        shadow_host = self._browser.find_element(shadow_host_selector)
        time.sleep(8)
        shadow_root = self._browser.execute_javascript("return arguments[0].shadowRoot", shadow_host)
        time.sleep(8)
        close_pop = shadow_root.find_element_by_css_selector(close_pop_locator)
        time.sleep(8)
        close_pop.click()

    # Add other methods from your original class here...

    def news_fetch(self):
        ''' Main function that calls the rest of them
        '''
        self.open_url(ConfigManager.BASE_URL)
        # Your logic to scrape news...

# cs = CustomSelenium()
# cs.news_fetch()
# cs._browser.close_all_browsers()
