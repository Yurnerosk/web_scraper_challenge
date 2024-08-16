from RPA.Browser.Selenium import Selenium

# Initialize the Selenium library
browser = Selenium()

# Retrieve and print the Selenium WebDriver version
webdriver_version = browser.driver.capabilities['chrome']['chromedriverVersion']
print(f"Selenium WebDriver Version: {webdriver_version}")

# Close the browser (if opened)
# browser.close_browser()
