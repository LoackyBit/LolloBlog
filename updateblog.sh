#!/bin/bash

# Variabili
OBSIDIAN_POST_DIR="/Users/lorenzo/Library/Mobile Documents/iCloud~md~obsidian/Documents/Ken vault/08 - Blog"
HUGO_POST_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog/content/posts"
IMAGES_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/images.py"
CLEANUP_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/cleanup.py"
SYNC_EXCLUDE_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/sync_exclude_drafts.py"
CONVERT_BUNDLES_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/convert_to_bundles.py"
ORGANIZE_MULTILANG_SCRIPT="/Users/lorenzo/Documents/GitHub/LolloBlog/organize_multilang.py"
EXCLUDE_FILE="/Users/lorenzo/Documents/GitHub/LolloBlog/.rsyncexclude"
HUGO_DIR="/Users/lorenzo/Documents/GitHub/LolloBlog"
REPO_URL="https://github.com/LoackyBit/LolloBlog"

echo "🌐 Avvio sincronizzazione multilingua del blog..."

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
echo "Step 2 completato: Sincronizzazione terminata."

# Step 3: Converte file markdown in page bundles
echo "Step 3: Conversione file markdown in page bundles..."
python3 "$CONVERT_BUNDLES_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Conversione in page bundles fallita. Controlla il file convert_to_bundles.py."
    exit 1
fi
echo "Step 3 completato: Conversione page bundles terminata."

# Step 4: Organizza i post nelle cartelle multilingua
echo "Step 4: Organizzazione post nelle cartelle multilingua..."
python3 "$ORGANIZE_MULTILANG_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Organizzazione multilingua fallita. Controlla il file organize_multilang.py."
    exit 1
fi
echo "Step 4 completato: Post organizzati per lingua."

# Step 5: Esegui lo script Python per sincronizzare markdown e immagini
echo "Step 5: Esecuzione dello script Python per sincronizzare markdown e immagini..."
python3 "$IMAGES_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Esecuzione dello script Python fallita. Controlla il file images.py o i percorsi."
    exit 1
fi
echo "Step 5 completato: Elaborazione Python terminata."

# Step 6: Pulizia file markdown duplicati
echo "Step 6: Pulizia file markdown duplicati..."
python3 "$CLEANUP_SCRIPT"
if [ $? -ne 0 ]; then
    echo "Errore: Pulizia file duplicati fallita. Controlla il file cleanup.py."
    exit 1
fi
echo "Step 6 completato: Pulizia terminata."

# Step 7: Vai alla directory di Hugo
echo "Step 7: Spostamento nella directory di Hugo..."
cd "$HUGO_DIR" || {
    echo "Errore: Impossibile cambiare directory in $HUGO_DIR."
    exit 1
}
echo "Step 7 completato: Directory cambiata in $HUGO_DIR."

# Step 8: Genera il sito
echo "Step 8: Generazione del sito con Hugo..."
hugo --buildDrafts --buildFuture
if [ $? -ne 0 ]; then
    echo "Errore: Generazione del sito con Hugo fallita. Controlla la configurazione."
    exit 1
fi
echo "Step 8 completato: Generazione del sito terminata."

# Step 9: Aggiungi e commita i file
echo "Step 9: Aggiunta e commit dei file..."
git add .
git commit -m "Aggiornamento blog multilingua $(date +%F)"
if [ $? -ne 0 ]; then
    echo "Errore: Commit dei file fallito. Controlla lo stato del repository Git."
    exit 1
fi
echo "Step 9 completato: Commit eseguito."

# Step 10: Push sul branch principale (per Vercel)
echo "Step 10: Push sul branch principale per Vercel..."
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Errore: Push sul branch principale fallito. Controlla la connessione SSH o il repository."
    exit 1
fi
echo "Step 10 completato: Push eseguito con successo."

echo ""
echo "🎉 Aggiornamento blog multilingua completato con successo!"
echo "🌐 Il blog è ora disponibile in italiano e inglese"
echo "🇮🇹 Post italiani: content/it/post"
echo "🇺🇸 Post inglesi: content/en/post"