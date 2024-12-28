# Script for replacing the Arweave gateway in the HTML file

import re
import os

def replace_gateway(html_file, old_gateway, new_gateway):
    if not os.path.exists(html_file):
        print(f"File '{html_file}' does not exist.")
        return

    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()

    updated_content = re.sub(re.escape(old_gateway), new_gateway, content)

    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)

    print(f"Updated gateway in '{html_file}' to '{new_gateway}'.")

def main():
    html_file = input("Enter the path to the HTML file: ")
    old_gateway = input("Enter the current gateway to replace (e.g., permagate.io): ")
    new_gateway = input("Enter the new gateway to use: ")

    replace_gateway(html_file, old_gateway, new_gateway)

if __name__ == "__main__":
    main()
