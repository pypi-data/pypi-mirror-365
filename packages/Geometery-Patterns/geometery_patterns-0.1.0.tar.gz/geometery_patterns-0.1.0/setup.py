# setup.py

from setuptools import setup, find_packages

setup(
    name="Geometery_Patterns",
    version="0.1.0",
    author="Vivek Tomar",
    author_email="vivek.tomar.data@gmail.com",
    description="Print Pattern Like Pyramid, Right Angle, and Left ",
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