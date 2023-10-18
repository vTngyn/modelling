import os
from torchvision import transforms
from PIL import Image
import torch

# Define a function to extract labels from filenames
def extract_label_from_filename(filename):
    # Assuming the label is the first part of the filename before an underscore
    label = filename.split('_')[0]
    return label

# Directory containing the images
image_dir = 'path/to/your/image/directory'

# List to store image data and corresponding labels
data = []
labels = []

# Iterate through the image directory
for filename in os.listdir(image_dir):
    # Load image
    image_path = os.path.join(image_dir, filename)
    image = Image.open(image_path).convert('RGB')  # Convert to RGB if needed

    # Preprocess image (resize, normalize, etc.)
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),  # Adjust size as needed
        transforms.ToTensor(),
    ])
    image = preprocess(image)

    # Extract label from filename
    label = extract_label_from_filename(filename)

    # Append the preprocessed image and label
    data.append(image)
    labels.append(label)

# Convert the list of images and labels to tensors
data = torch.stack(data)
labels = torch.tensor([int(label) for label in labels])  # Convert labels to integers if needed

# Print the shape of the data and labels tensors
print('Data shape:', data.shape)
print('Labels shape:', labels.shape)
