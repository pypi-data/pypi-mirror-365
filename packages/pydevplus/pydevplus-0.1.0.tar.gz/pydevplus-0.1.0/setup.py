from setuptools import setup, find_packages

setup(
    name="pydevplus",
    version="0.1.0",
    author="sksanju",
    author_email="sanjayskpy1@gmail.com",
    description="A powerful toolkit for Python developers.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sksanju/pydevplus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
