from robocorp.tasks import task
from web_scraper import CustomSelenium 

@task
def main():
    cs = CustomSelenium()
    cs.news_fetch()