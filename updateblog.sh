#!/bin/bash

# Variabili
OBSIDIAN_POST_DIR="/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog"
HUGO_POST_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
IMAGES_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/images.py"
CLEANUP_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/cleanup.py"
HUGO_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog"
REPO_URL="https://github.com/LoackyBit/LolloBlog"

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

# Step 3: Pulizia file markdown duplicati
echo "Step 3: Pulizia file markdown duplicati..."
python3 "$CLEANUP_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Pulizia file duplicati fallita. Controlla il file cleanup.py."
    exit 1
fi
echo "Step 3 completato: Pulizia terminata."

# Step 4: Vai alla directory di Hugo
echo "Step 4: Spostamento nella directory di Hugo..."
cd "$HUGO_DIR" || {
    echo "Errore: Impossibile cambiare directory in $HUGO_DIR."
    exit 1
}
echo "Step 4 completato: Directory cambiata in $HUGO_DIR."

# Step 5: Genera il sito
echo "Step 5: Generazione del sito con Hugo..."
hugo
if [ $? -ne 0 ]; then
    echo "Errore: Generazione del sito con Hugo fallita. Controlla la configurazione."
    exit 1
fi
echo "Step 5 completato: Generazione del sito terminata."

# Step 6: Aggiungi e commita i file
echo "Step 6: Aggiunta e commit dei file..."
git add .
git commit -m "Aggiornamento blog $(date +%F)"
if [ $? -ne 0 ]; then
    echo "Errore: Commit dei file fallito. Controlla lo stato del repository Git."
    exit 1
fi
echo "Step 6 completato: Commit eseguito."

# Step 7: Push sul branch principale (per Vercel)
echo "Step 7: Push sul branch principale per Vercel..."
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Errore: Push sul branch principale fallito. Controlla la connessione SSH o il repository."
    exit 1
fi
echo "Step 7 completato: Push eseguito con successo."