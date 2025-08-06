#!/usr/bin/env bash

set -euo pipefail

AUR_REPO_DIR="${AUR_REPO_DIR:-../aur-repo}"
PROJECT_NAME="${PROJECT_NAME:-$(grep -Po '^pkgname=\K.*' PKGBUILD)}"
ICON_DIR="${ICON_DIR:-${PROJECT_NAME}/assets/logo}"


# git clone ssh://aur@aur.archlinux.org/${PROJECT_NAME}.git "$AUR_REPO_DIR"


# 1 - cleanup
rm -rf pkg/ src/ ./*.pkg.*

# 2 - .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# 3 - copia nel repo AUR
cp PKGBUILD .SRCINFO "$AUR_REPO_DIR/"
for f in "$PROJECT_NAME".{install,desktop}; do
  [[ -f $f ]] && cp "$f" "$AUR_REPO_DIR/"
done
[[ -d $ICON_DIR ]] && cp "$ICON_DIR"/*.png "$AUR_REPO_DIR/" || true

# 4 - commit / push
cd "$AUR_REPO_DIR"
git add -A
git commit -m "update $(date --iso-8601=seconds)"
git push
