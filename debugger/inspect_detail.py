# coding: utf-8
import sys
from bs4 import BeautifulSoup
import re

sys.stdout.reconfigure(encoding='utf-8')

print("=== DETAIL SAMPLE ===")
with open('detail_sample.html', 'r', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

# Title
title = soup.find('h2')
print("Title:", title.get_text(strip=True) if title else "No h2")

# Cover
cover = soup.find('div', class_='asTBcell uwthumb') or soup.find('div', class_='pic_box') or soup.find('img', class_='pic')
print("Cover container:", cover)

# Tags and info
info_box = soup.find('div', class_='asTBcell uwconn') or soup.find('div', class_='user-body') or soup.find('div', class_='uwconn')
if info_box:
    print("Info box:")
    print(info_box.get_text(separator="\n", strip=True))
    print("Tags inside info box:")
    for a in info_box.find_all('a'):
        print(f"Tag: {a.get_text(strip=True)} -> {a.get('href')}")
else:
    print("Checking all links with /albums-index-tag- or /search-:")
    for a in soup.find_all('a'):
        if 'tag' in a.get('href', ''):
            print(f"Tag link: {a.get_text(strip=True)} -> {a.get('href')}")

# Breadcrumbs / Category
crumbs = soup.find('div', class_=re.compile(r'crumb|bread|position|place', re.I))
if crumbs:
    print("Breadcrumbs:", crumbs.get_text(strip=True))

# Fast read / Gallery links
print("\n--- ACTION BUTTONS / READ BUTTONS ---")
for a in soup.find_all('a', class_=re.compile(r'btn|read|gallary', re.I)):
    print(f"Btn: {a.get_text(strip=True)} -> {a.get('href')}")

# Pagination in detail
pag = soup.find('div', class_='paginator')
if pag:
    print("Detail Paginator:", [a.get('href') for a in pag.find_all('a')])

print("\n=== READ SAMPLE ===")
with open('read_sample.html', 'r', encoding='utf-8', errors='ignore') as f:
    read_soup = BeautifulSoup(f.read(), 'html.parser')

img = read_soup.find('img', id='picarea') or read_soup.find('img', class_='picarea')
print("Read page main img:", img)

# Check script in read page (fast gallery / preload / img_list)
scripts = read_soup.find_all('script')
for s in scripts:
    text = s.string or ""
    if 'img_url' in text or 'fast_img_host' in text or 'url' in text or 'pic' in text or 'photos' in text:
        if len(text) < 1000:
            print("Interesting script:", text)
        else:
            print("Long script snippet:", text[:300])

