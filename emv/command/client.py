# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import sys
import logging
import smartcard
import textwrap
import click
from terminaltables import SingleTable
import emv
from emv.card import Card
from emv.protocol.data import Tag, render_element
from emv.protocol.structures import TLV
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
    if type(tlv) is not TLV:
        return ''
    for tag, value in tlv.items():
        res.append([format_bytes(tag.id),
                    tag.name or '',
                    '\n'.join(textwrap.wrap(render_element(tag, value, redact=redact), 80))])
    table = SingleTable(res)
    if title is not None:
        table.title = title
    return table.table


def get_reader(reader):
    try:
        return Card(smartcard.System.readers()[reader].createConnection())
    except IndexError:
        click.echo("Reader or card not found")
        sys.exit(2)


def run():
    ' Command line entrypoint '
    cli(obj={})


@click.group(help="""Utility to interact with EMV payment cards.

Although this tool has been relatively well tested, it's possible to
block or even potentially damage your card. Please make sure you understand the risks.
""")
@click.option('--reader', '-r', type=int, metavar="READER", default=0,
              help="the reader to use (default 0)")
@click.option('--pin', '-p', type=str, metavar='PIN',
              help="PIN. Note this may be shown in the system process list.")
@click.option('--loglevel', '-l', type=str, metavar='LOGLEVEL',
              default='warn', help="log level")
@click.pass_context
def cli(ctx, reader=None, pin=None, loglevel=None):
    logging.basicConfig(level=LOG_LEVELS[loglevel])
    ctx.obj['pin'] = pin
    ctx.obj['reader'] = reader


@cli.command(help="Show the version of emvtool")
def version():
    click.echo(emv.__version__)


@cli.command(help="List available card readers")
def readers():
    click.echo("Available card readers:\n")
    readers = smartcard.System.readers()
    for i in range(0, len(readers)):
        click.echo("%i: %s" % (i, readers[i]))


def render_app(card, df, redact):
    try:
        data = card.select_application(df).data
    except ErrorResponse as e:
        click.secho("Unable to access app: %s" % e, fg="yellow")
        return

    click.echo(as_table(data[Tag.FCI][Tag.FCI_PROP], 'FCI Proprietary Data', redact=redact))
    for i in range(1, 31):
        try:
            for j in range(1, 16):
                rec = card.read_record(j, sfi=i).data
                click.echo(as_table(rec[Tag.RECORD], 'File: %s,%s' % (i, j), redact=redact))
        except ErrorResponse as e:
            continue


@cli.command(help="Dump card information")
@click.option('--redact/--no-redact', default=False,
              help='redact sensitive data for public display. Note that this is not foolproof ' +
                   '''- your card may send sensitive data in tags we don't know about!''')
@click.pass_context
def info(ctx, redact):
    card = get_reader(ctx.obj['reader'])
    apps = card.list_applications()

    click.secho("\n1PAY.SYS.DDF01 (Index of apps for chip payments)", bold=True)
    render_app(card, '1PAY.SYS.DDF01', redact)
    click.secho("\n2PAY.SYS.DDF01 (Index of apps for contactless payments)", bold=True)
    render_app(card, '2PAY.SYS.DDF01', redact)

    click.echo("Available named apps: %s" % (", ".join(render_element(Tag.APP_LABEL, app[Tag.APP_LABEL])
                                             for app in apps)))

    for app in apps:
        click.secho("\nApplication %s, DF Name: %s" % (
            render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]),
            render_element(Tag.DF, app[Tag.ADF_NAME])), bold=True)
        render_app(card, app[Tag.ADF_NAME], redact)

    click.echo("\nFetching card metadata...")
    try:
        tab = SingleTable(card.get_metadata().items())
        tab.inner_heading_row_border = False
        print(tab.table)
    except ErrorResponse as e:
        print("Unable to fetch card data: %s" % e)


@cli.command(help="Perform EMV CAP authentication")
@click.option('--challenge', '-c', metavar="CHALLENGE", help="account number or challenge")
@click.option('--amount', '-a', metavar="AMOUNT", help="amount")
@click.pass_context
def cap(ctx, challenge, amount):
    if 'pin' not in ctx.obj:
        click.secho("PIN is required", fg='red')
        sys.exit(2)

    if amount is not None and challenge is None:
        click.secho("Challenge (account number) must be supplied with amount", fg='red')
        sys.exit(3)

    card = get_reader(ctx.obj['reader'])
    try:
        click.echo(card.generate_cap_value(ctx.obj['pin'], challenge=challenge, value=amount))
    except InvalidPINException as e:
        click.secho("Invalid PIN", fg='red')
        sys.exit(1)
