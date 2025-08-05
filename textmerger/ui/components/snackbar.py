from PyQt5.QtCore import QTimer, QPropertyAnimation, QRect, Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

class SnackBar(QFrame):
    def __init__(self, parent=None):
        super(SnackBar, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel("")
        self.layout.addWidget(self.label)
        self.hide()
        self.click_to_close = True
        self.dark_mode = True

    def apply_theme(self, dark_mode):
        self.dark_mode = dark_mode
        if dark_mode:
            bg_color = "#333333"
            text_color = "#FFFFFF"
        else:
            bg_color = "#F0F0F0"
            text_color = "#000000"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 4px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def showMessage(self, message, duration=1000):
        self.label.setText(message)
        parent_rect = self.parent().rect()
        self_size = self.sizeHint()
        x = (parent_rect.width() - self_size.width()) // 2
        start_y = parent_rect.height() + self_size.height()
        end_y = parent_rect.height() - self_size.height() - 20

        self.move(x, start_y)
        self.show()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(x, start_y, self_size.width(), self_size.height()))
        self.anim.setEndValue(QRect(x, end_y, self_size.width(), self_size.height()))
        self.anim.start()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hideWithAnimation)
        self.timer.start(duration)

    def hideWithAnimation(self):
        if self.isVisible():
            current_geometry = self.geometry()
            end_y = self.parent().rect().height() + self.height()

            self.anim = QPropertyAnimation(self, b"geometry")
            self.anim.setDuration(300)
            self.anim.setStartValue(current_geometry)
            self.anim.setEndValue(QRect(
                current_geometry.x(),
                end_y,
                current_geometry.width(),
                current_geometry.height()
            ))
            self.anim.finished.connect(self.hide)
            self.anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.isVisible():
            self.timer.stop()
            self.hideWithAnimation()
