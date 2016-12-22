# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import sys
import logging
import argparse
import smartcard
import textwrap
from terminaltables import SingleTable
import emv
from emv.card import Card
from emv.protocol.data import Tag, render_element
from emv.protocol.response import ErrorResponse
from emv.exc import InvalidPINException
from emv.util import format_bytes

LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warn': logging.WARN
}


def as_table(tlv, title=None, redact=False):
    res = [['Tag', 'Name', 'Value']]
    for tag, value in tlv.items():
        res.append([format_bytes(tag.id),
                    tag.name or '',
                    '\n'.join(textwrap.wrap(render_element(tag, value, redact=redact), 80))])
    table = SingleTable(res)
    if title is not None:
        table.title = title
    return table.table


# Function called by the emvtool shim installed by setuptools
def run():
    EMVClient().run()


class EMVClient(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='EMV Smartcard Tool')
        parser.add_argument('-r', type=int, metavar="READER", default=0, dest='reader',
                            help="the reader to use (default 0)")
        parser.add_argument('-p', type=str, metavar='PIN', dest='pin',
                            help="PIN. Note this may be shown in the system process list.")
        parser.add_argument('-l', type=str, choices=LOG_LEVELS.keys(),
                            dest='loglevel', default='warn',
                            help="log level")
        subparsers = parser.add_subparsers(title="subcommands")

        version = subparsers.add_parser('version', help="show version")
        version.set_defaults(func=self.version)

        list_readers = subparsers.add_parser('readers', help="list available card readers")
        list_readers.set_defaults(func=self.list_readers)

        info = subparsers.add_parser('info', help="retrieve card info")
        info.add_argument('-r', dest='redact', action='store_true',
                          help='''redact sensitive data for public display. Note that this is not foolproof
                                    - your card may send sensitive data in tags we don't know about!''')
        info.set_defaults(func=self.card_info)

        cap = subparsers.add_parser('cap', help="perform EMV CAP authentication")
        cap.add_argument('-c', type=str, metavar="CHALLENGE", dest='challenge',
                         help="account number or challenge")
        cap.add_argument('-a', type=str, metavar="AMOUNT", dest='amount',
                         help="amount")
        cap.set_defaults(func=self.cap)

        self.args = parser.parse_args()
        logging.basicConfig(level=LOG_LEVELS[self.args.loglevel])

    def run(self):
        self.args.func()

    def get_reader(self):
        try:
            return Card(smartcard.System.readers()[self.args.reader].createConnection())
        except IndexError:
            print("Reader or card not found")
            sys.exit(2)

    def list_readers(self):
        print("Available card readers:\n")
        readers = smartcard.System.readers()
        for i in range(0, len(readers)):
            print("%i: %s" % (i, readers[i]))

    def card_info(self):
        card = self.get_reader()
        apps = card.list_applications()

        if type(apps) != list:
            apps = [apps]

        print("Available apps: %s" % (", ".join(render_element(Tag.APP_LABEL, app[Tag.APP_LABEL])
                                                for app in apps)))

        for app in apps:
            print("\nApplication %s, DF Name: %s" % (
                render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]),
                render_element(Tag.DF, app[Tag.ADF_NAME])))
            data = card.select_application(app[Tag.ADF_NAME]).data
            print(as_table(data[Tag.FCI][Tag.FCI_PROP], 'FCI Proprietary Data', redact=self.args.redact))
            for i in range(1, 10):
                try:
                    rec = card.read_record(1, sfi=i).data
                except ErrorResponse as e:
                    break
                print(as_table(rec[Tag.RECORD], 'File: %s' % i, redact=self.args.redact))

        print("\nFetching card data...")
        try:
            tab = SingleTable(card.get_metadata().items())
            tab.inner_heading_row_border = False
            print(tab.table)
        except ErrorResponse as e:
            print("Unable to fetch card data: %s" % e)

    def cap(self):
        if self.args.pin is None:
            print("PIN is required")
            return
        card = self.get_reader()
        try:
            print(card.generate_cap_value(self.args.pin,
                                          challenge=self.args.challenge,
                                          value=self.args.amount))
        except InvalidPINException as e:
            print(e)
            sys.exit(1)

    def version(self):
        print(emv.__version__)
