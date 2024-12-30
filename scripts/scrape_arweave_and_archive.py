import os
import re
import requests
from bs4 import BeautifulSoup
import markdown


def scrape_arweave_and_archive(base_url):
    # Create directories for saving posts and transactions
    os.makedirs("posts", exist_ok=True)

    tx_file_path = "arweave_transactions.txt"

    # Load existing transaction IDs
    if os.path.exists(tx_file_path):
        with open(tx_file_path, "r", encoding="utf-8") as tx_file:
            existing_tx_ids = set(line.strip() for line in tx_file)
    else:
        existing_tx_ids = set()

    # Try scraping the base URL
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('a', href=True)
        post_links = [link['href'] for link in articles if link['href'].startswith(f"{base_url}/")]
        post_links = list(set(post_links))

        # Process each post link
        with open(tx_file_path, "a", encoding="utf-8") as tx_file:
            for idx, link in enumerate(post_links, start=1):
                post_url = link if link.startswith("http") else f"{base_url}{link}"
                post_response = requests.get(post_url)
                if post_response.status_code != 200:
                    print(f"Failed to fetch {post_url}. Skipping.")
                    continue

                post_soup = BeautifulSoup(post_response.text, 'html.parser')
                content = post_soup.get_text()
                match = re.search(r"ARWEAVE TX\s+([A-Za-z0-9_-]+)", content)
                if match:
                    arweave_tx = match.group(1)

                    if arweave_tx in existing_tx_ids:
                        print(f"Transaction {arweave_tx} already processed. Skipping.")
                        continue

                    print(f"Processing transaction: {arweave_tx}")

                    # Save the transaction ID
                    tx_file.write(f"{arweave_tx}\n")
                    tx_file.flush()

                    process_arweave_transaction(arweave_tx, idx)
                else:
                    print(f"No transactions found in {post_url}")
    except requests.RequestException:
        print(f"Base URL {base_url} unavailable. Checking unprocessed transactions...")

    # Process transactions from the transaction file
    process_pending_transactions(existing_tx_ids)


def process_arweave_transaction(tx_id, idx):
    permagate_url = f"https://permagate.io/{tx_id}"
    try:
        json_response = requests.get(permagate_url)
        json_response.raise_for_status()
        data = json_response.json()

        if "markdown" in data:
            markdown_text = data["markdown"]
            title = data.get("title", "Untitled")
            subtitle = data.get("subtitle", "")
            cover_img = data.get("cover_img", {}).get("img", {}).get("src", "")

            html_content = markdown_to_html(markdown_text, title, subtitle, cover_img)
            save_to_file(f"posts/post_{idx:02d}_{tx_id}.html", html_content)
        else:
            print(f"Markdown field missing in the response for transaction {tx_id}")
    except requests.RequestException:
        print(f"Failed to process transaction {tx_id}")


def process_pending_transactions(existing_tx_ids):
    with open("arweave_transactions.txt", "r", encoding="utf-8") as tx_file:
        for idx, line in enumerate(tx_file, start=1):
            tx_id = line.strip()
            post_path = f"posts/post_{idx:02d}_{tx_id}.html"
            if not os.path.exists(post_path):
                print(f"Processing unrendered transaction: {tx_id}")
                process_arweave_transaction(tx_id, idx)


def markdown_to_html(markdown_text, title, subtitle, cover_img):
    html_parts = ["<!DOCTYPE html>", "<html>", "<head>", "<title>", title, "</title>", "</head>", "<body>"]

    if cover_img:
        html_parts.append(f'<img src="{cover_img}" alt="Cover Image" style="width:100%; max-width:600px;">')

    html_parts.append(f"<h1>{title}</h1>")

    if subtitle:
        html_parts.append(f"<h2>{subtitle}</h2>")

    html_parts.append(markdown.markdown(markdown_text))
    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)


def save_to_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"Saved: {filepath}")


base_url = "https://paragraph.xyz/@aurora-mm"
scrape_arweave_and_archive(base_url)
