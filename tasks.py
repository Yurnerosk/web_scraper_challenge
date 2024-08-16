from robocorp.tasks import task
from web_scraper_RPA import CustomSelenium 

@task
def main():
    cs = CustomSelenium()
    cs.news_fetch()
    cs._browser.close_browser()