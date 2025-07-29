#!/usr/bin/env python3
"""
Setup configuration for time-economy
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="time-economy",
    version="1.0.0",
    author="Double-N-A",
    description="A comprehensive toolkit for time-based economy simulation, focusing on wealth distribution and economic modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/double-n-a/time-economy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.12",
    install_requires=[
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "seaborn>=0.11.0",
        "joblib>=1.0.0",
        "scipy>=1.7.0",
        "IPython>=7.0.0",
    ],
    extras_require={
        "gpu": ["cupy >=10.0.0"],  # For GPU acceleration
        "dev": ["pytest>=6.0", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "time-economy-analyze=time_economy.multi_config_analysis:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 