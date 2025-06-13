#!/bin/bash

# Variabili
OBSIDIAN_POST_DIR="/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog"
HUGO_POST_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
IMAGES_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/images.py"
HUGO_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog"
REPO_URL="https://github.com/Lod34/LolloBlog"

# Step 1: Sincronizza i file markdown da Obsidian a Hugo con rsync
echo "Step 1: Sincronizzazione dei file markdown da Obsidian a Hugo con rsync..."
rsync -av --delete "$OBSIDIAN_POST_DIR/" "$HUGO_POST_DIR/"
if [ $? -ne 0 ]; then
    echo "Errore: Sincronizzazione con rsync fallita. Controlla i percorsi o installa rsync."
    exit 1
fi
echo "Step 1 completato: Sincronizzazione terminata."

# Step 2: Esegui lo script Python per sincronizzare markdown e immagini
echo "Step 2: Esecuzione dello script Python per sincronizzare markdown e immagini..."
python3 "$IMAGES_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Esecuzione dello script Python fallita. Controlla il file images.py o i percorsi."
    exit 1
fi
echo "Step 2 completato: Elaborazione Python terminata."

# Step 3: Vai alla directory di Hugo
echo "Step 3: Spostamento nella directory di Hugo..."
cd "$HUGO_DIR" || {
    echo "Errore: Impossibile cambiare directory in $HUGO_DIR."
    exit 1
}
echo "Step 3 completato: Directory cambiata in $HUGO_DIR."

# Step 4: Genera il sito
echo "Step 4: Generazione del sito con Hugo..."
hugo
if [ $? -ne 0 ]; then
    echo "Errore: Generazione del sito con Hugo fallita. Controlla la configurazione."
    exit 1
fi
echo "Step 4 completato: Generazione del sito terminata."

# Step 5: Aggiungi e commita i file
echo "Step 5: Aggiunta e commit dei file..."
git add .
git commit -m "Aggiornamento blog $(date +%F)"
if [ $? -ne 0 ]; then
    echo "Errore: Commit dei file fallito. Controlla lo stato del repository Git."
    exit 1
fi
echo "Step 5 completato: Commit eseguito."

# Step 6: Push sul branch principale (per Vercel)
echo "Step 6: Push sul branch principale per Vercel..."
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Errore: Push sul branch principale fallito. Controlla la connessione SSH o il repository."
    exit 1
fi
echo "Step 6 completato: Push eseguito con successo."