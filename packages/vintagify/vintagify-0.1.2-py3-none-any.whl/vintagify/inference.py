#inference
import torch
from torchvision.utils import save_image
import matplotlib.pyplot as plt
import torchvision.transforms as T
import os
from .generator import ResnetGenerator
from .preprocess import preprocess #将测试的图像同样预处理完才能给模型
from PIL import Image

def inference_image(image_path,model_path,output_path,direction="A2B",image_size=512):
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Check image size before preprocessing
    with Image.open(image_path) as img:
        if img.size[0] < 500 or img.size[1] < 500:
            raise ValueError(f"❌ Input image is too small: {img.size}. Minimum size is 500x500.")

    G=ResnetGenerator().to(device)
    G.load_state_dict(torch.load(model_path,map_location=device))
    G.eval()

    image_tensor=preprocess(image_path,image_size=image_size).to(device)

    with torch.no_grad():
        fake_image=G(image_tensor)

    # Denormalize: [-1,1] --> [0,1], because Normalize was applied during training
    fake_image=(fake_image+1.0)/2.0
    
    # Output image
    output_image=T.ToPILImage()(fake_image.squeeze(0)) # Convert to PIL image
    plt.imshow(output_image) # Display the image
    plt.axis("off") # Turn off axes
    plt.show() # Actually render the window

    # Create output directory and save
    os.makedirs(os.path.dirname(output_path),exist_ok=True)
    save_image(fake_image,output_path)
    print(f"Successfully saved the image to {output_path}")






