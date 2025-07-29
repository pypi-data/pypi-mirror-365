from setuptools import setup, find_packages

setup(
    name="btd",
    version="1.0.0",
    author="TheGhost",
    author_email="gabriel.gamerx11g@gmail.com",
    description="A simple tool for working with .btd files",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)