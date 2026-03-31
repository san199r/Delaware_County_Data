import time
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import Workbook, load_workbook
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os
import re

import sys
import argparse
import io

# === Fix for Windows CPU-1252 character encoding issues (GitHub Actions) ===
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# === Parse arguments for Headless execution (GitHub Actions) ===
parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", help="Run in headless mode")
args, unknown = parser.parse_known_args()

def send_email(file_path):
    sender_email = os.environ.get('SENDER_EMAIL')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    password = os.environ.get('EMAIL_PASSWORD') # App Password for Gmail
    
    if not (sender_email and receiver_email and password):
        print("[Log] Email credentials missing. Skipping email send.")
        return

    print(f"Sending email to {receiver_email}...")
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Delaware County Probate Scraper Output - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        body = "Automated scrape completed. Please find the attached probate records export file."
        msg.attach(MIMEText(body, 'plain'))
        
        # Attachment
        file_basename = os.path.basename(file_path)
        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {file_basename}")
            msg.attach(part)
        
        # SMTP Session (using Gmail's server as default)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# === Setup driver ===
chrome_options = webdriver.ChromeOptions()
if args.headless or os.environ.get('GITHUB_ACTIONS'):
    print("Running in HEADLESS mode...")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
driver.maximize_window()
driver.get("https://delcorowonlineservices.co.delaware.pa.us/countyweb/disclaimer.do")

wait = WebDriverWait(driver, 15)

# === Automated Navigation (navigation.txt) ===
# === Automated Navigation ===
print("Starting automated navigation...")

# 1. Click here to logout
try:
    print("Checking for logout link...")
    logout = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Click here to logout")))
    logout.click()
    print("Clicked logout.")
    time.sleep(2)
except:
    pass

# 2. Login as guest
try:
    print("Looking for Guest Login...")
    guest_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value=' Login as Guest ' or @value='Guest Login']")))
    driver.execute_script("arguments[0].click();", guest_btn)
    print("Clicked Login as Guest.")
    time.sleep(3)
except Exception as e:
    print("Guest Login step failed:", e)

# 3. Accept Disclaimer
print("Waiting for Accept button...")
try:
    driver.switch_to.default_content()
    # Wait for the frame to be ready
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    
    # Use standard script or JS to accept
    accept_btn = wait.until(EC.presence_of_element_located((By.ID, "accept")))
    driver.execute_script("arguments[0].click();", accept_btn)
    print("Clicked Accept via JS.")
    time.sleep(5)
except Exception as e:
    print("Accept Disclaimer step failed:", e)

# 4. Search Public Record
print("Looking for 'Search Public Records'...")
try:
    driver.switch_to.default_content()
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    
    # Specific XPath provided by the USER
    search_xpath = '//div[contains(@class,"datagrid-cell") and contains(normalize-space(.),"Search Public Records")]'
    search_link = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    driver.execute_script("arguments[0].click();", search_link)
    print("Clicked Search Public Records.")
    time.sleep(5)
except Exception as e:
    print("Failed to click Search Public Records:", e)

# 5. Enter Dates
print("Preparing to enter dates...")
today = datetime.datetime.now()
seven_days_ago = today - datetime.timedelta(days=7)
start_date_str = seven_days_ago.strftime("%m/%d/%Y")
end_date_str = today.strftime("%m/%d/%Y")

date_from_xpath = "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])[3]"
date_to_xpath = "(//span[contains(@class,'datebox')]//input[contains(@class,'textbox-text')])[4]"

