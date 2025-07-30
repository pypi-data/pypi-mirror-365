# api.py
from .inference import inference_image
import os

model_dir = os.path.join(os.path.dirname(__file__), "resources")
default_model_path = os.path.join(model_dir, "G_A2B_epoch33.pth")

def translate_image(input_path: str, output_path: str, model_path: str = None, image_size: int = 512, direction="A2B"):
    """
    High-level API to apply CycleGAN model to an image.

    Args:
        input_path (str): Path to input image.
        output_path (str): Where to save the translated image.
        model_path (str, optional): Custom model path. If None, use built-in pretrained.
        image_size (int): Image size (default: 512).
        direction (str): "A2B" or "B2A".
    """
    if model_path is None:
        model_path = default_model_path

    inference_image(
        image_path=input_path,
        model_path=model_path,
        output_path=output_path,
        direction=direction,
        image_size=image_size
    )
