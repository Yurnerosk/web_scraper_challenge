from RPA.Browser.Selenium import Selenium
# from webdriver_manager import ChromeDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from SeleniumLibrary.base import keyword

class ExtendedSelenium(Selenium):

    def __init__(self, *args, **kwargs):
        Selenium.__init__(self, *args, **kwargs)
        cdm = ChromeDriverManager(link_path="AUTO")
        cdm.download_and_install()
        
    @keyword
    def looking_at_element(self, locator):
        element = self.get_webelement(locator)
        self.logger.warn(dir(element))

    @keyword
    def open_site(self, url, **kwargs):
        desired_capabilities = {
            "goog:loggingPrefs" : { 'browser':'ALL',  'driver': 'ALL', 'performance': 'ALL' }
        }
        self.open_browser(
            url=url,
            desired_capabilities=desired_capabilities,
            **kwargs
        )

    @keyword
    def print_webdriver_log(self, logtype):
        print(f"\n{logtype.capitalize()} Log")
        return self.driver.get_log(logtype)
        