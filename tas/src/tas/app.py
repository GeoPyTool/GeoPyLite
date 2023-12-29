"""
An expanded TAS illustration that enhances the readability and degree of quantification of the results.
"""
import toga, os, math, platform, toga_chart
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import numpy as np 
import pandas as pd
import scipy as sp 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class TAS(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.data = pd.DataFrame()
        main_box = toga.Box(style=Pack(direction=COLUMN))
        horizontal_box = toga.Box(style=Pack(direction=ROW, padding=5))

        self.column_names = ['Label', 'Color', 'SiO2', 'Na2O', 'K2O']

        button_open = toga.Button('Open', style=Pack(flex=1), on_press=self.open_data)
        button_plot = toga.Button('Plot', style=Pack(flex=1), on_press=self.plot_data)
        self.table_view = toga.Table(headings= self.column_names, style=Pack(flex=1,alignment='center',text_align='center'))
        self.chart = toga_chart.Chart(style=Pack(flex=1), on_draw=self.draw_chart)
        self.label_status = toga.Label('Ready', style=Pack(padding=5))
        
        horizontal_box.add(button_open)
        horizontal_box.add(button_plot)
        main_box.add(horizontal_box)
        main_box.add(self.table_view)
        main_box.add(self.chart)
        main_box.add(self.label_status)

        self.main_window = toga.MainWindow(title=self.formal_name)
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

    def plot_data(self, widget):
        self.fig.savefig('result.svg')

    def draw_chart(self, chart, figure, *args, **kwargs):
        num_bins = 50
        MU = 100  # mean of distribution
        SIGMA = 15  # standard deviation of distribution
        x = MU + SIGMA * np.random.randn(437)
        # Add a subplot that is a histogram of the data,
        # using the normal matplotlib API
        self.fig = figure
        ax = self.fig.add_subplot(1, 1, 1)
        n, bins, patches = ax.hist(x, num_bins, density=1)

        # add a 'best fit' line
        y = (1 / (np.sqrt(2 * np.pi) * SIGMA)) * np.exp(
            -0.5 * (1 / SIGMA * (bins - MU)) ** 2
        )
        ax.plot(bins, y, "--")

        ax.set_xlabel("Value")
        ax.set_ylabel("Probability density")
        ax.set_title(r"Histogram: $\mu=100$, $\sigma=15$")

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