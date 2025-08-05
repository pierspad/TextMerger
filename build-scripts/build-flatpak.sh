#!/usr/bin/env bash
set -euo pipefail

# posizionati nella root del progetto (assumendo che questo script sia in build-scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install -y --user flathub org.kde.Sdk//5.15-24.08 org.kde.Platform//5.15-24.08
flatpak install -y --user flathub com.riverbankcomputing.PyQt.BaseApp//5.15-24.08

flatpak-builder --user --force-clean --install flatpak-build packaging/io.github.pierspad.TextMerger.yml
