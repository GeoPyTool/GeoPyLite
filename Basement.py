import csv
import importlib
import subprocess
import webbrowser
import os
import random
import requests
import re
import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QTableView, QMessageBox, QApplication, QMainWindow, QFileDialog, QAction, QTableWidget, QTextEdit, QTableWidgetItem, QAbstractItemView, QWidget, QLineEdit, QPushButton, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QProxyStyle, QStyle, qApp, QCheckBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex, QCoreApplication


class GrowingTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 8

    def sizeChange(self):
        docHeight = self.document().size().height()
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(int(docHeight))

class PandasModel(QAbstractTableModel):
    _df = pd.DataFrame()
    _changed = False

    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self._changed = False

        self._filters = {}
        self._sortBy = []
        self._sortDirection = []

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError,):
                return QVariant()

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            try:
                row = index.row()
                col = index.column()
                name = self._struct[col]['name']
                return self._data[row][name]
            except:
                pass
        elif role == Qt.CheckStateRole:
            return None

        return QVariant(str(self._df.iloc[index.row(), index.column()]))

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    '''
    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        col = index.column()
        name = self._struct[col]['name']
        self._data[row][name] = value
        self.emit(SIGNAL('dataChanged()'))
        return True
    '''

    def setData(self, index, value, role=Qt.EditRole):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        # self._df.set_value(row, col, value)
        self._df.at[row, col] = value
        self._changed = True
        # self.emit(SIGNAL('dataChanged()'))
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]

        index = self._df.index.tolist()
        self.layoutAboutToBeChanged.emit()

        # self._df.sort_values(colname, ascending=order == Qt.AscendingOrder, inplace=True)
        # self._df.reset_index(inplace=True, drop=True)

        try:
            self._df.sort_values(colname, ascending=order == Qt.AscendingOrder, inplace=True)
        except:
            pass
        try:
            self._df.reset_index(inplace=True, drop=True)
        except:
            pass

        self.layoutChanged.emit()

class CustomQTableView(QTableView):
    df = pd.DataFrame()

    def __init__(self, *args):
        super().__init__(*args)

        self.resize(800, 600)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers |
                             QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):  # Reimplement the event here
        return

class PoweredQTableView(QTableView):
    path = ''

    def __init__(self, *args):
        super().__init__(*args)
        self.setAcceptDrops(True)

        self.resize(800, 600)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers |
                             QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):  # Reimplement the event here
        return

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            files = [(u.toLocalFile()) for u in event.mimeData().urls()]
            for f in files:
                if 'csv' in f or 'xls' in f:
                    print('Drag', f)
                    self.path = f

                    if ('csv' in f):
                        self.parent().raw = pd.read_csv(f,engine='python')
                    elif ('xls' in f):
                        self.parent().raw = pd.read_excel(f,engine='openpyxl')

                    # #print(self.raw)

            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [(u.toLocalFile()) for u in event.mimeData().urls()]
        for f in files:
            print('Drop')


