"""
An expanded TAS illustration that enhances the readability and degree of quantification of the results.
"""
import json
import math
import os
import platform

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.path import Path
import numpy as np
import pandas as pd
import scipy as sp
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import toga_chart


class TAS(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        self.raw_df = pd.DataFrame()
        self.data = pd.DataFrame()

        # 获取当前文件的绝对路径
        file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录的路径
        dir_path = os.path.dirname(file_path)
        # 更改当前工作目录
        os.chdir(dir_path)

        with open(dir_path+'\cord.json') as file:
            self.cord = json.load(file)

        self.x_list = [0,0]
        self.y_list = [1,1]
        self.label_list =['test1','test2']
        self.color_list = ['red','blue']

        self.main_box = toga.Box(style=Pack(direction=COLUMN))
        self.horizontal_box = toga.Box(style=Pack(direction=ROW, padding=5))
        self.horizontal_box2 = toga.Box(style=Pack(direction=ROW, padding=5))
        self.left_box  = toga.Box(style=Pack(direction=ROW, padding=5))
        self.right_box = toga.Box(style=Pack(direction=ROW, padding=5))


        self.column_names = ['Label', 'Color', 'SiO2', 'Na2O', 'K2O']

        button_open = toga.Button('Open', style=Pack(flex=1), on_press=self.open_data)
        # button_load = toga.Button('Load', style=Pack(flex=1), on_press=self.load_cord)
        button_plot = toga.Button('Plot', style=Pack(flex=1), on_press=self.plot_data)
        button_save = toga.Button('Save', style=Pack(flex=1), on_press=self.save_plot)
        
        button_clear= toga.Button('Clear', style=Pack(flex=1), on_press=self.clear_data)

        self.table_view = toga.Table(headings=['Data will be shown here'], style=Pack(flex=1, alignment='center', text_align='center', width=250, height=450))
        self.chart = toga_chart.Chart(style=Pack(flex=1, width=600, height=450), on_draw=self.draw_chart)
        self.label_status = toga.Label('Ready', style=Pack(padding=5))
        
        self.horizontal_box.add(button_open)
        self.horizontal_box.add(button_clear)
        # self.horizontal_box.add(button_load)
        self.horizontal_box.add(button_plot)
        self.horizontal_box.add(button_save)
        self.left_box.add(self.table_view)
        self.right_box.add(self.chart)
        self.horizontal_box2.add(self.left_box)
        self.horizontal_box2.add(self.right_box)
        self.main_box.add(self.horizontal_box)
        self.main_box.add(self.horizontal_box2)
        self.main_box.add(self.label_status)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
    
    async def open_data(self, widget):
        try:
            fname = await self.main_window.open_file_dialog(
                "Open data file", file_types=["csv", "xls", "xlsx"]
            )
            print(type(fname),fname.__str__())
            if fname is not None:
                self.label_status.text = f"File to open: {fname}"
                if ('csv' in fname.__str__()):
                    df = pd.read_csv(fname)
                else:
                    df = pd.read_excel(fname)
                
                self.data =  df[[col for col in df.columns if any(name in col for name in self.column_names)]]
                self.left_box.remove(self.table_view)
                self.table_view = toga.Table(headings=self.column_names, style=Pack(flex=1, alignment='center', text_align='center', width=250, height=450))
                self.left_box.add(self.table_view)    
                self.table_view.data = self.data.values.tolist()
                self.raw_df = df
                
                self.label_status.text = "Data file opened!"
                

            else:
                self.label_status.text = "No data file selected!"
        except ValueError:
            self.label_status.text = "Open data file dialog was canceled"
    
    def clear_data(self, widget):
        self.x_list = [0,0]
        self.y_list = [1,1]
        self.label_list =['test1','test2']
        self.color_list = ['red','blue']
        self.left_box.remove(self.table_view)
        self.table_view = toga.Table(headings=['Data will be shown here'], style=Pack(flex=1, alignment='center', text_align='center', width=250, height=450))
        self.left_box.add(self.table_view)
        
        self.right_box.remove(self.chart)
        self.chart = toga_chart.Chart(style=Pack(flex=1, width=600, height=450), on_draw=self.draw_chart)        
        self.right_box.add(self.chart)
        
        self.label_status = toga.Label('Ready', style=Pack(padding=5))

    
    def plot_data(self, widget):        
        self.ax = self.fig.add_subplot(1, 1, 1)
        # Replace non-numeric characters outside the first row and first column and Label, Color, Marker, Size, Width, Style, Alpha with 0
        cols_to_exclude = ['Label', 'Color', 'Marker', 'Size', 'Width', 'Style', 'Alpha']
        cols_to_include = self.raw_df.columns.difference(cols_to_exclude)
        self.raw_df[cols_to_include] = self.raw_df[cols_to_include].apply(pd.to_numeric, errors='coerce').fillna(0)

        # 计算'Na2O(wt%)'和'K2O(wt%)'的和
        # Calculate the sum of 'Na2O(wt%)' and 'K2O(wt%)'
        self.raw_df['Na2O(wt%) + K2O(wt%)'] = self.raw_df['Na2O(wt%)'] + self.raw_df['K2O(wt%)']

        elements = [('SiO2(wt%)', 'Na2O(wt%) + K2O(wt%)')]
        
        # 绘制每个元素对
        # Plot each element pair
        for i, (x, y) in enumerate(elements):
            for label, group_df in self.raw_df.groupby('Label'):
                self.ax.scatter(group_df[x], group_df[y], c=group_df['Color'], marker=group_df['Marker'].iloc[0], s=group_df['Size'], alpha=group_df['Alpha'], label=label)
            self.ax.set_xlabel(x, fontsize=9)
            self.ax.set_ylabel(y, fontsize=9)
            self.ax.tick_params(axis='both', labelsize=9)
            self.ax.legend(fontsize=9)

        # 绘制TAS图解边界线条
        # Draw TAS diagram boundary lines
        for line in self.cord['coords'].values():
            x_coords = [point[0] for point in line]
            y_coords = [point[1] for point in line]
            self.ax.plot(x_coords, y_coords, color='black', linewidth=0.3)

        # 在TAS图解中添加岩石种类标签
        # Add rock type labels in TAS diagram
        for label, coords in self.cord['coords'].items():
            x_coords = [point[0] for point in coords]
            y_coords = [point[1] for point in coords]
            x_center = sum(x_coords) / len(x_coords)
            y_center = sum(y_coords) / len(y_coords)
            self.ax.text(x_center, y_center, label, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.3), fontsize=9)

        self.ax.set_xlabel(r"$SiO2$", fontsize=9)
        self.ax.set_ylabel(r"$Na2O+K2O$", fontsize=9)
        self.ax.set_title(r"Extended TAS Diagram", fontsize=9)
        self.ax.set_xlim(35,80)
        self.ax.set_ylim(0,17.647826086956513)
        self.chart._draw(figure=self.fig)
        self.label_status.text = "Data has been plotted"
        
    # def save_plot(self, widget):
    #     self.fig.savefig('result.svg')
    async def save_plot(self, widget):
        fname = "result.svg"
        try:
            save_path = await self.main_window.save_file_dialog(
                "Save the Plot",
                suggested_filename=fname,
            )
            if save_path is not None:
                self.label_status.text = f"File saved as: {save_path}"
                if str(save_path).lower().endswith('.png'):
                    self.fig.savefig(save_path, dpi=600, format='png')
                elif str(save_path).lower().endswith('.jpg'):
                    self.fig.savefig(save_path, dpi=600, format='jpeg')
                elif str(save_path).lower().endswith('.svg'):
                    self.fig.savefig(save_path, format='svg')
                else:
                    self.label_status.text = "Unsupported file type"

        except ValueError:
            self.label_status.text = "Save file dialog was canceled"

    def draw_chart(self, chart, figure, *args, **kwargs):

        self.fig = figure       
        

        self.fig.tight_layout()
        


def main():
    return TAS('TAS', 'geopytool.com.tas')


if __name__ == '__main__':
    # 获取当前文件的绝对路径
    file_path = os.path.abspath(__file__)
    # 获取当前文件所在目录的路径
    dir_path = os.path.dirname(file_path)
    # 更改当前工作目录
    os.chdir(dir_path)
    main().main_loop()