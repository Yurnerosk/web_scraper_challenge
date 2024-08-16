"""tasks module
"""

from robocorp.tasks import task
from web_scraper_rpa import CustomSelenium 

@task
def main():
    cs = CustomSelenium()
    cs.news_fetch()
    cs._browser.close_browser()