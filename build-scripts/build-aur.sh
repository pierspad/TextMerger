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

echo "Synchronising version in packaging/pyproject.toml..."
sed -i "s/^version\s*=.*/version = \"$VERSION\"/" ../packaging/pyproject.toml

echo "Installing build dependencies..."
sudo pacman -S --needed python python-build python-installer python-wheel python-setuptools

echo "Preparing source package..."
rm -rf src pkg
mkdir -p src

echo "Creating clean source copy..."
rsync -av \
    --exclude='.git/' \
    --exclude='dist/' \
    --exclude='build/' \
    --exclude='src/' \
    --exclude='pkg/' \
    --exclude='*.egg-info/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.venv*/' \
    --exclude='venv/' \
    --exclude='env/' \
    --exclude='*.pkg.tar.*' \
    --exclude='.idea/' \
    ../ src/TextMerger-"$VERSION"/

cp ../packaging/*       src/TextMerger-"$VERSION"/
cp ../docs/LICENSE      src/TextMerger-"$VERSION"/

echo "Building Arch package..."
makepkg -sf

echo ""
echo "Build completed! Install with:"
echo "sudo pacman -U textmerger-$VERSION-1-any.pkg.tar.zst"
