import sys
from pathlib import Path
# Ensure the parent directory of 'callbook' is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))
from callbook.gui.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QFontDatabase
from importlib.resources import files


def main():
    try:
        # https://www.pythontutorial.net/pyqt/pyqt-qmenu/
        import ctypes
        appid = 'cjtool.codebook.1.0'  # arbitrary string
        if sys.platform.startswith('win'):
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    finally:
        app = QApplication(sys.argv)
        logo_path = files('callbook').joinpath('image/logo.png')
        app.setWindowIcon(QIcon(str(logo_path)))

        font_path = files('callbook').joinpath('font/Inconsolata.ttf')
        id = QFontDatabase.addApplicationFont(str(font_path))
        assert (id == 0)
        families = QFontDatabase.applicationFontFamilies(id)
        assert (families[0] == 'Inconsolata')

        demo = MainWindow()
        demo.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
