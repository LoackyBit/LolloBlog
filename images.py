import os
import re
import shutil
import yaml

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"  # Cartella dei post in Obsidian
ATTACHMENTS_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/99 - Meta/Clipboard"  # Cartella degli allegati
HUGO_IT_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/it/post"  # Cartella dei post italiani in Hugo
HUGO_EN_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/en/post"  # Cartella dei post inglesi in Hugo

# Lista di tutte le directory dei post Hugo per il multilingua
HUGO_POST_DIRS = [HUGO_IT_POST_DIR, HUGO_EN_POST_DIR]

# Regex per trovare i link delle immagini in formato Obsidian (con singolo !)
IMAGE_REGEX = r'!\[\[([^]]*\.png)\]\]'

# Regex per estrarre il front matter YAML
FRONT_MATTER_REGEX = r'^---\s*\n(.*?)\n---\s*\n'

def parse_front_matter(content):
    """Parse YAML front matter from markdown content."""
    match = re.match(FRONT_MATTER_REGEX, content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1)) or {}
            return front_matter, match.group(0)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML front matter: {e}")
            return {}, None
    return {}, None

def is_draft_post(file_path):
    """Controlla se un post è marcato come draft."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        front_matter, _ = parse_front_matter(content)
        return front_matter.get('draft', False)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def update_front_matter(content, front_matter, original_front_matter):
    """Update the front matter with modified image name and return new content."""
    if 'image' in front_matter and front_matter['image']:
        image_name = front_matter['image']
        new_image_name = image_name.replace(" ", "-")
        if image_name != new_image_name:
            front_matter['image'] = new_image_name
            # Regenerate YAML front matter
            new_yaml = yaml.dump(front_matter, allow_unicode=True, sort_keys=False, default_flow_style=False)
            # Replace original front matter with updated version
            new_front_matter = f"---\n{new_yaml}---\n"
            return content.replace(original_front_matter, new_front_matter)
    return content

def process_multilingual_posts():
    """Processa i post nelle cartelle multilingua."""
    processed_count = 0
    
    # Processa i post in entrambe le cartelle lingua
    for hugo_dir in HUGO_POST_DIRS:
        if not os.path.exists(hugo_dir):
            print(f"Directory not found: {hugo_dir}")
            continue
            
        print(f"\n📁 Processing posts in: {hugo_dir}")
        
        for bundle_name in os.listdir(hugo_dir):
            bundle_path = os.path.join(hugo_dir, bundle_name)
            
            # Salta file che non sono cartelle
            if not os.path.isdir(bundle_path):
                continue
                
            # Salta cartelle che iniziano con punto
            if bundle_name.startswith('.'):
                continue
            
            markdown_file = os.path.join(bundle_path, "index.md")
            if not os.path.exists(markdown_file):
                print(f"⚠️  No index.md found in {bundle_path}")
                continue
                
            print(f"📝 Processing bundle: {bundle_name}")
            processed_count += 1
            
            # Processa le immagini per questo post
            process_images_for_post(bundle_path, markdown_file)
    
    return processed_count

def process_images_for_post(bundle_dir, markdown_file):
    """Processa le immagini per un singolo post."""
    # Leggi il contenuto del file markdown
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Estrai il front matter
    front_matter, original_front_matter = parse_front_matter(content)
    
    # Gestisci l'immagine specificata nel parametro 'image' del front matter
    if 'image' in front_matter and front_matter['image']:
        image_name = front_matter['image']
        new_image_name = image_name.replace(" ", "-")
        src_path = os.path.join(ATTACHMENTS_DIR, image_name)
        dst_path = os.path.join(bundle_dir, new_image_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"  ✅ Copied featured image: {new_image_name}")
        else:
            print(f"  ❌ Featured image {image_name} not found")

    # Aggiorna il front matter con il nome dell'immagine modificato
    content = update_front_matter(content, front_matter, original_front_matter)

    # Trova e sostituisci i link delle immagini nel contenuto
    def replace_image(match):
        image_name = match.group(1)
        new_image_name = image_name.replace(" ", "-")
        src_path = os.path.join(ATTACHMENTS_DIR, image_name)
        dst_path = os.path.join(bundle_dir, new_image_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"  ✅ Copied content image: {new_image_name}")
        else:
            print(f"  ❌ Content image {image_name} not found")
        return f"![{new_image_name}]({new_image_name})"

    new_content = re.sub(IMAGE_REGEX, replace_image, content)

    # Salva il file modificato
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(new_content)

# Processo principale
print("🖼️  Starting multilingual image processing...")
processed = process_multilingual_posts()
print(f"\n✅ Processing completed! Processed {processed} post bundles.")