"""
Setup script for PyMBO - Python Multi-objective Bayesian Optimization
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback dependencies if requirements.txt is not found
    requirements = [
        "torch>=1.12.0",
        "botorch>=0.8.0", 
        "gpytorch>=1.9.0",
        "numpy>=1.21.0",
        "pandas>=1.4.0",
        "scipy>=1.8.0",
        "scikit-learn>=1.1.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
        "xlsxwriter>=3.0.0",
        "Pillow>=9.0.0",
    ]

setup(
    name="pymbo",
    version="3.1.3",
    author="Jakub Jagielski",
    author_email="jakubjagielski93@gmail.com",
    description="PyMBO - Python Multi-objective Bayesian Optimization framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jakub-jagielski/pymbo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pymbo=pymbo.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pymbo": ["*.md"],
    },
)