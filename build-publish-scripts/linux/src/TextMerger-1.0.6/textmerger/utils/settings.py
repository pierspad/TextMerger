import json
import os
from pathlib import Path

DEFAULT_SHORTCUTS = {
    "open_action_shrtc": "Ctrl+O",
    "save_action_shrtc": "Ctrl+S",
    "exit_action_shrtc": "Ctrl+Q",
    "remove_file_action_shrtc": "Ctrl+D",
    "remove_all_files_action_shrtc": "Ctrl+Shift+D",
    "copy_text_action_shrtc": "Ctrl+Alt+C",
    "refresh_action_shrtc": "F5"
}

class Settings:
    def __init__(self):
        self.localization = None
        self._settings = {
            'theme': 'dark',
            'language': 'en',
            'shortcuts': DEFAULT_SHORTCUTS.copy()
        }
        self._settings_file = self._get_settings_path()
        self.load_settings()

    def _get_settings_path(self):
        app_data_dir = os.getenv('APPDATA') if os.name == 'nt' else str(Path.home() / '.config')
        settings_dir = os.path.join(app_data_dir, 'TextMerger')
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, 'settings.json')

    def load_settings(self):
        try:
            if os.path.exists(self._settings_file):
                with open(self._settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    shortcuts = DEFAULT_SHORTCUTS.copy()
                    if 'shortcuts' in saved_settings:
                        shortcuts.update(saved_settings['shortcuts'])
                    saved_settings['shortcuts'] = shortcuts
                    self._settings.update(saved_settings)
            else:
                self._settings['shortcuts'] = DEFAULT_SHORTCUTS.copy()
        except Exception as e:
            self._settings['shortcuts'] = DEFAULT_SHORTCUTS.copy()

    def save_settings(self):
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings, f)
        except Exception as e:
            print(f"{self.localization.tr('error_saving_settings')}: {e}")

    def get_theme(self):
        return self._settings.get('theme', 'dark')

    def set_theme(self, theme):
        self._settings['theme'] = theme
        self.save_settings()

    def get_language(self):
        return self._settings.get('language', 'en')

    def set_language(self, language):
        self._settings['language'] = language
        self.save_settings()

    def get_shortcuts(self):
        return self._settings.get('shortcuts', DEFAULT_SHORTCUTS.copy())

    def set_shortcuts(self, shortcuts):
        self._settings['shortcuts'] = shortcuts
        self.save_settings()
