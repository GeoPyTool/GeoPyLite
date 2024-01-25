from sklearn.cluster import KMeans
from sklearn.neighbors import KernelDensity
from scipy.spatial import distance
from scipy.stats import norm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def Compare(df_train, df_test):
    # Extract x_train and y_train from df_train
    x_train = df_train['x'].values
    y_train = df_train['y'].values

    # Combine x_train and y_train into a 2D array
    data_train = np.column_stack((x_train, y_train))

    # Use KMeans to find the cluster center
    kmeans = KMeans(n_clusters=1).fit(data_train)

    # The cluster center is stored in the cluster_centers_ attribute
    center_x, center_y = kmeans.cluster_centers_[0]

    print(f"Cluster center is at ({center_x:.5f}, {center_y:.5f})")

    # Fit a Kernel Density Estimation model
    kde = KernelDensity(kernel='gaussian').fit(data_train)

    # Calculate the log probability density for each point in the training set
    log_prob_density = kde.score_samples(data_train)

    # Convert the log probability density to the original probability density
    prob_density = np.exp(log_prob_density)

    # Calculate the weighted distance for each point in the training set
    weighted_distance = [distance.euclidean((center_x, center_y), (x, y)) * prob for x, y, prob in zip(x_train, y_train, prob_density)]

    # Calculate the maximum weighted distance
    max_weighted_distance = max(weighted_distance)

    # Extract x_test and y_test from df_test
    x_test = df_test['x'].values
    y_test = df_test['y'].values

    # Calculate the probability for each test point
    test_probabilities = []

    for x, y in zip(x_test, y_test):
        # Calculate the distance from the test point to the center
        test_distance = distance.euclidean((center_x, center_y), (x, y))

        # Calculate the distance for each point in the training set
        distances = [distance.euclidean((center_x, center_y), (x, y)) for x, y in zip(x_train, y_train)]

        # Calculate the maximum distance
        max_distance = max(distances)

        # Normalize the test distance to the range [0, 1]
        normalized_test_distance = test_distance / max_distance

        # Use a Gaussian function to calculate the probability of the test point
        test_probability = norm.pdf(normalized_test_distance, 0, 1)

        test_probabilities.append(test_probability)

        

    for i, prob in enumerate(test_probabilities):
        # print(f"Probability for test point {i+1} ({x_test[i]}, {y_test[i]}) is: {prob}")
        pass
    
    return(test_probabilities)




n = 64

# Generate training data
x_train = np.random.normal(45, 1, n)
y_train = np.random.normal(8, 1, n)
df_train = pd.DataFrame({'x': x_train, 'y': y_train})

# Generate testing data
x_test = np.array([45.76428218, 31.81390091, 55.28563359, 60.96200656, 70.43711105,
       40.88503457])
y_test = np.array([13.76185634, 10.33199649, 8.79003757, 14.88086825, 9.92049699,
       2.49193062])

x_test = np.linspace(35, 90, n)
y_test = np.linspace(0, 18, n)

x_test_mesh, y_test_mesh = np.meshgrid(x_test, y_test)
test_points = np.c_[x_test_mesh.ravel(), y_test_mesh.ravel()]
df_test = pd.DataFrame(test_points, columns=['x', 'y'])
# df_test = pd.DataFrame({'x': x_test, 'y': y_test})


# Call the Compare function
target_probabilities = Compare(df_train, df_test)

# Plot training data in blue
plt.scatter(df_train['x'], df_train['y'], color='blue', label='Training data')

# Plot testing data in red
plt.scatter(df_test['x'], df_test['y'], color='red', label='Testing data',edgecolors= None,alpha=target_probabilities)

# # Add probability labels to the test points
# for i, (x, y) in enumerate(zip(df_test['x'], df_test['y'])):
#     plt.text(x, y, f"{target_probabilities[i]:.2f}", ha='right')

# Add a legend
plt.legend()




# Show the plot
plt.show()