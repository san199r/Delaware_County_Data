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

try:
    driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
    
    # 2. Login as Guest
    guest = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")))
    driver.execute_script("arguments[0].click();", guest)
    time.sleep(3)
        
    # 3. Accept
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    driver.execute_script("executeCommand('Accept');")
    time.sleep(3)
    
    # 4. Search
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    search_xpath = '//div[contains(@class,"datagrid-cell") and contains(normalize-space(.),"Search Public Records")]'
    item = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", item)
    time.sleep(6)
    
    # 5. FIND DATES RECURSIVELY
    xpath_3 = "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])[3]"
    
    def check_this_frame(path):
        try:
            if driver.find_elements(By.XPATH, xpath_3):
                with open("FRAME_FOUND.txt", "a") as f:
                    f.write(f"FOUND DATES AT: {path}\n")
                return True
        except:
            pass
        return False

    driver.switch_to.default_content()
    check_this_frame("Default")
    
    # Check top level frames
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i in range(len(iframes)):
        driver.switch_to.default_content()
        ifr = driver.find_elements(By.TAG_NAME, "iframe")[i]
        name = ifr.get_attribute("name") or ifr.get_attribute("id") or str(i)
        driver.switch_to.frame(ifr)
        if check_this_frame(f"Default -> {name}"): continue
            
        inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for j in range(len(inner_iframes)):
            driver.switch_to.default_content()
            ifr = driver.find_elements(By.TAG_NAME, "iframe")[i]
            driver.switch_to.frame(ifr)
            inner_ifr = driver.find_elements(By.TAG_NAME, "iframe")[j]
            inner_name = inner_ifr.get_attribute("name") or inner_ifr.get_attribute("id") or str(j)
            driver.switch_to.frame(inner_ifr)
            if check_this_frame(f"Default -> {name} -> {inner_name}"): continue
            
            # Double check deeper
            deep_iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for k in range(len(deep_iframes)):
                driver.switch_to.default_content()
                ifr = driver.find_elements(By.TAG_NAME, "iframe")[i]
                driver.switch_to.frame(ifr)
                inner_ifr = driver.find_elements(By.TAG_NAME, "iframe")[j]
                driver.switch_to.frame(inner_ifr)
                deep_ifr = driver.find_elements(By.TAG_NAME, "iframe")[k]
                deep_name = deep_ifr.get_attribute("name") or str(k)
                driver.switch_to.frame(deep_ifr)
                check_this_frame(f"Default -> {name} -> {inner_name} -> {deep_name}")

finally:
    driver.quit()
