import logging
import requests
import lxml
from bs4 import BeautifulSoup
from selenium import webdriver
# from RPA.core.webdriver import cache, download, start
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from RPA.FileSystem import FileSystem
from typing import Tuple, Optional
from configurations_class import ConfigManager
# from excel_class import ExcelManager

from dateutil.relativedelta import relativedelta
from datetime import date
import requests
import time
import re
import os
import ssl
import urllib3

class CustomSelenium:

    def __init__(self) -> None:
        self.driver = None
        self.file = FileSystem()

        # Data required by the challenge:
        self.news_list = {
            "title": [],
            "date": [],
            "description": [],
            "picture_filename": [],
            "phrase_count": [],
            "contains_money": [],
        }
        # Create output folder
        # self.setup_output_folder()
        # self.set_webdriver()
    
    def setup_output_folder(self):
        """ Creates output folder if not exists
        If exists deletes all contents
        """
        output_dir = os.path.join('.', 'output')
        if self.file.does_directory_exist(output_dir):
            for dir_file in self.file.list_files_in_directory(output_dir):
                self.file.remove_file(dir_file[0])
        else:
            self.file.create_directory(output_dir)

    def calculate_daterange(self) -> Tuple[str, str]:
        """ Returns the start_date and end_date.
        Calculates the dates based on today's date and the MONTHS_NUMBER from the config_manager.py file
        If the MONTHS_NUMBER input equals 0 is replaced to 1 to ensure both 0 an 1 can work to subtract 1 month from today's date
        """
        today = date.today()
        months_number = ConfigManager.MONTHS_NUMBER
        if not months_number: months_number = 1
        start_date = (today - relativedelta(months=months_number)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        return start_date, end_date

    def set_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-web-security')
        options.add_argument("--start-maximized")
        options.add_argument('--remote-debugging-port=9222')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return options

    def set_webdriver(self):
        # options = self.set_chrome_options()
        # service = Service(ChromeDriverManager().install())
        # self.driver = webdriver.Chrome(service=service, options=options)

        options = webdriver.ChromeOptions()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        print("WebDriver initialized successfully.")

    def set_page_size(self, width:int, height:int):
        #Extract the current window size from the driver
        current_window_size = self.driver.get_window_size()

        #Extract the client window size from the html tag
        html = self.driver.find_element_by_tag_name('html')
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))

        #"Internal width you want to set+Set "outer frame width" to window size
        target_width = width + (current_window_size["width"] - inner_width)
        target_height = height + (current_window_size["height"] - inner_height)
        self.driver.set_window_rect(
            width=target_width,
            height=target_height)

    def open_url(self, url:str, screenshot:str=None):
        """Opens the browser and navigates to the input URL."""
        self.driver.get(url)

    def driver_quit(self):
        if self.driver:
            self.driver.quit()

    def full_page_screenshot(self, url):
        self.driver.get(url)
        page_width = self.driver.execute_script('return document.body.scrollWidth')
        page_height = self.driver.execute_script('return document.body.scrollHeight')
        self.driver.set_window_size(page_width, page_height)
        self.driver.save_screenshot('screenshot.png')
        self.driver.quit()

    def news_fetch(self):
        ''' Main function that calls the rest of them
        '''

my_driver = CustomSelenium()
# my_driver.set_webdriver()
my_driver.setup_output_folder()
my_driver.driver_quit()

# my_driver = CustomSelenium()
# options = my_driver.set_chrome_options()
# my_driver.set_webdriver()
# my_link = 'https://gothamist.com/'
# # my_driver.open_url(url=my_link)
# my_driver.full_page_screenshot(url = my_link)
# my_driver.driver_quit()