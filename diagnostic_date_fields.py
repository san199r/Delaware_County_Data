import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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
    
    search_xpath = '//div[contains(@class,"datagrid-cell") and contains(normalize-space(.),"Search Public Records")]'
    search_item = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", search_item)
    print("Clicked Search Public Records.")
    time.sleep(8)
    
    # 5. DUMP SEARCH PAGE
    driver.switch_to.default_content()
    # It might be in bodyframe.
    try:
        driver.switch_to.frame("bodyframe")
        print("Inside bodyframe. URL:", driver.current_url)
        with open("dump_search_page_bodyframe.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        # Check for date fields in bodyframe
        xpath_3 = "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])[3]"
        fields = driver.find_elements(By.XPATH, "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])")
        print(f"Found {len(fields)} datebox textbox-text fields in bodyframe")
        
        # Check for iframes in bodyframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} inner iframes")
        for ifr in iframes:
            print("  Name:", ifr.get_attribute("name"), "Src:", ifr.get_attribute("src"))
            
    except Exception as e:
        print("Failed to switch to bodyframe:", e)

finally:
    driver.quit()
