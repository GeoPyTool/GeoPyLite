from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity
from scipy.spatial import distance
from scipy.stats import norm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def Compare(df_train= pd.DataFrame(),df_test= pd.DataFrame(), x='x',y='x'):
    # Extract x_train and y_train from df_train
    x_train = df_train[x].values
    y_train = df_train[y].values

    # Combine x_train and y_train into a 2D array
    data_train = np.column_stack((x_train, y_train))

    # Use KMeans to find the cluster center
    kmeans = KMeans(n_clusters=1).fit(data_train)

    # The cluster center is stored in the cluster_centers_ attribute
    center_x, center_y = kmeans.cluster_centers_[0]

    print(f"Cluster center is at ({center_x:.5f}, {center_y:.5f})")

    # Fit a Kernel Density Estimation model
    kde = KernelDensity(kernel='gaussian').fit(data_train)
    # kde = KernelDensity(kernel='epanechnikov').fit(data_train)
    # kde = KernelDensity(kernel='exponential').fit(data_train)
    # kde = KernelDensity(kernel='linear').fit(data_train)

    # Calculate the log probability density for each point in the training set
    log_prob_density = kde.score_samples(data_train)

    # Convert the log probability density to the original probability density
    prob_density = np.exp(log_prob_density)

    # Extract x_test and y_test from df_test
    x_test = df_test[x].values
    y_test = df_test[y].values

    # Calculate the probability for each test point
    test_probabilities = []

    for x, y in zip(x_test, y_test):
        # Calculate the probability density for each test point
        test_densities = kde.score_samples(np.c_[x_test, y_test])

        # Convert densities to probabilities
        test_probabilities = np.exp(test_densities)

        # Normalize probabilities
        test_probabilities /= np.max(test_probabilities)

        # # Print probabilities
        # for i, prob in enumerate(test_probabilities):
        #     print(f"Probability for test point {i+1} ({x_test[i]}, {y_test[i]}) is: {prob}")

    
    return(test_probabilities)


# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件的目录
current_directory = os.path.dirname(current_file_path)
# 改变当前工作目录
os.chdir(current_directory)


n = 10


df_mugearite = pd.read_pickle('df_mugearite.pkl')



df_mugearite['SIO2_wt_calibred']
df_mugearite['ALL_Alkaline_wt_calibred']
# print(df_mugearite)

# Generate testing data
x_test = np.array([45.76428218, 31.81390091, 55.28563359, 60.96200656, 70.43711105,
       40.88503457])
y_test = np.array([13.76185634, 10.33199649, 8.79003757, 14.88086825, 9.92049699,
       2.49193062])

x_test = np.linspace(40, 70, 2*n)
y_test = np.linspace(2, 12, 6*n)

x_test_mesh, y_test_mesh = np.meshgrid(x_test, y_test)
test_points = np.c_[x_test_mesh.ravel(), y_test_mesh.ravel()]
df_test = pd.DataFrame(test_points, columns=['SIO2_wt_calibred', 'ALL_Alkaline_wt_calibred'])
# df_test = pd.DataFrame({'x': x_test, 'y': y_test})


# Call the Compare function
target_probabilities = Compare(df_mugearite, df_test,'SIO2_wt_calibred', 'ALL_Alkaline_wt_calibred')

# Plot training data in blue
plt.scatter(df_mugearite['SIO2_wt_calibred'], df_mugearite['ALL_Alkaline_wt_calibred'], color='blue', label='Training data',edgecolors= None,alpha=0.3)


# Plot testing data in red
plt.scatter(df_test['SIO2_wt_calibred'], df_test['ALL_Alkaline_wt_calibred'], color='red', label='Testing data',edgecolors= None,alpha=target_probabilities)

# # Add probability labels to the test points
# for i, (x, y) in enumerate(zip(df_test['SIO2_wt_calibred'], df_test['ALL_Alkaline_wt_calibred'],)):
#     plt.text(x, y, f"{target_probabilities[i]:.2f}", ha='right')

# Add a legend
plt.legend()

# Show the plot
plt.show()