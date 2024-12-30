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

    # Set up a custom User-Agent (some sites block default requests UA)
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
            # If there's a path component, build the local path prefix
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url

            print(f"[{count}] Processing: {url}")

            # Skip domain if same_domain=True and this link is outside of base_domain
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
                soup = BeautifulSoup(response.text, features="lxml")
            except Exception as e:
                print(f"    [!] Could not parse HTML: {e}")
                continue

            for anchor in soup.find_all("a"):
                link = anchor.attrs.get('href', '')

                # Ignore mailto: links, empty, or anchor links (#)
                if not link or link.startswith("mailto:") or link.startswith("#"):
                    continue

                if link.startswith("/"):
                    link = base_url + link
                elif not link.startswith("http"):
                    link = urllib.parse.urljoin(path, link)

                # Add the new link to the queue if not visited
                if link not in scraped_urls and link not in urls:
                    urls.append(link)

    except KeyboardInterrupt:
        print("[-] Interrupted by user. Exiting...")

    # If output_file is specified, write all emails to it
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
        same_domain=True,   # set to False to allow off-domain crawling
        output_file=None    # set a filename if you want results in a file
    )

    print("\n=== Emails Found ===")
    for mail in found_emails:
        print(mail)
