# Email Scraper

A Python script that crawls a target website to collect email addresses. It uses [Requests](https://pypi.org/project/requests/) to fetch pages and [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) (with a simple regex) to identify email patterns. You can configure the script to limit its crawl to the initial domain, preventing it from wandering off to external sites.

---
# What is ?

**Email Scraper** is a Python script that crawls a target website, collecting emails found in the page’s text. It uses the Requests library to fetch pages and Beautiful Soup (along with a regex) to identify email patterns. By default, the script follows internal links up to a specified limit (e.g., 100 links) and can optionally limit its crawl to the starting domain only. It’s useful for gathering contact emails or testing web scraping techniques in a controlled manner.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Script Overview](#script-overview)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Features

1. **Domain Restriction (Optional)**
   - If enabled, the script will only follow links on the same domain as the starting URL.

2. **Timeout & Error Handling**
   - Prevents the script from hanging on slow or unresponsive servers.

3. **Regex-Based Email Extraction**
   - Emails are identified by a simple regular expression (`[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+`), capturing typical email patterns.

4. **Ignore `mailto:` Links**
   - Prevents following email links as though they were normal webpages.

5. **Configurable User-Agent**
   - Helps avoid potential blocks by servers that reject the default Python `requests` User-Agent.

6. **Optional File Output**
   - Stores collected email addresses in a text file if desired.

---

## Requirements

- **Python 3.6+** (Recommended)
- **pip** or another Python package manager

**Python Libraries**:
- **requests**
- **beautifulsoup4**
- **lxml** (optional but recommended for performance)

---

## Installation

1. **Clone or Download** the repository:
   ```bash
   git clone https://github.com/Shahyru/Email-Scrapper.git

## Usage
   - 1.Clone or Download this repository.
   - 2.Navigate to the folder containing the script.
   - 3.Run the script:
   ```
   python3 Email-Scrapper.py
   ```
   **Enter the Target URL when prompted:**
   
   ```
   [+] Enter Target URL To Scan: https://example.com
   ```
   **View the Printed Results or check the optional output file (if configured).**

   ## Script Overview
   ```
   import requests
   import requests.exceptions
   from bs4 import BeautifulSoup
   from collections import deque
   import urllib.parse
   import re

   def scrape_emails(start_url, max_links=100, same_domain=True, output_file=None):
       """
       Scrape emails starting from `start_url` up to `max_links` links.

       :param start_url:  The initial URL to crawl.
       :param max_links:  The maximum number of links to process.
       :param same_domain: If True, only follow links on the same domain as `start_url`.
       :param output_file: If provided, path to a file for saving email results.
       :return: A set of unique emails found.
       """

       # Use a deque for BFS-like approach
       urls = deque([start_url])
       scraped_urls = set()
       emails = set()

      # Parse domain from the initial URL (for same-domain restriction if needed)
      base_domain = urllib.parse.urlsplit(start_url).netloc

      # Set up a custom User-Agent
      headers = {
           'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
       }

       count = 0
       try:
           while urls:
               count += 1
               if count > max_links:
                   print(f"[!] Reached max limit of {max_links} links.")
                   break

               url = urls.popleft()
               scraped_urls.add(url)

               parts = urllib.parse.urlsplit(url)
               base_url = "{0.scheme}://{0.netloc}".format(parts)
               path = url[:url.rfind('/') + 1] if '/' in parts.path else url

               print(f"[{count}] Processing: {url}")

               # Skip if same_domain=True and the URL is outside the base domain
               if same_domain and urllib.parse.urlsplit(url).netloc != base_domain:
                   print("    [i] Skipping, different domain.")
                   continue

               try:
                   response = requests.get(url, headers=headers, timeout=10)
               except (requests.exceptions.MissingSchema,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.ReadTimeout):
                   print("    [!] Request failed or timed out.")
                   continue
               except Exception as e:
                   print(f"    [!] Unexpected error: {e}")
                   continue

               # Extract emails via regex
               new_emails = set(re.findall(
                   r"[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+",
                   response.text,
                   flags=re.I
               ))
               if new_emails:
                   print(f"    [+] Found {len(new_emails)} new email(s).")
               emails.update(new_emails)

               # Use BeautifulSoup to find all links
               try:
                   soup = BeautifulSoup(response.text, "lxml")
               except Exception as e:
                   print(f"    [!] Could not parse HTML: {e}")
                   continue

               for anchor in soup.find_all("a"):
                   link = anchor.attrs.get('href', '')

                   # Ignore mailto: links, empty, or anchor links
                   if not link or link.startswith("mailto:") or link.startswith("#"):
                       continue

                   if link.startswith("/"):
                       link = base_url + link
                   elif not link.startswith("http"):
                       link = urllib.parse.urljoin(path, link)

                   if link not in scraped_urls and link not in urls:
                       urls.append(link)

       except KeyboardInterrupt:
           print("[-] Interrupted by user. Exiting...")

       # If output_file is specified, write emails to it
       if output_file:
           try:
               with open(output_file, 'w', encoding='utf-8') as f:
                   for mail in emails:
                      f.write(mail + "\n")
               print(f"[+] Emails saved to {output_file}")
           except Exception as e:
               print(f"[!] Could not write emails to file: {e}")

       return emails


   if __name__ == "__main__":
       user_url = input("[+] Enter Target URL To Scan: ").strip()
       found_emails = scrape_emails(
           start_url=user_url,
           max_links=100,
           same_domain=True,
           output_file=None
       )

       print("\n=== Emails Found ===")
       for mail in found_emails:
           print(mail)
   ```

## Configuration

   - `max_links:` The maximum number of links the script will follow. Default is `100`.
   - `same_domain:` If set to `True`, the script will only scrape links on the same domain as the initial URL.
   - `output_file:` Provide a file path (e.g., `emails.txt`) to save the emails. If `None`, results are only printed.

## Troubleshooting

   - **No emails found**?
   - Ensure the target site actually contains email addresses in its HTML. Some pages may load content dynamically (which this script won’t handle).
   - **Connection errors or timeouts**?
   - Try increasing the `timeout` parameter in the `requests.get(...) call`.
   - Check if the site blocks web scraping or requires a different User-Agent.
   - **Script exits immediately**?
   - Make sure your Python environment is installed and properly set up with the required libraries.

## Disclaimer
  **This script is for educational and authorized research purposes only**.
  **Always check the website’s `robots.txt` policy and respect site terms of service**.
  **Use ethically and responsibly. The author assumes no liability for misuse of this tool**.

## License
  **This project is provided under the MIT License. Feel free to modify and distribute as you wish**.
