import os
from typing import List
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class DroppableTextEdit(QTextEdit):
    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        self.dragEnterEvent(event)

    def dropEvent(self, event) -> None:
        paths = self._extract_paths(event.mimeData())
        event.acceptProposedAction()
        if paths:
            self._main_window.add_files(paths)

    @staticmethod
    def _extract_paths(mime_data) -> List[str]:
        paths = []
        if mime_data.hasUrls():
            paths.extend(url.toLocalFile() for url in mime_data.urls() if url.toLocalFile())
        elif mime_data.hasText():
            text = mime_data.text().strip()
            if text.lower().startswith("file:"):
                text = text[5:].lstrip("/")
            if os.path.exists(text):
                paths.append(text)
        return paths
