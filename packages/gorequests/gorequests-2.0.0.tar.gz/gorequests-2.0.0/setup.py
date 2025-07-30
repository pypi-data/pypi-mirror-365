#!/usr/bin/env python
"""Setup script for GoRequests library."""

from setuptools import setup, find_packages
import os
import shutil

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the version
def get_version():
    version_file = os.path.join("gorequests", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "2.0.0"

# Prepare the package (files already copied)
print("Package files ready for build")

setup(
    name="gorequests",
    version=get_version(),
    author="GoRequests Team",
    author_email="team@gorequests.io",
    description="High-performance HTTP client library powered by Go FastHTTP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coffeecms/gorequests",
    project_urls={
        "Bug Tracker": "https://github.com/coffeecms/gorequests/issues",
        "Documentation": "https://gorequests.readthedocs.io",
        "Source Code": "https://github.com/coffeecms/gorequests",
    },
    packages=find_packages(),
    package_data={
        "gorequests": ["*.dll", "*.so", "*.dylib"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.7",
    keywords="http requests client fasthttp go performance async web api networking fast",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "requests>=2.25.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "requests>=2.25.0",
        ],
    },
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "gorequests-benchmark=gorequests.benchmark:main",
        ],
    },
)
