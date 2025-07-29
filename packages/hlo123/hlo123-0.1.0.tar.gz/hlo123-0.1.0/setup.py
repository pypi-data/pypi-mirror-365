# setup.py
from setuptools import setup, find_packages

setup(
    name="hlo123",
    version="0.1.0",
    description="A sample Python package named hlo123",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/hlo123",  # Update if you have a repo
    packages=find_packages(),
    install_requires=[],   # Add dependencies here as needed
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
