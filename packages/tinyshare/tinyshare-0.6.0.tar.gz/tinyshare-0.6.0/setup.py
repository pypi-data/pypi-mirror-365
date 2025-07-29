
from setuptools import setup, find_packages
import glob
import os

# 查找所有.pyc文件
def find_pyc_files():
    pyc_files = []
    for root, dirs, files in os.walk("tinyshare"):
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    return pyc_files

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tinyshare",
    version="0.6.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight wrapper for tushare financial data API (Bytecode Protected Version)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tinyshare",
    packages=find_packages(),
    package_data={
        "tinyshare": ["*.pyc"],
    },
    include_package_data=True,
    data_files=[
        ("tinyshare", [f for f in find_pyc_files() if f.startswith("tinyshare/")])
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "tushare>=1.2.0",
        "pandas>=1.0.0",
    ],
    keywords="finance, stock, data, tushare, api, protected, bytecode",
    zip_safe=False,
)
