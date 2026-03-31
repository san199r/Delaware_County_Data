import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)

def print_page():
    print(driver.current_url)

driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
time.sleep(3)
print_page()
try:
    logout = driver.find_element(By.PARTIAL_LINK_TEXT, "Click here to logout")
    logout.click()
    time.sleep(3)
    print_page()
except Exception as e:
    pass

with open("step_login.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

try:
    guest = driver.find_element(By.PARTIAL_LINK_TEXT, "Login as Guest")
    guest.click()
    time.sleep(3)
    print_page()
except Exception:
    try:
        guest2 = driver.find_element(By.XPATH, "//input[@value='Guest Login' or contains(@value, 'Guest')]")
        guest2.click()
        time.sleep(3)
    except:
        pass

with open("step_disclaimer.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

try:
    accept = driver.find_element(By.XPATH, "//input[@value='Accept' or contains(@value, 'Accept')]")
    accept.click()
    time.sleep(3)
    print_page()
except Exception:
    pass

with open("step_nav.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

driver.quit()
