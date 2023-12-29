import pandas as pd
from pywebio import *
from pywebio.input import *
from pywebio.output import *
import matplotlib.pyplot as plt
def plot_data():
    # Get the file path from the user
    file_path = file_upload("Upload CSV or XLSX file")

    # Read the data from the file
    if file_path['name'].endswith('.csv'):
        data = pd.read_csv(file_path['content'])
    elif file_path['name'].endswith('.xlsx'):
        data = pd.read_excel(file_path['content'])
    else:
        put_text("Invalid file format. Please upload a CSV or XLSX file.")
        return

    # Plot and display the data
    plt.plot(data)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Data Plot')
    plt.grid(True)
    plt.show()

# Run the function
plot_data()
