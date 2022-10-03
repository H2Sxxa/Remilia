#!/usr/bin/env python
# coding=utf-8

from time import localtime, strftime
from setuptools import setup, find_packages

__version__=strftime("%Y.%m.%d.%H.%M.%S", localtime())

with open("Remilia/__init__.py","r",encoding="utf-8") as pkg:
    text=pkg.read().replace("#__VERSION__#","__version__=\"%s\""%__version__)
with open("Remilia/__init__.py","w",encoding="utf-8") as pkg:
    pkg.write(text)
setup(
    name='Remilia',
    version=__version__,
    description=(
        'Use python with dignity,here offer some utils'
    ),
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    author='h2sxxa',
    author_email='H2Sxxa0w0@gmail.com',
    maintainer='h2sxxa',
    maintainer_email='H2Sxxa0w0@gmail.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/IAXRetailer/Remilia',
    classifiers=[
    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    ],
    install_requires = [
        "colorama",
        "pyyaml",
        ]
)