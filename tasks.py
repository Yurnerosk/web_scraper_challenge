from robocorp.tasks import task
from web_scraper import CustomSelenium 

@task
def main():
    my_driver = CustomSelenium()
    my_driver.get_fresh_news()