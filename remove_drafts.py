#!/usr/bin/env python3
"""
Script per rimuovere i post draft dalle cartelle multilingua.
Controlla se i post pubblicati sono diventati draft in Obsidian e li rimuove.
"""

import os
import re
import yaml
import shutil
from pathlib import Path

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"
HUGO_IT_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/it/post"
HUGO_EN_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/en/post"

# Lista di tutte le directory dei post Hugo per il multilingua
HUGO_POST_DIRS = [HUGO_IT_POST_DIR, HUGO_EN_POST_DIR]

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

def is_draft_in_obsidian(post_name):
    """Controlla se un post è draft in Obsidian."""
    obsidian_file = os.path.join(OBSIDIAN_POST_DIR, f"{post_name}.md")
    
    if not os.path.exists(obsidian_file):
        print(f"⚠️  Obsidian file not found: {post_name}.md")
        return False
    
    try:
        with open(obsidian_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        front_matter = parse_front_matter(content)
        is_draft = front_matter.get('draft', False)
        
        if is_draft:
            print(f"📝 Found draft in Obsidian: {post_name}")
        
        return is_draft
        
    except Exception as e:
        print(f"❌ Error reading {obsidian_file}: {e}")
        return False

def remove_draft_posts():
    """Rimuove i post draft dalle cartelle multilingua."""
    removed_count = 0
    
    print(f"🧹 Checking for draft posts to remove...")
    
    for hugo_dir in HUGO_POST_DIRS:
        if not os.path.exists(hugo_dir):
            print(f"Directory not found: {hugo_dir}")
            continue
            
        lang = "IT" if "it" in hugo_dir else "EN"
        print(f"\n📁 Checking {lang} posts in: {hugo_dir}")
        
        for item in os.listdir(hugo_dir):
            item_path = os.path.join(hugo_dir, item)
            
            # Salta file che non sono cartelle
            if not os.path.isdir(item_path):
                continue
                
            # Salta cartelle che iniziano con punto
            if item.startswith('.'):
                continue
            
            print(f"📝 Checking post: {item}")
            
            # Controlla se il post è draft in Obsidian
            if is_draft_in_obsidian(item):
                try:
                    shutil.rmtree(item_path)
                    removed_count += 1
                    print(f"🗑️  Removed draft post: {item}")
                except Exception as e:
                    print(f"❌ Error removing {item}: {e}")
            else:
                print(f"✅ Post still published: {item}")
    
    return removed_count

if __name__ == "__main__":
    print("🧹 Starting draft post cleanup...")
    removed = remove_draft_posts()
    if removed > 0:
        print(f"\n✅ Cleanup completed! Removed {removed} draft post(s).")
    else:
        print(f"\n✅ Cleanup completed! No draft posts found to remove.")
    exit(0)
