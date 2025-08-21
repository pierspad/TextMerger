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
        print(f"PyInstaller mode - Base path: {base_path}")
        print(f"PyInstaller mode - Assets folder: {assets_folder}")
    else:
        # Running in development
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_folder = os.path.join(base_path, 'assets')
        print(f"Dev mode - Base path: {base_path}")
        print(f"Dev mode - Assets folder: {assets_folder}")
    
    asset_path = os.path.join(assets_folder, relative_path)
    print(f"Final asset path: {asset_path}")
    print(f"Asset exists: {os.path.exists(asset_path)}")
    
    # Debug: List directory contents if asset not found
    if not os.path.exists(asset_path):
        print(f"Asset not found: {asset_path}")
        if os.path.exists(assets_folder):
            print(f"Contents of {assets_folder}:")
            try:
                for item in os.listdir(assets_folder):
                    print(f"  - {item}")
            except Exception as e:
                print(f"  Error listing directory: {e}")
        else:
            print(f"Assets folder does not exist: {assets_folder}")
    
    return asset_path

def get_translations_path():
    """Get path to translations directory, working for both dev and PyInstaller environments"""
    
    # Check if running in PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
        translations_folder = os.path.join(base_path, 'textmerger', 'translations')
    else:
        # Running in development
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        translations_folder = os.path.join(base_path, 'translations')
    
    return translations_folder

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

