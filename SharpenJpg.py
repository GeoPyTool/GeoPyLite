from PIL import Image, ImageFilter
import os
import torch
from torchvision.models import vgg19
from torch.nn import functional as F

# Get the current directory
current_directory = os.getcwd()

# Change the current directory to the file's directory
file_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_directory)

# Load the image
filename = "source.jpg"
image = Image.open(filename)

# Enhance the image quality
enhanced_image = image.filter(ImageFilter.SHARPEN)

# Increase the resolution
new_size = (image.size[0] * 2, image.size[1] * 2)
resized_image = enhanced_image.resize(new_size)

# Save the enhanced and resized image
resized_image.save("enhanced_"+filename)

# Change the current directory back to the original directory
os.chdir(current_directory)


import torchvision.transforms as transforms
# Define the super-resolution model
model = torch.hub.load('sukkritsharmaofficial/SuperResGAN', 'rrdb_net', pretrained=True)

# Set the device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Preprocess the image
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
input_image = preprocess(resized_image).unsqueeze(0).to(device)

# Upscale the image using the super-resolution model
with torch.no_grad():
    output_image = model(input_image).clamp(0, 1)

# Convert the output image to PIL format
output_image = output_image.squeeze(0).cpu()
output_image = transforms.ToPILImage()(output_image)

# Save the enhanced image
output_image.save("enhanced_sr_"+filename)

# Compare the original, enhanced, and super-resolved images
image.show()
enhanced_image.show()
output_image.show()



