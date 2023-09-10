import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read data file
data = 'https://raw.githubusercontent.com/GeoPyTool/GeoPyTool/master/DataFileSamples/Geochemistry.csv'
# Change the data here to the path of your modified local data file
df = pd.read_csv(data)

# Replace non-numeric characters outside the first row and first column and Label, Color, Marker, Size, Width, Style, Alpha with 0
cols_to_exclude = ['Label', 'Color', 'Marker', 'Size', 'Width', 'Style', 'Alpha']
cols_to_include = df.columns.difference(cols_to_exclude)
df[cols_to_include] = df[cols_to_include].apply(pd.to_numeric, errors='coerce').fillna(0)

# Define element pairs to be plotted
elements = [('SiO2(wt%)', 'TiO2(wt%)'), ('SiO2(wt%)', 'Al2O3(wt%)'), ('SiO2(wt%)', 'Fe2O3(wt%)'), ('SiO2(wt%)', 'MnO(wt%)'), ('SiO2(wt%)', 'MgO(wt%)'), ('SiO2(wt%)', 'CaO(wt%)'), ('SiO2(wt%)', 'Na2O(wt%)'), ('SiO2(wt%)', 'K2O(wt%)'), ('SiO2(wt%)', 'P2O5(wt%)')]

# Create figure
fig, axs = plt.subplots(3, 3, figsize=(15, 15))

# Plot each element pair
for i, (x, y) in enumerate(elements):
    ax = axs[i // 3, i % 3]
    for label, group_df in df.groupby('Label'):
        ax.scatter(group_df[x], group_df[y], c=group_df['Color'], marker=group_df['Marker'].iloc[0], s=group_df['Size'], alpha=group_df['Alpha'], label=label)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.legend()
# Show figure
plt.show()
