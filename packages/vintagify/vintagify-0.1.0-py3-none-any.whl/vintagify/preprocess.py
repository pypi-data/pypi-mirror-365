#prprocess.py
from PIL import Image
from torchvision import transforms
import torch

def preprocess(image_path, image_size=512):
    """
    Load and preprocess an input image for CycleGAN style transfer.

    Args:
        image_path (str): Path to the input image (supports PNG, JPG, etc).
        image_size (int): Target output image size, default is 512.

    Returns:
        torch.Tensor: A normalized tensor of shape [1, 3, H, W] with pixel values in [-1, 1].
    """
    # Load image and convert to RGB (removes alpha channel or grayscale)
    image = Image.open(image_path).convert("RGB")

    # Define transformation pipeline: Resize → CenterCrop → ToTensor → Normalize
    transform = transforms.Compose([
        transforms.Resize(image_size + 30),  # Add margin for center crop
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),              # Convert to [C, H, W] with range [0,1]
        transforms.Normalize((0.5, 0.5, 0.5),  # Normalize to [-1,1]
                             (0.5, 0.5, 0.5))
    ])

    # Apply transformation and add batch dimension [1, 3, H, W]
    tensor = transform(image).unsqueeze(0)
    return tensor
