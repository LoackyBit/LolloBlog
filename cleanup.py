#!/usr/bin/env python3
"""
Script per pulire i file markdown duplicati dopo la creazione dei page bundle.
Questo script rimuove i file .md originali dalla cartella posts per evitare 
conflitti con i page bundle creati da images.py.
"""

import os

# Percorsi
HUGO_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"

def cleanup_original_markdown_files():
    """
    Rimuove i file markdown originali (.md) dalla cartella posts
    per evitare conflitti con i page bundle.
    """
    print("🧹 Starting cleanup of original markdown files...")
    
    if not os.path.exists(HUGO_POST_DIR):
        print(f"❌ Error: Posts directory not found: {HUGO_POST_DIR}")
        return False
    
    removed_count = 0
    for filename in os.listdir(HUGO_POST_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(HUGO_POST_DIR, filename)
            try:
                os.remove(file_path)
                print(f"✅ Removed: {filename}")
                removed_count += 1
            except OSError as e:
                print(f"❌ Error removing {filename}: {e}")
                return False
    
    if removed_count > 0:
        print(f"🎉 Cleanup completed! Removed {removed_count} original markdown file(s).")
    else:
        print("ℹ️  No original markdown files found to remove.")
    
    return True

if __name__ == "__main__":
    success = cleanup_original_markdown_files()
    exit(0 if success else 1)
