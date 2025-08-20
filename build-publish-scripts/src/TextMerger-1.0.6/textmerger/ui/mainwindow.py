import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                             QFileDialog, QDesktopWidget, QApplication, QTreeWidgetItem,
                             QFrame, QStackedWidget, QSpacerItem, QSizePolicy, QTreeWidget, QSplitter, QHeaderView,
                             QShortcut, QMenu, QAction, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit)
from PyQt5.QtCore import Qt, QCoreApplication, QEvent
from PyQt5.QtGui import QIcon, QFont, QKeySequence
from ui.components.snackbar import SnackBar
from ui.components.droppable_text_edit import DroppableTextEdit
from ui.components.loading_overlay import LoadingOverlay
from ui.components.droppable_tree_widget import DroppableTreeWidget
from ui.components.shortcut_editor import ShortcutEditor
from utils.constants import (DARKER_BG, TEXT_COLOR, BORDER_COLOR, DARK_BG, PRIMARY_COLOR,
                             SECONDARY_COLOR, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, WINDOW_WIDTH_PERCENTAGE,
                             WINDOW_HEIGHT_PERCENTAGE, LIGHT_BG, LIGHTER_BG, LIGHT_TEXT_COLOR, LIGHT_BORDER_COLOR,
                             LIGHT_PRIMARY_COLOR, LIGHT_SECONDARY_COLOR)
from utils.helpers import get_asset_path, get_colored_icon
from core.file_manager import load_files
from utils.localization import Localization
from utils.settings import Settings

DASH_LINE = "-------------------"

EXTENSION_COLOR_MAP = {
    '.py': "#FFA500",
    '.cpp': "#00BFFF",
    '.c': "#00BFFF",
    '.cu': "#00BFFF",
    '.ipynb': "#ADFF2F",
    '.txt': "#FFFFFF",
}
DEFAULT_COLOR = "#CCCCCC"



