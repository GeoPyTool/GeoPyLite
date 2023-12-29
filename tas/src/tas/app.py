"""
An expanded TAS illustration that enhances the readability and degree of quantification of the results.
"""
import toga, os, math, platform, toga_chart, json, urllib.request
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import numpy as np 
import pandas as pd
import scipy as sp 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path


class TAS(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.data = pd.DataFrame()
        self.cord = {}
        self.x_list = [0,0]
        self.y_list = [1,1]
        self.label_list =['test1','test2']
        self.color_list = ['red','blue']

        main_box = toga.Box(style=Pack(direction=COLUMN))
        horizontal_box = toga.Box(style=Pack(direction=ROW, padding=5))

        self.column_names = ['Label', 'Color', 'SiO2', 'Na2O', 'K2O']

        button_open = toga.Button('Open', style=Pack(flex=1), on_press=self.open_data)
        button_load = toga.Button('Load', style=Pack(flex=1), on_press=self.load_cord)
        button_plot = toga.Button('Plot', style=Pack(flex=1), on_press=self.plot_data)
        button_save = toga.Button('Save', style=Pack(flex=1), on_press=self.save_plot)
        self.table_view = toga.Table(headings= self.column_names, style=Pack(flex=1,alignment='center',text_align='center'))
        self.chart = toga_chart.Chart(style=Pack(flex=1), on_draw=self.draw_chart)
        self.label_status = toga.Label('Ready', style=Pack(padding=5))
        
        horizontal_box.add(button_open)
        horizontal_box.add(button_load)
        horizontal_box.add(button_plot)
        horizontal_box.add(button_save)
        main_box.add(horizontal_box)
        main_box.add(self.table_view)
        main_box.add(self.chart)
        main_box.add(self.label_status)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(300, 600))
        self.main_window.content = main_box
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
                self.table_view.data = self.data.values.tolist()
                
                self.label_status.text = "Data file opened!"
                

            else:
                self.label_status.text = "No data file selected!"
        except ValueError:
            self.label_status.text = "Open data file dialog was canceled"

    
    async def load_cord(self, widget):
        try:
            fname = await self.main_window.open_file_dialog(
                "Load cord file", file_types=["json"]
            )
            print(type(fname),fname.__str__())
            if fname is not None:
                self.label_status.text = f"File to open: {fname}"

                with open(fname) as file:
                    self.cord = json.load(file)         
                self.label_status.text = "Cord file loaded!"
            else:
                self.label_status.text = "No cord file selected!"
        except ValueError:
            self.label_status.text = "Load cord file dialog was canceled"
                    
            # 读取TAS图解边界数据
            # Read TAS diagram boundary data
            with urllib.request.urlopen('https://raw.githubusercontent.com/GeoPyTool/GeochemDataFormat/main/Known%20Coords/TAS.json') as url:
                self.cord = json.loads(url.read().decode())

    def plot_data(self, widget):

        
        self.ax = self.fig.add_subplot(1, 1, 1)




        # 绘制TAS图解边界线条
        # Draw TAS diagram boundary lines
        for line in self.cord['coords'].values():
            x_coords = [point[0] for point in line]
            y_coords = [point[1] for point in line]
            self.ax.plot(x_coords, y_coords, color='black')

        # 在TAS图解中添加岩石种类标签
        # Add rock type labels in TAS diagram
        for label, coords in self.cord['coords'].items():
            x_coords = [point[0] for point in coords]
            y_coords = [point[1] for point in coords]
            x_center = sum(x_coords) / len(x_coords)
            y_center = sum(y_coords) / len(y_coords)
            self.ax.text(x_center, y_center, label, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.3))


        num_bins = 50
        MU = 100  # mean of distribution
        SIGMA = 15  # standard deviation of distribution
        x = MU + SIGMA * np.random.randn(437)
        n, bins, patches = self.ax.hist(x, num_bins, density=1)

        # add a 'best fit' line
        y = (1 / (np.sqrt(2 * np.pi) * SIGMA)) * np.exp(
            -0.5 * (1 / SIGMA * (bins - MU)) ** 2
        )



        self.ax.plot(bins, y, "--")

        self.ax.set_xlabel(r"$SiO2$")
        self.ax.set_ylabel(r"$Na2O+K2O$")
        self.ax.set_title(r"Extended TAS Diagram")
        self.ax.set_xlim(38,80)
        self.ax.set_ylim(-0.5,18)
        self.chart._draw(figure=self.fig)
        
    def save_plot(self, widget):
        self.fig.savefig('result.svg')

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