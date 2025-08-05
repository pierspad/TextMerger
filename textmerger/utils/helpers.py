import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer

def get_asset_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    assets_folder = os.path.join(base_path, '..', 'assets')
    return os.path.join(assets_folder, relative_path)

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

