#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 TextMerger Release Creator${NC}"
echo "=================================="

if [[ ! -f "$SCRIPT_DIR/PKGBUILD" ]]; then
    echo -e "${RED}❌ Errore: PKGBUILD non trovato in $SCRIPT_DIR${NC}"
    exit 1
fi


echo -e "${YELLOW}📋 Estrazione versione dal PKGBUILD...${NC}"
PKGVER=$(grep "^pkgver=" "$SCRIPT_DIR/PKGBUILD" | cut -d'=' -f2)
PKGREL=$(grep "^pkgrel=" "$SCRIPT_DIR/PKGBUILD" | cut -d'=' -f2)

if [[ -z "$PKGVER" ]]; then
    echo -e "${RED}❌ Errore: Impossibile estrarre pkgver dal PKGBUILD${NC}"
    exit 1
fi

VERSION="v$PKGVER"
echo -e "${GREEN}✅ Versione trovata: $VERSION${NC}"

RELEASE_NOTES_FILE="$PROJECT_ROOT/docs/release-notes.md"
if [[ ! -f "$RELEASE_NOTES_FILE" ]]; then
    echo -e "${RED}❌ Errore: $RELEASE_NOTES_FILE non trovato${NC}"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ Errore: GitHub CLI (gh) non è installato${NC}"
    echo "Installa con: sudo pacman -S github-cli"
    exit 1
fi

echo -e "${YELLOW}🔐 Verifica autenticazione GitHub...${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Non sei autenticato con GitHub CLI${NC}"
    echo "Esegui: gh auth login"
    exit 1
fi

echo -e "${YELLOW}🏷️  Verifica esistenza tag...${NC}"
if git tag -l | grep -q "^$VERSION$"; then
    echo -e "${RED}❌ Il tag $VERSION esiste già${NC}"
    read -p "Vuoi eliminare il tag esistente e continuare? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🗑️  Eliminazione tag locale e remoto...${NC}"
        git tag -d "$VERSION" || true
        git push origin --delete "$VERSION" || true
    else
        echo -e "${YELLOW}⏹️  Operazione annullata${NC}"
        exit 0
    fi
fi

echo -e "${YELLOW}🌿 Verifica stato repository...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${RED}❌ Non sei sul branch main (attuale: $CURRENT_BRANCH)${NC}"
    exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Ci sono modifiche non committate${NC}"
    git status --short
    exit 1
fi

echo -e "${YELLOW}⬇️  Pull delle ultime modifiche...${NC}"
git pull origin main

echo -e "${YELLOW}🏷️  Creazione tag $VERSION...${NC}"
git tag -a "$VERSION" -m "Release $VERSION"

echo -e "${YELLOW}⬆️  Push del tag...${NC}"
git push origin "$VERSION"

echo -e "${YELLOW}🎉 Creazione release GitHub...${NC}"
gh release create "$VERSION" \
    --target main \
    --title "TextMerger $VERSION" \
    --notes-file "$RELEASE_NOTES_FILE" \
    --generate-notes

echo -e "${GREEN}✅ Release $VERSION creato con successo!${NC}"
echo -e "${BLUE}🔗 Visualizza il release: https://github.com/pierspad/TextMerger/releases/tag/$VERSION${NC}"

read -p "Vuoi aprire il release nel browser? (Y/n): " -n 1 -r
echo
REPLY=${REPLY:-Y}
if [[ $REPLY =~ ^[Yy]$ ]]; then
    gh release view "$VERSION" --web
fi