from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self)
        self.movie = QMovie("spinner.gif")
        self.movie.setScaledSize(QSize(64, 64))
        self.label.setMovie(self.movie)
        layout.addWidget(self.label)
        self.hide()

    def show_overlay(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.movie.start()
        self.raise_()
        self.show()

    def hide_overlay(self):
        self.movie.stop()
        self.hide()
