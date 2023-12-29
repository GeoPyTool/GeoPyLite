import os
import pandas as pd
import numpy as np
from sklearn import svm

# 列名列表
columns = ['Label', 'Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6', 'Data7', 'Data8', 'Data9', 'Data10', 'Data11']

# 创建一个空的数据表格
# df = pd.DataFrame(columns=columns)
# 获取当前文件的绝对路径
file_path = os.path.abspath(__file__)
# 获取当前文件所在目录的路径
dir_path = os.path.dirname(file_path)
# 更改当前工作目录
os.chdir(dir_path)
df = pd.read_csv('data.csv')

cols_to_exclude = ['Label', 'Color', 'Marker', 'Size', 'Width', 'Style', 'Alpha', 'Age(ma)']

cols_to_include = df.columns.difference(cols_to_exclude)
new_df = df[cols_to_include] = df[cols_to_include].apply(pd.to_numeric, errors='coerce').fillna(0)
# 使用numpy读取数据
major_df = new_df.filter(regex='wt%')
ppm_df = new_df.filter(regex='ppm')
ppt_df = new_df.filter(regex='ppt')



print(major_df.shape, ppm_df.shape)
print(major_df, ppm_df)

data = np.array(major_df.iloc[:, 1:].values)
data_matrix = np.matrix(data)

# labels = np.array(df['Label'])

label_encoder = np.unique(df['Label'], return_inverse=True)[1]
labels = label_encoder.astype(np.int32)

def svm_train(data, labels):
    # Initialize SVM parameters
    learning_rate = 0.01
    num_iterations = 1000
    num_samples, num_features = data.shape
    weights = np.zeros(num_features)
    bias = 0

    # Training loop
    for _ in range(num_iterations):
        # Compute SVM predictions
        scores = np.dot(data, weights) + bias
        predictions = np.sign(scores)

        # Update weights and bias
        gradient = np.dot(data.T, labels - predictions)
        weights += learning_rate * gradient
        bias += learning_rate * np.sum(labels - predictions)

    return weights, bias

# Train SVM using major_df as data and labels as labels
weights, bias = svm_train(data, labels)
print(weights, bias)

# Generate test data similar to major_df
test_data = np.random.rand(data.shape[0], data.shape[1])
test_data = test_data / np.sum(test_data, axis=1, keepdims=True) * 100

# Predict the labels of test data using trained SVM model
test_scores = np.dot(test_data, weights) + bias
test_predictions = np.sign(test_scores)
label_encoder_inverse = np.unique(df['Label'])[test_predictions.astype(int)]
# print(label_encoder_inverse)

# Combine label_encoder_inverse and test_data into a new DataFrame
combined_df = pd.DataFrame({'Label': label_encoder_inverse})
combined_df = pd.concat([combined_df, pd.DataFrame(test_data, columns=major_df.columns[1:])], axis=1)
print(combined_df)




