"""
An expanded TAS illustration that enhances the readability and degree of quantification of the results.
"""
import toga, os, math, platform
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
        self.label_status = toga.Label('Ready', style=Pack(padding=5))
        
        horizontal_box.add(button_open)
        horizontal_box.add(button_plot)
        main_box.add(horizontal_box)
        main_box.add(self.table_view)
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
                
                self.label_status.text = "File opened!"
            else:
                self.label_status.text = "No file selected!"
        except ValueError:
            self.label_status.text = "Open file dialog was canceled"

    def plot_data(self, widget):
        pass



def main():
    return TAS('TAS', 'geopytool.com.tas')


if __name__ == '__main__':
    main().main_loop()