import os
from typing import List, Callable
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.constants import (
    DARKER_BG, SECONDARY_COLOR, TEXT_COLOR, PRIMARY_COLOR, DARK_BG,
    LIGHTER_BG, LIGHT_SECONDARY_COLOR, LIGHT_TEXT_COLOR, LIGHT_PRIMARY_COLOR, LIGHT_BG
)

class FileDropArea(QWidget):
    def __init__(self, on_files_added: Callable[[List[str]], None], placeholder: str) -> None:
        super().__init__()
        self._on_files_added = on_files_added
        self._placeholder = placeholder
        self._is_dark_mode = True
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.label = QLabel(self._placeholder, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setMinimumSize(200, 200)

    def set_theme(self, is_dark: bool) -> None:
        self._is_dark_mode = is_dark
        theme = self._get_theme_colors(is_dark)
        
        self.setStyleSheet(
        f"""
            QWidget {{
                background-color: {theme['background']};
                border: 2px dashed {theme['border_color']};
                border-radius: 10px;
                color: {theme['text_color']};
                font-size: 16px;
            }}
            QWidget:hover {{
                border-color: {theme['primary']};
                background-color: {theme['hover_bg']};
            }}
        """)
        self.label.setStyleSheet(f"color: {theme['text']};")

    @staticmethod
    def _get_theme_colors(is_dark: bool) -> dict:
        return {
            'background': DARKER_BG if is_dark else LIGHTER_BG,
            'border': SECONDARY_COLOR if is_dark else LIGHT_SECONDARY_COLOR,
            'hover_bg': DARK_BG if is_dark else LIGHT_BG,
            'text': TEXT_COLOR if is_dark else LIGHT_TEXT_COLOR,
            'primary': PRIMARY_COLOR if is_dark else LIGHT_PRIMARY_COLOR
        }

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        self.dragEnterEvent(event)

    def dropEvent(self, event) -> None:
        paths = []
        
        if event.mimeData().hasUrls():
            paths = [url.toLocalFile() for url in event.mimeData().urls()]
        elif event.mimeData().hasText():
            text = event.mimeData().text().strip()
            if os.path.exists(text):
                paths.append(text)
                
        if paths:
            self._on_files_added(paths)
        event.acceptProposedAction()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._show_file_dialog()

    def set_placeholder(self, text: str) -> None:
        self._placeholder = text
        self.label.setText(text)

    def _show_file_dialog(self) -> None:
        options = QFileDialog.Options() | QFileDialog.DontUseCustomDirectoryIcons
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select file or folders",
            os.getcwd(),
            "All files or folders (*)",
            options=options
        )
        if paths:
            self._on_files_added(paths)

