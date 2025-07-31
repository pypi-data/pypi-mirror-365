""" This module provides a class that can generate random prompts with who-what-when template. """

import codecs
import os
from setuptools import setup
from setuptools import find_packages

def readme():
    """ Reads the README.md from file """
    with open("README.md", encoding = "utf-8") as file:
        return file.read()

def read(rel_path):
    """ Helper module to read version """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), encoding = "utf-8") as fp:
        return fp.read()

def get_version(rel_path):
    """ Processes __version__ from __init__ file """
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            break
    else:
        raise RuntimeError("Unable to find version string.")
    return line.split(delim)[1]

setup(
    name="prompter-r3ap3rpy",
    description="Prompt your text-to-image AI",
    version = get_version('prompter/__init__.py'),
    long_description = readme(),
    long_description_content_type = "text/markdown",
    author = "Szabó Dániel Ernő",
    author_email = "r3ap3rpy@gmail.com",
    url = "https://pypi.org/project/prompter-r3ap3rpy/",
    include_package_data = True,
    license = "MIT",
    packages=find_packages(),
    python_requires='>=3.10.0',
    classifiers= [
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
