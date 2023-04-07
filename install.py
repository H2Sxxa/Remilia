#!/usr/bin/env python
# coding=utf-8

from time import localtime, strftime
from setuptools import setup, find_packages
from requests import get
from requests import get
from json import loads
from sys import argv

ver="%sdev0"% strftime("%Y.%m.%d.", localtime())

setup(
    name='Remilia',
    version=ver,
    description=(
        'Use python with dignity,here offer a tookit'
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
    'Programming Language :: Python :: 3.11',
    ],
    install_requires = [
        "colorama",
        "pyyaml",
        ]
)