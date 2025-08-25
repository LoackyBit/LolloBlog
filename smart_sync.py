#!/usr/bin/env python3
"""
Script per sincronizzare selettivamente i post da Obsidian a Hugo,
escludendo automaticamente i post con draft: true
"""

import os
import shutil
import re
import yaml
from pathlib import Path

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"
HUGO_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"

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

def is_draft_post(file_path):
    """Controlla se un post è marcato come draft."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        front_matter = parse_front_matter(content)
        return front_matter.get('draft', False)
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def get_active_obsidian_posts():
    """Ottiene l'elenco dei post attivi (non draft) in Obsidian."""
    active_posts = {}  # nome_file -> percorso_completo
    
    if not os.path.exists(OBSIDIAN_POST_DIR):
        print(f"⚠️  Warning: Obsidian directory not found: {OBSIDIAN_POST_DIR}")
        return active_posts
    
    for filename in os.listdir(OBSIDIAN_POST_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(OBSIDIAN_POST_DIR, filename)
            
            if not is_draft_post(file_path):
                active_posts[filename] = file_path
                print(f"📄 Active post found: {filename}")
            else:
                print(f"⏭️  Skipping draft post: {filename}")
    
    return active_posts

def get_existing_hugo_posts():
    """Ottiene l'elenco dei post esistenti in Hugo."""
    existing_posts = set()
    
    if not os.path.exists(HUGO_POST_DIR):
        os.makedirs(HUGO_POST_DIR)
        return existing_posts
    
    for item in os.listdir(HUGO_POST_DIR):
        if item.startswith('.'):  # Skip hidden files like .DS_Store
            continue
            
        item_path = os.path.join(HUGO_POST_DIR, item)
        if os.path.isdir(item_path):
            # È una cartella (page bundle)
            existing_posts.add(item)
        elif item.endswith(".md"):
            # È un file markdown
            bundle_name = os.path.splitext(item)[0]
            existing_posts.add(bundle_name)
    
    return existing_posts

def remove_hugo_post(post_name):
    """Rimuove un post da Hugo."""
    removed = False
    
    # Rimuovi cartella page bundle
    bundle_dir = os.path.join(HUGO_POST_DIR, post_name)
    if os.path.exists(bundle_dir) and os.path.isdir(bundle_dir):
        try:
            shutil.rmtree(bundle_dir)
            print(f"🗑️  Removed bundle directory: {post_name}")
            removed = True
        except Exception as e:
            print(f"❌ Error removing bundle directory {post_name}: {e}")
    
    # Rimuovi file markdown
    markdown_file = os.path.join(HUGO_POST_DIR, f"{post_name}.md")
    if os.path.exists(markdown_file):
        try:
            os.remove(markdown_file)
            print(f"🗑️  Removed markdown file: {post_name}.md")
            removed = True
        except Exception as e:
            print(f"❌ Error removing markdown file {post_name}.md: {e}")
    
    return removed

def sync_posts():
    """Sincronizza i post da Obsidian a Hugo, escludendo i draft."""
    print("🔄 Starting intelligent post synchronization...")
    
    # Ottieni post attivi da Obsidian
    active_obsidian_posts = get_active_obsidian_posts()
    active_obsidian_names = set(os.path.splitext(name)[0] for name in active_obsidian_posts.keys())
    
    # Ottieni post esistenti in Hugo
    existing_hugo_posts = get_existing_hugo_posts()
    
    print(f"📊 Found {len(active_obsidian_posts)} active posts in Obsidian")
    print(f"📊 Found {len(existing_hugo_posts)} posts in Hugo")
    
    # Copia/aggiorna post attivi
    copied_count = 0
    for filename, file_path in active_obsidian_posts.items():
        post_name = os.path.splitext(filename)[0]
        destination = os.path.join(HUGO_POST_DIR, filename)
        
        try:
            # Copia il file se non esiste o se è più nuovo
            if not os.path.exists(destination) or os.path.getmtime(file_path) > os.path.getmtime(destination):
                shutil.copy2(file_path, destination)
                print(f"📥 Copied/Updated: {filename}")
                copied_count += 1
        except Exception as e:
            print(f"❌ Error copying {filename}: {e}")
    
    # Rimuovi post che non esistono più in Obsidian o sono diventati draft
    removed_count = 0
    posts_to_remove = existing_hugo_posts - active_obsidian_names
    for post_name in posts_to_remove:
        if remove_hugo_post(post_name):
            removed_count += 1
    
    print(f"✅ Synchronization completed!")
    print(f"📥 Copied/Updated: {copied_count} posts")
    print(f"🗑️  Removed: {removed_count} posts")
    
    return True

if __name__ == "__main__":
    success = sync_posts()
    exit(0 if success else 1)
