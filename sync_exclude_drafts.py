#!/usr/bin/env python3
"""
Script per creare un file di esclusione per rsync basato sui post draft.
Questo script scansiona i file markdown in Obsidian e crea un file .rsyncexclude
con i nomi dei file che hanno draft: true.
"""

import os
import re
import yaml
from pathlib import Path

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"
EXCLUDE_FILE = "/Users/lorenzo/Documents/GitHub/LolloBlog/.rsyncexclude"

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

def create_exclude_file():
    """Crea il file di esclusione per rsync basato sui post draft."""
    draft_files = []
    
    if not os.path.exists(OBSIDIAN_POST_DIR):
        print(f"⚠️  Warning: Obsidian directory not found: {OBSIDIAN_POST_DIR}")
        return False
    
    print(f"🔍 Scanning for draft posts in: {OBSIDIAN_POST_DIR}")
    
    for filename in os.listdir(OBSIDIAN_POST_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(OBSIDIAN_POST_DIR, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                front_matter = parse_front_matter(content)
                
                # Controlla se il post è in draft
                if front_matter.get('draft', False):
                    draft_files.append(filename)
                    print(f"📝 Found draft post: {filename}")
                    
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    
    # Crea il file di esclusione
    try:
        with open(EXCLUDE_FILE, "w", encoding="utf-8") as f:
            if draft_files:
                for draft_file in draft_files:
                    f.write(f"{draft_file}\n")
                print(f"📄 Created exclude file with {len(draft_files)} draft post(s): {EXCLUDE_FILE}")
            else:
                # File vuoto se non ci sono draft
                print(f"📄 Created empty exclude file (no drafts found): {EXCLUDE_FILE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating exclude file: {e}")
        return False

if __name__ == "__main__":
    success = create_exclude_file()
    exit(0 if success else 1)
