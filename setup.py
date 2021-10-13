from setuptools import setup, find_packages
from io import open

import pathlib

BASE_DIR = pathlib.Path(__file__).parent

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name="CloudPhoto",
    description="Store albums in cloud",
    long_description=(BASE_DIR / "readme.md").read_text(),
    long_description_content_type="text/markdown",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False,
    python_requires=">=3",
    entry_points={
        'console_scripts':
            'cloudphoto = cloudphoto.__main__:main'
    },
    author="Khaziev Bulat 11-806",
    keyword="yandex, cloud, itis",
    license="MIT",
    url="https://github.com/unbrokenguy/cloudphoto",
    download_url="https://github.com/unbrokenguy/cloudphoto/archive/refs/heads/master.zip",
    author_email="khazievbulatphanzilovich@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.7",
    ],
)
