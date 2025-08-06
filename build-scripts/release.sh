#!/usr/bin/env bash
set -euo pipefail

# Script principale per automatizzare il rilascio di TextMerger
# Uso: ./release.sh [versione]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

# Funzione per stampare l'aiuto
show_help() {
    echo "Uso: $0 [versione]"
    echo ""
    echo "Esempi:"
    echo "  $0 1.0.2          # Rilascia la versione 1.0.2"
    echo "  $0                # Usa la versione dal PKGBUILD"
    echo ""
    echo "Questo script:"
    echo "  1. Aggiorna la versione nel PKGBUILD (se specificata)"
    echo "  2. Sincronizza tutti i file con le info dal PKGBUILD"
    echo "  3. Crea il tag git"
    echo "  4. Prepara i build per AUR e Flatpak"
    echo ""
}

# Funzione per estrarre informazioni dal PKGBUILD
get_pkgbuild_info() {
    local field="$1"
    grep -E "^${field}=" build-scripts/PKGBUILD | head -1 | cut -d '=' -f2 | tr -d '"'"'"
}

# Aggiorna la versione nel PKGBUILD se specificata
update_pkgbuild_version() {
    local new_version="$1"
    sed -i "s/^pkgver=.*/pkgver=$new_version/" build-scripts/PKGBUILD
    echo "PKGBUILD aggiornato alla versione $new_version"
}

# Verifica che siamo in un repository git pulito
check_git_status() {
    if [[ -n $(git status --porcelain) ]]; then
        echo "Attenzione: Ci sono modifiche non committate."
        echo "Vuoi continuare? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Operazione annullata."
            exit 1
        fi
    fi
}

commit_and_push_flathub_repo() {
    echo "=== Commit e Push nel repo Flathub ==="
    local flathub_dir="flathub-repo"

    pushd "$flathub_dir" >/dev/null

    if [[ -n $(git status --porcelain) ]]; then
        git add .
        git commit -m "Updated Flatpak for release v$VERSION"

        current_branch=$(git symbolic-ref --short HEAD)
        # Se esiste un upstream push “normale”, altrimenti crea il tracking
        if git rev-parse --verify --quiet "@{u}" >/dev/null; then
            git push
        else
            git push -u origin "$current_branch"
        fi

        echo "✓ Modifiche nel repo Flathub pushate con successo."
    else
        echo "✓ Nessuna modifica da pushare nel repo Flathub."
    fi

    popd >/dev/null
}

# Crea tag git
create_git_tag() {
    local version="$1"
    local tag="v$version"
    
    if git tag | grep -q "^$tag$"; then
        echo "Tag $tag già esistente. Vuoi sovrascriverlo? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            git tag -d "$tag"
            git push origin ":refs/tags/$tag" 2>/dev/null || true
        else
            echo "Operazione annullata."
            exit 1
        fi
    fi

    git add -A
    git commit -m "Release v$version" || echo "Nessuna modifica da committare"
    git tag -a "$tag" -m "Release v$version"
    
    git push origin "$tag"
    git push
    
    echo "Tag $tag creato e pushato."
}


# Parsing argomenti
if [[ $# -gt 1 ]] || [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

NEW_VERSION="${1:-}"

# Se viene specificata una nuova versione, aggiorna il PKGBUILD
if [[ -n "$NEW_VERSION" ]]; then
    echo "=== Aggiornamento versione ==="
    update_pkgbuild_version "$NEW_VERSION"
fi

# Estrai informazioni dal PKGBUILD
VERSION=$(get_pkgbuild_info "pkgver")
PKGNAME=$(get_pkgbuild_info "pkgname")

if [[ -z "$VERSION" ]]; then
    echo "Errore: Non riesco a leggere la versione dal PKGBUILD"
    exit 1
fi

echo "=== Rilascio di $PKGNAME v$VERSION ==="

# Verifica stato git
check_git_status

# Sincronizza tutti i file
echo "=== Sincronizzazione file ==="

# Aggiorna pyproject.toml nella root
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" pyproject.toml
echo "✓ pyproject.toml aggiornato"

# Aggiorna packaging/pyproject.toml
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" packaging/pyproject.toml
echo "✓ packaging/pyproject.toml aggiornato"

# Aggiorna il manifest Flatpak
MANIFEST_PATH="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.yml"
sed -i "s/tag: v.*/tag: v$VERSION/" "$MANIFEST_PATH"
echo "✓ Manifest Flatpak aggiornato"

# Aggiorna metainfo XML
METAINFO_PATH="flathub-repo/io.github.pierspad.TextMerger/io.github.pierspad.TextMerger.metainfo.xml"
CURRENT_DATE=$(date '+%Y-%m-%d')
sed -i "s/<release version=\".*\"/<release version=\"$VERSION\"/" "$METAINFO_PATH"
sed -i "s/date=\".*\"/date=\"$CURRENT_DATE\"/" "$METAINFO_PATH"
echo "✓ Metainfo XML aggiornato"

# Commit e push Flathub submodule
commit_and_push_flathub_repo

# Verifica coerenza versioni
echo ""
echo "=== Verifica coerenza versioni ==="
echo "PKGBUILD: $VERSION"
echo "pyproject.toml: $(grep -E '^version\s*=' pyproject.toml | cut -d '=' -f2 | tr -d ' "'"'")"
echo "packaging/pyproject.toml: $(grep -E '^version\s*=' packaging/pyproject.toml | cut -d '=' -f2 | tr -d ' "'"'")"
echo "Flatpak manifest: $(grep -E 'tag: v' "$MANIFEST_PATH" | cut -d 'v' -f2)"
echo "Metainfo XML: $(grep -E '<release version=' "$METAINFO_PATH" | sed 's/.*version="\([^"]*\)".*/\1/')"

# Crea tag git
echo ""
echo "=== Creazione tag git ==="
create_git_tag "$VERSION"

echo ""
echo "=== Rilascio completato! ==="
echo ""
echo "Prossimi passi:"
echo "1. git push origin v$VERSION    # Pusha il tag"
echo "2. git push                     # Pusha le modifiche"
echo "3. ./build-scripts/build-aur.sh # Builda per AUR"
echo "4. ./build-scripts/build-flatpak.sh # Builda per Flatpak"
echo ""
echo "Oppure usa gli script automatici:"
echo "  ./build-scripts/push-aur.sh"
echo "  ./build-scripts/build-flatpak.sh"
