from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def capture_screenshot_and_dom(url, screenshot_path='screenshot.png', dom_path='dom.html', wait_time=2):
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
