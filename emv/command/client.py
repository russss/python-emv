# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import sys
import logging
import argparse
import smartcard
import emv
from emv.card import Card
from emv.protocol.data import Tag, render_element
from emv.protocol.response import WarningResponse, ErrorResponse
from emv.cap import get_arqc_req, get_cap_value

LOG_LEVELS = {
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'warn': logging.WARN
}


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
        print("Testing for existence of MF...")
        try:
            print(card.get_mf())
        except ErrorResponse as e:
            print("MF not found: %s" % e)
        print("Applications:")
        apps = card.list_applications()

        if type(apps) != list:
            apps = [apps]

        print("Available apps: %s" % (", ".join(render_element(Tag.APP_LABEL, app[Tag.APP_LABEL])
                                                for app in apps)))

        for app in apps:
            print("\nApplication %s:" % render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]))
            print(card.select_application(app[Tag.ADF_NAME]).data)

        print("\nFetching card data...")
        try:
            for k, v in card.get_metadata().items():
                print("%s: %s" % (k, v))
        except ErrorResponse as e:
            print("Unable to fetch card data: %s" % e)

    def cap(self):
        if self.args.pin is None:
            print("PIN is required")
            return
        card = self.get_reader()
        apps = card.list_applications()

        # We're selecting the last app on the card here, which on Barclays
        # cards seems to always be the Barclays one.
        #
        # It would be good to work out what logic to use to
        card.select_application(apps[-1][Tag.ADF_NAME])

        opts = card.get_processing_options()
        app_data = card.get_application_data(opts['AFL'])
        res = card.verify_pin(self.args.pin)
        if type(res) == WarningResponse:
            print("PIN verification failed!")
            sys.exit(1)
        resp = card.tp.exchange(get_arqc_req(app_data,
                                challenge=self.args.challenge,
                                value=self.args.amount))
        print(get_cap_value(resp))

    def version(self):
        print(emv.__version__)
