from setuptools import setup, find_packages

setup(
    name="jackblack",
    version="0.8.0",
    author="Michael Munson",
    author_email="michaelmunsonm@gmail.com",
    description="A Blackjack simulator and strategy engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/michaelmunson/blackjack",
    packages=find_packages(),  # auto-discovers `jackblack`
    include_package_data=True,
    install_requires=[
    "escprint==1.0.4",
    "argparse==1.4.0",
    ],  # or read from requirements.txt
    entry_points={
        "console_scripts": [
            "jackblack=jackblack.cli:main",  # if you want a CLI
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
