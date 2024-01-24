"""
An Extended TAS Diagram.
"""
import sys
import re

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    # Backwards compatibility - importlib.metadata was added in Python 3.8
    import importlib_metadata

from PySide6 import QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu

class TAS_Extended(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Tas Extended')
        self.resize(1024, 600)  # 设置窗口尺寸为1024*600
        
        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        # 在File菜单中添加一个action
        open_action = QAction('Open', self)
        file_menu.addAction(open_action)

        self.show()

def main():
    # Linux desktop environments use app's .desktop file to integrate the app
    # to their application menus. The .desktop file of this app will include
    # StartupWMClass key, set to app's formal name, which helps associate
    # app's windows to its menu item.
    #
    # For association to work any windows of the app must have WMCLASS
    # property set to match the value set in app's desktop file. For PySide2
    # this is set with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules['__main__'].__package__
    # Retrieve the app's metadata
    metadata = importlib_metadata.metadata(app_module)

    QtWidgets.QApplication.setApplicationName(metadata['Formal-Name'])

    app = QtWidgets.QApplication(sys.argv)
    main_window = TAS_Extended()
    sys.exit(app.exec())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TAS_Extended()
    main_window.show()  # 显示主窗口
    sys.exit(app.exec())