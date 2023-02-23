# -*- coding: utf-8 -*-

import setuptools
import versioneer
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="KiAssemblyVariant",
    python_requires='>=3.7',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jan Mrázek",
    author_email="email@honzamrazek.cz",
    description="Assembly variants switcher for KiCAD 6 and 7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaqwsx/KiCAD-assembly-variants",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy", # Required for MacOS
        "pcbnewTransition >= 0.3.4, <=0.4",
        "click>=7.1",
    ],
    setup_requires=[
        "versioneer"
    ],
    extras_require={
        "dev": ["pytest"],
    },
    include_package_data=True,
    entry_points = {
        "console_scripts": [
            "kiAsm=kiAssemblyVariant.ui:cli",
        ],
    }
)