def find_and_fill_dates():
    # Try multiple frames recursively
    driver.switch_to.default_content()
    
    # Check bodyframe
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
        print("Switched to bodyframe.")
    except:
        print("Could not find bodyframe.")
        return False
        
    # Navigating to Case Name tab first (if present) to ensure correct search
    def try_select_case_name():
        for tab_text in ["Case Name", "CaseName", "Search Case"]:
            try:
                tab = driver.find_element(By.PARTIAL_LINK_TEXT, tab_text)
                driver.execute_script("arguments[0].click();", tab)
                print(f"Clicked {tab_text} tab.")
                time.sleep(2)
                return True
            except:
                continue
        return False

    # Recursive search for date fields
    def check_frames_and_fill(depth=0):
        if depth > 3: return False
        
        # Try to select the tab in this frame context
        try_select_case_name()
        
        # Try to find date fields in current frame
        try:
            print(f"Checking frame at depth {depth}...")
            el_from = driver.find_element(By.XPATH, date_from_xpath)
            el_to = driver.find_element(By.XPATH, date_to_xpath)
            
            # Found! Click first, then send values as requested
            print("Date fields found! Entering values...")
            for el, val in [(el_from, start_date_str), (el_to, end_date_str)]:
                el.click()
                time.sleep(0.5)
                el.clear()
                el.send_keys(val)
            return True
        except:
            # Not found, try inner iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for i in range(len(iframes)):
                try:
                    driver.switch_to.frame(iframes[i])
                    if check_frames_and_fill(depth + 1):
                        return True
                    driver.switch_to.parent_frame()
                except:
                    continue
        return False

    return check_frames_and_fill()

if not find_and_fill_dates():
    print("Failed to find date fields in any frame.")
    # Fallback/Debug dump
    driver.switch_to.default_content()
    with open("debug_search_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
else:
    print(f"Successfully entered dates: {start_date_str} to {end_date_str}.")
    
    # 6. Click search at top
    print("Clicking Search...")
    def find_and_click_search():
        driver.switch_to.default_content()
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
        except:
            return False
            
        search_btn_xpath = "(//a[contains(@onclick,'search')])[1]"
        
        def check_frames_and_click(depth=0):
            if depth > 3: return False
            try:
                btn = driver.find_element(By.XPATH, search_btn_xpath)
                print(f"Search button found at depth {depth}! Clicking...")
                driver.execute_script("arguments[0].click();", btn)
                return True
            except:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for i in range(len(iframes)):
                    try:
                        driver.switch_to.frame(iframes[i])
                        if check_frames_and_click(depth + 1):
                            return True
                        driver.switch_to.parent_frame()
                    except:
                        continue
            return False
        return check_frames_and_click()

    if not find_and_click_search():
        print("Failed to click Search button in any frame.")
    else:
        print("Clicked Search button.")
        time.sleep(8)
# 7. Tool starts to run
print("Automated navigation complete. Tool starts to run.")

# === Switch into Results Frames ===
# These frames only appear AFTER a search is performed
# === Switch into Results Frames ===
# These frames only appear AFTER a search is performed
print("Waiting for results to load...")
driver.switch_to.default_content()
try:
    # After search, the top-level usually has corediv containing an iframe, 
    # which in turn contains resultFrame
    wait.until(EC.presence_of_element_located((By.ID, "corediv")))
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
    
    # Wait for the results frame to appear inside that iframe
    wait.until(EC.frame_to_be_available_and_switch_to_it("resultFrame"))
    print("Switched to resultFrame.")
except Exception as e:
    print(f"Could not find result frames using standard path: {e}. Trying fallback...")
    driver.switch_to.default_content()
    # Fallback: find bodyframe first
    wait.until(EC.frame_to_be_available_and_switch_to_it("bodyframe"))
    try:
        wait.until(EC.frame_to_be_available_and_switch_to_it("resultFrame"))
        print("Switched to resultFrame via bodyframe.")
    except Exception as e2:
         print(f"Fallback also failed: {e2}")

# Now we should be able to find navDisplay
display_text = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="navDisplay"]'))).text
print(f"Result summary: {display_text}")

# Extract total records and per-page
m = re.search(r'Displaying (\d+)-(\d+) of (\d+)', display_text)
if m:
    per_page = int(m.group(2)) - int(m.group(1)) + 1
    total_records = int(m.group(3))
else:
    per_page, total_records = 40, 40  # fallback
