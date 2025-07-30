# AddPlus Claim Automation Bot

This Python script automates the process of visiting a list of AddPlus boost URLs and clicking the 'Claim' button. It uses a persistent browser session to handle login automatically after the first time.

## Features

* ✅ Reads target URLs from a `url_list.csv` file.
* ✅ Uses a persistent Chrome session to stay logged in.
* ✅ Automatically skips URLs that have already been claimed by checking console logs.
* ✅ Skips invalid or 'Page Not Found' URLs.
* ✅ Configurable delay between each claim attempt.

---
## Prerequisites

Before you begin, ensure you have the following installed:
* Python 3.x
* Google Chrome browser

---
## Installation & Setup

### 1. Install Dependencies

Install the required Python packages by running the following command in your terminal:

```bash
cd AddplusMightBeScam
pip install selenium webdriver-manager
```


### 2. Create the Input CSV File

In the same directory as the script, create a file named **`url_list.csv`**. It must have a header row with at least a column named **`url`**.

---
## How to Use

Follow these steps exactly to run the bot.

### Step 1: First-Time Login (Crucial!)

You only need to do this step **once**.

1.  Run the script for the first time from your terminal:
    ```
    python claim_script.py
    ```
2.  A Chrome browser window will open. It will be controlled by the script.
3.  In **that specific browser window**, manually navigate to `https://addplus.org` and log in with your account.
4.  After you have successfully logged in, you can **close the browser window**.

Your login session is now saved in a new folder named `chrome_profile`.

### Step 2: Run the Automation

After the one-time login setup, simply run the script again:\

---

## Configuration

You can change the script's behavior by editing the variables at the top of the `claim_script.py` file.

* **`CSV_FILE`**: The name of the input file containing the URLs.
    ```
    CSV_FILE = "url_list.csv"
    ```

* **`DELAY_BETWEEN_URLS`**: The number of seconds to wait after each successful claim before starting the next one.
    ```
    DELAY_BETWEEN_URLS = 3
# AddplusMightBeScam
