import os
from typing import List
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt, QTimer

class DroppableTextEdit(QTextEdit):
    def __init__(self, main_window, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._main_window = main_window
        self.setAcceptDrops(True)
        # Timer per ritardare l'aggiornamento del placeholder durante il ridimensionamento
        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_finished)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Avvia/riavvia il timer quando la finestra viene ridimensionata
        self._resize_timer.stop()
        self._resize_timer.start(100)  # Attendi 100ms prima di aggiornare

    def _on_resize_finished(self):
        # Aggiorna il placeholder solo quando il ridimensionamento è finito
        if hasattr(self._main_window, 'update_supported_formats_placeholder'):
            self._main_window.update_supported_formats_placeholder()

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
