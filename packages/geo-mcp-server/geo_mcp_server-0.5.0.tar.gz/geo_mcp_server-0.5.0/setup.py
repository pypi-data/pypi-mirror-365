from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geo-mcp-server",
    version="0.5.0",
    author="MCP Developer",
    author_email="developer@example.com",
    description="DEPRECATED: This package is no longer maintained. Use https://github.com/MCPmed/GEOmcp instead.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MCPmed/GEOmcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[],
    keywords=[
        "deprecated",
        "bioinformatics",
        "e-utils", 
        "gene-expression",
        "geo",
        "mcp",
        "ncbi",
        "geneexpression",
        "mcp-server"
    ],
)