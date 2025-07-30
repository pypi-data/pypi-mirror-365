 # autotestmap/setup.py

from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autotestmap",
    version="1.0.0",  
    author="mohTalib",
    description="A tool to automatically map Python source files to their corresponding test files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohTalib/autotestmap",
    packages=find_packages(),
    # Define the command-line script entry point.
    entry_points={
        "console_scripts": ["autotestmap=autotestmap.cli:main"],
    },
    # No external dependencies are needed for this core version.
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
)
