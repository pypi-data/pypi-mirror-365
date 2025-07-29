#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="trace-dev",
    version="1.0.1",
    author="trace-dev",
    author_email="dev@trace-dev.com",
    description="A lightweight Python CLI that generates language-aware, recursive trace prompts for AI-driven development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trace-dev/trace-dev",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "trace-dev=trace_dev.cli:cli",
        ],
    },
)

