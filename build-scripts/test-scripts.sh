#!/usr/bin/env bash
set -euo pipefail

# Script di test per verificare le funzioni degli script Flatpak

echo "=== Test delle funzioni degli script Flatpak ==="

# Test funzione get_pkgbuild_info
source_get_pkgbuild_info() {
    local field="$1"
    grep -E "^${field}=" ./PKGBUILD | head -1 | cut -d '=' -f2 | tr -d '"'"'"
}

echo "Test lettura PKGBUILD:"
VERSION=$(source_get_pkgbuild_info "pkgver")
PKGNAME=$(source_get_pkgbuild_info "pkgname")
echo "  - Nome: $PKGNAME"
echo "  - Versione: $VERSION"

# Test esistenza file necessari
echo ""
echo "Verifica file necessari:"

FILES=(
    "./PKGBUILD"
    "../flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
    "../flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.metainfo.xml"
    "../packaging/pyproject.toml"
)

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MANCANTE)"
    fi
done

# Test Python e PyYAML
echo ""
echo "Verifica dipendenze Python:"
if command -v python3 >/dev/null 2>&1; then
    echo "  ✓ Python3 installato"
    if python3 -c "import yaml" 2>/dev/null; then
        echo "  ✓ PyYAML disponibile"
    else
        echo "  ✗ PyYAML non disponibile"
        echo "    Installa con: pip3 install PyYAML"
    fi
else
    echo "  ✗ Python3 non installato"
fi

# Test Git
echo ""
echo "Verifica Git:"
if command -v git >/dev/null 2>&1; then
    echo "  ✓ Git installato"
    if git config user.name >/dev/null 2>&1; then
        echo "  ✓ Git configurato (nome: $(git config user.name))"
    else
        echo "  ✗ Git non configurato"
    fi
else
    echo "  ✗ Git non installato"
fi

# Test Flatpak (opzionale per push-flathub.sh)
echo ""
echo "Verifica Flatpak (per build-flatpak.sh):"
if command -v flatpak >/dev/null 2>&1; then
    echo "  ✓ Flatpak installato"
    if command -v flatpak-builder >/dev/null 2>&1; then
        echo "  ✓ flatpak-builder installato"
    else
        echo "  ✗ flatpak-builder non installato"
        echo "    Installa con: sudo apt install flatpak-builder"
    fi
else
    echo "  ✗ Flatpak non installato"
fi

echo ""
echo "=== Test completato ==="
