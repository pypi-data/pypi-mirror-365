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
    name="xerror",
    version="0.1.0",
    author="XError Team",
    author_email="contact@xerror.dev",
    description="A smart CLI tool to analyze error logs from multiple languages and return AI-generated explanations and fix suggestions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/xerror/xerror",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),

    entry_points={
        "console_scripts": [
            "xerror=xerror.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="error, debugging, ai, cli, python, traceback, exception",
    project_urls={
        "Bug Reports": "https://github.com/xerror/xerror/issues",
        "Source": "https://github.com/xerror/xerror",
        "Documentation": "https://github.com/xerror/xerror#readme",
    },
) 