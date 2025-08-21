from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor

class DroppableTreeWidget(QTreeWidget):
    def __init__(self, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)
        self._drop_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        self._drop_pos = event.pos()
        self.viewport().update()

    def dragLeaveEvent(self, event):
        super().dragLeaveEvent(event)
        self._drop_pos = None
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._drop_pos is not None:
            painter = QPainter(self.viewport())
            pen = QPen(QColor("red"), 2, Qt.SolidLine)
            painter.setPen(pen)
            y = self._drop_pos.y()
            painter.drawLine(0, y, self.viewport().width(), y)
            painter.end()

    def dropEvent(self, event):
        if not event.source():
            paths = []
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    local_file = url.toLocalFile()
                    if local_file:
                        paths.append(local_file)
            if paths:
                self.main_window.add_files(paths)
                event.acceptProposedAction()
                return
        super().dropEvent(event)
        self._drop_pos = None
        self.viewport().update()
        self.fix_hierarchy()
        self.main_window.on_tree_item_moved()

    def fix_hierarchy(self):
        items_to_reparent = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            self._check_item_hierarchy(item, None, items_to_reparent)
        for item, parent in items_to_reparent:
            if parent is not None:
                parent.removeChild(item)
                self.addTopLevelItem(item)

    def _check_item_hierarchy(self, item, parent, items_to_reparent):
        data = item.data(0, Qt.UserRole)
        if parent is not None:
            parent_data = parent.data(0, Qt.UserRole)
            if parent_data and parent_data.get('type') == 'file' and data and data.get('type') == 'file':
                items_to_reparent.append((item, parent))
        for i in range(item.childCount()):
            child = item.child(i)
            self._check_item_hierarchy(child, item, items_to_reparent)
