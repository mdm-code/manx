"""Package setup module for manx."""

# Standard library imports
from setuptools import setup, find_packages


setup(
    name="manx",
    version="0.1.0",
    description="A toolkit for early Middle English lemmatization.",
    long_description=open("README.md").read(),
    author="Michał Adamczyk",
    author_email="code.madamczyk@gmail.com",
    url="https://github.com/mdm-code/manx",
    key="lemmatization, deep learning, neural networks, Middle English, NLP",
    packages=find_packages(include=["manx", "manx.*"]),
    python_requires=">=3.10",
    install_requires=[
        pkg.strip() for pkg in open("requirements.txt").readlines()
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "mypy",
            "black",
        ]
    },
    entry_points={
        "console_scripts": [
            "manx=manx.console:main",
        ]
    }
)
