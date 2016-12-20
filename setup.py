# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
from setuptools import setup

setup(name='EMV',
      version='0.1',
      description='EMV Smartcard Protocol Library',
      author='Russ Garrett',
      author_email='russ@garrett.co.uk',
      packages=[b'emv', b'emv.protocol'],
      install_requires=['enum']
      )
