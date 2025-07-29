# setup.py
from setuptools import setup, find_packages

setup(
    name="bilberrydb",
    version="1.0.0",
    author="BilberryDB Team",
    author_email="app@bilberrydb.com",
    description="Python SDK for BilberryDB - Image Vector Search Database",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No third-party dependencies as requested
    ],
    keywords="vector database, image search, similarity search, computer vision, machine learning",
    project_urls={
        "Bug Reports": "https://github.com/bilberrydb/python-sdk/issues",
        "Documentation": "https://docs.bilberrydb.com",
    },
)