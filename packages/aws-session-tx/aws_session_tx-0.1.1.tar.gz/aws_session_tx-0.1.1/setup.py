#!/usr/bin/env python3
"""
Setup script for AWS Session TX
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aws-session-tx",
    version="0.1.1",
    author="Session TX Team",
    description="A per-session 'begin → plan → rollback' tool for AWS sandboxes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GarvitBanga/aws-session-tx",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
        "boto3>=1.34.0",
        "botocore>=1.34.0",
        "pydantic>=2.5.0",
        "rich>=13.7.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-tx=cli.main:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 