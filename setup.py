#!/usr/bin/env python3

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="goit",
    version="0.1.2",
    author="Mike 'Fuzzy' Partin",
    author_email="fuzzy@thwap.org",
    description="A TUI wrapping many github cli operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuzzy/goit",
    packages=find_packages(include=["goitlib", "goit.*"]),
    py_modules=["goit"],
    entry_points={
        "console_scripts": [
            "goit=goit:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rich",
        "textual",
    ],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
