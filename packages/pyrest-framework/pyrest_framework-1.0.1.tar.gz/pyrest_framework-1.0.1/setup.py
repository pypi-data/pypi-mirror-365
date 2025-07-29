#!/usr/bin/env python3
"""
Setup script for PYREST-FRAMEWORK
Framework Python para criação de APIs REST - Desenvolvido para ADS
"""

from setuptools import setup, find_packages
import os

# Lê o README para usar como descrição longa
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Lê os requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pyrest-framework",
    version="1.0.1",
    author="Mamadu Sama",
    author_email="mamadusama19@gmail.com",
    description="Framework Python para criação de APIs REST - Estilo Express.js",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mamadusamadev/pyrest-framework",
    project_urls={
        "Bug Tracker": "https://github.com/mamadusamadev/pyrest-framework/issues",
        "Documentation": "https://github.com/mamadusamadev/pyrest-framework/blob/main/docs/README.md",
        "Source Code": "https://github.com/mamadusamadev/pyrest-framework",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords=[
        "api", "rest", "framework", "web", "http", "server", 
        "express", "microframework", "ads", "education",
        "python", "web-framework", "rest-api", "middleware"
    ],
    python_requires=">=3.7",
    install_requires=[
        # Mantemos zero dependências para simplicidade educacional
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "examples": [
            "requests>=2.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyrest=pyrest.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pyrest": [
            "templates/*.py",
            "templates/*.md",
        ],
    },
    zip_safe=False,
    license="MIT",
    platforms=["any"],
)