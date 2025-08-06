#!/usr/bin/env bash
set -euo pipefail

# Script per buildare Flatpak localmente
# Uso: ./build-flatpak.sh

# Posizionati nella root del progetto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

# Funzione per estrarre informazioni dal PKGBUILD
get_pkgbuild_info() {
    local field="$1"
    grep -E "^${field}=" build-scripts/PKGBUILD | head -1 | cut -d '=' -f2 | tr -d '"'"'"
}

# Estrai versione e altre info dal PKGBUILD
VERSION=$(get_pkgbuild_info "pkgver")
PKGNAME=$(get_pkgbuild_info "pkgname")
PKGDESC=$(get_pkgbuild_info "pkgdesc")
URL=$(get_pkgbuild_info "url")

if [ -z "$VERSION" ] || [ -z "$PKGNAME" ]; then
    echo "Errore: Non riesco a leggere versione o nome dal PKGBUILD"
    exit 1
fi

echo "=== Informazioni dal PKGBUILD ==="
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

# Verifica che flatpak-builder sia installato
if ! command -v flatpak-builder >/dev/null 2>&1; then
    echo "Errore: flatpak-builder non è installato"
    echo "Installa con: sudo apt install flatpak-builder (Ubuntu/Debian) o equivalente per la tua distro"
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

echo "=== Configurazione Flathub repository ==="
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

echo "=== Installazione SDK e Runtime ==="
echo "Installazione delle dipendenze Flatpak..."
flatpak install -y --user flathub org.kde.Sdk//5.15-24.08 org.kde.Platform//5.15-24.08
flatpak install -y --user flathub com.riverbankcomputing.PyQt.BaseApp//5.15-24.08

echo "=== Pulizia cache precedente ==="
# Rimuovi installazione precedente
echo "Rimozione installazione precedente..."
flatpak uninstall --user io.github.pierspad.TextMerger -y 2>/dev/null || true

# Rimuovi directory di build
echo "Pulizia directory di build..."
rm -rf flatpak-build
rm -rf .flatpak-builder

echo "=== Preparazione manifest per build locale ==="
# Crea una copia temporanea del manifest per il build locale
MANIFEST_PATH="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
TEMP_MANIFEST_PATH="build-scripts/io.github.pierspad.TextMerger-local.yml"

if [[ ! -f "$MANIFEST_PATH" ]]; then
    echo "Errore: Manifest non trovato in $MANIFEST_PATH"
    exit 1
fi

# Copia e modifica il manifest per usare i sorgenti locali
cp "$MANIFEST_PATH" "$TEMP_MANIFEST_PATH"

# Copia anche i file desktop necessari nella directory di build-scripts
cp "flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.desktop" "build-scripts/"
cp "flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.metainfo.xml" "build-scripts/"
cp "flathub-repo/io.github.pierspad.TextMerger/logo.png" "build-scripts/"

# Sostituisci la fonte Git con la directory locale per il modulo textmerger
# E aggiorna i percorsi del modulo desktop per puntare ai file corretti
python3 -c "
import yaml
import sys
import os

manifest_file = '$TEMP_MANIFEST_PATH'

with open(manifest_file, 'r') as f:
    data = yaml.safe_load(f)

# Trova il modulo textmerger e sostituisci le sue sources
for module in data['modules']:
    if module['name'] == 'textmerger':
        module['sources'] = [{'type': 'dir', 'path': '..'}]
    elif module['name'] == 'textmerger-desktop':
        # Aggiorna i percorsi per puntare ai file nella directory build-scripts
        for source in module.get('sources', []):
            if source.get('type') == 'file':
                filename = source.get('path', '')
                if filename:
                    source['path'] = filename

with open(manifest_file, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
" || {
    # Fallback se Python/yaml non è disponibile
    echo "Avviso: Usando fallback sed (potrebbe non funzionare perfettamente)"
    # Sostituisci solo la sezione sources del modulo textmerger
    sed -i '/- name: textmerger/,/- name: textmerger-desktop/{
        /sources:/,/commit:/{
            /sources:/c\    sources:\
\      - type: dir\
\        path: ..
            /type: git/d
            /url:/d
            /tag:/d
            /commit:/d
        }
    }' "$TEMP_MANIFEST_PATH"
}

echo "=== Build del Flatpak ==="
echo "Avvio build Flatpak..."
flatpak-builder --user --force-clean --install flatpak-build "$TEMP_MANIFEST_PATH"

# Rimuovi il manifest temporaneo e i file copiati
rm -f "$TEMP_MANIFEST_PATH"
rm -f "build-scripts/io.github.pierspad.TextMerger.desktop"
rm -f "build-scripts/io.github.pierspad.TextMerger.metainfo.xml"
rm -f "build-scripts/logo.png"

echo ""
echo "=== Build completato! ==="
echo "Per testare l'app: flatpak run io.github.pierspad.TextMerger"
echo ""
echo "Note:"
echo "- Questo build usa i sorgenti locali"
echo "- Per creare un pacchetto per Flathub, usa il script push-flathub.sh"
echo "- Prima del push, assicurati che tutti i cambiamenti siano committati e taggati"
