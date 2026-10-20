# coding: utf-8
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open('wnacg_home.html', 'r', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- CATEGORIES ---")
nav = soup.find('div', class_='nav') or soup.find('div', id='nav') or soup.find('ul', class_='nav')
if nav:
    for a in nav.find_all('a'):
        href = a.get('href', '')
        if 'albums' in href:
            print(f"{a.get_text(strip=True)}: {href}")

print("\n--- SEARCH FORM ---")
search_form = soup.find('form')
if search_form:
    print(search_form.prettify())
else:
    print("No form found on homepage, let's check all inputs:")
    for inp in soup.find_all(['input', 'button', 'form']):
        print(inp)

