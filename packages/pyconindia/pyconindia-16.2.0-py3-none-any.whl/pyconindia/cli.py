#!/usr/bin/env python3
"""
PyCon India CLI Tool
"""

import click
import json
from .conference import Conference
from . import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="pyconindia")
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
@click.pass_context
def cli(ctx, output_json):
    """PyCon India - The largest gathering of Pythonistas in India"""
    ctx.ensure_object(dict)
    ctx.obj['json'] = output_json
    
    if ctx.invoked_subcommand is None:
        conf = Conference()
        info = conf.get_conference_info()
        
        if output_json:
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo("🐍 Welcome to PyCon India CLI!")
            click.echo(f"📅 Year: {info['year']}")
            click.echo(f"📍 Location: {info['location']}")
            click.echo(f"📅 Dates: {info['dates']}")
            click.echo(f"🎯 Theme: {info['theme']}")
            click.echo(f"📝 CFP: {info['cfp']}")
            click.echo("\nUse --help to see available commands.")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def info(ctx, year):
    """Show conference information"""
    conf = Conference()
    data = conf.get_conference_info(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"🐍 PyCon India {data['year']}")
        click.echo(f"📅 Year: {data['year']}")
        click.echo(f"📍 Location: {data['location']}")
        click.echo(f"📅 Dates: {data['dates']}")
        click.echo(f"🎯 Theme: {data['theme']}")
        click.echo(f"📝 CFP: {data['cfp']}")
        click.echo(f"🌐 Website: {data['website']}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def location(ctx, year):
    """Get conference location"""
    conf = Conference()
    result = conf.location(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps({"location": result}))
    else:
        click.echo(f"📍 {result}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def dates(ctx, year):
    """Get conference dates"""
    conf = Conference()
    result = conf.dates(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps({"dates": result}))
    else:
        click.echo(f"📅 {result}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def theme(ctx, year):
    """Get conference theme"""
    conf = Conference()
    result = conf.theme(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps({"theme": result}))
    else:
        click.echo(f"🎯 {result}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def cfp(ctx, year):
    """Get Call For Proposals information"""
    conf = Conference()
    result = conf.cfp(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps({"cfp": result}))
    else:
        click.echo(f"📝 {result}")


@cli.command()
@click.option('--year', '-y', type=int, help='Specific year to query')
@click.pass_context
def website(ctx, year):
    """Get conference website"""
    conf = Conference()
    result = conf.website(year)
    
    if ctx.obj['json']:
        click.echo(json.dumps({"website": result}))
    else:
        click.echo(f"🌐 {result}")


@cli.command()
@click.pass_context
def year_cmd(ctx):
    """Get current year"""
    conf = Conference()
    current_year = conf.year()
    
    if ctx.obj['json']:
        click.echo(json.dumps({"year": current_year}))
    else:
        click.echo(f"📅 {current_year}")


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    if ctx.obj['json']:
        click.echo(json.dumps({"version": __version__}))
    else:
        click.echo(f"pyconindia v{__version__}")


@cli.command()
@click.option('--start-year', type=int, default=2009, help='Start year for history')
@click.option('--end-year', type=int, help='End year for history (default: current year)')
@click.pass_context
def history(ctx, start_year, end_year):
    """Show PyCon India history"""
    conf = Conference()
    current_year = conf.year()
    end_year = end_year or current_year
    available_years = conf.get_all_years()
    
    years = [y for y in available_years if start_year <= y <= end_year]
    
    if ctx.obj['json']:
        history_data = []
        for y in years:
            history_data.append(conf.get_conference_info(y))
        click.echo(json.dumps({"history": history_data}, indent=2))
    else:
        click.echo("📚 PyCon India History:")
        for y in years:
            info = conf.get_conference_info(y)
            click.echo(f"  {y}: {info['location']} - {info['theme']}")


@cli.command()
@click.option('--browser', '-b', is_flag=True, help='Open in browser')
@click.option('--year', '-y', type=int, help='Specific year website')
def open_website(browser, year):
    """Open PyCon India website"""
    conf = Conference()
    url = conf.website(year)
    
    if browser:
        import webbrowser
        webbrowser.open(url)
        click.echo(f"🌐 Opening {url} in browser...")
    else:
        click.echo(f"🌐 Website: {url}")


if __name__ == '__main__':
    cli()
