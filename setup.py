from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jackblack",
    version="0.6.0",
    author="Michael Munson",
    author_email="munson.s.michael@gmail.com",
    description="A Python library for playing and simulating Black Jack games with customizable strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelmunson/blackjack",
    packages=find_packages(where="jackblack"),
    package_dir={"": "jackblack"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "escprint",
        "argparse",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "jackblack=jackblack.cli:main",
        ],
    },
) 