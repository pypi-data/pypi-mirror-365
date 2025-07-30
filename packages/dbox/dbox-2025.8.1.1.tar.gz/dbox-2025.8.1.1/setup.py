#!/usr/bin/env python
# coding:utf-8
"""将个人封装的公共方法打包"""
from setuptools import setup, find_packages
from dbox import __version__


PACKAGE_NAME = "dbox"
PACKAGE_VERSION = __version__

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Personal method encapsulation",
    url="https://github.com/Deng2016/dbox",
    author="dqy",
    author_email="yu12377@163.com",
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_data={
        "dbox": ["*.py"],
    },
    exclude_package_data={
        "": [
            ".gitignore",
            "lab.py",
            "tests/",
            "*.bat",
            "*.log",
            "*.out",
            "*.zip",
            "*.txt",
            "pytest.ini",
            "README_TESTS.md",
        ]
    },
    python_requires=">=3.13",
    install_requires=[
        "requests~=2.32.4",
        "redis~=6.2.0",
        "pycryptodome~=3.23.0",
        "xpinyin~=0.7.7",
        "pysmb~=1.2.11",
        "pyjwt~=2.10.1",
        "pytz~=2025.2",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
    ],
)
