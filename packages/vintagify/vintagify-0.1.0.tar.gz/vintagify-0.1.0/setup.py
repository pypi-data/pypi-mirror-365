from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vintagify",
    version="0.1.0",
    description="A simple CycleGAN-based image translation package (modern <-> vintage)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yusong Zhao, Fangyi Wang",
    author_email="yusongzhao@link.cuhk.edu.cn, fangyiwang@link.cuhk.edu.cn",
    license="MIT",
    license_files=["LICENSE"],
    packages=find_packages(include=["vintagify", "vintagify.*"]),
    include_package_data=True,
    package_data={"vintagify": ["resources/*.pth"]},
    install_requires=[
        "torch",
        "torchvision",
        "Pillow",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Image Recognition"
    ],
    python_requires=">=3.7",
)
