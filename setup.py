from setuptools import setup

setup(name='emv',
      version='0.1',
      description='EMV Smartcard Protocol Library',
      license='MIT',
      author='Russ Garrett',
      author_email='russ@garrett.co.uk',
      packages=['emv', 'emv.protocol', 'emv.command'],
      install_requires=['enum', 'argparse', 'pyscard'],
      scripts=['bin/emvtool']
      )
