#!/usr/bin/env python3
"""
Test script per verificare la funzionalità di remove_posts.py
"""

import os
import tempfile
import shutil
import yaml
from remove_posts import parse_front_matter, remove_hugo_post

def test_front_matter_parsing():
    """Test parsing del front matter YAML"""
    print("🧪 Test: Parsing front matter YAML")
    
    # Test con front matter normale
    content1 = """---
title: "Test Post"
date: 2025-08-25
draft: false
tags: ["test", "blog"]
---

# Content here
"""
    
    front_matter1 = parse_front_matter(content1)
    assert front_matter1["title"] == "Test Post"
    assert front_matter1["draft"] == False
    assert "test" in front_matter1["tags"]
    
    # Test con draft: true
    content2 = """---
title: "Draft Post"
date: 2025-08-25
draft: true
---

# Draft content
"""
    
    front_matter2 = parse_front_matter(content2)
    assert front_matter2["title"] == "Draft Post"
    assert front_matter2["draft"] == True
    
    print("✅ Test front matter parsing: SUCCESSO")

def test_remove_hugo_post():
    """Test rimozione post Hugo"""
    print("🧪 Test: Rimozione post Hugo")
    
    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    hugo_posts_dir = os.path.join(temp_dir, "posts")
    os.makedirs(hugo_posts_dir)
    
    try:
        # Backup del percorso originale
        import remove_posts
        original_path = remove_posts.HUGO_POST_DIR
        remove_posts.HUGO_POST_DIR = hugo_posts_dir
        
        # Crea un post di test (page bundle)
        test_post_dir = os.path.join(hugo_posts_dir, "test-post")
        os.makedirs(test_post_dir)
        
        with open(os.path.join(test_post_dir, "index.md"), "w") as f:
            f.write("Test content")
        
        with open(os.path.join(test_post_dir, "image.png"), "w") as f:
            f.write("fake image")
        
        # Verifica che esista
        assert os.path.exists(test_post_dir)
        
        # Rimuovi il post
        result = remove_hugo_post("test-post")
        
        # Verifica che sia stato rimosso
        assert result == True
        assert not os.path.exists(test_post_dir)
        
        print("✅ Test remove hugo post: SUCCESSO")
        
        # Ripristina il percorso originale
        remove_posts.HUGO_POST_DIR = original_path
        
    finally:
        shutil.rmtree(temp_dir)

def test_markdown_file_removal():
    """Test rimozione file markdown singolo"""
    print("🧪 Test: Rimozione file markdown singolo")
    
    # Crea directory temporanea
    temp_dir = tempfile.mkdtemp()
    hugo_posts_dir = os.path.join(temp_dir, "posts")
    os.makedirs(hugo_posts_dir)
    
    try:
        # Backup del percorso originale
        import remove_posts
        original_path = remove_posts.HUGO_POST_DIR
        remove_posts.HUGO_POST_DIR = hugo_posts_dir
        
        # Crea un file markdown di test
        test_md_file = os.path.join(hugo_posts_dir, "test-post.md")
        with open(test_md_file, "w") as f:
            f.write("Test markdown content")
        
        # Verifica che esista
        assert os.path.exists(test_md_file)
        
        # Rimuovi il post
        result = remove_hugo_post("test-post")
        
        # Verifica che sia stato rimosso
        assert result == True
        assert not os.path.exists(test_md_file)
        
        print("✅ Test remove markdown file: SUCCESSO")
        
        # Ripristina il percorso originale
        remove_posts.HUGO_POST_DIR = original_path
        
    finally:
        shutil.rmtree(temp_dir)

def main():
    """Esegui tutti i test"""
    print("🔧 Avvio test per remove_posts.py")
    print("-" * 50)
    
    try:
        test_front_matter_parsing()
        test_remove_hugo_post()
        test_markdown_file_removal()
        
        print("-" * 50)
        print("🎉 Tutti i test sono passati con successo!")
        
    except Exception as e:
        print(f"❌ Test fallito: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
