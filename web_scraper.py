from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from RPA.FileSystem import FileSystem

from typing import Tuple, Optional
from configurations_class import ConfigManager
from excel_class import ExcelManager
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException
import time
import os
import re
import requests
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timezone
from robocorp import log

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
        self._picture_link_list = []
        self.set_chrome_options
        self.setup_output_folder()

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

    def setup_output_folder(self):
        """ Creates output folder if not exists
        If exists deletes all contents
        """
        output_dir = os.path.join('.', 'output')
        if self._file.does_directory_exist(output_dir):
            for dir_file in self._file.list_files_in_directory(output_dir):
                self._file.remove_file(dir_file[0])
        else:
            self._file.create_directory(output_dir)

    def download_article_picture(self):
        """ Downloads the article picture if available based on an input url
        """
        for i in range(len(self._picture_link_list)):
            picture_url = self._picture_link_list[i]
            picture_filename = self._news_list["picture_filename"][i]

            output_folder = os.path.join(os.getcwd(), 'output')
            output_path = os.path.join(output_folder, picture_filename)
            response = requests.get(picture_url)
            # Download
            if response.status_code:
                fp = open(output_path, 'wb')
                fp.write(response.content)
                fp.close()

    def open_url(self, url:str, screenshot:str=None):
        """Opens the browser and navigates to the input URL."""
        self._driver.get(url)

    def set_webdriver(self):
        if self._driver is None:
            self._driver = webdriver.Chrome(options=self._options)
        return self._driver
        print("WebDriver initialized successfully.")

    def get_image_url(self, article:WebElement) -> str:
        image_locator ='img'
        image_element = article.find_element(By.CSS_SELECTOR, image_locator)
        image_src = image_element.get_attribute('src')
        return image_src

    def calculate_daterange(self) -> Tuple[datetime, datetime]:
        """ Returns the start_date and end_date.
        Calculates the dates based on today's date and the MONTHS_NUMBER from the config_manager.py file
        If the MONTHS_NUMBER input equals 0 is replaced to 1 to ensure both 0 an 1 can work to subtract 1 month from today's date
        """
        today = date.today()
        months_number = int(ConfigManager.MONTHS_NUMBER)
        if months_number == 0:
            months_number = 1
        # start_date = (today - relativedelta(months=months_number)).strftime('%Y-%m-%d')
        # end_date = today.strftime('%Y-%m-%d')
        start_date = (today - relativedelta(months=months_number))
        end_date = today

        return start_date, end_date

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
    
    def get_news_date(self, article: WebElement) -> Tuple[datetime, str]:
        """ Returns the Description of the current article by looking for the '.promo-title a' css selector
        """
        date_locator = '.promo-timestamp'
        timestamp_element = article.find_element(By.CSS_SELECTOR, date_locator)
        timestamp_ms = int(timestamp_element.get_attribute('data-timestamp'))
        timestamp_seconds = timestamp_ms / 1000
        datetime_obj = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        
        # Convert to date object
        date_obj = datetime_obj.date()
        date_string = datetime_obj.strftime('%b. %d, %Y %H:%M:%S')  # Example format: "Aug. 14, 2024 12:34:56"
        
        return date_obj, date_string
    
    def get_search_count(self, search_phrase: str, article_text: str) -> int:
        """ counts the amount of occurrences of the search phrase in the article text,
        keeping in mind to lower both
        """
        search_count = article_text.lower().count(search_phrase.lower())
        return search_count

    def money_pattern(self, article_text: str) -> bool:
        patterns = [
            r"\$\d{1,3}(,\d{3})*(\.\d{2})?",  # Matches $11.1 or $111,111.11
            r"\b\d+\s+dollars?\b",             # Matches 11 dollars
            r"\b\d+\s+USD\b"                   # Matches 11 USD
        ]

        # Combine patterns into one
        combined_pattern = r"|".join(patterns)
        if re.search(combined_pattern, article_text, re.IGNORECASE):
            return True
        else:
            return False

    def get_article_picture_filename(self, picture_url: str) -> str:
        """ Returns the picture filename by cleaning the base img URL. """
        # Extract the part after the last '%2F'
        picture_filename = picture_url.split(r'%2F')[-1]
        if '.' not in picture_filename:
            picture_filename = picture_filename + '.jpg'
        return picture_filename

    def get_news_title(self, article: WebElement) -> str:
        """ Returns the Title of the current article by looking for the '.promo-title a' css selector
        """
        title_locator = '.promo-title a'
        title = article.find_element(By.CSS_SELECTOR, title_locator).text
        return title
    
    def turn_page(self):
        """ Returns the Title of the current article by looking for the '.promo-title a' css selector
        """
        turn_page_locator = "div[class='search-results-module-next-page'] a svg"
        turn_page = self._driver.find_element(By.CSS_SELECTOR, turn_page_locator)
        turn_page.click()
        time.sleep(8)

    def kill_popup(self):
        ''' Closes the popup asking if I want to pay for scraping news
        '''
        shadow_host_selector = 'modality-custom-element'
        close_pop_locator = '.met-flyout-close'
        shadow_host = self._driver.find_element(By.CSS_SELECTOR, value=shadow_host_selector)
        time.sleep(8)
        shadow_root = self._driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        time.sleep(8)
        close_pop = shadow_root.find_element(By.CSS_SELECTOR, value=close_pop_locator)
        time.sleep(8)
        close_pop.click()

    def scrolldown(self):
        ''' Scrolls for a distance; it is useful to activate the popup before it messes up
        something else.
        '''
        self._driver.execute_script("window.scrollBy(0, 1000);")

    def scrolltop(self):
        ''' Scrolls back to top position
        '''
        self._driver.execute_script("window.scrollTo(0, 0);")

    def news_fetch(self):
        ''' Main function that calls the rest of them
        '''
        self.open_url(ConfigManager.BASE_URL)
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

        self.scrolldown()
        time.sleep(8)

        self.scrolltop()
        time.sleep(8)

        self.kill_popup()
        time.sleep(8)

        for section in ConfigManager.SECTIONS:
            filter_xpath = ConfigManager.SECTION_CODES[section]
            print(section)
            filter = self._driver.find_element(By.XPATH, filter_xpath)
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
                # Now, retry clicking element A
                filter2 = self._driver.find_element(By.XPATH, filter_xpath)
                filter2.click()
                time.sleep(8)

        drop_down_newest = self._driver.find_elements(By.TAG_NAME, value="Option")
        drop_down_newest[1].click()
        time.sleep(8)
        #Ok. Time to work!
        
        self.start_date, self.end_date = self.calculate_daterange()

        limit_date = self.end_date

        while limit_date >= self.start_date:

            promo_elements = self._driver.find_elements(By.CSS_SELECTOR, value='ps-promo.promo')

            for promo in promo_elements:
                limit_date, date_str = self.get_news_date(promo)
                print(limit_date)
                print(limit_date > self.start_date)
                print(self.start_date, self.end_date)
                if limit_date >= self.start_date:

                    title = self.get_news_title(promo)
                    description = self.get_news_description(promo)
                    
                    title_and_description = title + ' ' + description
                    search_count = self.get_search_count(search_phrase=ConfigManager.SEARCH_PHRASE, article_text=title_and_description)
                    has_money = self.money_pattern(article_text=title_and_description)
                    image_url = self.get_image_url(article=promo)
                    image_name = self.get_article_picture_filename(picture_url = image_url)
                    
                    self._news_list["title"].append(title)
                    self._news_list["description"].append(description)
                    self._news_list["date"].append(date_str)
                    self._news_list["phrase_count"].append(search_count)
                    self._news_list["contains_money"].append(has_money)
                    self._picture_link_list.append(image_url)
                    self._news_list["picture_filename"].append(image_name)

            self.turn_page()

        self.excel.write_in_excel_file(self._news_list)
        for i in range(len(self._news_list["picture_filename"])):
            self.download_article_picture()

# cs = CustomSelenium()
# cs.set_webdriver()
# cs.news_fetch()