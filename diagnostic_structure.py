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
    
    # Try all possible ways to find the Search Public Records item
    # Since it's a datagrid cell
    search_xpath = "//*[contains(normalize-space(.), 'Search Public Records')]"
    search_items = driver.find_elements(By.XPATH, search_xpath)
    print(f"Found {len(search_items)} candidates for Search Public Records")
    
    clicked = False
    for item in search_items:
        try:
            print(f"Trying to click item with tag {item.tag_name} and text {item.text}")
            driver.execute_script("arguments[0].click();", item)
            clicked = True
            break
        except:
            continue
            
    if not clicked:
        print("Falling back to direct URL navigation for searchMain.do")
        # Relative to countyweb/
        driver.execute_script("window.location = 'search/searchMain.do';")
    
    print("Waiting for search page to load...")
    time.sleep(8)
    
    # 5. Diagnostic Dump
    driver.switch_to.default_content()
    with open("diagnostic_top.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Top level iframes: {len(iframes)}")
    for ifr in iframes:
        name = ifr.get_attribute("name")
        print(f"  Frame name: {name}")
        try:
            driver.switch_to.frame(ifr)
            print(f"    Switched to {name}. URL: {driver.current_url}")
            with open(f"diagnostic_frame_{name}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            # Check for inner frames
            inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
            if inner_iframes:
                print(f"    Found {len(inner_iframes)} inner iframes in {name}")
                for inner_ifr in inner_iframes:
                    print(f"      Inner name: {inner_ifr.get_attribute('name')} id: {inner_ifr.get_attribute('id')}")
            
            driver.switch_to.parent_frame()
        except Exception as e:
            print(f"    Could not switch to frame {name}: {e}")
            driver.switch_to.default_content()

finally:
    driver.quit()
