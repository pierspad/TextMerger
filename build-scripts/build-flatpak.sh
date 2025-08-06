#!/usr/bin/env bash
set -euo pipefail

# Posizionati nella root del progetto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

echo "=== Configurazione Flathub repository ==="
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

echo "=== Installazione SDK e Runtime ==="
flatpak install -y --user flathub org.kde.Sdk//5.15-24.08 org.kde.Platform//5.15-24.08
flatpak install -y --user flathub com.riverbankcomputing.PyQt.BaseApp//5.15-24.08

echo "=== Pulizia cache precedente ==="
# Rimuovi installazione precedente
flatpak uninstall --user io.github.pierspad.TextMerger -y 2>/dev/null || true

# Rimuovi directory di build
rm -rf flatpak-build
rm -rf .flatpak-builder

echo "=== Build del Flatpak ==="
# Verifica il path corretto del manifest
MANIFEST_PATH="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
if [[ ! -f "$MANIFEST_PATH" ]]; then
    echo "Errore: Manifest non trovato in $MANIFEST_PATH"
    exit 1
fi

flatpak-builder --user --force-clean --install flatpak-build "$MANIFEST_PATH"

echo "=== Build completato! ==="
echo "Per testare l'app: flatpak run io.github.pierspad.TextMerger"