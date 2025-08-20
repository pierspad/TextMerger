import sys
import os
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if 'linux' in sys.platform:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QIcon

        import ui.mainwindow
        import utils.helpers

        app = QApplication(sys.argv)
        app.setApplicationName("TextMerger")
        app.setApplicationDisplayName("TextMerger")
        app.setApplicationVersion("1.0.0")

        try:
            icon_path = utils.helpers.get_asset_path("logo/logo.png")
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Warning: Could not set application icon: {e}")

        window = ui.mainwindow.MainWindow()
        window.show()

        sys.exit(app.exec_())

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting TextMerger: {e}")
        print("Traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
