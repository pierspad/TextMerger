#!/bin/bash
set -e

get_version() {
    grep -E '^pkgver=' PKGBUILD | head -1 | cut -d '=' -f2
}

get_release() {
    grep -E '^pkgrel=' PKGBUILD | head -1 | cut -d '=' -f2
}

echo "Building TextMerger for Arch Linux..."

if ! command -v pacman &> /dev/null; then
    echo "Warning: This script is designed for Arch Linux"
fi

VERSION=$(get_version)
RELEASE=$(get_release)
if [ -z "$VERSION" ]; then
    echo "Error: Could not extract version from PKGBUILD"
    exit 1
fi
if [ -z "$RELEASE" ]; then
    echo "Error: Could not extract release from PKGBUILD"
    exit 1
fi
echo "Detected version: $VERSION-$RELEASE"

echo "Installing build dependencies..."
sudo pacman -S --needed python python-build python-installer python-wheel python-setuptools

echo "Cleaning old build files..."
cd ..

rm -rf build/ dist/ *.egg-info/ **/__pycache__/ **/*.pyc
echo "Cleaned old build files"

echo "Preparing source package..."
cd build-publish-scripts
rm -rf src pkg *.pkg.tar.*
mkdir -p src

echo "Creating source tarball..."

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
    -czf "build-publish-scripts/textmerger-$VERSION.tar.gz" \
    --transform="s,^,TextMerger-$VERSION/," \
    --exclude='build-publish-scripts/src' \
    --exclude='build-publish-scripts/pkg' \
    --exclude='build-publish-scripts/textmerger' \
    .

cd build-publish-scripts
updpkgsums

echo "Building Arch package..."
makepkg -sf

echo ""
echo "Build completed! Install with:"
echo "sudo pacman -U textmerger-$VERSION-$RELEASE-any.pkg.tar.zst"
