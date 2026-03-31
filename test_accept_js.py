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

# Step 1: Load disclaimer page
driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")
time.sleep(3)
print("Step 1 URL:", driver.current_url)

# Step 2: If session timeout error page, click logout link
try:
    logout = driver.find_element(By.PARTIAL_LINK_TEXT, "Click here to logout")
    logout.click()
    print("Clicked logout link")
    time.sleep(3)
    print("After logout URL:", driver.current_url)
except:
    print("No logout link on page")

# Step 3: Click Login as Guest
try:
    guest = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")
    ))
    driver.execute_script("arguments[0].click();", guest)
    print("Clicked Login as Guest")
except Exception as e:
    print("Could not click guest login:", e)

# Step 4: Wait until main.jsp is loaded (has bodyframe)
print("Waiting for main.jsp to load...")
try:
    wait.until(EC.url_contains("main.jsp"))
    print("main.jsp loaded, URL:", driver.current_url)
except:
    print("URL did not contain main.jsp within 20s, current URL:", driver.current_url)

time.sleep(2)

# Step 5: Switch to bodyframe (disclaimer)
try:
    driver.switch_to.default_content()
    driver.switch_to.frame("bodyframe")
    print("✅ Switched to bodyframe. Current bodyframe URL:", driver.current_url)
except Exception as e:
    print("❌ Failed switching to bodyframe:", e)
    # List ALL frames instead
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Available iframes on page: {len(iframes)}")
    for ifr in iframes:
        print("  name:", ifr.get_attribute("name"), "src:", ifr.get_attribute("src"))
    driver.quit()
    exit()

# Step 6: Click Accept via JS
try:
    driver.execute_script("executeCommand('Accept');")
    print("Executed executeCommand('Accept')")
except Exception as e:
    print("JS error:", e)

# Step 7: Wait for parent to navigate away from disclaimer
driver.switch_to.default_content()
print("Waiting for page after Accept...")
time.sleep(6)
print("URL after Accept:", driver.current_url)

# Step 8: Check bodyframe
try:
    driver.switch_to.frame("bodyframe")
    print("✅ bodyframe loaded. URL:", driver.current_url)
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Links in bodyframe ({len(links)}):")
    for lnk in links:
        print("  ", repr(lnk.text.strip()), "->", lnk.get_attribute("href"))
    with open("bodyframe_post_accept.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved bodyframe_post_accept.html")
except Exception as e:
    print("❌ bodyframe not accessible after Accept:", e)

driver.quit()
