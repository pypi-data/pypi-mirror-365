#!/usr/bin/env python3
"""
PyCon India CLI Tool
"""

import click
from .conference import Conference
from . import __version__, year, location, cfp


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="pyconindia")
@click.pass_context
def cli(ctx):
    """PyCon India - The largest gathering of Pythonistas in India"""
    if ctx.invoked_subcommand is None:
        click.echo("🐍 Welcome to PyCon India CLI!")
        click.echo(f"📅 Year: {year}")
        click.echo(f"📍 Location: {location}")
        click.echo(f"📝 CFP: {cfp}")
        click.echo("\nUse --help to see available commands.")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
def info(year):
    """Show conference information"""
    conf = Conference()
    current_year = year or conf.year()
    
    click.echo(f"🐍 PyCon India {current_year}")
    click.echo(f"📅 Year: {current_year}")
    click.echo(f"📍 Location: {conf.location(current_year)}")
    click.echo(f"📝 CFP: {conf.cfp(current_year)}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
def location_cmd(year):
    """Get conference location"""
    conf = Conference()
    result = conf.location(year)
    click.echo(f"📍 {result}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
def cfp_cmd(year):
    """Get Call For Proposals information"""
    conf = Conference()
    result = conf.cfp(year)
    click.echo(f"📝 {result}")


@cli.command()
def year_cmd():
    """Get current year"""
    conf = Conference()
    click.echo(f"📅 {conf.year()}")


@cli.command()
def version():
    """Show version information"""
    click.echo(f"pyconindia v{__version__}")


if __name__ == '__main__':
    cli()
