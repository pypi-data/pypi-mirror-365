# setup.py

from setuptools import setup, find_packages

setup(
    name="pattern_pk",
    version="0.1.0",
    author="Prachi Kabra",
    author_email="codebakery8889@gmail.com",
    description="This Package is for printing patterns",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prachikabra121/Pattern",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)