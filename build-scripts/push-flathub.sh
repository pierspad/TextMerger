#!/usr/bin/env bash
set -euo pipefail

# Script per preparare e pushare su Flathub
# Uso: ./push-flathub.sh [versione]
# Se non specifichi una versione, verrà usata quella dal PKGBUILD

# Posizionati nella root del progetto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

# Funzione per estrarre informazioni dal PKGBUILD
get_pkgbuild_info() {
    local field="$1"
    grep -E "^${field}=" build-scripts/PKGBUILD | head -1 | cut -d '=' -f2 | tr -d '"'"'"
}

# Usa la versione passata come parametro o quella dal PKGBUILD
if [ $# -gt 0 ]; then
    VERSION="$1"
    echo "Uso della versione specificata: $VERSION"
else
    VERSION=$(get_pkgbuild_info "pkgver")
    echo "Uso della versione dal PKGBUILD: $VERSION"
fi

PKGNAME=$(get_pkgbuild_info "pkgname")
PKGDESC=$(get_pkgbuild_info "pkgdesc")
URL=$(get_pkgbuild_info "url")

if [ -z "$VERSION" ] || [ -z "$PKGNAME" ]; then
    echo "Errore: Non riesco a leggere versione o nome dal PKGBUILD"
    exit 1
fi

echo "=== Informazioni per Flathub ==="
echo "Nome: $PKGNAME"
echo "Versione: $VERSION"
echo "Descrizione: $PKGDESC"
echo "URL: $URL"
echo ""

echo "=== Verifica prerequisiti ==="
# Verifica che Git sia configurato
if ! git config user.name >/dev/null 2>&1 || ! git config user.email >/dev/null 2>&1; then
    echo "Errore: Git non è configurato correttamente"
    echo "Esegui: git config --global user.name 'Il Tuo Nome'"
    echo "        git config --global user.email 'tua-email@example.com'"
    exit 1
fi

# Verifica che il repository sia pulito
if ! git diff-index --quiet HEAD --; then
    echo "Errore: Ci sono modifiche non committate nel repository"
    echo "Committa tutte le modifiche prima di procedere"
    git status
    exit 1
fi

# Verifica che il tag esista
if ! git tag | grep -q "v$VERSION"; then
    echo "Errore: Il tag v$VERSION non esiste"
    echo "Crea il tag con: git tag v$VERSION"
    echo "E pushalo con: git push origin v$VERSION"
    exit 1
fi

echo "=== Aggiornamento file Flatpak per Flathub ==="

# Aggiorna automaticamente il manifest YAML con le info dal PKGBUILD
update_flatpak_manifest() {
    local manifest_path="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
    
    # Crea un backup
    cp "$manifest_path" "${manifest_path}.bak"
    
    # Aggiorna il tag della versione
    sed -i "s/tag: v.*/tag: v$VERSION/" "$manifest_path"
    
    # Ottieni l'hash del commit per il tag
    local commit_hash=$(git rev-list -n 1 "v$VERSION")
    sed -i "s/commit: .*/commit: $commit_hash/" "$manifest_path"
    
    echo "Manifest aggiornato:"
    echo "  - Versione: v$VERSION"
    echo "  - Commit: $commit_hash"
}

# Aggiorna il metainfo XML con la nuova versione
update_metainfo() {
    local metainfo_path="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.metainfo.xml"
    local current_date=$(date '+%Y-%m-%d')
    
    # Backup del file originale
    cp "$metainfo_path" "${metainfo_path}.bak"
    
    # Aggiorna la versione nel metainfo (se presente)
    if grep -q '<release version=' "$metainfo_path"; then
        sed -i "s/<release version=\".*\"/<release version=\"$VERSION\"/" "$metainfo_path"
        sed -i "s/date=\".*\"/date=\"$current_date\"/" "$metainfo_path"
        echo "Metainfo aggiornato:"
        echo "  - Versione: $VERSION"
        echo "  - Data: $current_date"
    else
        echo "Nessuna sezione release trovata nel metainfo"
    fi
}

# Aggiorna pyproject.toml nella root
echo "Sincronizzazione versione in pyproject.toml..."
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" pyproject.toml

# Aggiorna i file Flatpak
update_flatpak_manifest
update_metainfo

echo ""
echo "=== Verifica modifiche ==="
echo "File modificati:"
git status --porcelain

echo ""
echo "=== Test build Flatpak ==="
read -p "Vuoi eseguire un test build prima del push? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Esecuzione test build..."
    
    # Pulisci build precedenti
    rm -rf flatpak-build
    rm -rf .flatpak-builder
    
    # Configura Flathub se necessario
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    
    # Installa dipendenze se necessario
    flatpak install -y --user flathub org.kde.Sdk//5.15-24.08 org.kde.Platform//5.15-24.08 2>/dev/null || true
    flatpak install -y --user flathub com.riverbankcomputing.PyQt.BaseApp//5.15-24.08 2>/dev/null || true
    
    # Test build
    MANIFEST_PATH="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
    if flatpak-builder --user --force-clean flatpak-build "$MANIFEST_PATH"; then
        echo "✓ Test build completato con successo!"
        rm -rf flatpak-build .flatpak-builder
    else
        echo "✗ Test build fallito!"
        exit 1
    fi
fi

echo ""
echo "=== Commit delle modifiche ==="
echo "File che verranno committati:"
git add flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml
git add flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.metainfo.xml
git add pyproject.toml

echo ""
git status --staged

read -p "Procedi con il commit? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Aggiorna file Flathub per versione $VERSION"
    echo "✓ Modifiche committate"
else
    echo "Commit annullato"
    exit 1
fi

echo ""
echo "=== Push su GitHub ==="
read -p "Vuoi pushare le modifiche su GitHub? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo "✓ Modifiche pushate su GitHub"
else
    echo "Push annullato"
    exit 1
fi

echo ""
echo "=== Istruzioni per Flathub ==="
echo "✓ I file Flatpak sono stati aggiornati e pushati"
echo ""
echo "Passi successivi per pubblicare su Flathub:"
echo "1. Vai su https://github.com/flathub/flathub"
echo "2. Crea un fork del repository flathub/flathub"
echo "3. Clona il tuo fork: git clone https://github.com/TUO_USERNAME/flathub.git"
echo "4. Copia la cartella flathub-repo/io.github.pierspad.TextMerger nel tuo fork"
echo "5. Crea un commit: git add . && git commit -m 'Add/Update TextMerger $VERSION'"
echo "6. Push: git push origin main"
echo "7. Crea una Pull Request su https://github.com/flathub/flathub"
echo ""
echo "Oppure se hai già un fork:"
echo "1. Copia la cartella aggiornata nel tuo fork di Flathub"
echo "2. Committa e pusha le modifiche"
echo "3. Crea/aggiorna la Pull Request"
echo ""
echo "Nota: La prima submission richiede l'approvazione del team Flathub"
