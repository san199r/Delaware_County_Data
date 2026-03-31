import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 15)

driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
time.sleep(3)
try:
    logout = driver.find_element(By.PARTIAL_LINK_TEXT, "Click here to logout")
    logout.click()
    time.sleep(3)
except:
    pass

try:
    guest_btn = driver.find_element(By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")
    driver.execute_script("arguments[0].click();", guest_btn)
    time.sleep(3)
except:
    pass

driver.switch_to.default_content()
driver.switch_to.frame("bodyframe")

try:
    accept_btn = driver.find_element(By.XPATH, "//input[@id='accept' or @value='Accept']")
    driver.execute_script("arguments[0].click();", accept_btn)
    print("Clicked Accept via JS.")
    time.sleep(5)
except Exception as e:
    print("Failed to click Accept:", e)

driver.switch_to.default_content()
driver.switch_to.frame("bodyframe")
with open("dump_after_accept_real.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)

print("Dumped page source after accept.")
driver.quit()
