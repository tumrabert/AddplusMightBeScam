import time
import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

# --- CONFIGURATION ---
# CSV file containing URLs to process
CSV_FILE = "url_list.csv"

# Delay in seconds between processing each URL.
DELAY_BETWEEN_URLS = 3

BASE_URL = "https://addplus.org"
# --- END CONFIGURATION ---

def setup_driver():
    """Sets up the Selenium WebDriver to use a persistent user profile and enable logging."""
    print("Setting up the Chrome driver with a persistent profile...")
    
    options = webdriver.ChromeOptions()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    profile_path = os.path.join(script_dir, "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    
    # --- NEW: Enable Performance Logging ---
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def read_urls_from_csv(csv_file):
    """Reads URLs from the CSV file."""
    urls = []
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                url = row.get('url', '').strip()
                if url:
                    urls.append(url)
        print(f"Successfully loaded {len(urls)} URLs from {csv_file}")
        return urls
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} not found. Please make sure the file exists.")
        return []
    except Exception as e:
        print(f"❌ Error reading {csv_file}: {e}")
        return []

def process_urls(driver, urls, delay):
    """Loops through each URL, checks console logs for skip conditions, and clicks the claim button."""
    for i, url in enumerate(urls):
        print(f"\n--- Processing URL {i+1}/{len(urls)}: {url} ---")
        try:
            driver.get(url)
            time.sleep(2) 

            logs = driver.get_log('performance')
            for entry in logs:
                log_data = json.loads(entry['message'])
                if (log_data.get('message', {}).get('params', {}).get('name') == 'RpcClientError' and
                    'You have already claimed points from' in log_data.get('message', {}).get('params', {}).get('message', '')):
                    print("🔵 'Already claimed' error found in console logs. Skipping immediately.")
                    raise StopIteration("Already claimed")

            if "Page Not Found" in driver.title or "404" in driver.title:
                print("🔴 Invalid URL (Page Not Found). Skipping immediately.")
                continue

            claim_button_xpath = "//button[contains(., 'Claim') or contains(., 'claim')]"
            claim_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, claim_button_xpath))
            )
            
            print("Claim button found. Clicking now...")
            claim_button.click()
            
            # The popup verification has been removed. We now assume success after the click.
            print("✅ Successfully clicked claim button.")

            # Wait for the specified delay only AFTER a successful action.
            if i < len(urls) - 1:
                print(f"Waiting for {delay} seconds...")
                time.sleep(delay)

        except StopIteration as e:
            # Catches our custom "Already claimed" signal and moves on.
            pass
        except Exception as e:
            # Catches any other error during the process.
            print(f"❌ An error occurred. Skipping. Reason: {e}")
          
if __name__ == "__main__":
    driver = setup_driver()
    
    # Read URLs from CSV file
    urls_to_claim = read_urls_from_csv(CSV_FILE)
    
    if urls_to_claim:
        # Process the URLs from CSV
        process_urls(driver, urls_to_claim, DELAY_BETWEEN_URLS)
    else:
        print("❌ No URLs to process. Please check your CSV file.")
    
    print("\n🎉 All tasks completed. You can close the browser.")
