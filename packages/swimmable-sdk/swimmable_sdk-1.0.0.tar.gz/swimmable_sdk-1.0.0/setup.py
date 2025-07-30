"""
Setup script for the Swimmable Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="swimmable-sdk",
    version="1.0.0",
    author="Swimmable",
    author_email="developers@swimmable.app",
    description="Official Python SDK for the Swimmable API - Real-time swimming conditions and water quality data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swimmable/python-sdk",
    project_urls={
        "Documentation": "https://swimmable.app/docs",
        "Source": "https://github.com/swimmable/python-sdk",
        "Tracker": "https://github.com/swimmable/python-sdk/issues",
        "Homepage": "https://swimmable.app",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "mypy>=0.900",
            "flake8>=3.8",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="swimming water quality weather API ocean beach lake safety conditions",
    include_package_data=True,
    zip_safe=False,
)