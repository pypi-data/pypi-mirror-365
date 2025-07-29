# setup.py

from setuptools import setup, find_packages

setup(
    name="Patterns_SIDDV26",
    version="0.1.1",
    author="Siddharth Verma",
    author_email="Siddv261001@gmail.com",
    description="Sample Test Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prachikabra121/prachi-test-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)