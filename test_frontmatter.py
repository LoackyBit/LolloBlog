#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/lorenzo/Documents/GitHub/LolloBlog')

# Import le funzioni dallo script images.py
import yaml
import re

def parse_front_matter(content):
    """Parse YAML front matter from markdown content."""
    FRONT_MATTER_REGEX = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(FRONT_MATTER_REGEX, content, re.DOTALL)
    if match:
        try:
            front_matter = yaml.safe_load(match.group(1)) or {}
            return front_matter, match.group(0)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML front matter: {e}")
            return {}, None
    return {}, None

def update_front_matter(content, front_matter, original_front_matter, featured_field):
    """Update the front matter with modified image name and return new content."""
    image_fields = [featured_field, 'image', 'cover']
    updated = False
    
    for field in image_fields:
        if field in front_matter and front_matter[field]:
            image_name = front_matter[field]
            new_image_name = image_name.replace(" ", "-")
            if image_name != new_image_name:
                front_matter[field] = new_image_name
                updated = True
                print(f"Updated {field} field: '{image_name}' -> '{new_image_name}'")
            break
    
    if updated:
        new_yaml = yaml.dump(front_matter, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_front_matter = f"---\n{new_yaml}---\n"
        return content.replace(original_front_matter, new_front_matter)
    return content

# Test con il file First Post.md
file_path = '/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts/First Post.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

front_matter, original_front_matter = parse_front_matter(content)
print("Original front matter:")
print(front_matter)

new_content = update_front_matter(content, front_matter, original_front_matter, 'cover')

print("\n" + "="*50)
print("Testing front matter update with 'cover' field...")

if new_content != content:
    print("✅ Content was updated!")
    # Mostra solo la parte del front matter aggiornata
    new_front_matter, _ = parse_front_matter(new_content)
    print("New front matter:")
    print(new_front_matter)
else:
    print("❌ Content was not updated")
