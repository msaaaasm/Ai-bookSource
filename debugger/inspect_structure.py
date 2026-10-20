import urllib.request
from bs4 import BeautifulSoup
import re

with open('wnacg_home.html', 'r', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print("--- NAV LINKS ---")
nav = soup.find('div', class_='nav') or soup.find('div', id='nav') or soup.find('ul', class_='nav')
if nav:
    for a in nav.find_all('a'):
        print(f"{a.get_text(strip=True)}: {a.get('href')}")
else:
    print("Nav not found, checking all top header links:")
    header = soup.find('div', class_='header')
    if header:
        for a in header.find_all('a'):
            print(f"{a.get_text(strip=True)}: {a.get('href')}")

print("\n--- SEARCH INPUT ---")
for inp in soup.find_all('input'):
    print(inp.parent.name, inp.attrs)

print("\n--- TAG CLOUD OR SIDEBAR ---")
for tag_box in soup.find_all(class_=re.compile(r'tag|label|sort|cate', re.I)):
    print(tag_box.get('class'))

print("\n--- GALLARY ITEM STRUCTURE ---")
item = soup.find('li', class_=re.compile(r'gallary_item|li'))
if item:
    print(item.prettify()[:800])

