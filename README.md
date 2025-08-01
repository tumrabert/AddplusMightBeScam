# AddPlus Claim Automation Bot

This Python script automates the process of visiting a list of AddPlus boost URLs and clicking the 'Claim' button. It uses a persistent browser session to handle login automatically after the first time.

## ⚠️ Disclaimer
This tool is intended for educational and legitimate use only. Users are responsible for ensuring their use complies with AddPlus terms of service and applicable laws. The authors are not responsible for any misuse of this software.

## Features

* ✅ Reads target URLs from a `url_list.csv` or `url_list2.csv` file.
* ✅ Uses a persistent Chrome session to stay logged in.
* ✅ Automatically skips URLs that have already been claimed by checking console logs.
* ✅ Skips invalid or 'Page Not Found' URLs.
* ✅ Configurable delay between each claim attempt.
* ✅ Multi-profile support (general and Twitter-specific profiles)

---
## Prerequisites

Before you begin, ensure you have the following installed:
* Python 3.7 or higher
* Google Chrome browser
* Stable internet connection

---
## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tumrabert/AddplusMightBeScam.git
cd AddplusMightBeScam
```

### 2. Install Dependencies

Install the required Python packages by running the following command in your terminal:

```bash
pip install selenium webdriver-manager pandas requests beautifulsoup4
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

---
## How to Use

Follow these steps exactly to run the bot.

### Step 1: First-Time Login (Crucial!)

You only need to do this step **once**.

1. Run the script for the first time from your terminal:
   ```bash
   python claim_script.py
   ```
2. A Chrome browser window will open. It will be controlled by the script.
3. In **that specific browser window**, manually navigate to `https://addplus.org` and log in with your account.
4. After you have successfully logged in, you can **close the browser window**.

Your login session is now saved in a new folder named `chrome_profile`.

### Step 2: Run the Automation

After the one-time login setup, simply run the script again:
```bash
python claim_script.py
```

The script will:
- Load your saved login session
- Process each URL in your CSV file
- Automatically claim available boosts
- Skip already claimed or invalid URLs
- Log all activities to the console

---
## Configuration

You can change the script's behavior by editing the variables at the top of the `claim_script.py` file.

* **`CSV_FILE`**: The name of the input file containing the URLs.
    ```python
    CSV_FILE = "url_list.csv"
    ```

* **`DELAY_BETWEEN_URLS`**: The number of seconds to wait after each successful claim before starting the next one.
    ```python
    DELAY_BETWEEN_URLS = 3
    ```

---
## File Structure

```
├── claim_script.py          # Main automation script
├── url_list.csv            # Primary URL list for claims
├── url_list2.csv           # Secondary URL list
├── chrome_profile/         # Saved Chrome session data
├── twitter_chrome_profile/ # Twitter-specific profile
├── README.md              # This documentation
└── requirements.txt       # Python dependencies
```

---
## Troubleshooting

### Common Issues

1. **"Chrome profile not found"**
   - Make sure you completed Step 1 (first-time login)
   - Check if `chrome_profile` folder exists

2. **"Login session expired"**
   - Delete the `chrome_profile` folder
   - Repeat Step 1 to create a new session

3. **Script runs but doesn't claim**
   - Verify your CSV file format
   - Check if URLs are valid AddPlus boost URLs
   - Ensure you're logged into the correct account

### Debug Mode
Add debug output by modifying the script to include verbose logging.

---
## Legal Notice

This tool is for legitimate use with your own AddPlus account. Always:
- Respect AddPlus terms of service
- Use reasonable delays between requests
- Don't abuse the automation for unfair advantage
- Comply with local laws and regulations

---
## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

---
## Support

For issues or questions:
- Check the troubleshooting section above
- Open an issue on GitHub
- Ensure you're using the latest version

---
## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with AddPlus terms of service.
