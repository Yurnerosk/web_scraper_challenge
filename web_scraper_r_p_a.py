""" Main webscraping module
"""

# Standard library imports
import time
import os
import re
from datetime import date, datetime, timezone
from typing import Tuple
import logging

# Third-party imports
import requests
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)
from selenium.webdriver.remote.webelement import WebElement

# Robocorp/RPA imports
from RPA.FileSystem import FileSystem
from RPA.Browser.Selenium import Selenium

# Local application imports
from configurations_class import ConfigManager
from excel_class import ExcelManager

logger = logging.getLogger(__name__)

class CustomSelenium:
    """Class representing a driver"""

    excel = ExcelManager()
    def __init__(self) -> None:
        self.browser = Selenium()
        self._file = FileSystem()
        self._picture_link_list = []
        self.start_date, self.end_date = self.calculate_daterange()
        # Data required by the challenge:
        self._news_list = {
            "title": [],
            "date": [],
            "description": [],
            "picture_filename": [],
            "phrase_count": [],
            "contains_money": [],
            }

    def download_article_picture(self):
        """ Downloads the article picture if available based on an input url
        """
        logger.info('Starting to download pictures.')
        queue = len(self._picture_link_list)
        for i in range(queue):

            picture_url = self._picture_link_list[i]
            picture_filename = self._news_list["picture_filename"][i]

            output_folder = os.path.join(os.getcwd(), 'output')
            output_path = os.path.join(output_folder, picture_filename)
            response = requests.get(picture_url, verify=False, timeout=10)
            # Download
            logger.info(i+1, "requested download of ", queue)
            if response.status_code:
                fp = open(output_path, 'wb')
                fp.write(response.content)
                fp.close()
                logger.info(i+1, "downloaded of ", queue)

    def get_image_url(self, article:WebElement) -> str:
        """ Returns the image link
        """
        image_locator ='img'
        image_element = article.find_element(By.CSS_SELECTOR, image_locator)
        image_src = image_element.get_attribute('src')
        return image_src

    def calculate_daterange(self) -> Tuple[datetime, datetime]:
        """ Returns the start_date and end_date.
        Calculates the dates based on today's date and the MONTHS_NUMBER from the config_manager.py
        file.
        If the MONTHS_NUMBER input equals 0 is replaced to 1 to ensure both 0 an 1 can work
        to subtract 1 month from today's date
        """
        today = date.today()
        months_number = int(ConfigManager.MONTHS_NUMBER)
        if months_number == 0:
            months_number = 1
        # start_date = (today - relativedelta(months=months_number)).strftime('%Y-%m-%d')
        # end_date = today.strftime('%Y-%m-%d')
        start_date = today - relativedelta(months=months_number)
        end_date = today
        logger.info('Calculated daterange')

        return start_date, end_date

    def get_news_description(self, article: WebElement) -> str:
        """ Returns the Description of the current article by looking for the css selector
        """
        description_locator = '.promo-description'
        description = article.find_element(By.CSS_SELECTOR, description_locator).text
        return description

    def get_news_date(self, article: WebElement) -> Tuple[datetime, str]:
        """ Returns the date of the current article by looking for the css selector
        """
        date_locator = '.promo-timestamp'
        timestamp_element = article.find_element(By.CSS_SELECTOR, date_locator)
        timestamp_ms = int(timestamp_element.get_attribute('data-timestamp'))
        timestamp_seconds = timestamp_ms / 1000
        datetime_obj = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)

        # Convert to date object
        date_obj = datetime_obj.date()
        date_string = datetime_obj.strftime('%b. %d, %Y %H:%M:%S')
        # Example format: "Aug. 14, 2024 12:34:56"

        return date_obj, date_string

    def get_search_count(self, search_phrase: str, article_text: str) -> int:
        """ counts the amount of occurrences of the search phrase in the article text,
        keeping in mind to lower both
        """
        search_count = article_text.lower().count(search_phrase.lower())
        return search_count

    def money_pattern(self, article_text: str) -> bool:
        """Finds a pattern defined by the challenge
        """
        patterns = [
            r"\$\d{1,3}(,\d{3})*(\.\d{2})?",  # Matches $11.1 or $111,111.11
            r"\b\d+\s+dollars?\b",             # Matches 11 dollars
            r"\b\d+\s+USD\b"                   # Matches 11 USD
        ]

        # Combine patterns into one
        combined_pattern = r"|".join(patterns)
        if re.search(combined_pattern, article_text, re.IGNORECASE):
            return True
        return False

    def get_article_picture_filename(self, picture_url: str) -> str:
        """ Returns the picture filename by cleaning the base img URL. """
        # Extract the part after the last '%2F'
        picture_filename = picture_url.split(r'%2F')[-1]
        if '.' not in picture_filename:
            picture_filename = picture_filename + '.jpg'
        return picture_filename

    def get_news_title(self, article) -> str:
        """ Returns the Title of the current article by looking for the css selector
        """
        title_locator = '.promo-title a'
        title = self.browser.find_element(
            f"css:{title_locator}",
            parent=article
        ).text
        return title

    def turn_page(self):
        """ Turn to next page to search more results
        """
        turn_page_locator = "div[class='search-results-module-next-page'] a svg"
        turn_page = self.browser.find_element(
            f"css:{turn_page_locator}"
        )
        turn_page.click()
        time.sleep(8)
        logger.info('Next Page!')

    def scrolldown(self):
        ''' Scrolls for a distance; it is useful to activate the popup before it messes up
        something else.
        '''
        self.browser.execute_javascript("window.scrollBy(0, 1000);")

    def scrolltop(self):
        ''' Scrolls back to top position
        '''
        self.browser.execute_javascript("window.scrollTo(0, 0);")

    def navigate_to_search_area(self):
        """ Initial navigation
        """
        self.browser.open_chrome_browser(url=ConfigManager.BASE_URL)

        button_xpath = (
            "//button[@class='flex justify-center items-center h-10 py-0 px-2.5 "
            "bg-transparent border-0 text-header-text-color cursor-pointer transition-colors "
            "hover:opacity-80 xs-5:px-5 md:w-10 md:p-0 md:ml-2.5 md:border md:border-solid "
            "md:border-header-border-color md:rounded-sm lg:ml-3.75']//*[name()='svg']"
        )
        button = self.browser.find_element(
            f"xpath:{button_xpath}"
        )
        button.click()
        search_box_xpath = "//input[@placeholder='Search']"
        search_box = self.browser.find_element(
            f"xpath:{search_box_xpath}"
        )
        search_box.send_keys(ConfigManager.SEARCH_PHRASE)
        confirm_xpath = (
            "//button[@class='flex justify-center items-center transition-colors "
            "transition-bg cursor-pointer w-10 p-0 shrink-0 bg-transparent border-0']"
            "//*[name()='svg']"
        )

        confirm = self.browser.find_element(
            f"xpath:{confirm_xpath}"
        )

        confirm.click()
        time.sleep(8)

        # self.scrolldown()
        # time.sleep(8)

        # self.scrolltop()
        # time.sleep(8)

        # does the popup not apper when control room?
        # self.kill_popup()
        # time.sleep(8)

    def apply_sections(self):
        """ Applies the desired topics
        """
        for section in ConfigManager.SECTIONS:
            filter_xpath = ConfigManager.SECTION_CODES[section]
            logger.info(section, "applied.")
            filter1 = self.browser.find_element(
                f"xpath:{filter_xpath}"
            )
            try:
                # Attempt to click element A
                time.sleep(8)
                filter1.click()
                time.sleep(8)
            except (
                    NoSuchElementException,
                    ElementClickInterceptedException,
                    ElementNotInteractableException
                ):
                # If element A is not found or can't be clicked, click element B first
                time.sleep(8)
                see_all_css = (
                    "body > div:nth-child(4) > ps-search-results-module:nth-child(2) > "
                    "form:nth-child(1) > div:nth-child(2) > ps-search-filters:nth-child(1) > "
                    "div:nth-child(1) > aside:nth-child(1) > div:nth-child(2) > div:nth-child(4) > "
                    "div:nth-child(1) > ps-toggler:nth-child(1) > ps-toggler:nth-child(2) > "
                    "button:nth-child(2) > span:nth-child(1)"
                )
                see_all = self.browser.find_element(
                    f"css:{see_all_css}"
                )
                see_all.click()
                time.sleep(8)
                # Now, retry clicking element A
                filter2 = self.browser.find_element(
                    f"xpath:{filter_xpath}"
                )
                filter2.click()
                time.sleep(8)

        drop_down_newest = self.browser.find_elements("tag:Option")
        drop_down_newest[1].click()
        time.sleep(8)

    def data_extractor(self):
        """ Finds the promo and rips the data we want
        """
        promo_elements = self.browser.find_elements("css:ps-promo.promo")

        for promo in promo_elements:
            limit_date, date_str = self.get_news_date(promo)
            logger.info('Is %s within %s and %s?', limit_date, self.end_date, self.start_date)
            logger.info(limit_date >= self.start_date)
            if limit_date >= self.start_date:

                title = self.get_news_title(promo)
                description = self.get_news_description(promo)

                title_and_description = title + ' ' + description
                search_count = self.get_search_count(
                    search_phrase=ConfigManager.SEARCH_PHRASE,
                    article_text=title_and_description
                )
                has_money = self.money_pattern(article_text=title_and_description)
                image_url = self.get_image_url(article=promo)
                image_name = self.get_article_picture_filename(picture_url = image_url)

                self._news_list["title"].append(title)
                self._news_list["description"].append(description)
                self._news_list["date"].append(date_str[:-9])
                self._news_list["phrase_count"].append(search_count)
                self._news_list["contains_money"].append(has_money)
                self._picture_link_list.append(image_url)
                self._news_list["picture_filename"].append(image_name)

    def news_fetch(self):
        ''' Main function that calls the rest of them
        '''
        logger.info('Initiated news fetch.')
        # not control room
        # self.browser.open_browser(url=ConfigManager.BASE_URL, browser="chrome")
        # control room
        self.navigate_to_search_area()

        logger.info('Applying sections...')

        #Ok. Time to work!
        self.apply_sections()

        limit_date = self.end_date

        while limit_date >= self.start_date:

            self.data_extractor()
            self.turn_page()
        logger.info('Files determined. Starting file creation...')
        self.excel.write_in_excel_file(self._news_list)
        self.download_article_picture()

        logger.info('News fetched')

# not control room
# cs = CustomSelenium()
# cs.news_fetch()
# cs.browser.close_browser()
