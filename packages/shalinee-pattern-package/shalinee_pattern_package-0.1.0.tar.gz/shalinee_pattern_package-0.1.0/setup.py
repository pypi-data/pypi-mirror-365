# setup.py

from setuptools import setup, find_packages

setup(
    name="Shalinee_pattern_package",
    version="0.1.0",
    author="Shalinee",
    author_email="Shalinee.priya31@gmail.com",
    description="This package is for printing patterns",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Shalinee-Priya/pattern",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
