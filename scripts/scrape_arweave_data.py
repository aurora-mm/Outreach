# Script for scraping Paragraph.xyz blog posts from Arweave

import os
import re
import requests
from bs4 import BeautifulSoup
import json

# Extract Arweave transactions and process them
def scrape_arweave_data(base_url):
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Create a directory to save posts
    os.makedirs("posts", exist_ok=True)

    # Find links to posts
    articles = soup.find_all('a', href=True)
    post_links = [link['href'] for link in articles if link['href'].startswith(f"{base_url}/")]

    # Deduplicate and iterate through the links
    post_links = list(set(post_links))
    for idx, link in enumerate(post_links, start=1):
        post_url = link if link.startswith("http") else f"{base_url}{link}"
        post_response = requests.get(post_url)
        post_response.raise_for_status()

        post_soup = BeautifulSoup(post_response.text, 'html.parser')

        # Extract the transaction from the content
        content = post_soup.get_text()
        match = re.search(r"ARWEAVE TX\s+([A-Za-z0-9_-]+)", content)
        if match:
            arweave_tx = match.group(1)
            print(f"Found transaction: {arweave_tx}")

            # Retrieve JSON data
            permagate_url = f"https://permagate.io/{arweave_tx}"
            json_response = requests.get(permagate_url)
            json_response.raise_for_status()
            data = json_response.json()

            # Extract and cleanse text
            if "json" in data:
                content_json = json.loads(data["json"])
                text_content = extract_human_text(content_json)
                save_to_file(f"posts/post_{idx:02d}_{arweave_tx}.txt", text_content)
            else:
                print(f"JSON field missing in the response for transaction {arweave_tx}")
        else:
            print(f"No transactions found in {post_url}")

# Extract human-readable content from JSON, removing tags
def extract_human_text(json_data):
    text_parts = []

    # Traverse the content node by node
    for node in json_data.get("content", []):
        if "text" in node:  # Direct text content
            text_parts.append(node["text"])
        elif node.get("type") == "paragraph":  # Paragraph content
            text_parts.append(" ".join([part.get("text", "") for part in node.get("content", [])]))

    return "\n\n".join(text_parts)

# Save the given content to a file
def save_to_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        print(f"Saved: {filepath}")

base_url = "https://paragraph.xyz/@aurora-mm"
scrape_arweave_data(base_url)
