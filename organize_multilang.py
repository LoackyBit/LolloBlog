#!/usr/bin/env python3
"""
Script per organizzare i post in cartelle multilingua basato sul campo language nel front matter.
Questo script sposta i post dalle cartelle content/posts nelle cartelle specifiche per lingua:
- content/it/posts per post in italiano (language: it)
- content/en/posts per post in inglese (language: en)
Se non è specificata una lingua, il post rimane in content/posts
"""

import os
import shutil
import re
import yaml
from pathlib import Path

# Percorsi
HUGO_POSTS_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
HUGO_IT_POSTS_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/it/post"
HUGO_EN_POSTS_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/en/post"

# Regex per estrarre il front matter YAML
FRONT_MATTER_REGEX = r'^---\s*\n(.*?)\n---\s*\n'

def parse_front_matter(content):
    """Parse YAML front matter from markdown content."""
    match = re.match(FRONT_MATTER_REGEX, content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1)) or {}
            return front_matter
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML front matter: {e}")
            return {}
    return {}

def get_language_from_post(post_path):
    """Estrae la lingua dal front matter del post."""
    index_file = os.path.join(post_path, "index.md")
    if not os.path.exists(index_file):
        print(f"⚠️  No index.md found in {post_path}")
        return None
    
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        front_matter = parse_front_matter(content)
        
        # Cerca il campo language o lang
        language = front_matter.get('language') or front_matter.get('lang')
        return language
        
    except Exception as e:
        print(f"❌ Error reading {index_file}: {e}")
        return None

def organize_posts():
    """Organizza i post nelle cartelle per lingua."""
    if not os.path.exists(HUGO_POSTS_DIR):
        print(f"⚠️  Source directory not found: {HUGO_POSTS_DIR}")
        return False
    
    # Crea le cartelle di destinazione se non esistono
    os.makedirs(HUGO_IT_POSTS_DIR, exist_ok=True)
    os.makedirs(HUGO_EN_POSTS_DIR, exist_ok=True)
    
    moved_posts = {"it": [], "en": [], "unknown": []}
    
    print(f"🔍 Scanning posts in: {HUGO_POSTS_DIR}")
    
    for item in os.listdir(HUGO_POSTS_DIR):
        item_path = os.path.join(HUGO_POSTS_DIR, item)
        
        # Salta file che non sono cartelle
        if not os.path.isdir(item_path):
            continue
            
        # Salta cartelle che iniziano con punto
        if item.startswith('.'):
            continue
        
        print(f"\n� Processing post: {item}")
        
        # Determina la lingua del post
        language = get_language_from_post(item_path)
        
        if language == "it":
            # Sposta in cartella italiana
            dest_path = os.path.join(HUGO_IT_POSTS_DIR, item)
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.move(item_path, dest_path)
                moved_posts["it"].append(item)
                print(f"🇮🇹 Moved to Italian posts: {item}")
            except Exception as e:
                print(f"❌ Error moving {item} to Italian folder: {e}")
                
        elif language == "en":
            # Sposta in cartella inglese
            dest_path = os.path.join(HUGO_EN_POSTS_DIR, item)
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.move(item_path, dest_path)
                moved_posts["en"].append(item)
                print(f"🇺🇸 Moved to English posts: {item}")
            except Exception as e:
                print(f"❌ Error moving {item} to English folder: {e}")
                
        else:
            # Lingua non specificata o non riconosciuta
            moved_posts["unknown"].append(item)
            print(f"❓ No language specified for: {item} (will remain in posts/)")
    
    # Riepilogo
    print(f"\n📊 SUMMARY:")
    print(f"🇮🇹 Italian posts moved: {len(moved_posts['it'])}")
    for post in moved_posts['it']:
        print(f"   - {post}")
    
    print(f"🇺🇸 English posts moved: {len(moved_posts['en'])}")
    for post in moved_posts['en']:
        print(f"   - {post}")
    
    print(f"❓ Posts without language: {len(moved_posts['unknown'])}")
    for post in moved_posts['unknown']:
        print(f"   - {post}")
    
    return True

if __name__ == "__main__":
    print("🌍 Starting multilingual post organization...")
    success = organize_posts()
    if success:
        print("\n✅ Organization completed successfully!")
    else:
        print("\n❌ Organization failed!")
    exit(0 if success else 1)
