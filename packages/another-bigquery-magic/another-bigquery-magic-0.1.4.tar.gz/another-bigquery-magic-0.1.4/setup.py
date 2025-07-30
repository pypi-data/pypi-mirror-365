# -*- coding: utf-8 -*-

import os
from setuptools import setup
from bq import __version__

readmefile = os.path.join(os.path.dirname(__file__), "README.md")
with open(readmefile) as f:
    readme = f.read()

setup(
    name='another-bigquery-magic',
    version=__version__,
    description='Unofficial IPython magic command for bigquery',
    author='Kota Mori', 
    author_email='kmori05@gmail.com',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/kota7/another-bigquery-magic',
    
    py_modules=['bq'],
    install_requires=['pandas', 'polars', 'IPython', 'traitlets', 'google-cloud-bigquery']
)
