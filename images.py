import os
import re
import shutil
import yaml

# Percorsi
OBSIDIAN_POST_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog/"  # Cartella dei post in Obsidian
ATTACHMENTS_DIR = "/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/99 - Meta/Clipboard"  # Cartella degli allegati
HUGO_POST_DIR = "/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"  # Cartella dei post in Hugo

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

# Elabora ogni file markdown nella cartella post di Obsidian
for filename in os.listdir(OBSIDIAN_POST_DIR):
    if filename.endswith(".md"):
        # Nome del page bundle (es. "Prova" da "Prova.md")
        bundle_name = filename[:-3]  # Rimuove ".md"
        bundle_dir = os.path.join(HUGO_POST_DIR, bundle_name)
        markdown_file = os.path.join(bundle_dir, "index.md")

        # Crea la directory del page bundle
        os.makedirs(bundle_dir, exist_ok=True)

        # Copia il file markdown come index.md
        shutil.copy2(os.path.join(OBSIDIAN_POST_DIR, filename), markdown_file)

        # Leggi il contenuto del file markdown
        with open(markdown_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Estrai il front matter
        front_matter, original_front_matter = parse_front_matter(content)
        
        # Gestisci l'immagine specificata nel parametro 'image' del front matter
        if 'image' in front_matter and front_matter['image']:
            image_name = front_matter['image']
            # Rinomina l'immagine sostituendo spazi con trattini
            new_image_name = image_name.replace(" ", "-")
            # Verifica se l'immagine esiste in ATTACHMENTS_DIR
            src_path = os.path.join(ATTACHMENTS_DIR, image_name)
            dst_path = os.path.join(bundle_dir, new_image_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Copied featured image: {new_image_name} to {bundle_dir}")
            else:
                print(f"Warning: Featured image {image_name} not found in {ATTACHMENTS_DIR}")

        # Aggiorna il front matter con il nome dell'immagine modificato
        content = update_front_matter(content, front_matter, original_front_matter)

        # Trova e sostituisci i link delle immagini nel contenuto
        def replace_image(match):
            image_name = match.group(1)
            # Rinomina l'immagine sostituendo spazi con trattini
            new_image_name = image_name.replace(" ", "-")
            # Copia l'immagine da attachments alla directory del page bundle con il nuovo nome
            src_path = os.path.join(ATTACHMENTS_DIR, image_name)
            dst_path = os.path.join(bundle_dir, new_image_name)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Copied content image: {new_image_name} to {bundle_dir}")
            else:
                print(f"Warning: Content image {image_name} not found in {ATTACHMENTS_DIR}")
            # Riformatta il link per Stack (solo un !, percorso relativo)
            return f"![{new_image_name}]({new_image_name})"

        new_content = re.sub(IMAGE_REGEX, replace_image, content)

        # Salva il file modificato
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Markdown files processed and images copied successfully.")