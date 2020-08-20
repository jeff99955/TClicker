from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
driver = webdriver.Chrome()
driver.get("http://python.org")
try:
    wait = WebDriverWait(driver, 1000)
    element = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "donate-button"))
    )
    element.click()
    time.sleep(100)
finally:
    driver.quit()