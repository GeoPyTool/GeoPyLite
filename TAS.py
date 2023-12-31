import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import urllib.request
from matplotlib.path import Path

# 读取数据文件
# Read data file
url = 'https://raw.githubusercontent.com/GeoPyTool/GeoPyTool/master/DataFileSamples/Geochemistry.csv'
df = pd.read_csv(url)

# 将除第一行和第一列以及Label,Color,Marker,Size,Width,Style,Alpha之外的非数值字符替换为0
# Replace non-numeric characters outside the first row and first column and Label, Color, Marker, Size, Width, Style, Alpha with 0
cols_to_exclude = ['Label', 'Color', 'Marker', 'Size', 'Width', 'Style', 'Alpha']
cols_to_include = df.columns.difference(cols_to_exclude)
df[cols_to_include] = df[cols_to_include].apply(pd.to_numeric, errors='coerce').fillna(0)

# 计算'Na2O(wt%)'和'K2O(wt%)'的和
# Calculate the sum of 'Na2O(wt%)' and 'K2O(wt%)'
df['Na2O(wt%) + K2O(wt%)'] = df['Na2O(wt%)'] + df['K2O(wt%)']

# 定义要绘制的元素对
# Define element pairs to be plotted
elements = [('SiO2(wt%)', 'Na2O(wt%) + K2O(wt%)')]

# 创建图形
# Create figure
fig, axs = plt.subplots(figsize=(10, 10))

# 绘制每个元素对
# Plot each element pair
for i, (x, y) in enumerate(elements):
    for label, group_df in df.groupby('Label'):
        axs.scatter(group_df[x], group_df[y], c=group_df['Color'], marker=group_df['Marker'].iloc[0], s=group_df['Size'], alpha=group_df['Alpha'], label=label)
    axs.set_xlabel(x)
    axs.set_ylabel(y)
    axs.legend()

# 读取TAS图解边界数据
# Read TAS diagram boundary data
with urllib.request.urlopen('https://raw.githubusercontent.com/GeoPyTool/GeochemDataFormat/main/Known%20Coords/TAS.json') as url:
    tas_data = json.loads(url.read().decode())

# 绘制TAS图解边界线条
# Draw TAS diagram boundary lines
for line in tas_data['coords'].values():
    x_coords = [point[0] for point in line]
    y_coords = [point[1] for point in line]
    axs.plot(x_coords, y_coords, color='black')

# 在TAS图解中添加岩石种类标签
# Add rock type labels in TAS diagram
for label, coords in tas_data['coords'].items():
    x_coords = [point[0] for point in coords]
    y_coords = [point[1] for point in coords]
    x_center = sum(x_coords) / len(x_coords)
    y_center = sum(y_coords) / len(y_coords)
    axs.text(x_center, y_center, label, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.3))

# 根据每个数据点在TAS图解中的位置添加分类结果
# Add classification results based on the position of each data point in the TAS diagram
x_col = 'SiO2(wt%)'
y_col = 'Na2O(wt%) + K2O(wt%)'
points = df[[x_col, y_col]].values
df['Classification'] = ''
for label, coords in tas_data['coords'].items():
    path = Path(coords)
    mask = path.contains_points(points)
    df.loc[mask, 'Classification'] = label

print(df)

# 获取当前 Python 文件所在目录
# Get the current directory of the Python file
current_dir = os.getcwd()

# 构造结果 CSV 文件的完整路径
# Construct the full path of the result CSV file
result_file_path = os.path.join(current_dir, 'Geochemistry_result.csv')

# 保存结果到CSV文件
# Save results to CSV file
df.to_csv('Geochemistry_result.csv', index=False)

# 显示图形
# Show figure
plt.show()
