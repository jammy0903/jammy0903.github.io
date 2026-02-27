#!/usr/bin/env python3
"""Add post_number to each post's front matter (oldest=1)"""
import os, re

POSTS_DIR = "_posts"
files = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith(".md"))

for i, filename in enumerate(files, 1):
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove existing post_number if any
    content = re.sub(r'\npost_number:\s*\d+', '', content)

    # Add post_number after the first ---
    content = content.replace("---\nlayout:", f"---\npost_number: {i}\nlayout:", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  #{i:02d} -> {filename}")

print(f"\nDone! Numbered {len(files)} posts.")
