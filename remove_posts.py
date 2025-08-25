#!/usr/bin/env python3
"""
Script per rimuovere post dal blog Hugo quando:
1. Il campo draft è impostato a true nel front matter
2. Il file è stato eliminato dalla cartella Obsidian

Questo script deve essere eseguito DOPO la sincronizzazione con rsync
ma PRIMA della generazione dei page bundle.
"""

import os
import re
import shutil
import yaml
from pathlib import Path

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"
HUGO_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
HUGO_PUBLIC_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/public/posts"

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

def get_obsidian_posts():
    """Ottiene l'elenco dei post presenti in Hugo (dopo rsync) escludendo quelli con draft: true."""
    obsidian_posts = set()
    draft_posts = set()
    
    if not os.path.exists(HUGO_POST_DIR):
        print(f"⚠️  Warning: Hugo posts directory not found: {HUGO_POST_DIR}")
        return obsidian_posts, draft_posts
    
    # Controlla i file .md nella directory Hugo (copiati da rsync)
    for filename in os.listdir(HUGO_POST_DIR):
        if filename.endswith(".md"):
            bundle_name = os.path.splitext(filename)[0]
            file_path = os.path.join(HUGO_POST_DIR, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                front_matter = parse_front_matter(content)
                
                # Controlla se il post è in draft
                if front_matter.get('draft', False):
                    draft_posts.add(bundle_name)
                    print(f"📝 Found draft post: {bundle_name}")
                else:
                    obsidian_posts.add(bundle_name)
                    
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        
        elif os.path.isdir(os.path.join(HUGO_POST_DIR, filename)) and not filename.startswith('.'):
            # È una cartella page bundle - controlla il file index.md
            bundle_name = filename
            index_file = os.path.join(HUGO_POST_DIR, filename, "index.md")
            
            if os.path.exists(index_file):
                try:
                    with open(index_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    front_matter = parse_front_matter(content)
                    
                    # Controlla se il post è in draft
                    if front_matter.get('draft', False):
                        draft_posts.add(bundle_name)
                        print(f"📝 Found draft post: {bundle_name}")
                    else:
                        obsidian_posts.add(bundle_name)
                        
                except Exception as e:
                    print(f"❌ Error reading {index_file}: {e}")
    
    return obsidian_posts, draft_posts

def get_hugo_posts():
    """Ottiene l'elenco dei post presenti in Hugo."""
    hugo_posts = set()
    
    if not os.path.exists(HUGO_POST_DIR):
        print(f"⚠️  Warning: Hugo posts directory not found: {HUGO_POST_DIR}")
        return hugo_posts
    
    for item in os.listdir(HUGO_POST_DIR):
        item_path = os.path.join(HUGO_POST_DIR, item)
        if os.path.isdir(item_path):
            # È una cartella (page bundle)
            hugo_posts.add(item)
        elif item.endswith(".md"):
            # È un file markdown (post non ancora convertito in page bundle)
            bundle_name = os.path.splitext(item)[0]
            hugo_posts.add(bundle_name)
    
    return hugo_posts

def remove_hugo_post(bundle_name):
    """Rimuove un post da Hugo (sia cartella che file markdown) e dai file generati."""
    removed = False
    
    # Rimuovi la cartella del page bundle
    bundle_dir = os.path.join(HUGO_POST_DIR, bundle_name)
    if os.path.exists(bundle_dir) and os.path.isdir(bundle_dir):
        try:
            shutil.rmtree(bundle_dir)
            print(f"🗑️  Removed bundle directory: {bundle_name}")
            removed = True
        except Exception as e:
            print(f"❌ Error removing bundle directory {bundle_name}: {e}")
    
    # Rimuovi il file markdown originale (se esiste)
    markdown_file = os.path.join(HUGO_POST_DIR, f"{bundle_name}.md")
    if os.path.exists(markdown_file):
        try:
            os.remove(markdown_file)
            print(f"🗑️  Removed markdown file: {bundle_name}.md")
            removed = True
        except Exception as e:
            print(f"❌ Error removing markdown file {bundle_name}.md: {e}")
    
    # Rimuovi i file generati nella cartella public/ 
    # Hugo genera slug normalizzati (spazi diventano trattini, tutto minuscolo)
    normalized_slug = bundle_name.lower().replace(" ", "-")
    public_dir = os.path.join(HUGO_PUBLIC_DIR, normalized_slug)
    if os.path.exists(public_dir) and os.path.isdir(public_dir):
        try:
            shutil.rmtree(public_dir)
            print(f"🗑️  Removed public directory: {normalized_slug}")
            removed = True
        except Exception as e:
            print(f"❌ Error removing public directory {normalized_slug}: {e}")
    
    return removed

def cleanup_posts():
    """
    Rimuove i post che:
    1. Sono marcati come draft in Obsidian
    2. Non esistono più in Obsidian
    """
    print("🧹 Starting post cleanup...")
    
    # Ottieni l'elenco dei post
    obsidian_posts, draft_posts = get_obsidian_posts()
    hugo_posts = get_hugo_posts()
    
    print(f"📊 Found {len(obsidian_posts)} active posts in Obsidian")
    print(f"📊 Found {len(draft_posts)} draft posts in Obsidian")
    print(f"📊 Found {len(hugo_posts)} posts in Hugo")
    
    removed_count = 0
    
    # Rimuovi post marcati come draft
    for draft_post in draft_posts:
        if draft_post in hugo_posts:
            if remove_hugo_post(draft_post):
                removed_count += 1
                print(f"✅ Removed draft post: {draft_post}")
    
    # Rimuovi post che non esistono più in Obsidian
    posts_to_remove = hugo_posts - obsidian_posts - draft_posts
    for post_name in posts_to_remove:
        if remove_hugo_post(post_name):
            removed_count += 1
            print(f"✅ Removed deleted post: {post_name}")
    
    if removed_count > 0:
        print(f"🎉 Cleanup completed! Removed {removed_count} post(s).")
    else:
        print("ℹ️  No posts to remove.")
    
    return True

if __name__ == "__main__":
    success = cleanup_posts()
    exit(0 if success else 1)