class MainWindow(QMainWindow):
    SIDE_PANEL_MIN_WIDTH = 260
    BOTTOM_BAR_HEIGHT = 60

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.localization = Localization(self.settings)
        self.is_dark_mode = self.settings.get_theme() == 'dark'
        self.save_shortcut = None
        self.save_button = None
        self.language_button = None
        self.update_button = None
        self.char_count_label = None
        self.remove_all_button = None
        self.language_menu = None
        self.side_panel = None
        self.settings_button = None
        self.settings_page = None
        self.file_tree = None
        self.file_list_label = None
        self.files_page = None
        self.sidebar = None
        self.drag_open_button = None
        self.side_stacked = None
        self.side_panel_layout = None
        self.theme_button = None
        self.splitter = None
        self.text_edit = None
        self.merged_text_label = None
        self.copy_button = None
        self.snackbar = None
        self.remove_shortcut = None
        self.remove_all_shortcut = None
        self.open_shortcut = None
        self.exit_button = None
        self.current_side_page = None
        self.update_shortcut = None
        self.exit_shortcut = None
        self.copy_shortcut = None
        self.files_button = None
        self.remove_button = None
        self.lang_shortcut = None
        self.current_language = 'en'
        self.dark_mode = self.settings.get_theme() == 'dark'
        self.loading_overlay = LoadingOverlay(self)
        self.files_dict = {}
        self.offset_map = {}
        self.dir_files_map = {}
        self.is_sidebar_expanded = False
        self.shortcuts_page = None
        self.right_stacked = None
        self.text_page = None
        self.action_icons = {
            'open_action': 'open.svg',
            'save_action': 'save.svg',
            'exit_action': 'exit.svg',
            'remove_file_action': 'trash.svg',
            'remove_all_files_action': 'trash_all.svg',
            'copy_text_action': 'copy.svg',
            'refresh_action': 'update.svg'
        }
        self.init_ui()
        self.apply_theme()
        self.apply_translations()
        self.setAcceptDrops(True)
        self.localization.shortcuts_changed.connect(self.on_shortcuts_changed)

    def icon_color(self):
        return "#000000" if not self.dark_mode else "#FFFFFF"

    def update_theme_button(self):
        if self.dark_mode:
            icon = get_colored_icon("sun.svg", "#FFFFFF", size=18)
            text = self.localization.tr("light_mode")
        else:
            icon = get_colored_icon("moon.svg", "#FFFFFF", size=18)
            text = self.localization.tr("dark_mode")
        self.theme_button.setText(text)
        self.theme_button.setIcon(icon)

    def init_ui(self):
        logo_path = get_asset_path(os.path.join('logo', 'logo.png'))
        icon = QIcon(logo_path)
        self.setWindowIcon(icon)
        QApplication.setWindowIcon(icon)
        self.setWindowTitle(self.localization.tr("app_title"))
        screen = QDesktopWidget().screenGeometry()
        width = max(MIN_WINDOW_WIDTH, int(screen.width() * WINDOW_WIDTH_PERCENTAGE))
        height = max(MIN_WINDOW_HEIGHT, int(screen.height() * WINDOW_HEIGHT_PERCENTAGE))
        self.resize(width, height)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(50)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 10, 0, 10)
        sidebar_layout.setSpacing(10)
        self.files_button = QPushButton()
        self.files_button.setCheckable(True)
        self.files_button.setChecked(True)
        self.files_button.setProperty("active", True)
        self.files_button.clicked.connect(self.on_files_button_clicked)
        sidebar_layout.addWidget(self.files_button, alignment=Qt.AlignTop)
        self.settings_button = QPushButton()
        self.settings_button.setCheckable(True)
        self.settings_button.setChecked(False)
        self.settings_button.setProperty("active", False)
        self.settings_button.clicked.connect(self.on_settings_button_clicked)
        sidebar_layout.addWidget(self.settings_button, alignment=Qt.AlignTop)
        sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(self.sidebar)
        self.side_panel = QFrame()
        self.side_panel_layout = QVBoxLayout(self.side_panel)
        self.side_panel_layout.setContentsMargins(0, 0, 0, 0)
        self.side_panel_layout.setSpacing(0)
        self.side_stacked = QStackedWidget()
        self.side_panel_layout.addWidget(self.side_stacked)
        self.files_page = QWidget()
        files_page_layout = QVBoxLayout(self.files_page)
        files_page_layout.setContentsMargins(5, 20, 5, 5)
        files_page_layout.setSpacing(5)
        self.drag_open_button = QPushButton()
        self.drag_open_button.setObjectName("open_button")
        self.drag_open_button.setFont(QFont('Segoe UI', 9))
        self.drag_open_button.clicked.connect(self.open_files)
        self.drag_open_button.setIcon(get_colored_icon("open.svg", "#FFFFFF", size=18))
        files_page_layout.addWidget(self.drag_open_button)
        self.file_list_label = QLabel()
        self.file_list_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        files_page_layout.addWidget(self.file_list_label)
        self.file_tree = DroppableTreeWidget(self)
        self.file_tree.setHeaderHidden(False)
        self.file_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.file_tree.setTextElideMode(Qt.ElideNone)
        self.file_tree.setColumnCount(1)
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        files_page_layout.addWidget(self.file_tree, stretch=1)
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton()
        self.remove_button.setObjectName("remove_button")
        self.remove_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.remove_button.clicked.connect(self.remove_selected_file)
        self.remove_button.setIcon(get_colored_icon("trash.svg", "#FFFFFF", size=18))
        button_layout.addWidget(self.remove_button)
        self.remove_all_button = QPushButton()
        self.remove_all_button.setObjectName("remove_all_button")
        self.remove_all_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.remove_all_button.clicked.connect(self.remove_all_files)
        self.remove_all_button.setIcon(get_colored_icon("trash_all.svg", "#FFFFFF", size=18))
        button_layout.addWidget(self.remove_all_button)
        files_page_layout.addLayout(button_layout)
        self.files_page.setLayout(files_page_layout)
        self.side_stacked.addWidget(self.files_page)
        self.settings_page = QWidget()
        settings_page_layout = QVBoxLayout(self.settings_page)
        settings_page_layout.setContentsMargins(10, 20, 10, 10)
        settings_page_layout.setSpacing(10)
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("theme_button")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setStyleSheet("text-align: left; padding-left: 8px;")
        settings_page_layout.addWidget(self.theme_button)
        self.language_button = QPushButton()
        self.language_button.setObjectName("language_button")
        self.language_menu = QMenu(self.language_button)
        self.language_menu.setObjectName("language_menu")
        self.language_button.setMenu(self.language_menu)
        self.language_button.setIcon(get_colored_icon("language.svg", "#FFFFFF", size=18))
        settings_page_layout.addWidget(self.language_button)
        self.update_language_menu()
        settings_page_layout.addWidget(self.language_button)
        self.shortcuts_button = QPushButton()
        self.shortcuts_button.setObjectName("shortcuts_button")
        self.shortcuts_button.setText(self.localization.tr("edit_shortcuts"))
        self.shortcuts_button.clicked.connect(self.open_shortcuts_dialog)
        self.shortcuts_button.setIcon(get_colored_icon("shortcuts.svg", "#FFFFFF", size=18))
        self.shortcuts_button.setStyleSheet("text-align: left; padding-left: 8px;")
        settings_page_layout.addWidget(self.shortcuts_button)
        settings_page_layout.addStretch()
        self.settings_page.setLayout(settings_page_layout)
        self.side_stacked.addWidget(self.settings_page)
        main_layout.addWidget(self.side_panel)
        splitter = QSplitter(Qt.Horizontal)
        self.splitter = splitter
        splitter.setHandleWidth(5)
        splitter.addWidget(self.side_panel)
        self.right_stacked = QStackedWidget()
        self.text_page = QWidget()
        right_layout = QVBoxLayout(self.text_page)
        right_layout.setContentsMargins(5, 20, 5, 5)
        right_layout.setSpacing(5)
        self.merged_text_label = QLabel()
        self.merged_text_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        right_layout.addWidget(self.merged_text_label)
        self.text_edit = DroppableTextEdit(self)
        self.text_edit.setFont(QFont('Consolas', 11))
        self.update_supported_formats_placeholder()
        right_layout.addWidget(self.text_edit, stretch=1)
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(self.BOTTOM_BAR_HEIGHT)
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        bottom_layout.setSpacing(8)
        self.copy_button = QPushButton()
        self.copy_button.setObjectName("copy_button")
        self.copy_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.copy_button.clicked.connect(self.copy_text)
        bottom_layout.addWidget(self.copy_button)
        self.update_button = QPushButton()
        self.update_button.setObjectName("update_button")
        self.update_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.update_button.clicked.connect(self.update_files)
        bottom_layout.addWidget(self.update_button)
        self.char_count_label = QLabel()
        self.char_count_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        bottom_layout.addWidget(self.char_count_label)
        bottom_layout.addStretch()
        self.save_button = QPushButton()
        self.save_button.setObjectName("save_button")
        self.save_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.save_button.clicked.connect(self.save_file)
        bottom_layout.addWidget(self.save_button)
        self.exit_button = QPushButton()
        self.exit_button.setObjectName("exit_button")
        self.exit_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        self.exit_button.clicked.connect(self.exit_button_clicked)
        bottom_layout.addWidget(self.exit_button)
        right_layout.addWidget(bottom_frame)
        self.shortcuts_page = QWidget()
        shortcuts_layout = QVBoxLayout(self.shortcuts_page)
        shortcuts_layout.setContentsMargins(20, 20, 20, 20)
        self.shortcuts_table = QTableWidget()
        self.shortcuts_table.setColumnCount(2)
        self.shortcuts_table.setShowGrid(True)
        self.shortcuts_table.horizontalHeader().setStretchLastSection(True)
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.shortcuts_table.verticalHeader().setVisible(False)
        self.shortcuts_table.setSelectionMode(QTableWidget.NoSelection)
        self.shortcuts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.shortcuts_table.setAlternatingRowColors(True)
        table_container = QWidget()
        table_layout = QHBoxLayout(table_container)
        table_layout.addStretch()
        table_layout.addWidget(self.shortcuts_table)
        table_layout.addStretch()
        shortcuts_layout.addWidget(table_container)
        self.reset_shortcuts_button = QPushButton(self.localization.tr("reset_shortcuts"))
        self.reset_shortcuts_button.setObjectName("reset_shortcuts_button")
        self.reset_shortcuts_button.clicked.connect(self.confirm_reset_shortcuts)
        self.reset_shortcuts_button.setStyleSheet("""
            QPushButton#reset_shortcuts_button {
                background-color: #dc3545;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton#reset_shortcuts_button:hover {
                background-color: #c82333;
            }
        """)
        shortcuts_layout.addWidget(self.reset_shortcuts_button, alignment=Qt.AlignCenter)
        shortcuts_layout.addStretch()
        self.update_shortcuts_table()
        self.shortcuts_page.setLayout(shortcuts_layout)
        self.right_stacked.addWidget(self.text_page)
        self.right_stacked.addWidget(self.shortcuts_page)
        splitter.addWidget(self.right_stacked)
        main_layout.addWidget(splitter, stretch=1)
        
        # Modifica qui: impostiamo la sidebar estesa all'avvio
        total_width = width  # width è già definito nel metodo init_ui
        expanded_width = int(min(total_width * 0.3, 400))  # 30% della larghezza totale o max 400px
        splitter.setSizes([expanded_width, total_width - expanded_width])
        self.is_sidebar_expanded = True  # Aggiorniamo lo stato
        
        splitter.splitterMoved.connect(self.on_splitter_moved)
        self.snackbar = SnackBar(self.side_panel)
        self.side_stacked.setCurrentWidget(self.files_page)
        self.current_side_page = "files"
        self._set_button_icons()
        self.update_theme_button()
        self.setup_shortcuts()
        self.splitter.installEventFilter(self)

    def setup_shortcuts(self):
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+Alt+C"), self)
        self.copy_shortcut.activated.connect(self.copy_text)
        self.remove_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.remove_shortcut.activated.connect(self.remove_selected_file)
        self.remove_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+D"), self)
        self.remove_all_shortcut.activated.connect(self.remove_all_files)
        self.update_shortcut = QShortcut(QKeySequence("F5"), self)
        self.update_shortcut.activated.connect(self.update_files)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.open_files)
        self.lang_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.lang_shortcut.activated.connect(self.toggle_language)
        self.exit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.exit_shortcut.activated.connect(self.close)

    def open_shortcuts_dialog(self):
        current_widget = self.right_stacked.currentWidget()
        if current_widget == self.text_page:
            self.right_stacked.setCurrentWidget(self.shortcuts_page)
            available_width = self.shortcuts_page.width()
            available_height = self.shortcuts_page.height()
            margin = 80
            self.shortcuts_table.setFixedSize(
                available_width - margin,
                available_height - margin
            )
        else:
            self.right_stacked.setCurrentWidget(self.text_page)

    def on_splitter_moved(self):
        if self.splitter.sizes()[0] < 200:
            self.is_sidebar_expanded = False
            new_sizes = [5, self.splitter.sizes()[1] + self.splitter.sizes()[0] - 5]
            self.splitter.setSizes(new_sizes)
            self.side_panel.setMinimumWidth(5)
            self.current_side_page = None
        else:
            self.side_panel.setMinimumWidth(self.SIDE_PANEL_MIN_WIDTH)

    def collapse_side_panel(self):
        self.current_side_page = None
        self.side_panel.setMinimumWidth(5)
        new_sizes = [5, self.width() - 5]
        self.splitter.setSizes(new_sizes)

    def _set_button_icons(self):
        self.files_button.setIcon(get_colored_icon("files.svg", self.icon_color(), size=24))
        self.settings_button.setIcon(get_colored_icon("settings.svg", self.icon_color(), size=24))
        self.copy_button.setIcon(get_colored_icon("copy.svg", "#FFFFFF", size=18))
        self.update_button.setIcon(get_colored_icon("update.svg", "#FFFFFF", size=18))
        self.save_button.setIcon(get_colored_icon("save.svg", "#FFFFFF", size=18))
        self.exit_button.setIcon(get_colored_icon("exit.svg", "#FFFFFF", size=18))
        
        # Aggiungi tooltip ai pulsanti della sidebar
        self.files_button.setToolTip(self.localization.tr("files_tooltip"))
        self.settings_button.setToolTip(self.localization.tr("settings_tooltip"))

    def on_files_button_clicked(self):
        if self.current_side_page == "files" and self.files_button.isChecked():
            return
        if self.current_side_page == "files" and not self.files_button.isChecked():
            self.collapse_side_panel()
            return
            
        # Gestione pulsanti sidebar
        self.settings_button.setChecked(False)
        self.files_button.setChecked(True)
        self.files_button.setProperty("active", True)
        self.settings_button.setProperty("active", False)
        self.files_button.style().unpolish(self.files_button)
        self.files_button.style().polish(self.files_button)
        self.settings_button.style().unpolish(self.settings_button)
        self.settings_button.style().polish(self.settings_button)
        
        # Cambio pagina nella sidebar
        self.side_stacked.setCurrentWidget(self.files_page)
        self.side_panel.setMinimumWidth(self.SIDE_PANEL_MIN_WIDTH)
        self.side_panel.show()
        self.current_side_page = "files"
        
        # Assicurati che venga mostrata la pagina di testo principale
        self.right_stacked.setCurrentWidget(self.text_page)

    def on_settings_button_clicked(self):
        if self.current_side_page == "settings" and self.settings_button.isChecked():
            return
        if self.current_side_page == "settings" and not self.settings_button.isChecked():
            self.collapse_side_panel()
            return
        self.files_button.setChecked(False)
        self.settings_button.setChecked(True)
        self.files_button.setProperty("active", False)
        self.settings_button.setProperty("active", True)
        self.files_button.style().unpolish(self.files_button)
        self.files_button.style().polish(self.files_button)
        self.settings_button.style().unpolish(self.settings_button)
        self.settings_button.style().polish(self.settings_button)
        self.side_stacked.setCurrentWidget(self.settings_page)
        self.side_panel.setMinimumWidth(self.SIDE_PANEL_MIN_WIDTH)
        self.side_panel.show()
        self.current_side_page = "settings"

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.settings.set_theme('dark' if self.dark_mode else 'light')
        self.apply_theme()
        self._set_button_icons()
        self.update_theme_button()
        msg = self.localization.tr("dark_mode") if self.dark_mode else self.localization.tr("light_mode")
        self.snackbar.showMessage(msg, duration=700)

    def apply_theme(self):
        if self.dark_mode:
            bg = DARK_BG
            darker = DARKER_BG
            txt = TEXT_COLOR
            border = BORDER_COLOR
            primary = PRIMARY_COLOR
            secondary = SECONDARY_COLOR
            language_select = "#0055AA"
        else:
            bg = LIGHT_BG
            darker = LIGHTER_BG
            txt = LIGHT_TEXT_COLOR
            border = LIGHT_BORDER_COLOR
            primary = LIGHT_PRIMARY_COLOR
            secondary = LIGHT_SECONDARY_COLOR
            language_select = "#66B2FF"
        remove_normal = "#FF0000"
        remove_hover = "#CC0000"
        remove_all_normal = "#FF4D4D"
        remove_all_hover = "#CC3C3C"
        copy_normal = "#9B59B6"
        copy_hover = "#8E44AD"
        update_normal = "#28a745"
        update_hover = "#218838"
        open_normal = "#34495e"
        open_hover = "#2c3e50"
        shortcuts_normal = "#f39c12"  
        shortcuts_hover = "#d68910"  
        style_sheet = f"""
            QMainWindow {{
                background-color: {bg};
            }}
            QWidget {{
                background-color: {bg};
                color: {txt};
            }}
            QFrame#sidebar {{
                background-color: {darker};
            }}
            QTreeWidget {{
                background-color: {darker};
                border: 1px solid {border};
                border-radius: 5px;
                color: {txt};
                padding: 5px;
                font-size: 14px;
            }}
            QTreeWidget::item {{
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QTreeWidget::item:hover {{
                background-color: {bg};
            }}
            QTreeWidget::item:selected {{
                background-color: {secondary};
                color: {bg};
            }}
            QTextEdit {{
                background-color: {darker};
                color: {txt};
                border: 1px solid {border};
                border-radius: 5px;
                padding: 10px;
                selection-background-color: {primary};
                selection-color: {bg};
                font-size: 14px;
            }}
            QPushButton {{
                border: none;
                border-radius: 5px;
                padding: 6px 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {border};
            }}
            QPushButton#open_button {{
                background-color: {open_normal};
                color: #FFFFFF;
            }}
            QPushButton#open_button:hover {{
                background-color: {open_hover};
            }}
            QPushButton#remove_button {{
                background-color: {remove_normal};
                color: #FFFFFF;
            }}
            QPushButton#remove_button:hover {{
                background-color: {remove_hover};
            }}
            QPushButton#remove_all_button {{
                background-color: {remove_all_normal};
                color: #FFFFFF;
            }}
            QPushButton#remove_all_button:hover {{
                background-color: {remove_all_hover};
            }}
            QPushButton#copy_button {{
                background-color: {copy_normal};
                color: #FFFFFF;
            }}
            QPushButton#copy_button:hover {{
                background-color: {copy_hover};
            }}
            QPushButton#update_button {{
                background-color: {update_normal};
                color: #FFFFFF;
            }}
            QPushButton#update_button:hover {{
                background-color: {update_hover};
            }}
            QPushButton#save_button {{
                background-color: #f39c12;
                color: #FFFFFF;
            }}
            QPushButton#save_button:hover {{
                background-color: #d68910;
            }}
            QPushButton#exit_button {{
                background-color: #2c3e50;
                color: #FFFFFF;
            }}
            QPushButton#exit_button:hover {{
                background-color: #1f2c39;
            }}
            QPushButton#shortcuts_button {{
                background-color: {shortcuts_normal};
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px;
            }}
            QPushButton#shortcuts_button:hover {{
                background-color: {shortcuts_hover};
            }}
            QLineEdit {{
                background-color: {darker};
                color: {txt};
                border: 1px solid {border};
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton[active="true"] {{
                background-color: {secondary};
            }}
            QPushButton#theme_button {{
                background-color: {primary};
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px;
            }}
            QPushButton#language_button {{
                background-color: {secondary};
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px;
                text-align: left;
            }}
            QMenu#language_menu {{
                background-color: {darker};
                border: 1px solid {border};
                border-radius: 5px;
                padding: 5px;
            }}
            QMenu#language_menu::item {{
                padding: 8px 20px;
                border-radius: 3px;
                min-width: 150px;
            }}
            QMenu#language_menu::item:selected {{
                background-color: {language_select};
                color: {bg};
            }}
            QMenu#language_menu::item:hover {{
                background-color: {border};
            }}
            QMenu#language_menu::separator {{
                height: 1px;
                background-color: {border};
                margin: 5px 0px;
            }}
            QSplitter::handle {{
                background-color: {border};
            }}
            QSplitter::handle:hover {{
                background-color: {primary};
            }}
            QTableWidget {{
                background-color: {darker};
                border: 1px solid {border};
                border-radius: 5px;
                color: {txt};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {darker};
                color: {txt};
                border: 1px solid {border};
                padding: 8px;
                font-weight: bold;
            }}
            QTableWidget::item:alternate {{
                background-color: {bg};
            }}
        """
        self.setStyleSheet(style_sheet)
        self.snackbar.apply_theme(self.dark_mode)

    def open_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseCustomDirectoryIcons
        paths, _ = QFileDialog.getOpenFileNames(self, self.localization.tr("select_files_dialog"), os.getcwd(),
                                                "All Files (*)", options=options)
        if paths:
            self.add_files(paths)

    def add_files(self, file_paths, from_update=False):
        self.loading_overlay.show_overlay()
        QCoreApplication.processEvents()

        file_paths = [os.path.normpath(p) for p in file_paths]
        file_paths = list(dict.fromkeys(file_paths))
        
        existing_paths = [p for p in file_paths if os.path.exists(p)]
        if len(existing_paths) < len(file_paths):
            self.snackbar.showMessage(
                self.localization.tr("some_files_not_found"),
                duration=1500
            )

        new_files = load_files(existing_paths)
        
        for original_path in existing_paths:
            norm_path = os.path.normpath(original_path)
            
            if os.path.isdir(original_path):
                for file_path in new_files.keys():
                    if file_path.startswith(original_path) and file_path in self.files_dict:
                        del self.files_dict[file_path]
                
                for path, content in new_files.items():
                    if path.startswith(original_path):
                        self.files_dict[path] = content
                        
                self.dir_files_map[norm_path] = [
                    path for path in new_files.keys() 
                    if path.startswith(original_path)
                ]
            else:
                is_in_added_dir = False
                for dir_path in self.dir_files_map:
                    if original_path.startswith(dir_path):
                        is_in_added_dir = True
                        break
                
                if not is_in_added_dir:
                    self.files_dict[original_path] = new_files[original_path]

        self.repopulate_file_tree()
        self.update_text_content()
        self.loading_overlay.hide_overlay()

    def get_file_icon(self, path):
        ext = os.path.splitext(path)[1].lower()
        icon_map = {
            '.py': 'languages/python.svg',
            '.md': 'languages/markdown.svg',
            '.cpp': 'languages/cpp.svg',
            '.hpp': 'languages/cpp.svg',
            '.h': 'languages/c.svg',
            '.c': 'languages/c.svg',
            '.cu': 'languages/cuda.svg',
            '.txt': 'languages/txt.svg',
            '.json': 'languages/json.svg',
            '.ipynb': 'languages/python.svg',
            '.yaml': 'languages/yaml.svg',
            '.yml': 'languages/yaml.svg',
        }
        icon_name = icon_map.get(ext, 'languages/txt.svg')
        return get_colored_icon(icon_name, self.icon_color(), size=18)

    def remove_selected_file(self):
        current_item = self.file_tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if not data:
                return

            if data['type'] == 'directory':
                dir_path = data['path']
                files_to_remove = [
                    path for path in self.files_dict.keys()
                    if path.startswith(dir_path)
                ]
                for file_path in files_to_remove:
                    del self.files_dict[file_path]
                if dir_path in self.dir_files_map:
                    del self.dir_files_map[dir_path]
            else:
                file_path = data['path']
                if file_path in self.files_dict:
                    del self.files_dict[file_path]
                    for dir_files in self.dir_files_map.values():
                        if file_path in dir_files:
                            dir_files.remove(file_path)

            if data['type'] == 'directory':
                index = self.file_tree.indexOfTopLevelItem(current_item)
                self.file_tree.takeTopLevelItem(index)
            else:
                parent = current_item.parent()
                if parent:
                    parent.removeChild(current_item)
                    if parent.childCount() == 0:
                        index = self.file_tree.indexOfTopLevelItem(parent)
                        self.file_tree.takeTopLevelItem(index)
                else:
                    index = self.file_tree.indexOfTopLevelItem(current_item)
                    self.file_tree.takeTopLevelItem(index)

            self.update_text_content()
            self.snackbar.showMessage(self.localization.tr("file_removed"), duration=700)

    def remove_all_files(self):
        if self.files_dict or self.dir_files_map:
            self.files_dict.clear()
            self.dir_files_map.clear()
            self.file_tree.clear()
            self.update_text_content()
            self.snackbar.showMessage(self.localization.tr("files_removed_all"), duration=700)
        else:
            self.snackbar.showMessage(self.localization.tr("no_files_to_remove"), duration=700)
        self.update_text_content()

    def merge_contents_html(self):
        html_parts = []
        separator = "<br><br>"
        for path, data in self.files_dict.items():
            norm_path = os.path.normpath(path)
            part = f"<pre>{DASH_LINE}\n{norm_path}\n{DASH_LINE}\n"
            if data['content'] is not None:
                part += data['content']
            else:
                md = data.get('metadata', {})
                part += f"{norm_path} ({self.localization.tr('file_not_text')})\n"
                part += f"{self.localization.tr('file_name')}: {md.get('name', self.localization.tr('n_a'))} | "
                part += f"{self.localization.tr('file_size')}: {md.get('size', 0)} {self.localization.tr('bytes')} | "
                part += f"{self.localization.tr('file_type')}: {md.get('type', self.localization.tr('n_a'))}"
            part += f"\n{DASH_LINE}</pre>"
            html_parts.append(part)
            html_parts.append(separator)
        return "".join(html_parts)

    def update_text_content(self):
        merged_html = self.merge_contents_html()
        self.text_edit.setHtml(merged_html)
        self.update_char_count()

    def update_char_count(self):
        text_length = len(self.text_edit.toPlainText())
        formatted = f"{text_length:,}".replace(",", ".")
        self.char_count_label.setText(f"{self.localization.tr('characters')} {formatted}")

    def save_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseCustomDirectoryIcons
        file_name, _ = QFileDialog.getSaveFileName(self, self.localization.tr("save_action"), "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.snackbar.showMessage(self.localization.tr("file_saved"), duration=700)
            except Exception as e:
                self.snackbar.showMessage(self.localization.tr("file_save_error"), duration=700)

    def update_files(self):
        if not self.files_dict and not self.dir_files_map:
            self.snackbar.showMessage(self.localization.tr("no_files_to_update"), duration=700)
            return

        self.loading_overlay.show_overlay()
        QCoreApplication.processEvents()

        paths_to_update = []
        for dir_path, dir_files in self.dir_files_map.items():
            if os.path.exists(dir_path):
                paths_to_update.append(dir_path)
            else:
                del self.dir_files_map[dir_path]

        for file_path in list(self.files_dict.keys()):
            if os.path.exists(file_path):
                if not any(file_path.startswith(dir_path) for dir_path in self.dir_files_map):
                    paths_to_update.append(file_path)
            else:
                del self.files_dict[file_path]

        if paths_to_update:
            self.add_files(paths_to_update, from_update=True)
            self.snackbar.showMessage(self.localization.tr("content_updated"), duration=700)
        else:
            self.snackbar.showMessage(self.localization.tr("no_files_to_update"), duration=700)

        self.loading_overlay.hide_overlay()

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        self.snackbar.showMessage(self.localization.tr("copied_clipboard"), duration=700)

    def on_item_double_clicked(self, item):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        path = data.get('path')
        if path and path in self.offset_map:
            offset = self.offset_map[path]
            cursor = self.text_edit.textCursor()
            cursor.setPosition(offset)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()
            block_number = cursor.blockNumber()
            line_height = self.text_edit.fontMetrics().lineSpacing()
            scroll_bar = self.text_edit.verticalScrollBar()
            scroll_bar.setValue(block_number * line_height)

    def toggle_language(self):
        self.current_language = 'it' if self.current_language == 'en' else 'en'
        self.localization.load_language(self.current_language)
        self.apply_translations()

    def update_language_menu(self):
        self.language_menu.clear()
        current_lang = self.localization.current_language
        flag_icons = {
            'bn': 'flags/bangladesh.svg',
            'de': 'flags/germany.svg',
            'en': 'flags/uk.svg',
            'es': 'flags/spain.svg',
            'fr': 'flags/france.svg',
            'hi': 'flags/india.svg',
            'it': 'flags/italy.svg',
            'ja': 'flags/japan.svg',
            'ko': 'flags/south-korea.svg',
            'pt': 'flags/portugal.svg',
            'tr': 'flags/turkey.svg',
            'vi': 'flags/vietnam.svg',
            'zh': 'flags/china.svg',
            'ru': 'flags/russia.svg',
        }
        def load_flag_icon(icon_path):
            full_path = get_asset_path(os.path.join('icons', icon_path))
            return QIcon(full_path)
        for lang_code, lang_name in self.localization.get_available_languages():
            action = QAction(lang_name, self)
            if lang_code in flag_icons:
                icon = load_flag_icon(flag_icons[lang_code])
                action.setIcon(icon)
            action.setData(lang_code)
            action.setCheckable(True)
            action.setChecked(lang_code == current_lang)
            if lang_code == current_lang:
                if lang_code in flag_icons:
                    icon = load_flag_icon(flag_icons[lang_code])
                    text = f" {lang_name}"
                    self.language_button.setText(text)
                    if icon:
                        self.language_button.setIcon(icon)
            action.triggered.connect(lambda checked, code=lang_code, name=lang_name: self.change_language(code, name))
            self.language_menu.addAction(action)

    def change_language(self, lang_code, lang_name):
        if lang_code != self.localization.current_language:
            self.localization.load_language(lang_code)
            self.language_button.setText(f" {lang_name}")
            self.apply_translations()
            self.update_language_menu()
            self.snackbar.showMessage(self.localization.tr("language_changed"), duration=700)

    def apply_translations(self):
        self.setWindowTitle(self.localization.tr("app_title"))
        self.drag_open_button.setText(self.localization.tr("open_action"))
        self.file_list_label.setText(self.localization.tr("added_files_label"))
        self.remove_button.setText(self.localization.tr("remove_file_action"))
        self.remove_all_button.setText(self.localization.tr("remove_all_files_action"))
        self.merged_text_label.setText(self.localization.tr("open_drag_file"))
        self.copy_button.setText(self.localization.tr("copy_text_action"))
        self.update_button.setText(self.localization.tr("refresh_action"))
        self.save_button.setText(self.localization.tr("save_action"))
        self.exit_button.setText(self.localization.tr("exit_action"))
        self.merged_text_label.setText(self.localization.tr("open_drag_file"))
        self.theme_button.setText(
            self.localization.tr("dark_mode") if not self.dark_mode else self.localization.tr("light_mode"))
        self.language_button.setText(
            f"{self.localization.tr('language_menu')} ({dict(self.localization.get_available_languages())[self.localization.current_language]})")
        self.theme_button.setText(
            self.localization.tr("dark_mode") if not self.dark_mode else self.localization.tr("light_mode"))
        self.language_button.setText(self.localization.tr("language_menu"))
        self.shortcuts_button.setText(self.localization.tr("edit_shortcuts"))
        self.update_shortcuts_table()
        self.text_edit.setPlaceholderText(self.localization.tr("supported_formats"))
        self.update_supported_formats_placeholder()

    def update_shortcuts_table(self):
        self.shortcuts_table.clear()
        self.shortcuts_table.setColumnCount(3)
        self.shortcuts_table.setHorizontalHeaderLabels([
            self.localization.tr("shortcuts_table_icon"),
            self.localization.tr("shortcuts_table_action"),
            self.localization.tr("shortcuts_table_shortcut")
        ])
        shortcuts_data = self.localization.get_shortcuts_translations()
        self.shortcuts_table.setRowCount(len(shortcuts_data))
        font = self.shortcuts_table.font()
        font.setPointSize(12)
        self.shortcuts_table.setFont(font)
        row_height = 60
        icon_column_width = 80
        self.shortcuts_table.verticalHeader().setDefaultSectionSize(row_height)
        self.shortcuts_table.horizontalHeader().setDefaultSectionSize(icon_column_width)
        table_width = int(self.width() * 0.7)
        self.shortcuts_table.setMaximumWidth(table_width)
        for row, (action, shortcut) in enumerate(shortcuts_data):
            icon_item = QTableWidgetItem()
            for action_key, icon_name in self.action_icons.items():
                if self.localization.tr(action_key) == action:
                    icon = get_colored_icon(icon_name, "#000000" if not self.dark_mode else "#FFFFFF", size=32)
                    icon_item.setIcon(icon)
                    break
            icon_item.setTextAlignment(Qt.AlignCenter)
            self.shortcuts_table.setItem(row, 0, icon_item)
            self.shortcuts_table.setRowHeight(row, row_height)
            self.shortcuts_table.setColumnWidth(0, icon_column_width)
            self.shortcuts_table.item(row, 0).setData(Qt.DisplayRole, "   ")
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(Qt.AlignCenter)
            self.shortcuts_table.setItem(row, 1, action_item)
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setTextAlignment(Qt.AlignCenter)
            self.shortcuts_table.setItem(row, 2, shortcut_item)
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.shortcuts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table_layout = self.shortcuts_table.parent().layout()
        if table_layout:
            table_layout.setAlignment(self.shortcuts_table, Qt.AlignCenter)
        self.shortcuts_table.setStyleSheet("""
            QTableWidget::item {
                padding: 0px;
                margin: 0px;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.shortcuts_table.cellDoubleClicked.connect(self.edit_shortcut)

    def edit_shortcut(self, row, column):
        if column == 2:
            item = self.shortcuts_table.item(row, column)
            if item:
                cell_rect = self.shortcuts_table.visualItemRect(item)
                global_pos = self.shortcuts_table.viewport().mapToGlobal(cell_rect.topLeft())
                editor = ShortcutEditor(item.text(), self.shortcuts_table, self)
                editor.shortcutChanged.connect(self.on_shortcut_changed)
                editor.row = row
                editor.column = column
                editor.setGeometry(cell_rect)
                editor.move(global_pos.x(), global_pos.y())
                editor.setFixedSize(cell_rect.width(), cell_rect.height())
                editor.show()
                editor.setFocus()

    def on_shortcut_changed(self):
        self.localization.refresh_shortcuts()

    def on_tree_item_moved(self):
        new_files_dict = {}
        root = self.file_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            data = item.data(0, Qt.UserRole)
            if data and data.get('path') in self.files_dict:
                new_files_dict[data['path']] = self.files_dict[data['path']]
        self.files_dict = new_files_dict
        self.update_text_content()

    def eventFilter(self, source, event):
        if source == self.splitter and event.type() == QEvent.MouseButtonDblClick:
            if not self.is_sidebar_expanded:
                total_width = self.width()
                expanded_width = int(min(total_width * 0.6, 600))
                new_sizes = [expanded_width, total_width - expanded_width]
                self.splitter.setSizes(new_sizes)
                self.is_sidebar_expanded = True
            else:
                new_sizes = [self.SIDE_PANEL_MIN_WIDTH, self.width() - self.SIDE_PANEL_MIN_WIDTH]
                self.splitter.setSizes(new_sizes)
                self.is_sidebar_expanded = False
            return True
        return super(MainWindow, self).eventFilter(source, event)

    def resizeEvent(self, event):
        """Aggiorna il placeholder quando la finestra viene ridimensionata"""
        super().resizeEvent(event)
        if hasattr(self, 'text_edit') and self.text_edit:
            # Ritarda leggermente l'aggiornamento per permettere il completamento del resize
            QApplication.processEvents()
            self.update_supported_formats_placeholder()

    def closeEvent(self, event):
        message_box = QMessageBox(
            QMessageBox.Question,
            self.localization.tr("app_title"),
            self.localization.tr("exit_confirmation"),
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        yes_button = message_box.button(QMessageBox.Yes)
        yes_button.setText(self.localization.tr("yes"))
        yes_button.setStyleSheet("QPushButton { background-color: #FF0000; color: white; }")
        no_button = message_box.button(QMessageBox.No)
        no_button.setText(self.localization.tr("no"))
        no_button.setStyleSheet("QPushButton { background-color: #1e90ff; color: white; }")
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def exit_button_clicked(self):
        self.close

    def confirm_reset_shortcuts(self):
        message_box = QMessageBox(
            QMessageBox.Question,
            self.localization.tr("reset_shortcuts_title"),
            self.localization.tr("reset_shortcuts_confirm"),
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        yes_button = message_box.button(QMessageBox.Yes)
        yes_button.setText(self.localization.tr("reset"))
        yes_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; }")
        no_button = message_box.button(QMessageBox.No)
        no_button.setText(self.localization.tr("cancel"))
        no_button.setStyleSheet("QPushButton { background-color: #6c757d; color: white; }")
        reply = message_box.exec_()
        if reply == QMessageBox.Yes:
            if ShortcutEditor.reset_to_defaults():
                self.localization.refresh_shortcuts() 
                self.update_shortcuts_table()
                self.snackbar.showMessage(self.localization.tr("shortcuts_reset_success"), duration=700)
            else:
                self.snackbar.showMessage(self.localization.tr("shortcuts_reset_error"), duration=700)

    def on_shortcuts_changed(self):
        self.update_shortcuts_table()
        self.update_button_texts()

    def update_button_texts(self):
        self.drag_open_button.setText(self.localization.tr("open_action"))
        self.remove_button.setText(self.localization.tr("remove_file_action"))
        self.remove_all_button.setText(self.localization.tr("remove_all_files_action"))
        self.copy_button.setText(self.localization.tr("copy_text_action"))
        self.update_button.setText(self.localization.tr("refresh_action"))
        self.save_button.setText(self.localization.tr("save_action"))
        self.exit_button.setText(self.localization.tr("exit_action"))

    def repopulate_file_tree(self):
        self.file_tree.clear()
        
        dir_files = {}
        single_files = []
        
        for file_path in self.files_dict.keys():
            parent_dir = os.path.dirname(file_path)
            if parent_dir in self.dir_files_map:
                if parent_dir not in dir_files:
                    dir_files[parent_dir] = []
                dir_files[parent_dir].append(file_path)
            else:
                single_files.append(file_path)

        for dir_path, dir_file_list in dir_files.items():
            dir_item = QTreeWidgetItem([dir_path])
            dir_item.setIcon(0, get_colored_icon("folder.svg", self.icon_color(), size=18))
            dir_item.setData(0, Qt.UserRole, {'type': 'directory', 'path': dir_path})
            
            for file_path in sorted(dir_file_list):
                file_item = QTreeWidgetItem([file_path])
                file_item.setIcon(0, self.get_file_icon(file_path))
                file_item.setData(0, Qt.UserRole, {
                    'type': 'file',
                    'path': file_path,
                    'parent_dir': dir_path
                })
                dir_item.addChild(file_item)
            
            self.file_tree.addTopLevelItem(dir_item)

        for file_path in sorted(single_files):
            file_item = QTreeWidgetItem([file_path])
            file_item.setIcon(0, self.get_file_icon(file_path))
            file_item.setData(0, Qt.UserRole, {
                'type': 'file',
                'path': file_path,
                'parent_dir': None
            })
            self.file_tree.addTopLevelItem(file_item)

    def update_supported_formats_placeholder(self):
        # Testo principale
        main_text = self.localization.tr("drag_files_here")
        
        # Icona semplice
        icon_lines = [
            "      ↓↓↓↓     ",
            "  ┌──────────┐ ",
            "  │ ░░░░░░░░ │ ",
            "  │ ░░FILE░░ │ ",
            "  │ ░░░░░░░░ │ ",
            "  └──────────┘ "
        ]
        
        # Calcola il contenuto totale
        content_lines = []
        content_lines.extend(icon_lines)
        content_lines.append("")  # Spazio vuoto
        content_lines.extend(main_text.split('\n'))
        
        # Trova la riga più lunga per calcolare la larghezza
        max_content_width = max(len(line) for line in content_lines)
        
        # Ottieni le dimensioni effettive del text_edit se disponibile
        if hasattr(self, 'text_edit') and self.text_edit:
            widget_width = self.text_edit.width()
            widget_height = self.text_edit.height()
            
            # Calcola spazio disponibile in caratteri (approssimativo)
            font_metrics = self.text_edit.fontMetrics()
            chars_per_line = max(20, widget_width // font_metrics.averageCharWidth())
            lines_available = max(10, widget_height // font_metrics.lineSpacing())
        else:
            # Valori di fallback
            chars_per_line = 60
            lines_available = 25
        
        # Calcola padding per centrare
        total_lines_needed = len(content_lines)
        vertical_padding = max(2, (lines_available - total_lines_needed) // 2)
        
        horizontal_padding_chars = max(2, (chars_per_line - max_content_width) // 2)
        horizontal_padding = " " * horizontal_padding_chars
        
        # Costruisci il placeholder finale
        final_lines = []
        
        # Aggiungi spazio sopra
        final_lines.extend([""] * vertical_padding)
        
        # Aggiungi il contenuto centrato orizzontalmente
        for line in content_lines:
            if line.strip():  # Se la riga non è vuota
                final_lines.append(horizontal_padding + line)
            else:  # Se la riga è vuota, mantienila vuota
                final_lines.append("")
        
        # Aggiungi spazio sotto
        final_lines.extend([""] * vertical_padding)
        
        placeholder = "\n".join(final_lines)
        self.text_edit.setPlaceholderText(placeholder)
