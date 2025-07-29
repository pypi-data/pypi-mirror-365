# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="fstrent_charts",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "colorama",
    ],
    author="FSTrent",
    author_email="wrmartel3@gmail.com",
    description="Color Chart options for terminal output",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wrm3/fstrent_charts",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 