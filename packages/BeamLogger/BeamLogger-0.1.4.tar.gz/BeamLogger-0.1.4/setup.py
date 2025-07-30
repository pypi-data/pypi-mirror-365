from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="BeamLogger",
    version="0.1.4",  # Updated version
    author="Bhaskar",
    author_email="toolscord.supp@gmail.com",
    description="A stylish and colorful Python logging module with customizable console output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bhaskarsaikia-17/BeamLogger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "colorama",
        "pystyle",
    ],
)

# Crafted With <3 By Bhaskar 