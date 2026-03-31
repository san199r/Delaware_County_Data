import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

try:
    driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
    wait = WebDriverWait(driver, 15)
    
    # 2. Login as Guest
    guest = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")))
    driver.execute_script("arguments[0].click();", guest)
    time.sleep(4)
        
    # 3. Accept
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    driver.execute_script("executeCommand('Accept');")
    time.sleep(4)
    
    # 4. Search
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    search_xpath = '//div[contains(@class,"datagrid-cell") and contains(normalize-space(.),"Search Public Records")]'
    item = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", item)
    time.sleep(8)
    
    # 5. Diagnostic
    print("=== Final Structure Diagnostic ===")
    driver.switch_to.default_content()
    
    def dump_frames(frame_name="Top Level"):
        print(f"\n--- Frame: {frame_name} ---")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes in {frame_name}")
        for i, ifr in enumerate(iframes):
            name = ifr.get_attribute("name")
            id = ifr.get_attribute("id")
            src = ifr.get_attribute("src")
            print(f"  [{i}] name='{name}', id='{id}', src='{src}'")
            
        # Check for the user's date XPaths in this frame
        xpath_3 = "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])[3]"
        try:
            found = driver.find_elements(By.XPATH, xpath_3)
            if found:
                print(f"  ✅ FOUND {len(found)} date fields in {frame_name}!")
        except:
            pass

    dump_frames("Default Content")
    
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i in range(len(iframes)):
        driver.switch_to.default_content()
        ifr = driver.find_elements(By.TAG_NAME, "iframe")[i]
        name = ifr.get_attribute("name") or str(i)
        driver.switch_to.frame(ifr)
        dump_frames(f"Default -> {name}")
        
        # Check inner frames
        inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for j in range(len(inner_iframes)):
            driver.switch_to.default_content()
            ifr = driver.find_elements(By.TAG_NAME, "iframe")[i]
            driver.switch_to.frame(ifr)
            
            inner_ifr = driver.find_elements(By.TAG_NAME, "iframe")[j]
            inner_name = inner_ifr.get_attribute("name") or str(j)
            driver.switch_to.frame(inner_ifr)
            dump_frames(f"Default -> {name} -> {inner_name}")

finally:
    driver.quit()
