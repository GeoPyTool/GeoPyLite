"""
An Extended TAS Diagram.
"""
import json
import pickle
import sqlite3
import sys
import re
import os
import numpy as np


import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
from matplotlib.patches import ConnectionStyle

try:
    from importlib import metadata as importlib_metadata
except ImportError:
    # Backwards compatibility - importlib.metadata was added in Python 3.8
    import importlib_metadata

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QAbstractItemView, QMainWindow, QApplication, QMenu, QToolBar, QFileDialog, QTableView, QHBoxLayout, QWidget
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QVariantAnimation, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df
        self._changed = False
        self._filters = {}
        self._sortBy = []
        self._sortDirection = []

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError,):
                return None
        elif orientation == Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError,):
                return None

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            try:
                return str(self._df.iloc[index.row(), index.column()])
            except:
                pass
        elif role == Qt.CheckStateRole:
            return None

        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        dtype = self._df[col].dtype
        if dtype != object:
            value = None if value == '' else dtype.type(value)
        self._df.at[row, col] = value
        self._changed = True
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
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
        self.setEditTriggers(QAbstractItemView.NoEditTriggers |
                             QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):  # Reimplement the event here
        return


class TAS_Extended(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_data()
        self.init_ui()

    def init_data(self):
        self.df = pd.DataFrame()        
        self.dpi = 64
        pass

    def init_ui(self):
        self.setWindowTitle('Tas Extended')
        self.resize(1024, 600)  # 设置窗口尺寸为1024*600

        # 创建工具栏
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 在工具栏中添加一个Open action
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file)  # 连接到open_file方法
        toolbar.addAction(open_action)

        # 在工具栏中添加一个Connect action
        connect_action = QAction('Connect', self)
        toolbar.addAction(connect_action)

        # 在工具栏中添加一个Load action
        load_action = QAction('Load', self)
        toolbar.addAction(load_action)

        # 在工具栏中添加一个Plot action
        plot_action = QAction('Plot', self)
        plot_action.triggered.connect(self.plot_data)  # 连接到plot_data方法
        toolbar.addAction(plot_action)

        # 在工具栏中添加一个Hyper action
        hyper_action = QAction('Hyper', self)
        hyper_action.triggered.connect(self.hyper_data)  # 连接到hyper_data方法
        toolbar.addAction(hyper_action)

        # 在工具栏中添加一个Save action
        save_action = QAction('Savefig', self)
        save_action.triggered.connect(self.save_figure)  # 连接到save_figure方法
        toolbar.addAction(save_action)

        # 在工具栏中添加一个Clear action
        clear_action = QAction('Clear', self)
        clear_action.triggered.connect(self.clear_data)  # 连接到clear_data方法
        toolbar.addAction(clear_action)


        # 创建一个表格视图
        self.table = QTableView()

        # 创建一个Matplotlib画布
        self.fig = Figure((10,10), dpi=self.dpi)

        # self.ax = self.fig.subplots_adjust(hspace=0.5, wspace=0.5, left=0.13, bottom=0.2, right=0.7, top=0.9)

        self.canvas = FigureCanvas(self.fig)
        # self.canvas = MPLCanvas(self, width=5, height=4, dpi=100)

        # 创建一个水平布局并添加表格视图和画布
        base_layout = QHBoxLayout()
        self.left_layout = QHBoxLayout()
        self.right_layout = QHBoxLayout()
        self.left_layout.addWidget(self.table)
        self.right_layout.addWidget(self.canvas)
        base_layout.addLayout(self.left_layout)
        base_layout.addLayout(self.right_layout)

        # 创建一个QWidget，设置其布局为我们刚刚创建的布局，然后设置其为中心部件
        widget = QWidget()
        widget.setLayout(base_layout)
        self.setCentralWidget(widget)

        self.show()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'CSV Files (*.csv);;Excel Files (*.xls *.xlsx)')
        if file_name:
            if file_name.endswith('.csv'):
                self.df = pd.read_csv(file_name)
            elif file_name.endswith(('.xls', '.xlsx')):
                self.df = pd.read_excel(file_name)
            
            
            model = PandasModel(self.df)
            self.table.setModel(model)  # 设置表格视图的模型

    
    def clear_data(self):
        # 清空数据
        self.df = pd.DataFrame()
        self.table.setModel(PandasModel(self.df))

        # 清空图表
        self.canvas.figure.clear()
        self.canvas.draw()

    
    def plot_data(self):
        self.canvas.figure.clear()
        ax = self.canvas.figure.subplots()
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_directory = os.path.dirname(current_file_path)
        # 改变当前工作目录
        os.chdir(current_directory)

        with open('tas_cord.json') as file:
            cord = json.load(file)

        # 绘制TAS图解边界线条
        # Draw TAS diagram boundary lines
        for line in cord['coords'].values():
            x_coords = [point[0] for point in line]
            y_coords = [point[1] for point in line]
            ax.plot(x_coords, y_coords, color='black', linewidth=0.3)

                # 在TAS图解中添加岩石种类标签
        # Add rock type labels in TAS diagram
        for label, coords in cord['coords'].items():
            x_coords = [point[0] for point in coords]
            y_coords = [point[1] for point in coords]
            x_center = sum(x_coords) / len(x_coords)
            y_center = sum(y_coords) / len(y_coords)
            ax.text(x_center, y_center, label, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.3), fontsize=6.5)

        # 创建一个空的set
        label_set = set()
        if self.df.empty:
            return
        else:
            try:
                x = self.df['SiO2(wt%)']
                y = self.df['Na2O(wt%)'] + self.df['K2O(wt%)']
                color = self.df['Color']
                alpha = self.df['Alpha']
                size = self.df['Size']
                label = self.df['Label']

                def plot_group(group):
                    ax.scatter(group['x'], group['y'], c=group['color'], alpha=group['alpha'], s=group['size'], label=group.name)

                # 创建一个新的DataFrame，包含所有需要的列
                df = pd.DataFrame({
                    'x': x,
                    'y': y,
                    'color': color,
                    'alpha': alpha,
                    'size': size,
                    'label': label
                })

                # 按照'label'列进行分组，然后对每个组应用plot_group函数
                df.groupby('label').apply(plot_group)
                
            except KeyError:
                pass

        ax.legend()
        ax.set_xlabel(r"$SiO2$", fontsize=9)
        ax.set_ylabel(r"$Na2O+K2O$", fontsize=9)
        ax.set_title(r"Extended TAS Diagram", fontsize=9)
        ax.set_xlim(35,80)
        self.canvas.draw()

    
    def hyper_data(self):
        # Remove the old canvas from the layout        
        # self.canvas.figure.clear()
        self.right_layout.removeWidget(self.canvas)

        # Delete the old canvas
        self.canvas.deleteLater()

        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)

        # 获取当前文件的目录
        current_directory = os.path.dirname(current_file_path)
        # 改变当前工作目录
        os.chdir(current_directory)

        with open('tas_cord.json') as file:
            cord = json.load(file)
        # Load the Figure
        with open('TAS_Base_VOL.pkl', 'rb') as f:
            fig = pickle.load(f)
            print('fig loaded')
        # Create a new FigureCanvas

        # Get the Axes
        ax = fig.axes[0]
        print('ax called')


        # 创建一个空的set
        label_set = set()
        if self.df.empty:
            return
        else:
            try:
                x = self.df['SiO2(wt%)']
                y = self.df['Na2O(wt%)'] + self.df['K2O(wt%)']
                color = self.df['Color']
                alpha = self.df['Alpha']
                size = self.df['Size']
                label = self.df['Label']

                def plot_group(group):
                    ax.scatter(group['x'], group['y'], c=group['color'], alpha=group['alpha'], s=group['size'], label=group.name)

                # 创建一个新的DataFrame，包含所有需要的列
                df = pd.DataFrame({
                    'x': x,
                    'y': y,
                    'color': color,
                    'alpha': alpha,
                    'size': size,
                    'label': label
                })

                # 按照'label'列进行分组，然后对每个组应用plot_group函数
                df.groupby('label').apply(plot_group)
                
            except KeyError:
                pass

        ax.legend()
        # Print the size of the figure
        print('Figure size:', fig.get_size_inches())

        fig.dpi=self.dpi
        self.canvas = FigureCanvas(fig)

        # Add the new canvas to the layout
        self.right_layout.addWidget(self.canvas)
        print('fig sent to canvas')
        self.canvas.draw()
        print('canvas drawn')




    def save_figure(self):
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Figure', '', 'SVG Files (*.svg);;PDF Files (*.pdf);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)')
        if file_name:
            try:
                # Set dpi to 600 for bitmap formats
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.canvas.figure.savefig(file_name, dpi=self.dpi*10)
                else:
                    self.canvas.figure.savefig(file_name)
            except Exception as e:
                print(f"Failed to save figure: {e}")

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

    QApplication.setApplicationName(metadata['Formal-Name'])

    app = QApplication(sys.argv)
    main_window = TAS_Extended()
    sys.exit(app.exec())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = TAS_Extended()
    main_window.show()  # 显示主窗口
    sys.exit(app.exec())