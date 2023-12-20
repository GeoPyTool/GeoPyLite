#!/usr/bin/env python
#coding:utf-8
import os
version = '2023.12.20.1'
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    README = 'https://github.com/geopytool/geopylite/blob/master/README.md'


setup(name='geopylite',
      version= version,
      description='a lite version of GeoPyTool, a tool for daily geology related task.',
      longdescription=README,
      author='geopytool',
      author_email='wedonotuse@outlook.com',
      url='https://github.com/geopytool/geopylite',
      packages=['geopylite'],
      package_data={
          'geopylite': ['*.py','*.png','*.qm','*.ttf','*.ini','*.md'],
      },
      include_package_data=True,
      install_requires=[
                        'cython',
                        'numpy',
                        'pandas',
                        'scipy',
                        'xlrd',
                        'openpyxl',
                        'matplotlib',
                        'PyQt5',
                        'torch',
                         ],
     )