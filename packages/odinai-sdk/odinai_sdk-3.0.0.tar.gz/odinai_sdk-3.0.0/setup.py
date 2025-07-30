#!/usr/bin/env python3
"""
Odin AI Python SDK
Official Python client library for Odin AI API
"""

from setuptools import setup, find_packages
import os

# Read the contents of the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Odin AI Python SDK - Official Python client library for Odin AI API"

setup(
    name="odinai-sdk",
    version="3.0.0",
    description="Odin AI Python SDK - Official Python client library for Odin AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Odin AI Team",
    author_email="support@getodin.ai",
    url="https://getodin.ai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "urllib3>=1.25.3,<3.0.0",
        "python-dateutil>=2.8.2",
        "pydantic>=2.5.0",
        "typing-extensions>=4.7.1",
    ],
    keywords=["odin", "ai", "api", "sdk", "python", "cybersecurity", "security"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.9",
    project_urls={
        "Homepage": "https://getodin.ai",
        "Repository": "https://github.com/getodin/odin-sdk",
        "Documentation": "https://docs.getodin.ai",
        "Bug Reports": "https://github.com/getodin/odin-sdk/issues",
    },
)
