#!/bin/bash

# Variabili
OBSIDIAN_POST_DIR="/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog"
HUGO_POST_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
IMAGES_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/images.py"
CLEANUP_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/cleanup.py"
SYNC_EXCLUDE_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/sync_exclude_drafts.py"
EXCLUDE_FILE="/Users/lorenzo/Documents/GitHub/LolloBlog/.rsyncexclude"
HUGO_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog"
REPO_URL="https://github.com/LoackyBit/LolloBlog"

# Step 1: Crea file di esclusione per post draft
echo "Step 1: Creazione file di esclusione per post draft..."
python3 "$SYNC_EXCLUDE_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Creazione file di esclusione fallita. Controlla il file sync_exclude_drafts.py."
    exit 1
fi
echo "Step 1 completato: File di esclusione creato."

# Step 2: Sincronizza i file markdown da Obsidian a Hugo con rsync (escludendo draft)
echo "Step 2: Sincronizzazione dei file markdown da Obsidian a Hugo (escludendo draft)..."
rsync -av --delete --exclude-from="$EXCLUDE_FILE" "$OBSIDIAN_POST_DIR/" "$HUGO_POST_DIR/"
if [ $? -ne 0 ]; then
    echo "Errore: Sincronizzazione con rsync fallita. Controlla i percorsi o installa rsync."
    exit 1
fi

# Rimuovi eventuali cartelle page bundle corrispondenti ai post draft
echo "Rimozione cartelle page bundle per post draft..."
while IFS= read -r draft_file; do
    if [ -n "$draft_file" ]; then
        # Ricava il nome del bundle dalla filename (rimuove .md)
        bundle_name="${draft_file%.md}"
        bundle_dir="$HUGO_POST_DIR/$bundle_name"
        if [ -d "$bundle_dir" ]; then
            rm -rf "$bundle_dir"
            echo "🗑️  Removed draft bundle directory: $bundle_name"
        fi
    fi
done < "$EXCLUDE_FILE"

echo "Step 2 completato: Sincronizzazione terminata."

# Step 3: Esegui lo script Python per sincronizzare markdown e immagini
echo "Step 3: Esecuzione dello script Python per sincronizzare markdown e immagini..."
python3 "$IMAGES_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Esecuzione dello script Python fallita. Controlla il file images.py o i percorsi."
    exit 1
fi
echo "Step 3 completato: Elaborazione Python terminata."

# Step 4: Pulizia file markdown duplicati
echo "Step 4: Pulizia file markdown duplicati..."
python3 "$CLEANUP_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Pulizia file duplicati fallita. Controlla il file cleanup.py."
    exit 1
fi
echo "Step 4 completato: Pulizia terminata."

# Step 5: Vai alla directory di Hugo
echo "Step 5: Spostamento nella directory di Hugo..."
cd "$HUGO_DIR" || {
    echo "Errore: Impossibile cambiare directory in $HUGO_DIR."
    exit 1
}
echo "Step 5 completato: Directory cambiata in $HUGO_DIR."

# Step 6: Genera il sito
echo "Step 6: Generazione del sito con Hugo..."
hugo --buildDrafts --buildFuture
if [ $? -ne 0 ]; then
    echo "Errore: Generazione del sito con Hugo fallita. Controlla la configurazione."
    exit 1
fi
echo "Step 6 completato: Generazione del sito terminata."

# Step 7: Aggiungi e commita i file
echo "Step 7: Aggiunta e commit dei file..."
git add .
git commit -m "Aggiornamento blog $(date +%F)"
if [ $? -ne 0 ]; then
    echo "Errore: Commit dei file fallito. Controlla lo stato del repository Git."
    exit 1
fi
echo "Step 7 completato: Commit eseguito."

# Step 8: Push sul branch principale (per Vercel)
echo "Step 8: Push sul branch principale per Vercel..."
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Errore: Push sul branch principale fallito. Controlla la connessione SSH o il repository."
    exit 1
fi
echo "Step 8 completato: Push eseguito con successo."