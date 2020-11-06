from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md") as f:
    long_description = f.read()

version = {}
with open(path.join(here, "emv", "__init__.py")) as fp:
    exec(fp.read(), version)

setup(
    name="emv",
    version=version["__version__"],
    description="EMV Smartcard Protocol Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Russ Garrett",
    author_email="russ@garrett.co.uk",
    url="https://github.com/russss/python-emv",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="smartcard emv payment",
    python_requires=">=3.4",
    packages=["emv", "emv.protocol", "emv.command"],
    install_requires=[
        "enum-compat==0.0.3",
        "argparse==1.4.0",
        "pyscard==2.0.0",
        "pycountry==20.7.3",
        "terminaltables==3.1.0",
        "click==7.1.2",
    ],
    entry_points={"console_scripts": {"emvtool=emv.command.client:run"}},
)
