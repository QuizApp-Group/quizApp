#!/usr/bin/env python
"""Management script for common operations.
"""
import sys
import subprocess
import click
from flask.cli import FlaskGroup
from quizApp import create_app
from scripts import populate_db


@click.pass_context
def get_app(ctx, _):
    """Create an app with the correct config.
    """
    return create_app(ctx.parent.params["config"])


@click.option("-c", "--config", default="development")
@click.group(cls=FlaskGroup, create_app=get_app)
def cli(**_):
    """Define the top level group.
    """
    pass


@cli.command("test")
def test():
    """Set the app config to testing and run pytest, passing along command
    line args.
    """
    # This looks stupid, but see
    # https://github.com/pytest-dev/pytest/issues/1357
    sys.exit(subprocess.call(['py.test',
                              '--cov=quizApp',
                              '--flake8',
                              '--pylint',
                              './']))


@cli.command("populate-db")
def run_populate_db():
    """Run the populate_db.py script.
    """
    populate_db.setup_db()



if __name__ == '__main__':
    cli()