print(f"Total records: {total_records}, Per page: {per_page}")

# === Excel setup ===
now_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
file_name = f"Delaware_County_PA_Probate_Tool_Output_{now_ts}.xlsx"
print(f"File created: {file_name}")
if os.path.exists(file_name):
    wb = load_workbook(file_name)
    ws = wb.active
    sno = ws.max_row  # last saved S.No
    records_done = sno - 1
else:
    wb = Workbook()
    ws = wb.active
    ws.append([
        "S.No", "County", "State",
        "Decedent Name",
        "Decedent Address", "Decedent Address1",  # <-- added right after Decedent Address
        "Decedent City", "Decedent State", "Decedent Zip",
        "Case File Number", "Estate Type", "DOB", "Filing Date", "DOD", "Residence Code",
        "Letters Granted",
        "Personal Rep Name", "Personal Rep Address",
        "Attorney Name", "Attorney Address"
    ])
    sno = 1
    records_done = 0

# === Calculate total pages and resume info ===
total_pages = (total_records + per_page - 1) // per_page
resume_page = (records_done // per_page) + 1
resume_index = (records_done % per_page)  # 0-based index
print(f"Total Pages: {total_pages}, Resuming from Page {resume_page}, Record {resume_index + 1}")

def go_to_page(page_num):
    # 1. Go into resultFrame first
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultFrame"]'))

    # 2. Try to find the pageNumber input in this frame
    try:
        page_input = driver.find_element(By.NAME, "pageNumber")
    except:
        # If not here, it might be inside the navButtons iframe
        driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="navButtons"]/iframe'))
        page_input = driver.find_element(By.NAME, "pageNumber")

    # 3. Enter the desired page number
    page_input.clear()
    page_input.send_keys(str(page_num))

    # 4. Click the Go link that triggers goToResultPage()
    go_link = driver.find_element(
        By.XPATH,
        '//a[contains(@onclick, "goToResultPage")]'
    )
    go_link.click()

    # 5. Verify we landed on the expected page using navDisplay
    start = (page_num - 1) * per_page + 1
    end = min(page_num * per_page, total_records)
    expected_snippet = f"Displaying {start}-{end} of {total_records} Items"

    # navDisplay lives in resultFrame
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultFrame"]'))

    # Wait until the text matches the page we expect
    wait.until(
        lambda d: expected_snippet in d.find_element(By.ID, "navDisplay").text
    )

    actual = driver.find_element(By.ID, "navDisplay").text
    print(f"[OK] Now on page {page_num}: {actual}")

# === Navigate to correct page if resuming ===
if resume_page > 1:
    go_to_page(resume_page)

