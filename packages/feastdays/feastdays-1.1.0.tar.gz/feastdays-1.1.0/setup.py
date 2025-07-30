"""Setup configuration for the feastdays package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="feastdays",
    version="1.1.0",
    description="Python package for feast days celebrated in Opus Dei",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daniel Okonma",
    author_email="danielokonma@yahoo.com",
    url="https://github.com/okonma01/feast-days",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'feastdays': ['data/*.json'],
    },
    install_requires=[
        # No external dependencies - using only Python standard library
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Religion",
        "Topic :: Religion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    keywords="feastdays catholic feast days opus dei liturgical calendar saints",
)
