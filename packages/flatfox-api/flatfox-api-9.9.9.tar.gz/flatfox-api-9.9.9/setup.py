from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '9.9.9'
DESCRIPTION = 'PoC Package for Dependency Confusion'
LONG_DESCRIPTION = '''# !!! SECURITY RESEARCH PACKAGE !!!  
This package is part of a proof-of-concept dependency confusion attack.  
**DO NOT USE IN PRODUCTION.** Contact me@viktormares.com for details.'''

# Setting up
setup(
    name="flatfox-api",
    version=VERSION,
    author="vmares",
    author_email="me@viktormares.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=[]
   )
