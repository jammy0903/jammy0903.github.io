#!/usr/bin/env python3
"""Fix dates: convert GMT times to KST (+0900) properly"""

import xml.etree.ElementTree as ET
import urllib.request
import re
import os
from datetime import datetime, timedelta

RSS_URL = "https://v2.velog.io/rss/@jammy0903"
POSTS_DIR = "_posts"

def fetch_rss():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")

def slugify(title):
    slug = re.sub(r'[^\w\s가-힣-]', '', title)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug.strip('-')
    return slug[:80] if slug else "untitled"

def main():
    xml_data = fetch_rss()
    root = ET.fromstring(xml_data)
    channel = root.find("channel")
    items = channel.findall("item")

    # Build a map: title -> correct KST datetime
    title_to_kst = {}
    for item in items:
        title = item.find("title").text.strip()
        pub_date_str = item.find("pubDate").text
        # Parse GMT time
        gmt_dt = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        # Convert to KST (+9 hours)
        kst_dt = gmt_dt + timedelta(hours=9)
        title_to_kst[title] = kst_dt

    # Process each post file
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title from front matter
        title_match = re.search(r'title:\s*"(.+?)"', content)
        if not title_match:
            continue
        post_title = title_match.group(1)

        # Find matching RSS entry
        kst_dt = None
        for rss_title, dt in title_to_kst.items():
            if rss_title.replace("'", "'").strip() == post_title.replace("'", "'").strip():
                kst_dt = dt
                break
            # Fuzzy match - first 10 chars
            if rss_title[:10] == post_title[:10]:
                kst_dt = dt
                break

        if not kst_dt:
            print(f"  SKIP (no match): {filename}")
            continue

        # Update date in front matter
        old_date_match = re.search(r'date:\s*.+', content)
        if old_date_match:
            new_date_str = f'date: {kst_dt.strftime("%Y-%m-%d %H:%M:%S")} +0900'
            content = content.replace(old_date_match.group(0), new_date_str)

        # Check if filename date needs updating
        new_date_prefix = kst_dt.strftime("%Y-%m-%d")
        old_date_prefix = filename[:10]

        if old_date_prefix != new_date_prefix:
            new_filename = new_date_prefix + filename[10:]
            new_filepath = os.path.join(POSTS_DIR, new_filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            os.rename(filepath, new_filepath)
            print(f"  RENAMED: {filename} -> {new_filename}")
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  FIXED: {filename} (time updated)")

    print("\nDone!")

if __name__ == "__main__":
    main()
