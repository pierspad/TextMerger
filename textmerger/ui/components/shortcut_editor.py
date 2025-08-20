from PyQt5.QtWidgets import QLineEdit, QTableWidgetItem, QTableWidget, QMessageBox, QApplication, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from utils.settings import DEFAULT_SHORTCUTS
import json
import os

class ShortcutEditor(QLineEdit):
    shortcutChanged = pyqtSignal()

    def __init__(self, text, parent=None, main_window=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.original_text = text
        self.key_sequence = []
        self.setReadOnly(True)
        self.setPlaceholderText("Press keys combination...")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.main_window = main_window
        self.settings = main_window.settings if main_window else None
        self.row = -1
        self.column = -1
        
        if self.settings:
            self.current_shortcuts = self.settings.get_shortcuts()
            if not self.current_shortcuts:
                self.current_shortcuts = DEFAULT_SHORTCUTS.copy()
                self.settings.set_shortcuts(self.current_shortcuts)
        else:
            self.current_shortcuts = DEFAULT_SHORTCUTS.copy()

        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #1e90ff;
                border-radius: 0px;
                padding: 8px;
                margin: 0px;
                background-color: #2c2c2c;
                color: white;
                font-weight: bold;
            }
            QLineEdit:focus {
                border-color: #bb86fc;
                background-color: #1f1f1f;
            }
        """)
        self.setText("")

    def save_shortcuts(self, new_shortcut):
        try:
            self.settings.set_shortcuts(new_shortcut)
            print(f"Shortcuts saved successfully: {new_shortcut}")
        except Exception as e:
            print(f"Error saving shortcuts: {e}")

    def is_shortcut_duplicate(self, new_shortcut):
        for key, value in self.current_shortcuts.items():
            if value == new_shortcut and key != self.get_current_action_key():
                print(f"Duplicate shortcut found: {value} for action {key}")
                return True
        return False

    def get_current_action_key(self):
        if hasattr(self, 'row') and isinstance(self.parent(), QTableWidget):
            action_item = self.parent().item(self.row, 0)
            if action_item:
                action_text = action_item.text()
                for key, value in self.current_shortcuts.items():
                    if value == self.original_text:
                        return key
        return None

    def focusOutEvent(self, event):
        new_shortcut = self.text().strip()
        print(f"Attempting to save new shortcut: {new_shortcut}")

        if not new_shortcut:
            print("Empty shortcut, restoring original")
            self.setText(self.original_text)
        else:
            if self.is_shortcut_duplicate(new_shortcut):
                print("Duplicate shortcut detected")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("This shortcut is already in use!")
                msg.setWindowTitle("Warning")
                msg.exec_()
                self.setText(self.original_text)
            else:
                action_key = self.get_current_action_key()
                if action_key:
                    print(f"Saving new shortcut for action {action_key}: {new_shortcut}")
                    self.current_shortcuts[action_key] = new_shortcut
                    self.save_shortcuts(self.current_shortcuts) # quando viene eseguita questa istruzione crasha il programma
                    self.setText(new_shortcut)
                else:
                    print("Could not determine action key, shortcut not saved")
                    self.setText(self.original_text)

        parent = self.parent()
        if isinstance(parent, QTableWidget):
            if hasattr(self, 'row') and hasattr(self, 'column'):
                if 0 <= self.row < parent.rowCount() and 0 <= self.column < parent.columnCount():
                    try:
                        new_item = QTableWidgetItem(self.text())
                        new_item.setTextAlignment(Qt.AlignCenter)
                        parent.setItem(self.row, self.column, new_item)
                    except Exception as e:
                        print(f"Error updating table cell: {e}")

        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setText(self.original_text)
            self.clearFocus()
            return
            
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.clearFocus()
            return

        if event.key() in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta):
            return

        modifiers = event.modifiers()
        key = event.key()

        sequence = []

        if modifiers & Qt.ControlModifier:
            sequence.append("Ctrl")
        if modifiers & Qt.AltModifier:
            sequence.append("Alt")
        if modifiers & Qt.ShiftModifier:
            sequence.append("Shift")
        if modifiers & Qt.MetaModifier:
            sequence.append("Meta")

        key_text = QKeySequence(key).toString()
        if key_text:
            sequence.append(key_text)

        if sequence:
            self.setText("+".join(sequence))
        
        event.accept()
        self.shortcutChanged.emit()
        self.close()

    def keyReleaseEvent(self, event):
        event.accept()

    @staticmethod
    def reset_to_defaults():
        try:
            main_window = next(w for w in QApplication.topLevelWidgets() if isinstance(w, QMainWindow))
            main_window.settings.set_shortcuts(DEFAULT_SHORTCUTS.copy())
            return True
        except Exception as e:
            print(f"Error resetting shortcuts: {e}")
            return False
