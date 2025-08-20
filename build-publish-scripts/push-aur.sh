#!/usr/bin/env bash

set -euo pipefail

AUR_REPO_DIR="${AUR_REPO_DIR:-../aur-repo}"
PROJECT_NAME="${PROJECT_NAME:-$(grep -Po '^pkgname=\K.*' PKGBUILD)}"
ICON_DIR="${ICON_DIR:-${PROJECT_NAME}/assets/logo}"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Aggiornamento repository AUR per ${PROJECT_NAME}${NC}"

# git clone ssh://aur@aur.archlinux.org/${PROJECT_NAME}.git "$AUR_REPO_DIR"

# 1 - cleanup
rm -rf pkg/ src/ ./*.pkg.*

# 2 - Verifica e aggiorna checksum SHA256
echo -e "${YELLOW}🔍 Verifica del checksum SHA256...${NC}"

PKGVER=$(grep -Po '^pkgver=\K.*' PKGBUILD)
if [[ -z "$PKGVER" ]]; then
    echo -e "${RED}❌ Errore: Impossibile estrarre pkgver dal PKGBUILD${NC}"
    exit 1
fi

TARBALL_URL="https://github.com/pierspad/TextMerger/archive/v${PKGVER}.tar.gz"
TEMP_DIR=$(mktemp -d)
TARBALL_FILE="$TEMP_DIR/${PROJECT_NAME}-${PKGVER}.tar.gz"

echo -e "${YELLOW}⬇️  Scaricamento tarball da GitHub...${NC}"
if ! wget -q -O "$TARBALL_FILE" "$TARBALL_URL"; then
    echo -e "${RED}❌ Errore nel download del tarball da $TARBALL_URL${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

CORRECT_SHA256=$(sha256sum "$TARBALL_FILE" | cut -d' ' -f1)
CURRENT_SHA256=$(grep -Po "^sha256sums=\\('\K[^']*" PKGBUILD)

echo -e "${BLUE}📋 Checksum corrente: $CURRENT_SHA256${NC}"
echo -e "${BLUE}📋 Checksum corretto:  $CORRECT_SHA256${NC}"

if [[ "$CURRENT_SHA256" != "$CORRECT_SHA256" ]]; then
    echo -e "${YELLOW}🔧 Aggiornamento checksum SHA256...${NC}"
    sed -i "s/^sha256sums=.*$/sha256sums=('$CORRECT_SHA256')/" PKGBUILD
    echo -e "${GREEN}✅ Checksum aggiornato${NC}"
else
    echo -e "${GREEN}✅ Checksum già corretto${NC}"
fi

# Pulizia file temporanei
rm -rf "$TEMP_DIR"

# 3 - Genera .SRCINFO aggiornato
echo -e "${YELLOW}📄 Generazione .SRCINFO...${NC}"
makepkg --printsrcinfo > .SRCINFO

# 3 - Genera .SRCINFO aggiornato
echo -e "${YELLOW}📄 Generazione .SRCINFO...${NC}"
makepkg --printsrcinfo > .SRCINFO

# 4 - copia nel repo AUR
echo -e "${YELLOW}📁 Copia file nel repository AUR...${NC}"
cp PKGBUILD .SRCINFO "$AUR_REPO_DIR/"
for f in "$PROJECT_NAME".{install,desktop}; do
  [[ -f $f ]] && cp "$f" "$AUR_REPO_DIR/"
done
[[ -d $ICON_DIR ]] && cp "$ICON_DIR"/*.png "$AUR_REPO_DIR/" || true

# 5 - commit / push
echo -e "${YELLOW}🚀 Commit e push su AUR...${NC}"
cd "$AUR_REPO_DIR"
git add -A

# Verifica se ci sono modifiche da committare
if git diff --staged --quiet; then
    echo -e "${GREEN}✅ Nessuna modifica da committare${NC}"
else
    git commit -m "update $(date --iso-8601=seconds)"
    git push
    echo -e "${GREEN}✅ Push completato su AUR${NC}"
fi
