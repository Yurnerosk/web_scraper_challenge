"""tasks module
"""

from robocorp.tasks import task
from web_scraper_r_p_a import CustomSelenium

@task
def main():
    """ Calls the tasks
    """
    cs = CustomSelenium()
    cs.news_fetch()
    cs.browser.close_browser()
