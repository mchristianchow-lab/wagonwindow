#!/usr/bin/env python3
"""Merge split blog JSON files into build/data/blog.json."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

SOURCE_FILES = [
    '_blog_1_10.json',
    '_blog_11_15.json',
    '_blog_16_20.json',
    '_blog_21_30.json',
    '_blog_31_40.json',
    '_blog_41_50.json',
]

all_posts = []
seen_slugs = set()

for filename in SOURCE_FILES:
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding='utf-8') as f:
        posts = json.load(f)
    for post in posts:
        if post['slug'] in seen_slugs:
            print(f'  ⚠ DUPLICATE SLUG: {post["slug"]} in {filename}')
        else:
            seen_slugs.add(post['slug'])
            all_posts.append(post)
    print(f'  ✓ {filename}: {len(posts)} posts')

all_posts.sort(key=lambda p: p['published_date'])

assert len(all_posts) == 50, f'Expected 50 posts, got {len(all_posts)}'

out = os.path.join(DATA_DIR, 'blog.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

print(f'\n  ✓ blog.json written: {len(all_posts)} posts')
print(f'  Date range: {all_posts[0]["published_date"]} → {all_posts[-1]["published_date"]}')
