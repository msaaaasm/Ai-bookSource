# coding: utf-8
import sys
import urllib.request
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

albums_html = fetch('https://wnacg.com/albums.html')
soup = BeautifulSoup(albums_html, 'html.parser')

print("--- FORMS ON /albums.html ---")
for f in soup.find_all('form'):
    print(f.prettify())

print("--- INPUTS ON /albums.html ---")
for inp in soup.find_all('input'):
    print(inp)

print("--- SEARCH LINKS OR BUTTONS ---")
for a in soup.find_all('a'):
    href = a.get('href', '')
    if 'search' in href or 'tag' in href:
        print(f"{a.get_text(strip=True)}: {href}")

