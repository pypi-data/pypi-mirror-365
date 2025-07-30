#!/usr/bin/env python3
"""
Setup script for AWS Session TX
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aws-session-tx",
    version="0.1.0",
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
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aws-tx=cli.main:app",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 