from PIL import Image, ImageFilter
import matplotlib.pyplot as plt
import os
import pywt
# Get the current directory
current_directory = os.getcwd()

# Change the current directory to the file's directory
file_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_directory)

# Load the images
image1 = Image.open("source1.jpg")
image2 = Image.open("source2.jpg")
image3 = Image.open("source3.jpg")

# Convert the images to grayscale
image1_gray = image1.convert("L")
image2_gray = image2.convert("L")
image3_gray = image3.convert("L")

# Perform wavelet analysis on the images
coeffs1 = pywt.dwt2(image1_gray, "haar")
coeffs2 = pywt.dwt2(image2_gray, "haar")
coeffs3 = pywt.dwt2(image3_gray, "haar")

# Extract the high frequency and low frequency components
cA1, (cH1, cV1, cD1) = coeffs1
cA2, (cH2, cV2, cD2) = coeffs2
cA3, (cH3, cV3, cD3) = coeffs3

# Calculate the contrast between high frequency and low frequency components
contrast1 = cH1.std() + cV1.std() + cD1.std()
contrast2 = cH2.std() + cV2.std() + cD2.std()
contrast3 = cH3.std() + cV3.std() + cD3.std()

# Plot the images and their differences
fig, axs = plt.subplots(2, 4, figsize=(16, 8))

# Plot image1
axs[0, 0].imshow(image1_gray, cmap='gray')
axs[0, 0].set_title('Image 1')

# Plot image2
axs[0, 1].imshow(image2_gray, cmap='gray')
axs[0, 1].set_title('Image 2')

# Plot image3
axs[0, 2].imshow(image3_gray, cmap='gray')
axs[0, 2].set_title('Image 3')

# Plot cA1
axs[0, 3].imshow(cA1, cmap='gray')
axs[0, 3].set_title('cA1')

# Plot cA2
axs[1, 0].imshow(cA2, cmap='gray')
axs[1, 0].set_title('cA2')

# Plot cA3
axs[1, 1].imshow(cA3, cmap='gray')
axs[1, 1].set_title('cA3')

# Plot the difference between cA1 and cA2
diff_cA1_cA2 = cA1 - cA2
axs[1, 2].imshow(diff_cA1_cA2, cmap='gray')
axs[1, 2].set_title('Difference (cA1 - cA2)')

# Plot the difference between cA1 and cA3
diff_cA1_cA3 = cA1 - cA3
axs[1, 3].imshow(diff_cA1_cA3, cmap='gray')
axs[1, 3].set_title('Difference (cA1 - cA3)')

# Remove the axis labels
for ax in axs.flat:
    ax.axis('off')

# Adjust the spacing between subplots
plt.tight_layout()

# Show the plot
plt.show()

# Print the contrast values
print("Contrast of source1.jpg:", contrast1)
print("Contrast of source2.jpg:", contrast2)
print("Contrast of source3.jpg:", contrast3)

# Plot the images and their differences
fig, axs = plt.subplots(2, 3, figsize=(12, 8))

# Plot image1
axs[0, 0].imshow(image1_gray, cmap='gray')
axs[0, 0].set_title('Image 1')

# Plot image2
axs[0, 1].imshow(image2_gray, cmap='gray')
axs[0, 1].set_title('Image 2')

# Plot cA1
axs[0, 2].imshow(cA1, cmap='gray')
axs[0, 2].set_title('cA1')

# Plot cA2
axs[1, 0].imshow(cA2, cmap='gray')
axs[1, 0].set_title('cA2')

# Plot the difference between cA1 and cA2
diff_cA = cA1 - cA2
axs[1, 1].imshow(diff_cA, cmap='gray')
axs[1, 1].set_title('Difference (cA1 - cA2)')

# Plot the difference between cH1, cV1, cD1 and cH2, cV2, cD2
diff_cH = cH1 - cH2
diff_cV = cV1 - cV2
diff_cD = cD1 - cD2
axs[1, 2].imshow(diff_cH, cmap='gray')
axs[1, 2].set_title('Difference (cH1 - cH2), (cV1 - cV2), (cD1 - cD2)')

# Remove the axis labels
for ax in axs.flat:
    ax.axis('off')

# Adjust the spacing between subplots
plt.tight_layout()

# Show the plot
plt.show()

# Print the contrast values
print("Contrast of source1.jpg:", contrast1)
print("Contrast of source2.jpg:", contrast2)

