#!/usr/bin/env python3
"""
Setup script for the Security Code Scanner PyPI package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-code-scanner",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful Python tool that scans your codebase for security vulnerabilities using Claude AI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-CodeScanner",
    py_modules=["security_scanner"],
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ai-code-scanner=security_scanner:main",
        ],
    },
    keywords="security, code, scanner, vulnerability, claude, ai, static-analysis",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AI-CodeScanner/issues",
        "Source": "https://github.com/yourusername/AI-CodeScanner",
        "Documentation": "https://github.com/yourusername/AI-CodeScanner#readme",
    },
) 
