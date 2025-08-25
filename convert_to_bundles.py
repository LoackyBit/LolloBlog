#!/usr/bin/env python3
"""
Script per convertire i file markdown singoli in page bundles.
Converte file .md in cartelle con index.md per compatibilità con Hugo.
"""

import os
import shutil
import yaml
import re

# Percorsi
HUGO_POSTS_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"

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

def convert_to_page_bundles():
    """Converte i file markdown singoli in page bundles."""
    if not os.path.exists(HUGO_POSTS_DIR):
        print(f"⚠️  Directory not found: {HUGO_POSTS_DIR}")
        return False
    
    converted_count = 0
    
    print(f"🔄 Converting markdown files to page bundles in: {HUGO_POSTS_DIR}")
    
    for filename in os.listdir(HUGO_POSTS_DIR):
        if not filename.endswith(".md"):
            continue
            
        if filename.startswith('.'):
            continue
        
        file_path = os.path.join(HUGO_POSTS_DIR, filename)
        
        # Skip se non è un file
        if not os.path.isfile(file_path):
            continue
        
        print(f"📝 Converting: {filename}")
        
        # Leggi il contenuto del file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Controlla se è draft
        front_matter = parse_front_matter(content)
        if front_matter.get('draft', False):
            print(f"  ⏭️  Skipping draft: {filename}")
            continue
        
        # Nome del bundle (rimuove .md)
        bundle_name = os.path.splitext(filename)[0]
        bundle_dir = os.path.join(HUGO_POSTS_DIR, bundle_name)
        
        # Se la cartella bundle esiste già, saltala
        if os.path.exists(bundle_dir):
            print(f"  ⚠️  Bundle already exists: {bundle_name}")
            os.remove(file_path)  # Rimuovi il file .md originale
            continue
        
        # Crea la cartella bundle
        os.makedirs(bundle_dir, exist_ok=True)
        
        # Sposta il file come index.md
        index_path = os.path.join(bundle_dir, "index.md")
        shutil.move(file_path, index_path)
        
        converted_count += 1
        print(f"  ✅ Created bundle: {bundle_name}/")
    
    print(f"\n📦 Conversion completed! Converted {converted_count} markdown file(s) to page bundles.")
    return True

if __name__ == "__main__":
    print("📦 Starting markdown to page bundle conversion...")
    success = convert_to_page_bundles()
    exit(0 if success else 1)
