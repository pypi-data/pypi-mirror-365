"""
Setup script for Monkey Coder Python SDK.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="monkey-coder-sdk",
    version="1.0.1",
    author="Monkey Coder",
    author_email="support@monkeycoder.dev",
    description="Python SDK for Monkey Coder API - AI-powered code generation and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monkey-coder/sdk",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "monkey-coder-sdk=monkey_coder_sdk.cli:main",
        ],
    },
    keywords="ai, code generation, api, sdk, monkey coder, automation",
    project_urls={
        "Bug Reports": "https://github.com/monkey-coder/sdk/issues",
        "Source": "https://github.com/monkey-coder/sdk",
        "Documentation": "https://docs.monkeycoder.dev/sdk/python",
    },
)