# === Loop through pages ===
for page in range(resume_page, total_pages + 1):
    print(f"=== Page {page} of {total_pages} ===")

    # Switch to resultListFrame
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultFrame"]'))
    driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultListFrame"]'))

    # Determine start index for current page
    if page == resume_page:
        start_idx = resume_index
    else:
        start_idx = 0

    # Determine end index for current page
    if page < total_pages:
        end_idx = per_page
    else:
        end_idx = total_records - per_page * (total_pages - 1)

    # Loop through records in current page
    for i in range(start_idx, end_idx):
        try:
            record_xpath = f'//*[@id="inst{i}"]'
            wait.until(EC.element_to_be_clickable((By.XPATH, record_xpath))).click()
            time.sleep(2)

            # --- Decedent / Case Info ---
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="documentFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="docInfoFrame"]'))

            # Extract fields
            def get_text(xpath):
                try:
                    return driver.find_element(By.XPATH, xpath).text.strip()
                except:
                    return ""

            decedent_name = get_text('//*[@id="data"]/table[1]/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr/td[2]')
            decedent_address = get_text('//*[@id="data"]/table[2]/tbody/tr[1]/td[1]/table[3]/tbody/tr[1]/td[3]')

            # NEW: Decedent Address1 (leave blank if not present)
            decedent_address1 = get_text('//*[@id="data"]/table[2]/tbody/tr[1]/td[1]/table[3]/tbody/tr[2]/td[3]')

            decedent_city = get_text('//*[@id="data"]/table[2]/tbody/tr[1]/td[1]/table[3]/tbody/tr[3]/td[3]')
            decedent_state = get_text('//*[@id="data"]/table[2]/tbody/tr[1]/td[1]/table[3]/tbody/tr[4]/td[3]/table/tbody/tr/td[1]')
            decedent_zip = get_text('//*[@id="data"]/table[2]/tbody/tr[1]/td[1]/table[3]/tbody/tr[4]/td[3]/table/tbody/tr/td[3]')
            case_file = get_text('//*[@id="data"]/table[3]/tbody/tr[3]/td[1]/table/tbody/tr/td[3]')
            estate_type = get_text('//*[@id="data"]/table[3]/tbody/tr[4]/td[1]/table/tbody/tr/td[3]')
            dob = get_text('//*[@id="data"]/table[3]/tbody/tr[5]/td[1]/table/tbody/tr/td[3]')
            filing_date = get_text('//*[@id="data"]/table[3]/tbody/tr[3]/td[2]/table/tbody/tr/td[3]')
            dod = get_text('//*[@id="data"]/table[3]/tbody/tr[4]/td[2]/table/tbody/tr/td[3]')
            residence_code = get_text('//*[@id="data"]/table[3]/tbody/tr[5]/td[2]/table/tbody/tr/td[3]')
            letters_granted = get_text('//*[@id="data"]/table[3]/tbody/tr[6]/td[2]/table/tbody/tr/td[3]')

            # --- Personal Rep Tab ---
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="documentFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="docInfoFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="tabs"]'))
            driver.find_element(By.XPATH, '//*[@id="tabs"]/div[1]/div[3]/ul/li[2]/span').click()
            time.sleep(2)
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="documentFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="docInfoFrame"]'))

            rep_name = get_text('//*[@id="data"]/table[1]/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr[1]/td[2]')
            rep_address = get_text('//*[@id="data"]/table[1]/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr[2]/td[2]')

            # --- Attorney Tab ---
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="documentFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="docInfoFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="tabs"]'))
            driver.find_element(By.XPATH, '//*[@id="tabs"]/div[1]/div[3]/ul/li[3]/span').click()
            time.sleep(2)
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="documentFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="docInfoFrame"]'))

            attorney_name = get_text('//*[@id="data"]/table[1]/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr[1]/td[2]')
            attorney_address = get_text('//*[@id="data"]/table[1]/tbody/tr[2]/td/table[3]/tbody/tr/td[2]/table/tbody/tr[2]/td[2]')

            # Save row (Address1 inserted right after Address)
            ws.append([
                sno, "Delaware", "PA",
                decedent_name,
                decedent_address, decedent_address1,   # <-- new column value here
                decedent_city, decedent_state, decedent_zip,
                case_file, estate_type, dob, filing_date, dod, residence_code,
                letters_granted,
                rep_name, rep_address,
                attorney_name, attorney_address
            ])
            wb.save(file_name)
            print(f"S.No {sno} saved")

        except Exception as e:
            print(f"Error on record {i+1} (Page {page}): {e}")

        finally:
            sno += 1
            # Back to result list
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resnavframe"]'))
            time.sleep(1)
            try:
                back_btn = driver.find_element(By.XPATH, '//*[@id="btntable"]/tbody/tr/td[2]/a')
                back_btn.click()
                print("Returned to main result table")
            except:
                print("[Warning] Could not find 'Back' button")
            time.sleep(3)
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="corediv"]/iframe'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultFrame"]'))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="resultListFrame"]'))

    # === Go to Next Page if not last ===
    if page < total_pages:
        go_to_page(page + 1)

# === Done ===
driver.quit()
print("Data scraping complete. Process finished automatically.")

# Send email after scraping
send_email(file_name)