class TableViewer(QMainWindow):

    raw = pd.DataFrame()
    begin_result = pd.DataFrame()
    load_result = pd.DataFrame()

    def __init__(self, parent=None, df=pd.DataFrame(), title='Statistical Result'):
        QMainWindow.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setWindowTitle(title)
        self.df = df
        self.create_main_frame()
        self.create_status_bar()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [(u.toLocalFile()) for u in event.mimeData().urls()]
        for f in files:
            print(f)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())


    def ErrorEvent(self, text=''):
        _translate = QCoreApplication.translate

        if (text == ''):
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Some Items missing?\n Or maybe there are blanks in items names?\n Or there are nonnumerical value？'))
        else:
            reply = QMessageBox.information(self, _translate('MainWindow', 'Warning'), _translate('MainWindow',
                                                                                                  'Your Data mismatch this Function.\n Error infor is:') + text)

    def create_main_frame(self):

        self.resize(800, 600)
        self.main_frame = QWidget()

        self.save_button = QPushButton('&Save')
        self.save_button.clicked.connect(self.save_file)

        self.pie_button = QPushButton('&Pie')
        self.pie_button.clicked.connect(self.MyPie)

        self.bar_button = QPushButton('&Bar')
        self.bar_button.clicked.connect(self.MyBar)

        self.table_view = CustomQTableView(self.main_frame)
        self.table_view.setObjectName('tableView')
        self.table_view.setSortingEnabled(True)

        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.table_view)
        self.hbox = QHBoxLayout()

        for w in [self.save_button, self.pie_button, self.bar_button]:
            self.hbox.addWidget(w)

        self.vbox.addLayout(self.hbox)

        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)

        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)

    def create_status_bar(self):
        self.status_text = QLabel("Click Save button to save.")
        self.statusBar().addWidget(self.status_text, 1)

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def save_file(self):
        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/',
                                                          'Excel Files (*.xlsx);;CSV Files (*.csv)')  # 数据文件保存输出

        if "Label" in self.model._df.columns.values.tolist():
            self.model._df = self.model._df.set_index('Label')

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):
                self.model._df.to_csv(DataFileOutput, sep=',', encoding='utf-8')

            elif ('xls' in DataFileOutput):
                self.model._df.to_excel(DataFileOutput, encoding='utf-8')

    def create_action(self, text, slot=None, shortcut=None,
                      icon=None, tip=None, checkable=False,
                      signal='triggered()'):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(':/%s.png' % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action


    def MyPie(self):
        # try:
        #     self.MyPiepop = Pie(df=self.df)
        #     self.MyPiepop.Magic()
        #     self.MyPiepop.show()
        # except Exception as e:
        #     self.ErrorEvent(text=repr(e))
        pass

    def MyBar(self):
        # try:
        #     self.MyBarpop = Bar(df=self.df)
        #     self.MyBarpop.Magic()
        #     self.MyBarpop.show()
        # except Exception as e:
        #     self.ErrorEvent(text=repr(e))
        pass
 
class AppWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('GeoPyLite')
        self.setGeometry(100, 100, 800, 600)

        self.df = pd.DataFrame()
        self.DataFileInputPath =''
        self.DataFileOutputPath =''

        self.create_menu()
        self.create_main_frame()


    def create_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu('File')

        open_csv_action = self.create_action('Open File', self.open_file)
        file_menu.addAction(open_csv_action)

        # Result menu
        result_menu = menu_bar.addMenu('Result')

        generate_result_action = self.create_action('Generate Result', self.generate_result)
        result_menu.addAction(generate_result_action)

        # Help menu
        help_menu = menu_bar.addMenu('Help')

        version_action = self.create_action('Version', self.show_version)
        help_menu.addAction(version_action)

    def create_action(self, text, slot=None):
        action = QAction(text, self)
        if slot is not None:
            action.triggered.connect(slot)
        return action

    def create_main_frame(self):
        
        self.main_frame = QWidget()
        # self.setCentralWidget(self.table_view)
        self.table_view = PoweredQTableView(self.main_frame)
        self.table_view.setObjectName('tableView')
        self.table_view.setSortingEnabled(True)

        self.save_button = QPushButton('&Save')
        self.save_button.clicked.connect(self.save_file)

        self.vbox = QVBoxLayout()

        self.vbox.addWidget(self.table_view)
        self.hbox = QHBoxLayout()

        for w in [self.save_button,]:
            self.hbox.addWidget(w)

        self.vbox.addLayout(self.hbox)

        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)
        
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)


    def open_file(self):
        DataFileInput, filetype = QFileDialog.getOpenFileName(self, (u'Choose Data File'),
                                                              '~/',
                                                              'CSV Files (*.csv);;Excel Files (*.xlsx);;Excel 2003 Files (*.xls)')  # 设置文件扩展名过滤,注意用双分号间隔
        print(DataFileInput)

        raw_input_data = pd.DataFrame()



        if ('csv' in DataFileInput):
            raw_input_data = pd.read_csv(DataFileInput, engine='python')
        elif ('xls' in DataFileInput):
            raw_input_data = pd.read_excel(DataFileInput,engine='openpyxl')

        if len(raw_input_data) > 0:
            self.df = raw_input_data
            self.model = PandasModel(self.df)
            self.table_view.setModel(self.model)
            
            return (raw_input_data, DataFileInput)

        else:
            return ('Blank')
    


    
    def save_file(self):

        # if self.model._changed == True:
        # print('changed')
        # print(self.model._df)

        DataFileOutput, ok2 = QFileDialog.getSaveFileName(self,
                                                          '文件保存',
                                                          'C:/',
                                                          'CSV Files (*.csv);;Excel Files (*.xlsx)')  # 数据文件保存输出

        if "Label" in self.model._df.columns.values.tolist():
            self.model._df = self.model._df.set_index('Label')

        if (DataFileOutput != ''):

            if ('csv' in DataFileOutput):
                self.model._df.to_csv(DataFileOutput, sep=',', encoding='utf-8')

            elif ('xls' in DataFileOutput):
                self.model._df.to_excel(DataFileOutput)

    def generate_result(self):
        # Implement your logic to generate result here
        pass

    def show_version(self):
        # Implement your logic to show version here
        pass

    def ErrorEvent(self, text=''):
        # Implement your error handling logic here
        pass



def main():

    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
