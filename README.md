EMV for Python
==============

![Tests](https://github.com/russss/python-emv/workflows/Tests/badge.svg)

A Pythonic implementation of the EMV smartcard protocol, which is used
worldwide for chip-and-PIN payments. This is intended to be readable,
tested, and heavily cross-referenced with the appropriate sections of the
[EMV Specification](http://www.emvco.com/specifications.aspx).

This also includes an implementation of the `EMV CAP` (aka Pinsentry)
standard which is known to work for Barclays cards.

Installation
------------

You'll need the pcsc smartcard libraries on your system in order to build the
smartcard bindings. On Ubuntu:

    sudo apt-get install build-essential swig libpcsclite-dev python-pip python-devel

Then you can install emv from pip:

    sudo pip install emv

To check if everything's working, plug in a smartcard reader, put a bank
card in, and run:

    emvtool info

If all goes well, you should see some data about your card.

Warning
-------

Although this tool has been relatively well tested, it's possible to block
or even damage your card, as well as get in trouble with your card issuer.
Please make sure you understand the risks.

Commands marked in the `--help` output with [!] will initiate a transaction
on the card, resulting in a permanent change to the card's internal state
which could potentially be detected by your card issuer, particularly if you
initiate many transactions.

Command Line
------------

This library ships with `emvtool` - a simple command-line tool for testing
and CAP password generation. To fetch some card metadata, run:

    emvtool info

If you have more than one smartcard reader (or smartcard-like devices, such as a YubiKey)
connected, you may have to select a specific reader. List all the readers with:

    emvtool readers

Then use the `-r` option to select the specific reader ID, e.g.:

    emvtool -r 1 info

To generate an EMV CAP one-time passcode:

    emvtool -p <PIN> cap

You can also conduct CAP signing and challenge-response:

    emvtool -p <PIN> cap -c <challenge>
    emvtool -p <PIN> cap -c <accountno> -a <amount>

Legal Stuff
-----------

`EMV` is a trademark of [EMVCo](http://www.emvco.com/) and is used
purely for descriptive purposes. This library is not affiliated with
EMVCo.
