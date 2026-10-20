import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    return urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')

html = fetch('https://wnacg.com/')

print("=== NAVIGATION / CATEGORIES ===")
nav_section = re.search(r'<div class="nav">([\s\S]*?)</div>\s*</div>', html)
if nav_section:
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', nav_section.group(1))
    for href, text in links:
        print(f"{text.strip()}: {href}")

print("\n=== SEARCH FORM ===")
forms = re.findall(r'<form[\s\S]*?</form>', html)
for f in forms:
    print(f)

print("\n=== SAMPLE ALBUM LINK ===")
album_links = re.findall(r'href="(/photos-index-aid-\d+\.html)"', html)
print("Album links found:", album_links[:5])

if album_links:
    aid_url = 'https://wnacg.com' + album_links[0]
    print(f"\nFetching album detail: {aid_url}")
    detail_html = fetch(aid_url)
    with open('detail_sample.html', 'w', encoding='utf-8') as f:
        f.write(detail_html)
    print("Saved detail_sample.html")

    # Look for read online link or gallery index
    read_links = re.findall(r'href="(/photos-view-id-\d+\.html|/photos-read-id-\d+\.html|/photos-gallery-aid-\d+\.html)"', detail_html)
    print("Read/Gallery links:", read_links)

    if read_links:
        read_url = 'https://wnacg.com' + read_links[0]
        print(f"\nFetching read page: {read_url}")
        read_html = fetch(read_url)
        with open('read_sample.html', 'w', encoding='utf-8') as f:
            f.write(read_html)
        print("Saved read_sample.html")

