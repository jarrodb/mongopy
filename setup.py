#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'mongopy',
    version = '0.01',
    description = 'schemaless python memory store',
    author = 'Jarrod Baumann',
    author_email = 'jarrod@ipglobal.net',
    url = 'https://github.com/jarrodb/mongopy',
    license = "http://www.apache.org/licenses/LICENSE-2.0",
    packages = find_packages(),
    package_dir={'mypkg': 'src/mypkg'},
    install_requires = ['nose'],
    )

