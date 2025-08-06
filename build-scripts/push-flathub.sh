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

# Verifica che Python e PyYAML siano disponibili per processare il manifest
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "Avviso: PyYAML non trovato, installo..."
    pip3 install --user PyYAML 2>/dev/null || {
        echo "Errore: Non riesco a installare PyYAML"
        echo "Installa con: pip3 install PyYAML o sudo apt install python3-yaml"
        exit 1
    }
fi

# Verifica che il repository sia pulito
if ! git diff-index --quiet HEAD --; then
    echo "Errore: Ci sono modifiche non committate nel repository"
    echo "Committa tutte le modifiche prima di procedere"
    git status
    exit 1
fi

# Verifica che il tag esista
if ! git tag -l | grep -q "^v$VERSION$"; then
    echo "Errore: Il tag v$VERSION non esiste"
    echo "Tag esistenti:"
    git tag -l | grep -E '^v[0-9]' | sort -V | tail -5
    echo ""
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
    
    # Ottieni l'hash del commit per il tag
    local commit_hash=$(git rev-list -n 1 "v$VERSION" 2>/dev/null) || {
        echo "Errore: Impossibile trovare il commit per il tag v$VERSION"
        return 1
    }
    
    # Usa Python per aggiornare il manifest YAML in modo sicuro
    python3 -c "
import yaml
import sys

manifest_file = '$manifest_path'

try:
    with open(manifest_file, 'r') as f:
        content = f.read()
        data = yaml.safe_load(content)

    # Trova il modulo textmerger e aggiorna tag e commit
    found = False
    for module in data['modules']:
        if module['name'] == 'textmerger':
            for source in module.get('sources', []):
                if source.get('type') == 'git':
                    source['tag'] = 'v$VERSION'
                    source['commit'] = '$commit_hash'
                    found = True
                    break
            break
    
    if not found:
        print('Errore: Modulo textmerger con source git non trovato', file=sys.stderr)
        sys.exit(1)

    with open(manifest_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=float('inf'))

    print('Manifest aggiornato con successo')
except Exception as e:
    print(f'Errore durante l\\'aggiornamento del manifest: {e}', file=sys.stderr)
    sys.exit(1)
" || {
        echo "Errore: Impossibile aggiornare il manifest con Python"
        # Ripristina il backup in caso di errore
        mv "${manifest_path}.bak" "$manifest_path"
        return 1
    }
    
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
    
    # Verifica se il file esiste
    if [[ ! -f "$metainfo_path" ]]; then
        echo "Avviso: File metainfo non trovato in $metainfo_path"
        return 0
    fi
    
    # Aggiorna la versione nel metainfo (se presente)
    if grep -q '<release version=' "$metainfo_path"; then
        # Aggiorna la prima occorrenza di release version
        sed -i "0,/<release version=\"[^\"]*\"/{s/<release version=\"[^\"]*\"/<release version=\"$VERSION\"/}" "$metainfo_path"
        sed -i "0,/date=\"[^\"]*\"/{s/date=\"[^\"]*\"/date=\"$current_date\"/}" "$metainfo_path"
        echo "Metainfo aggiornato:"
        echo "  - Versione: $VERSION"
        echo "  - Data: $current_date"
    else
        echo "Nessuna sezione release trovata nel metainfo"
    fi
}

# Aggiorna pyproject.toml nella cartella packaging
echo "Sincronizzazione versione in packaging/pyproject.toml..."
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" packaging/pyproject.toml

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
git add packaging/pyproject.toml

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
