from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pydevplus",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    description="A versatile toolkit offering essential utilities to boost Python development productivity.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="sksanju",
    author_email="sanjayskpy1@gmail.com",
    url="https://github.com/sk-sanju/pydevplus",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
