from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="farady-python",
    version="0.1.3",
    author="Tinger",
    author_email="email@tingerx.com",
    description="Farady Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tinger-X/Farady-Python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "matplotlib"
    ]
)
