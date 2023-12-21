from PIL import Image, ImageFilter
import os

# Get the current directory
current_directory = os.getcwd()

# Change the current directory to the file's directory
file_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_directory)

# Load the image
image = Image.open("source.jpg")

# Enhance the image quality
enhanced_image = image.filter(ImageFilter.SHARPEN)

# Increase the resolution
new_size = (image.size[0] * 2, image.size[1] * 2)
resized_image = enhanced_image.resize(new_size)

# Save the enhanced and resized image
resized_image.save("enhanced_image.jpg")

# Change the current directory back to the original directory
os.chdir(current_directory)


