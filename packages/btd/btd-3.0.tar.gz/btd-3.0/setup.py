from setuptools import setup, find_packages

setup(
    name="btd",
    version="3.0",
    author="TheGhost",
    author_email="gabriel.gamerx11g@gmail.com",
    description="BTD — Binary To Data: Ferramentas para salvar arquivos .btd",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="",  # Você não tem URL, então deixei vazio
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)