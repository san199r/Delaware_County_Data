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
    driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
    time.sleep(2)
    
    # 2. Login as Guest
    try:
        guest = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")))
        driver.execute_script("arguments[0].click();", guest)
        time.sleep(3)
    except:
        pass
        
    # 3. Accept
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    driver.execute_script("executeCommand('Accept');")
    time.sleep(5)
    
    # 4. Click Search Public Records
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    search_xpath = "//div[contains(normalize-space(.), 'Search Public Records')] | //li[contains(normalize-space(.), 'Search Public Records')]"
    search_link = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", search_link)
    print("Clicked Search Public Records")
    time.sleep(8)
    
    # 5. Dump the result
    driver.switch_to.default_content()
    print("Top level URL:", driver.current_url)
    with open("top_level_post_search.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
        
    try:
        driver.switch_to.frame("bodyframe")
        print("Inside bodyframe URL:", driver.current_url)
        with open("bodyframe_post_search.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        # Check for nested frames
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Iframes in bodyframe: {len(iframes)}")
        for ifr in iframes:
            print("  name:", ifr.get_attribute("name"), "id:", ifr.get_attribute("id"), "src:", ifr.get_attribute("src"))
            
    except Exception as e:
        print("Could not switch to bodyframe post search:", e)

finally:
    driver.quit()
