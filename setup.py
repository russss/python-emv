from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

readme_rst = path.join(here, 'README.rst')

if path.isfile(readme_rst):
    with open(readme_rst, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ''

version = {}
with open(path.join(here, 'emv', "__init__.py")) as fp:
    exec(fp.read(), version)

setup(name='emv',
      version=version['__version__'],
      description='EMV Smartcard Protocol Library',
      long_description=long_description,
      license='MIT',
      author='Russ Garrett',
      author_email='russ@garrett.co.uk',
      url='https://github.com/russss/python-emv',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3'
      ],
      keywords='smartcard emv payment',

      packages=['emv', 'emv.protocol', 'emv.command'],
      install_requires=['enum-compat', 'argparse', 'pyscard', 'pycountry', 'terminaltables'],
      entry_points={
          'console_scripts': {
              'emvtool=emv.command.client:run'
          }
      }
      )
