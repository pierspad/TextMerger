#!/bin/bash
set -e

get_version() {
    grep -E '^pkgver=' PKGBUILD | head -1 | cut -d '=' -f2
}

echo "Building TextMerger for Arch Linux..."

if ! command -v pacman &> /dev/null; then
    echo "Warning: This script is designed for Arch Linux"
fi

VERSION=$(get_version)
if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from PKGBUILD"
    exit 1
fi
echo "Detected version: $VERSION"

echo "Installing build dependencies..."
sudo pacman -S --needed python python-build python-installer python-wheel python-setuptools

echo "Preparing source package..."
rm -rf src pkg *.pkg.tar.*
mkdir -p src

echo "Creating source tarball..."
# Crea il tarball nella directory corrente per makepkg
cd ..
tar --exclude='.git' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='src' \
    --exclude='pkg' \
    --exclude='*.egg-info' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.venv*' \
    --exclude='venv' \
    --exclude='env' \
    --exclude='*.pkg.tar.*' \
    --exclude='.idea' \
    --exclude='.flatpak-builder' \
    --exclude='flatpak-build' \
    -czf "build-scripts/TextMerger-$VERSION.tar.gz" \
    --transform="s,^,TextMerger-$VERSION/," \
    --exclude='build-scripts/src' \
    --exclude='build-scripts/pkg' \
    --exclude='build-scripts/TextMerger' \
    .

cd build-scripts

echo "Building Arch package..."
makepkg -sf

echo ""
echo "Build completed! Install with:"
echo "sudo pacman -U textmerger-$VERSION-1-any.pkg.tar.zst"
