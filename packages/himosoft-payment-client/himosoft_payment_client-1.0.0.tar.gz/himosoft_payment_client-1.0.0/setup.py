"""
Setup script for Himosoft Payment Client package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="himosoft-payment-logging-client",
    version="1.0.0",
    author="Himosoft",
    author_email="support@himosoft.com.bd",
    description="A Python client library for integrating with the Himosoft Payment Logging API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Swe-HimelRana/payment-logging-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "responses>=0.13.0",
        ],
    },
    keywords="payment, logging, api, client, himosoft",
    project_urls={
        "Bug Reports": "https://github.com/Swe-HimelRana/payment-logging-client/issues",
        "Source": "https://github.com/Swe-HimelRana/payment-logging-client",
        "Documentation": "https://github.com/Swe-HimelRana/payment-logging-client#readme",
    },
) 