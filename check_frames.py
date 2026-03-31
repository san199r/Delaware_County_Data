import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)

def dump_page(filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

try:
    driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
    time.sleep(3)
    try:
        driver.find_element(By.PARTIAL_LINK_TEXT, "Click here to logout").click()
        time.sleep(3)
    except:
        pass
    
    # Dump login page frames
    dump_page("dump_login.html")
    
    # Login as guest
    try:
        driver.find_element(By.XPATH, "//input[@value=' Login as Guest ']").click()
    except Exception as e:
        print("Guest login error:", e)
    time.sleep(3)
    
    # Now we are on main.jsp, dump main
    dump_page("dump_main.html")
    
    # Switch to bodyframe for disclaimer
    try:
        driver.switch_to.frame("bodyframe")
        dump_page("dump_main_bodyframe.html")
        driver.find_element(By.XPATH, "//input[@value='Accept' or @id='accept']").click()
    except Exception as e:
        print("Accept error:", e)
    time.sleep(3)
    
    driver.switch_to.default_content()
    dump_page("dump_after_accept.html")
    try:
        driver.switch_to.frame("bodyframe")
        dump_page("dump_after_accept_bodyframe.html")
    except:
        pass

finally:
    driver.quit()
