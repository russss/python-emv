# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import sys
import logging
import argparse
import smartcard
from emv.card import Card
from emv.protocol.data import Tag, render_element
from emv.protocol.response import WarningResponse
from emv.cap import get_arqc_req, get_cap_value


class EMVClient(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        parser = argparse.ArgumentParser(description='EMV Smartcard Tool')
        parser.add_argument('-r', type=int, metavar="READER", default=0, dest='reader',
                            help="the reader to use (default 0)")
        parser.add_argument('-p', type=str, metavar='PIN', dest='pin',
                            help="PIN. Note this may be shown in the system process list.")
        subparsers = parser.add_subparsers(title="subcommands")

        list_readers = subparsers.add_parser('readers', help="list available card readers")
        list_readers.set_defaults(func=self.list_readers)

        info = subparsers.add_parser('info', help="retrieve card info")
        info.set_defaults(func=self.card_info)

        cap = subparsers.add_parser('cap', help="perform EMV CAP authentication")
        cap.set_defaults(func=self.cap)

        self.args = parser.parse_args()

    def run(self):
        self.args.func()

    def get_reader(self):
        return Card(smartcard.System.readers()[self.args.reader].createConnection())

    def list_readers(self):
        print("Available card readers:\n")
        readers = smartcard.System.readers()
        for i in range(0, len(readers)):
            print("%i: %s" % (i, readers[i]))

    def card_info(self):
        card = self.get_reader()
        print("Applications:")
        apps = card.list_applications()
        print(apps.data)
        app = apps.data[Tag.RECORD][Tag.APP]
        print("\nSelecting application %s..." % render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]))
        print(card.select_application(app[Tag.ADF_NAME]).data)
        print("\nFetching card data...")
        for k, v in card.get_metadata().items():
            print("%s: %s" % (k, v))

    def cap(self):
        if self.args.pin is None:
            print("PIN is required")
            return
        card = self.get_reader()
        apps = card.list_applications()
        app = apps.data[Tag.RECORD][Tag.APP]
        card.select_application(app[Tag.ADF_NAME])

        opts = card.get_processing_options()
        app_data = card.get_application_data(opts['AFL'])
        res = card.verify_pin(self.args.pin)
        if type(res) == WarningResponse:
            print("PIN verification failed!")
            sys.exit(1)
        resp = card.tp.exchange(get_arqc_req(app_data))
        print(get_cap_value(resp))
