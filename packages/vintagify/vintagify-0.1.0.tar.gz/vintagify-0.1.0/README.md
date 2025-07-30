# vintagify

A simple Python package for image-to-image translation using  CycleGAN model.  
Easily convert modern photos into vintage-style images with just one function call.

---

## ✨ Features

- 🎨 Translate modern images to vintage style using pretrained model.
- 🔁 Based on CycleGAN with unpaired training capability.
- 📦 Packaged with built-in pretrained model – no extra downloads required.
- 🔧 Simple API, minimal setup.

---

## 📦 Installation

Install via pip:

```bash
pip install vintagify
```
---

## 🚀 Quick Start

```python
from vintagify import translate_image

translate_image("photo.jpg", "photo_vintage.jpg")
```

---

## 📐 Input Requirements

- Input image should be at least **500×500** pixels.
- The image will be automatically center-cropped and resized to 512×512.

---

## 📝 License

MIT License © 2025 beingbetter11643



