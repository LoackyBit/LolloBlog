#!/usr/bin/env python3
"""
Script per sincronizzare i post da Obsidian a Hugo con supporto multilingua.
Rileva automaticamente la lingua dei post e li sincronizza nelle cartelle corrette.
"""

import os
import shutil
import re
import yaml
from pathlib import Path
from langdetect import detect
import argparse

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"
HUGO_IT_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/it/posts"
HUGO_EN_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/en/posts"
EXCLUDE_FILE = "/Users/lorenzo/Documents/GitHub/LolloBlog/.rsyncexclude"

# Regex per estrarre il front matter YAML
FRONT_MATTER_REGEX = r'^---\s*\n(.*?)\n---\s*\n'

def parse_front_matter(content):
    """Parse YAML front matter from markdown content."""
    match = re.match(FRONT_MATTER_REGEX, content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1)) or {}
            return front_matter, match.end()
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML front matter: {e}")
            return {}, 0
    return {}, 0

def detect_language(content, front_matter):
    """
    Rileva la lingua del post.
    Controlla prima il front matter per un campo 'lang' o 'language',
    poi cerca di rilevare automaticamente dalla lingua del contenuto.
    """
    # Controllo esplicito nel front matter
    lang = front_matter.get('lang') or front_matter.get('language')
    if lang:
        return lang.lower()
    
    # Rilevazione automatica dal contenuto
    try:
        # Rimuovi il front matter e codice per migliorare la rilevazione
        content_without_fm = content[content.find('---', 3) + 3:] if '---' in content else content
        # Rimuovi blocchi di codice
        content_clean = re.sub(r'```.*?```', '', content_without_fm, flags=re.DOTALL)
        content_clean = re.sub(r'`[^`]*`', '', content_clean)
        # Rimuovi link e immagini
        content_clean = re.sub(r'!\[.*?\]\(.*?\)', '', content_clean)
        content_clean = re.sub(r'\[.*?\]\(.*?\)', '', content_clean)
        
        if len(content_clean.strip()) < 50:
            print("⚠️  Contenuto troppo breve per rilevare la lingua, assumo italiano")
            return 'it'
            
        detected = detect(content_clean)
        print(f"🔍 Lingua rilevata automaticamente: {detected}")
        return detected
    except Exception as e:
        print(f"⚠️  Errore nella rilevazione della lingua: {e}, assumo italiano")
        return 'it'

def is_draft_post(front_matter):
    """Controlla se un post è marcato come draft."""
    return front_matter.get('draft', False)

def get_target_directory(language):
    """Ottieni la directory di destinazione basata sulla lingua."""
    if language == 'en':
        return HUGO_EN_POST_DIR
    else:  # Default a italiano per tutte le altre lingue
        return HUGO_IT_POST_DIR

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
                
                front_matter, _ = parse_front_matter(content)
                
                # Controlla se il post è in draft
                if is_draft_post(front_matter):
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

def sync_posts():
    """Sincronizza i post da Obsidian a Hugo con supporto multilingua."""
    if not os.path.exists(OBSIDIAN_POST_DIR):
        print(f"❌ Error: Obsidian directory not found: {OBSIDIAN_POST_DIR}")
        return False
    
    # Assicurati che le directory di destinazione esistano
    os.makedirs(HUGO_IT_POST_DIR, exist_ok=True)
    os.makedirs(HUGO_EN_POST_DIR, exist_ok=True)
    
    # Leggi il file di esclusione
    excluded_files = set()
    if os.path.exists(EXCLUDE_FILE):
        with open(EXCLUDE_FILE, "r", encoding="utf-8") as f:
            excluded_files = set(line.strip() for line in f if line.strip())
    
    posts_processed = 0
    posts_it = 0
    posts_en = 0
    
    print(f"🔄 Sincronizzazione post da Obsidian...")
    
    for filename in os.listdir(OBSIDIAN_POST_DIR):
        if not filename.endswith(".md"):
            continue
            
        if filename in excluded_files:
            print(f"⏭️  Skipping draft post: {filename}")
            continue
        
        source_path = os.path.join(OBSIDIAN_POST_DIR, filename)
        
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            front_matter, _ = parse_front_matter(content)
            
            # Rileva la lingua
            language = detect_language(content, front_matter)
            target_dir = get_target_directory(language)
            
            # Crea directory bundle
            bundle_name = filename[:-3]  # Rimuovi .md
            bundle_dir = os.path.join(target_dir, bundle_name)
            os.makedirs(bundle_dir, exist_ok=True)
            
            # Copia il file markdown come index.md
            dest_path = os.path.join(bundle_dir, "index.md")
            shutil.copy2(source_path, dest_path)
            
            if language == 'en':
                posts_en += 1
                print(f"🇺🇸 English post: {filename} -> {target_dir}/{bundle_name}/")
            else:
                posts_it += 1
                print(f"🇮🇹 Italian post: {filename} -> {target_dir}/{bundle_name}/")
            
            posts_processed += 1
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            continue
    
    print(f"\n✅ Sincronizzazione completata:")
    print(f"   📊 Post processati: {posts_processed}")
    print(f"   🇮🇹 Post italiani: {posts_it}")
    print(f"   🇺🇸 Post inglesi: {posts_en}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Sincronizza post multilingua da Obsidian a Hugo')
    parser.add_argument('--dry-run', action='store_true', help='Mostra cosa verrebbe fatto senza eseguire')
    args = parser.parse_args()
    
    if args.dry_run:
        print("🧪 Modalità dry-run attivata")
        return
    
    # Step 1: Crea file di esclusione
    print("Step 1: Creazione file di esclusione per post draft...")
    if not create_exclude_file():
        return False
    
    # Step 2: Sincronizza post
    print("\nStep 2: Sincronizzazione post multilingua...")
    if not sync_posts():
        return False
    
    print("\n🎉 Sincronizzazione multilingua completata con successo!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
