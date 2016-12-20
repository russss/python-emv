EMV for Python
==============

[![Build Status](https://travis-ci.org/russss/python-emv.svg?branch=master)](https://travis-ci.org/russss/python-emv)

A Pythonic implementation of the EMV smartcard protocol, which is used
worldwide for chip-and-PIN payments. This is intended to be readable,
and heavily cross-referenced with the appropriate sections of the [EMV
Specification](http://www.emvco.com/specifications.aspx).

This also includes an implementation of the `EMV CAP` (aka PinSentry)
standard which works for Barclays cards.

Command-line tool
-----------------

This library ships with `emvtool` - a simple command-line tool for testing
and CAP password generation. Run `emvtool -h` for more info.
