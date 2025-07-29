# setup.py

from setuptools import setup, find_packages

setup(
    name="prachi_package_test",
    version="0.1.0",
    author="Prachi Kabra",
    author_email="codebakery8889@gmail.com",
    description="Sample Test Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prachikabra121/prachi_package_test",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)