#batch_preprocess.py, convert to .pt
import os
from pathlib import Path
import torch
from preprocess import preprocess

def batch_preprocess(input_dir, output_dir, image_size=512):
    """
    Batch read images from input_dir, preprocess them, and save each image as a separate .pt file.

    Args:
        input_dir (str): Directory path containing input images
        output_dir (str): Directory path to save tensor files
        image_size (int): Target image size (default is 512)
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    assert input_dir.exists(), f"❌ Input path does not exist: {input_dir}"
    output_dir.mkdir(parents=True, exist_ok=True)

    supported_exts = {".png", ".jpg", ".jpeg", ".webp"}

    count = 0
    for file in sorted(input_dir.iterdir()):
        if file.suffix.lower() in supported_exts:
            try:
                tensor = preprocess(str(file), image_size=image_size)  # [1, 3, H, W]
                single_tensor = tensor.squeeze(0)  # Remove batch dimension → [3, H, W]
                out_file = output_dir / f"{count:04d}.pt"
                torch.save(single_tensor, out_file)
                print(f"✅ Saved: {out_file.name}")
                count += 1
            except Exception as e:
                print(f"❌ Error processing {file.name}: {e}")

    if count == 0:
        print("⚠️ No images were successfully processed")
    else:
        print(f"\n🎉 Saved {count} images as individual .pt files")
