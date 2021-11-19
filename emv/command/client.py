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
from emv.exc import InvalidPINException, MissingAppException, CAPError
from emv.util import format_bytes

LOG_LEVELS = {"info": logging.INFO, "debug": logging.DEBUG, "warn": logging.WARN}


def as_table(tlv, title=None, redact=False):
    res = [["Tag", "Name", "Value"]]
    if type(tlv) is not TLV:
        return ""
    for tag, value in tlv.items():
        res.append(
            [
                format_bytes(tag.id),
                tag.name or "",
                "\n".join(textwrap.wrap(render_element(tag, value, redact=redact), 80)),
            ]
        )
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
    "Command line entrypoint"
    cli(obj={})


@click.group(
    help="""Utility to interact with EMV payment cards.

Although this tool has been relatively well tested, it's possible to
block or even damage your card, as well as get in trouble with your
card issuer. Please make sure you understand the risks.

Commands marked with [!] will initiate a transaction on the card,
resulting in a permanent change to the card's internal state which
could potentially be detected by your card issuer, particularly if
you initiate many transactions.
"""
)
@click.option(
    "--reader",
    "-r",
    type=int,
    metavar="READER",
    default=0,
    help="the reader to use (default 0)",
)
@click.option(
    "--pin",
    "-p",
    type=str,
    metavar="PIN",
    help="PIN. Note this may be shown in the system process list.",
)
@click.option(
    "--loglevel", "-l", type=str, metavar="LOGLEVEL", default="warn", help="log level"
)
@click.option(
    "--redact/--no-redact",
    default=False,
    help="redact sensitive data for public display. Note that this is not foolproof "
    + """- your card may send sensitive data in tags we don't know about!""",
)
@click.pass_context
def cli(ctx, reader, pin, loglevel, redact):
    logging.basicConfig(level=LOG_LEVELS[loglevel])
    ctx.obj["pin"] = pin
    ctx.obj["reader"] = reader
    ctx.obj["redact"] = redact


@cli.command(help="Show the version of emvtool.")
def version():
    click.echo(emv.__version__)


@cli.command(help="List available card readers.")
def readers():
    click.echo("Available card readers:\n")
    readers = smartcard.System.readers()
    for i in range(0, len(readers)):
        click.echo("%i: %s" % (i, readers[i]))


def render_app(card, df, redact):
    data = card.select_application(df).data

    click.echo(
        as_table(data[Tag.FCI][Tag.FCI_PROP], "FCI Proprietary Data", redact=redact)
    )
    for i in range(1, 31):
        try:
            for j in range(1, 16):
                rec = card.read_record(j, sfi=i).data
                if Tag.RECORD not in rec:
                    break
                click.echo(
                    as_table(rec[Tag.RECORD], "File: %s,%s" % (i, j), redact=redact)
                )
        except ErrorResponse:
            continue


@cli.command(help="Dump card information.")
@click.pass_context
def info(ctx):
    redact = ctx.obj["redact"]
    card = get_reader(ctx.obj["reader"])
    apps = card.list_applications()

    click.secho("\n1PAY.SYS.DDF01 (Index of apps for chip payments)", bold=True)
    try:
        render_app(card, "1PAY.SYS.DDF01", redact)
    except MissingAppException:
        click.secho(
            "1PAY.SYS.DDF01 not available (this is normal on some cards)", fg="yellow"
        )
    except Exception as e:
        click.secho("Error reading 1PAY.SYS.DDF01 (may be normal): " + str(e), fg="red")

    click.secho("\n2PAY.SYS.DDF01 (Index of apps for contactless payments)", bold=True)
    try:
        render_app(card, "2PAY.SYS.DDF01", redact)
    except MissingAppException:
        click.secho(
            "2PAY.SYS.DDF01 not available (this is normal on some cards)", fg="yellow"
        )
    except Exception as e:
        click.secho("Error reading 2PAY.SYS.DDF01 (may be normal): " + str(e), fg="red")

    for app in apps:
        click.secho(
            "\nApplication %s, DF Name: %s"
            % (
                render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]),
                render_element(Tag.DF, app[Tag.ADF_NAME]),
            ),
            bold=True,
        )
        render_app(card, app[Tag.ADF_NAME], redact)

    click.echo("\nFetching card metadata...")
    try:
        tab = SingleTable(card.get_metadata().items())
        tab.inner_heading_row_border = False
        click.echo(tab.table)
    except ErrorResponse as e:
        click.secho("Unable to fetch card data: %s" % e, fg="yellow")


@cli.command(
    help="""[!] Perform EMV CAP authentication.
This will initiate a transaction on the card."""
)
@click.option(
    "--challenge", "-c", metavar="CHALLENGE", help="account number or challenge"
)
@click.option("--amount", "-a", metavar="AMOUNT", help="amount")
@click.pass_context
def cap(ctx, challenge, amount):
    pin = ctx.obj.get("pin", None)
    if not pin:
        click.secho("PIN is required", fg="red")
        sys.exit(2)

    if amount is not None and challenge is None:
        click.secho("Challenge (account number) must be supplied with amount", fg="red")
        sys.exit(3)

    card = get_reader(ctx.obj["reader"])
    try:
        click.echo(card.generate_cap_value(pin, challenge=challenge, value=amount))
    except InvalidPINException:
        click.secho("Invalid PIN", fg="red")
        sys.exit(1)
    except CAPError as e:
        click.secho("Error in CAP generation: %s" % e, fg="red")
        sys.exit(2)


@cli.command(help="List named applications on the card.")
@click.pass_context
def listapps(ctx):
    card = get_reader(ctx.obj["reader"])
    apps = card.list_applications()
    res = [["Index", "Label", "ADF"]]
    i = 0
    for app in apps:
        res.append(
            [
                i,
                render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]),
                render_element(Tag.ADF_NAME, app[Tag.ADF_NAME]),
            ]
        )
        i += 1

    table = SingleTable(res)
    table.title = "Applications"
    click.echo(table.table)


@cli.command(
    help="""[!] Get card processing options and app data.
This will initiate a transaction on the card."""
)
@click.argument("app_index", type=int)
@click.pass_context
def appdata(ctx, app_index):
    redact = ctx.obj["redact"]
    card = get_reader(ctx.obj["reader"])
    apps = card.list_applications()
    app = apps[app_index]
    card.select_application(app[Tag.ADF_NAME])
    click.secho(
        "Selected application %s (%s)"
        % (
            render_element(Tag.APP_LABEL, app[Tag.APP_LABEL]),
            render_element(Tag.ADF_NAME, app[Tag.ADF_NAME]),
        ),
        bold=True,
    )
    opts = card.get_processing_options()

    res = [["Key", "Value"]]
    for k, v in opts.items():
        res.append((k, v))
    table = SingleTable(res)
    table.title = "Processing Options"
    click.echo(table.table)

    app_data = card.get_application_data(opts["AFL"])
    click.echo(as_table(app_data, title="Application Data", redact=redact))
