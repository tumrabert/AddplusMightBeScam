import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException

# --- CONFIGURATION ---
# CSV file containing URLs to process
CSV_FILE = "url_list.csv"

# Delay in seconds between processing each URL.
DELAY_BETWEEN_URLS = 0.1

BASE_URL = "https://addplus.org"
# --- END CONFIGURATION ---

def setup_driver():
    """Sets up the Selenium WebDriver to use a persistent user profile and enable logging."""
    print("Setting up the Chrome driver with a persistent profile...")
    
    options = webdriver.ChromeOptions()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    profile_path = os.path.join(script_dir, "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    
    # Keep browser active when hidden/minimized
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-iframes-during-prerender")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Keep browser in background - don't bring to foreground
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--silent")
    
    # Prevent tab throttling when not in focus
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # --- Enable Performance Logging ---
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute script to prevent page from being throttled
    driver.execute_script("""
        // Prevent page from being throttled when hidden
        Object.defineProperty(document, 'hidden', {
            get: function() { return false; }
        });
        Object.defineProperty(document, 'visibilityState', {
            get: function() { return 'visible'; }
        });
    """)
    
    # Minimize the browser window initially
    driver.minimize_window()
    
    return driver

def read_pending_urls_from_csv(csv_file):
    """Reads URLs from the CSV file where is_done = 0."""
    try:
        df = pd.read_csv(csv_file)
        
        # Filter rows where is_done is 0
        pending_rows = df[df['is_done'] == 0]
        
        if pending_rows.empty:
            print("✅ All URLs have been processed! No pending items found.")
            return []
        
        urls_with_index = []
        for index, row in pending_rows.iterrows():
            url = row['url'].strip()
            if url:
                urls_with_index.append((index, url))
        
        print(f"📊 Total rows in CSV: {len(df)}")
        print(f"🚀 Found {len(urls_with_index)} pending URLs (is_done = 0)")
        print(f"✅ Successfully loaded pending URLs from {csv_file}")
                
        return urls_with_index
    except FileNotFoundError:
        print(f"❌ Error: {csv_file} not found. Please make sure the file exists.")
        return []
    except Exception as e:
        print(f"❌ Error reading {csv_file}: {e}")
        return []

def update_url_status(csv_file, row_index, status=1):
    """Updates the is_done status for a specific row in the CSV."""
    try:
        df = pd.read_csv(csv_file)
        df.loc[row_index, 'is_done'] = status
        df.to_csv(csv_file, index=False)
        print(f"📝 Updated row {row_index + 1} status to {status}")
    except Exception as e:
        print(f"❌ Error updating CSV: {e}")

def restart_driver_and_continue():
    """Restart the driver when session becomes invalid."""
    print("🔄 Restarting driver due to invalid session...")
    time.sleep(3)
    return setup_driver()

def process_urls(driver, urls_with_index, delay):
    """Loops through each URL, checks console logs for skip conditions, and clicks the claim button."""
    i = 0
    while i < len(urls_with_index):
        row_index, url = urls_with_index[i]
        print(f"\n--- Processing Row {row_index + 1} ({i+1}/{len(urls_with_index)}): {url} ---")
        
        try:
            # Navigate to URL without bringing browser to foreground
            driver.get(url)
            
            # Execute script to ensure page is considered visible
            driver.execute_script("""
                Object.defineProperty(document, 'hidden', {
                    get: function() { return false; }
                });
                Object.defineProperty(document, 'visibilityState', {
                    get: function() { return 'visible'; }
                });
            """)
            
            time.sleep(2)

            logs = driver.get_log('performance')
            for entry in logs:
                log_data = json.loads(entry['message'])
                if (log_data.get('message', {}).get('params', {}).get('name') == 'RpcClientError' and
                    'You have already claimed points from' in log_data.get('message', {}).get('params', {}).get('message', '')):
                    print("🔵 'Already claimed' error found in console logs. Marking as done.")
                    update_url_status(CSV_FILE, row_index, 1)
                    raise StopIteration("Already claimed")

            if "Page Not Found" in driver.title or "404" in driver.title:
                print("🔴 Invalid URL (Page Not Found). Marking as done.")
                update_url_status(CSV_FILE, row_index, 1)
                i += 1
                continue

            claim_button_xpath = "//button[contains(., 'Claim') or contains(., 'claim')]"
            
            # Use JavaScript to ensure element is visible and clickable
            try:
                claim_button = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, claim_button_xpath))
                )
                
                # Use JavaScript to scroll and click without bringing to foreground
                driver.execute_script("""
                    arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});
                """, claim_button)
                time.sleep(1)
                
                # Use JavaScript click to avoid bringing browser to foreground
                driver.execute_script("arguments[0].click();", claim_button)
                print("✅ Successfully clicked claim button (JavaScript click).")
                
            except Exception as button_error:
                print(f"❌ Could not find or click claim button: {button_error}")
                raise button_error
            
            # Update status to 1 (done) after successful processing
            update_url_status(CSV_FILE, row_index, 1)

            # Wait for the specified delay only AFTER a successful action.
            if i < len(urls_with_index) - 1:
                print(f"Waiting for {delay} seconds...")
                time.sleep(delay)
            
            i += 1

        except StopIteration as e:
            # Catches our custom "Already claimed" signal and moves on.
            i += 1
            pass
            
        except (InvalidSessionIdException, WebDriverException) as session_error:
            if "invalid session id" in str(session_error).lower():
                print(f"🔄 Invalid session detected. Restarting driver and marking row {row_index + 1} as pending (is_done = 0)...")
                # Mark current row as pending (0) so it can be retried
                update_url_status(CSV_FILE, row_index, 0)
                
                # Restart driver
                try:
                    driver.quit()
                except:
                    pass
                driver = restart_driver_and_continue()
                
                # Don't increment i, so we retry this URL with the new driver
                continue
            else:
                print(f"❌ WebDriver error occurred. Skipping. Reason: {session_error}")
                update_url_status(CSV_FILE, row_index, 1)
                i += 1
                
        except Exception as e:
            # Catches any other error during the process.
            print(f"❌ An error occurred. Skipping. Reason: {e}")
            # Mark as done even if there's an error to avoid infinite loops
            update_url_status(CSV_FILE, row_index, 1)
            i += 1
    
    return driver
          
if __name__ == "__main__":
    print(f"🔧 Configuration:")
    print(f"   CSV File: {CSV_FILE}")
    print(f"   Processing only URLs where is_done = 0")
    print(f"   Delay between URLs: {DELAY_BETWEEN_URLS} seconds")
    print(f"   Running in background mode")
    print(f"   Auto-recovery from session errors enabled")
    print("-" * 50)
    
    driver = setup_driver()
    
    try:
        while True:
            # Read pending URLs from CSV file (where is_done = 0)
            urls_to_claim = read_pending_urls_from_csv(CSV_FILE)
            
            if not urls_to_claim:
                print("✅ No pending URLs to process. All URLs have been completed!")
                break
            
            # Process the pending URLs from CSV
            driver = process_urls(driver, urls_to_claim, DELAY_BETWEEN_URLS)
            
            print("\n🔄 Checking for more pending URLs...")
            time.sleep(2)
        
        print("\n🎉 All pending tasks completed. You can close the browser.")
    
    except KeyboardInterrupt:
        print("\n⏹️  Script interrupted by user.")
    finally:
        # Keep browser open for a few seconds before closing
        try:
            driver.quit()
        except:
            pass
        print("👋 Script finished.")
