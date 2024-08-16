from robocorp.tasks import task
from web_scraper_2 import CustomSelenium 

@task
def main():
    cs = CustomSelenium()
    cs.news_fetch()
    cs._driver.quit()