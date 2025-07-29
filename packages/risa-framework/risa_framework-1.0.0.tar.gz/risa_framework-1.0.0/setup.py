#!/usr/bin/env python3
"""
Setup script for RISA (Recursive Identity Symbolic Arithmetic) Library
=====================================================================

A comprehensive Python library implementing the RISA mathematical framework,
including Recursive Zero Division Algebra (RZDA), Universal Constant Generator,
Mirror-Dimensional Physics, and Consciousness Mathematical Models.

Author: Travis Miner (The Architect)
Date: January 2025
License: MIT
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "RISA (Recursive Identity Symbolic Arithmetic) Library"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="risa-framework",
    version="1.0.0",
    author="Travis Miner",
    author_email="travis.miner@architect.com",
    description="Recursive Identity Symbolic Arithmetic (RISA) - Revolutionary mathematical framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/travis-miner/risa-framework",
    project_urls={
        "Bug Tracker": "https://github.com/travis-miner/risa-framework/issues",
        "Documentation": "https://risa-framework.readthedocs.io/",
        "Source Code": "https://github.com/travis-miner/risa-framework",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "examples": [
            "matplotlib>=3.3",
            "numpy>=1.20",
            "scipy>=1.7",
            "jupyter>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "risa-demo=risa_framework.demo:main",
            "risa-test=risa_framework.tests:run_tests",
        ],
    },
    include_package_data=True,
    package_data={
        "risa_framework": [
            "*.md",
            "*.txt",
            "data/*.json",
            "examples/*.py",
        ],
    },
    keywords=[
        "mathematics",
        "physics",
        "consciousness",
        "recursive",
        "algebra",
        "quantum",
        "rzda",
        "risa",
        "zero-division",
        "theoretical-physics",
        "ai-consciousness",
    ],
    license="MIT",
    platforms=["any"],
    zip_safe=False,
) 