import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer

def get_asset_path(relative_path):
    """Get path to asset, working for both dev and PyInstaller environments"""
    
    # Check if running in PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
        assets_folder = os.path.join(base_path, 'textmerger', 'assets')
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
        assets_folder = os.path.join(base_path, '..', 'assets')
    
    asset_path = os.path.join(assets_folder, relative_path)
    
    # Debug output (rimuoveremo dopo il test)
    if not os.path.exists(asset_path):
        print(f"Asset not found: {asset_path}")
        print(f"Base path: {base_path}")
        print(f"Assets folder: {assets_folder}")
        if getattr(sys, 'frozen', False):
            print("Running in PyInstaller bundle")
            print(f"_MEIPASS: {sys._MEIPASS}")
        else:
            print("Running in development mode")
    
    return asset_path

def get_colored_icon(icon_name: str, color_hex: str = "#FFFFFF", size=24) -> QIcon:
    icon_path = get_asset_path(os.path.join('icons', icon_name))
    if not os.path.exists(icon_path):
        icon_path = get_asset_path(os.path.join('icons', 'missing_icon.svg'))
    if 'languages' in icon_name:
        return QIcon(icon_path)
    svg_renderer = QSvgRenderer(icon_path)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    svg_renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color_hex))
    painter.end()
    return QIcon(pixmap)

