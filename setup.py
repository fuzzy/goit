#!/usr/bin/env python3

from setuptools import setup, find_packages

# Read the long description from a README file (optional, recommended)
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="goit",
    version="0.1.0",  # Increment this as needed
    author="Mike 'Fuzzy' Partin",
    author_email="fuzzy@thwap.org",
    description="A TUI wrapping many github cli operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuzzy/goit",  # Replace with your project's URL
    packages=find_packages(
        include=["goitlib", "goit.*"]
    ),  # Automatically find packages in `goit/`
    py_modules=["goit"],  # Include the standalone script `goit.py`
    entry_points={
        "console_scripts": [
            "goit=goit:main",  # Maps `goit` command to `main()` function in `goit.py`
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Change as appropriate
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # List your project's dependencies here
        # Example: "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest",  # Example: Include testing tools for development
        ],
    },
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    zip_safe=False,  # Ensure compatibility with zip imports
)
