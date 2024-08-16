"""tasks module
"""

from robocorp.tasks import task
from web_scraper_rpa import CustomSelenium

@task
def main():
    """ Calls the tasks
    """
    cs = CustomSelenium()
    cs.news_fetch()
    cs.browser.close_browser()
