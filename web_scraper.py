import logging
from lxml import html
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
# from RPA.core.webdriver import cache, download, start
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from RPA.FileSystem import FileSystem
from typing import Tuple, Optional
from configurations_class import ConfigManager
from excel_class import ExcelManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC

from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timezone
import time
import re
import os
import ssl
import urllib3
import requests

class CustomSelenium:

    excel = ExcelManager()

    def __init__(self) -> None:
        self._driver = None
        self._options = None
        self._file = FileSystem()

        # Data required by the challenge:
        self._news_list = {
            "title": [],
            "date": [],
            "description": [],
            "picture_filename": [],
            "phrase_count": [],
            "contains_money": [],
        }

    
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
        if self._options is None:
            self._options = ChromeOptions()
            self._options.add_argument('--headless')
            self._options.add_argument('--no-sandbox')
            self._options.add_argument("--disable-extensions")
            self._options.add_argument("--disable-gpu")
            self._options.add_argument('--disable-web-security')
            self._options.add_argument("--start-maximized")
            self._options.add_argument('--remote-debugging-port=9222')
            self._options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return self._options

    def set_webdriver(self):
        if self._driver is None:
            self._driver = webdriver.Chrome(options=self._options)
        return self._driver
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
        self._driver.set_window_rect(
            width=target_width,
            height=target_height)

    def open_url(self, url:str, screenshot:str=None):
        """Opens the browser and navigates to the input URL."""
        self._driver.get(url)

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def full_page_screenshot(self, url):
        self._driver.get(url)
        page_width = self._driver.execute_script('return document.body.scrollWidth')
        page_height = self._driver.execute_script('return document.body.scrollHeight')
        self._driver.set_window_size(page_width, page_height)
        self._driver.save_screenshot('screenshot.png')
        self._driver.quit()

    def put_search_in_url(self) -> str:
        """ Returns the base url
        Replaces the auxiliar [search_phrase] with the SEARCH_PHRASE constant from the config_manager.py file.
        """
        url = ConfigManager.BASE_URL.replace('[search_phrase]', ConfigManager.SEARCH_PHRASE)
        return url

    def put_sections_in_url(self, url: str) -> str:
        """ Returns the site url
        Embbeds all the input sections in the base url by replacing the auxiliar %2C[sections] with the corresponding section code.
        The section codes are extracted from the NYTimes site and are constants in the config manager file.
        This means new sections should be coded to work but the efficiency and robustness increases.
        """
        middle = ''
        for section in (ConfigManager.SECTIONS):
            print(section)
            middle = middle + ConfigManager.PREFIX + ConfigManager.SECTION_CODES[section]
            print(middle)
        url = url[:-4] + middle + url[-4:]
        return url
    
    def download_image(self, img_url, save_path):
        """Download an image from a URL and save it to the specified path."""
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()  # Check for HTTP errors
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Image saved to {save_path}")
        except requests.RequestException as e:
            print(f"Failed to download image: {e}")


    def scrape_and_download_images(self, url):
        """Scrape the provided URL and download images where class='promo-timestamp' is a number higher than 0."""
        try:
            response = requests.get(url)
            # Parse the page content using lxml
            tree = html.fromstring(response.content)
            # Convert lxml tree to BeautifulSoup object for easier processing
            soup = BeautifulSoup(html.tostring(tree, encoding='unicode'), 'lxml')

            # Loop through elements to find those with class 'promo-timestamp' with a number higher than 0
            for element in soup.find_all(class_='promo-timestamp'):
                try:
                    # Extract and convert the timestamp to an integer
                    timestamp = int(element.get_text().strip())
                    if timestamp > 0:
                        # Assuming the image URL is in an <img> tag within the element or its parent
                        img_tag = element.find('img')
                        if img_tag and img_tag.get('src'):
                            img_url = img_tag['src']
                            # Download the image
                            img_name = img_url.split('/')[-1]  # Extract image name from URL
                            save_path = os.path.join('output', img_name)
                            self.download_image(img_url, save_path)
                except ValueError:
                    # Handle the case where conversion to integer fails
                    continue
        except requests.RequestException as e:
            print(f"Failed to retrieve the URL: {e}")

    def click_element(driver, xpath, timeout=10):
        """Helper function to click an element with a retry mechanism."""
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            return True
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException) as e:
            print("Error clicking element with XPath" , xpath)
            return False

    def get_news_title(self, article: WebElement) -> str:
        """ Returns the Title of the current article by looking for the '.promo-title a' css selector
        """
        title_locator = '.promo-title a'
        title = article.find_element(By.CSS_SELECTOR, title_locator).text
        return title

    def get_news_description(self, article: WebElement) -> str:
        """ Returns the Description of the current article by looking for the '.promo-title a' css selector
        """
        description_locator = '.promo-description'
        description = article.find_element(By.CSS_SELECTOR, description_locator).text
        return description
    
    def get_news_date(self, article: WebElement) -> str:
        """ Returns the Description of the current article by looking for the '.promo-title a' css selector
        """
        date_locator = '.promo-timestamp'
        timestamp_element = article.find_element(By.CSS_SELECTOR, date_locator)
        timestamp_ms = int(timestamp_element.get_attribute('data-timestamp'))
        timestamp_seconds = timestamp_ms / 1000
        date = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        date_string = date.strftime('%b. %d, %Y %H:%M:%S')  # Example format: "Aug. 14, 2024 12:34:56"
        return date_string
    def news_fetch(self):
        ''' Main function that calls the rest of them
        '''
        self.open_url('https://www.latimes.com/')
        button_xpath = "//button[@class='flex justify-center items-center h-10 py-0 px-2.5 bg-transparent border-0 text-header-text-color cursor-pointer transition-colors hover:opacity-80 xs-5:px-5 md:w-10 md:p-0 md:ml-2.5 md:border md:border-solid md:border-header-border-color md:rounded-sm lg:ml-3.75']//*[name()='svg']"
        button = self._driver.find_element(By.XPATH, button_xpath)
        button.click()
        search_box_xpath = "//input[@placeholder='Search']"
        search_box = self._driver.find_element(By.XPATH, search_box_xpath)
        search_box.send_keys(ConfigManager.SEARCH_PHRASE)
        confirm_xpath = "//button[@class='flex justify-center items-center transition-colors transition-bg cursor-pointer w-10 p-0 shrink-0 bg-transparent border-0']//*[name()='svg']"
        confirm = self._driver.find_element(By.XPATH, confirm_xpath)
        confirm.click()

        
        
        time.sleep(8)
        
        for section in ConfigManager.SECTIONS:
            filter_xpath = ConfigManager.SECTION_CODES[section]
            print(section)
            filter = self._driver.find_element(By.XPATH, filter_xpath)

            # filter.click()
            # time.sleep(8)
            try:
                # Attempt to click element A
                time.sleep(8)
                filter.click()
                time.sleep(8)
            except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                # If element A is not found or can't be clicked, click element B first
                time.sleep(8)
                see_all = self._driver.find_element(By.CSS_SELECTOR, "body > div:nth-child(4) > ps-search-results-module:nth-child(2) > form:nth-child(1) > div:nth-child(2) > ps-search-filters:nth-child(1) > div:nth-child(1) > aside:nth-child(1) > div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > ps-toggler:nth-child(1) > ps-toggler:nth-child(2) > button:nth-child(2) > span:nth-child(1)")
                see_all.click()
                time.sleep(8)

        #         # Now, retry clicking element A
                filter2 = self._driver.find_element(By.XPATH, filter_xpath)
                filter2.click()
                time.sleep(8)


        drop_down_newest = self._driver.find_elements(By.TAG_NAME, value="Option")
        drop_down_newest[1].click()
        time.sleep(8)
        #Ok. Time to work!

        promo_elements = self._driver.find_elements(By.CSS_SELECTOR, value='ps-promo.promo')

        for promo in promo_elements:
            print(promo)
            title = self.get_news_title(promo)
            description = self.get_news_description(promo)
            date = self.get_news_date(promo)
            self._news_list["title"].append(title)
            self._news_list["description"].append(description)
            self._news_list["date"].append(date)

        self.excel.write_in_excel_file(self._news_list)




        


cs = CustomSelenium()

# try:
    # driver = cs.set_webdriver()
cs.set_webdriver()
cs.news_fetch()
    # use the driver in some way here
# finally:
    # ensure that driver is properly closed
    # cs.close()
