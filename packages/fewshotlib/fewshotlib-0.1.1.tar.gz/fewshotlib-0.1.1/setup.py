from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fewshotlib",
    version="0.1.1",
    author="Rohit Gomes",
    author_email="gomesrohit92@gmail.com",
    description="A flexible few-shot classifier toolkit.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["fewshotlib"]),
    install_requires=[
        "torch>=1.10.0",
        "torchvision>=0.11.0",
        "Pillow",
    ],
    python_requires=">=3.8",
)