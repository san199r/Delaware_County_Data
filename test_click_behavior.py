import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. Setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    print("Loading disclaimer...")
    driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
    time.sleep(2)
    
    # 2. Login as Guest
    print("Logging in as Guest...")
    guest = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")))
    driver.execute_script("arguments[0].click();", guest)
    time.sleep(5)
        
    # 3. Accept Disclaimer
    print("Accepting Disclaimer...")
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    driver.execute_script("executeCommand('Accept');")
    time.sleep(5)
    
    # 4. Click Search Public Records
    print("Clicking Search Public Records...")
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    
    # Try the user-provided XPath
    search_xpath = '//div[contains(@class,"datagrid-cell") and contains(normalize-space(.),"Search Public Records")]'
    search_item = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    
    # Record window handles to see if a popup opens
    old_handles = driver.window_handles
    print("Window handles before click:", old_handles)
    
    # Try a real click
    try:
        search_item.click()
    except Exception as e:
        print("Standard click failed, trying JS click...", e)
        driver.execute_script("arguments[0].click();", search_item)
    
    print("Clicked Search Public Records. Waiting 10s for navigation...")
    time.sleep(10)
    
    new_handles = driver.window_handles
    print("Window handles after click:", new_handles)
    
    if len(new_handles) > len(old_handles):
        print("Switching to new window...")
        driver.switch_to.window(new_handles[-1])
        
    driver.switch_to.default_content()
    print("Current top-level URL:", driver.current_url)
    
    with open("diagnostic_final_click.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    print("Dumping iframes...")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for ifr in iframes:
        print("  Frame:", ifr.get_attribute("name"), "id:", ifr.get_attribute("id"), "src:", ifr.get_attribute("src"))

finally:
    print("Closing browser in 5s...")
    time.sleep(5)
    driver.quit()
