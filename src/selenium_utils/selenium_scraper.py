# Utilities for Selenium-based browser automation
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def capture_screenshot_and_dom(url, screenshot_path='screenshot.png', dom_path='dom.html', wait_time=2):
    """
    Loads the given URL in headless Chrome, saves a screenshot and the DOM HTML.
    Args:
        url (str): The URL to visit.
        screenshot_path (str): Path to save the screenshot.
        dom_path (str): Path to save the DOM HTML.
        wait_time (int): Seconds to wait for page to load.
    Returns:
        tuple: (screenshot_path, dom_path)
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(wait_time)
        driver.save_screenshot(screenshot_path)
        with open(dom_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
    finally:
        driver.quit()
    return screenshot_path, dom_path
