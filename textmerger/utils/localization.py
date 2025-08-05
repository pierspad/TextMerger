import json
import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from utils.settings import DEFAULT_SHORTCUTS

class Localization(QObject):
    language_changed = pyqtSignal(str)
    shortcuts_changed = pyqtSignal()
    
    def __init__(self, settings):
        super().__init__()
        self.strings = {}
        self._available_languages = None
        self.settings = settings
        self.current_language = settings.get_language()
        self.load_language(self.current_language)
        self.shortcuts = settings.get_shortcuts()
        if not self.shortcuts:
            self.shortcuts = DEFAULT_SHORTCUTS.copy()
            settings.set_shortcuts(self.shortcuts)

    def get_available_languages(self):
        if self._available_languages is None:
            self._available_languages = []
            try:
                base_path = os.path.dirname(os.path.dirname(__file__))
                
                translations_dir = os.path.join(base_path, 'translations')

                for file in os.listdir(translations_dir):
                    if file.startswith('strings_') and file.endswith('.json'):
                        lang_code = file[8:-5]

                        with open(os.path.join(translations_dir, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            lang_name = data.get('language_name', lang_code)
                            self._available_languages.append((lang_code, lang_name))

                self._available_languages.sort(key=lambda x: x[1])
            except Exception as e:
                self._available_languages = [('en', 'English')]
        
        return self._available_languages

    def _load_shortcuts(self):
        self.shortcuts = self.settings.get_shortcuts()

    def load_language(self, lang_code):
        try:
            base_path = os.path.dirname(os.path.dirname(__file__))

            translation_file = os.path.join(base_path, 'translations', f'strings_{lang_code}.json')
            
            with open(translation_file, 'r', encoding='utf-8') as f:
                self.strings = json.load(f)
                self.current_language = lang_code
                self.settings.set_language(lang_code)
            self._load_shortcuts()
            self.language_changed.emit(lang_code)
        except Exception as e:
            self.strings = {}

    def get_string(self, key):
        return self.strings.get(key, key)

    def tr(self, key):
        return self.strings.get(key, key)

    def get_shortcuts_translations(self):
        shortcuts = []
        if not self.shortcuts:
            self.shortcuts = self.settings.get_shortcuts()
        
        for key in self.strings.keys():
            if key.endswith('_action'):
                shortcut_key = f"{key}_shrtc"
                if shortcut_key in self.shortcuts:
                    value = self.strings[key].replace('\n', '')
                    shortcuts.append((value, self.shortcuts[shortcut_key]))
        
        if not shortcuts:
            for key in DEFAULT_SHORTCUTS:
                action_key = key[:-6]
                if action_key in self.strings:
                    value = self.strings[action_key].replace('\n', '')
                    shortcuts.append((value, DEFAULT_SHORTCUTS[key]))
        
        return shortcuts

    def refresh_shortcuts(self):
        self.shortcuts = self.settings.get_shortcuts()
        self.shortcuts_changed.emit()
        main_window = self.parent().findChild(QMainWindow, "MainWindow")
        if main_window:
            main_window.refresh_file_list()

