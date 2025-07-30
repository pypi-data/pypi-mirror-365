#!/usr/bin/env python3
"""
Setup script for Data Analysis Framework
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="data-analysis-framework",
    version="1.0.0",
    author="Wes Jackson",
    author_email="wjackson@redhat.com",
    description="AI-powered analysis framework for structured data files and databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rdwj/data-analysis-framework",
    project_urls={
        "Bug Reports": "https://github.com/rdwj/data-analysis-framework/issues",
        "Source": "https://github.com/rdwj/data-analysis-framework",
        "Documentation": "https://github.com/rdwj/data-analysis-framework/blob/main/README.md",
    },
    packages=[
        "data_analysis_framework",
        "data_analysis_framework.core", 
        "data_analysis_framework.handlers",
        "data_analysis_framework.utils"
    ],
    package_dir={"data_analysis_framework": "src/data_analysis_framework"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Database",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
        "pyarrow>=8.0.0",
        "sqlalchemy>=1.4.0",
        "pyyaml>=6.0",
        "toml>=0.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx_rtd_theme>=0.5",
        ],
        "database": [
            "psycopg2-binary>=2.9.0",
            "pymongo>=4.0.0",
        ],
        "advanced": [
            "scikit-learn>=1.1.0",
            "scipy>=1.8.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "data-analyze=src.data_analysis_framework.examples.basic_framework_demo:main",
            "data-analyze-car-demo=src.data_analysis_framework.examples.car_sales_demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)