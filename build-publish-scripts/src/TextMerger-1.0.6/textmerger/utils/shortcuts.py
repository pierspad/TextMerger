class ShortcutManager:
    def __init__(self, localization):
        self.localization = localization
        self.shortcuts = []
        self.update_shortcuts()
        self.localization.language_changed.connect(self.update_shortcuts)

    def update_shortcuts(self):
        self.shortcuts = []
        current_shortcuts = self.localization.settings.get_shortcuts()
        
        action_mapping = {
            'open_action': ('open_file_action_shrtc', 'Open'),
            'save_action': ('save_file_action_shrtc', 'Save'),
            'exit_action': ('exit_app_action_shrtc', 'Exit'),
            'remove_file_action': ('remove_file_action_shrtc', 'Remove'),
            'remove_all_files_action': ('remove_all_files_action_shrtc', 'Remove All'),
            'copy_text_action': ('copy_text_action_shrtc', 'Copy Text'),
            'refresh_action': ('refresh_content_action_shrtc', 'Refresh'),
        }

        for action_key, (shortcut_key, _) in action_mapping.items():
            if shortcut_key in current_shortcuts:
                self.shortcuts.append((action_key, current_shortcuts[shortcut_key]))

    def get_shortcuts_data(self):
        return [
            (self.localization.tr(action), shortcut)
            for action, shortcut in self.shortcuts
        ]
