#!/usr/bin/env bash
set -euo pipefail

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

echo "=== Aggiornamento file Flatpak ==="
# Aggiorna automaticamente il manifest YAML con le info dal PKGBUILD
update_flatpak_manifest() {
    local manifest_path="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
    
    # Crea una versione temporanea del manifest
    cp "$manifest_path" "${manifest_path}.bak"
    
    # Aggiorna il tag della versione (assumendo che il tag sia v$VERSION)
    sed -i "s/tag: v.*/tag: v$VERSION/" "$manifest_path"
    
    # Prova a ottenere l'hash del commit per il tag (se disponibile)
    if git tag | grep -q "v$VERSION"; then
        local commit_hash=$(git rev-list -n 1 "v$VERSION")
        sed -i "s/commit: .*/commit: $commit_hash/" "$manifest_path"
        echo "Manifest aggiornato con versione v$VERSION e commit $commit_hash"
    else
        # Se il tag non esiste, usa l'HEAD corrente
        local commit_hash=$(git rev-parse HEAD)
        sed -i "s/commit: .*/commit: $commit_hash/" "$manifest_path"
        echo "Manifest aggiornato con versione v$VERSION e commit corrente $commit_hash"
        echo "NOTA: Il commit potrebbe cambiare se fai altri commit prima del push"
    fi
}

# Aggiorna pyproject.toml nella root
echo "Sincronizzazione versione in pyproject.toml..."
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" pyproject.toml

# Aggiorna il manifest Flatpak
update_flatpak_manifest

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
        echo "Metainfo aggiornato con versione $VERSION e data $current_date"
    else
        echo "Nessuna sezione release trovata nel metainfo"
    fi
}

update_metainfo

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