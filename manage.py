#!/usr/bin/env python
"""Management script for common operations.
"""
import subprocess
import sys

from flask import current_app
from flask.cli import FlaskGroup
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.exc import OperationalError
import click
import sqlalchemy_utils

from quizApp import create_app
from quizApp import db
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


@cli.command("create-db")
@click.option("-u", "--user")
@click.option("-p", "--password")
def create_db(password, user):
    """Bootstrap the database for this config.

    This means:

    1. Attempt to connect to the database. If successful, do nothing.

    2. If 1 is unsusccessful, then request root permissions. Create a user and
    database and grant ownership of the database to the user.

    This can be used to set up the database for any configuration. Just specify
    the configuration you wish to use via the -c option.
    """
    try:
        db.engine.connect()
    except OperationalError as e:
        click.echo(("Looks like the database is not configured. The error "
                    "from SQLAlchemy is: "))
        click.echo(e)
        click.echo(("If you enter the database credentials, I will try to "
                    "set up the database. If any conflicts exist, nothing "
                    "will happen - this operation is safe."))
        if not user:
            root_name = click.prompt("Enter root username", type=str)
            root_pass = click.prompt("Enter root password", type=str,
                                     hide_input=True)
        else:
            root_name = user
            root_pass = password
        db_uri = make_url(current_app.config["SQLALCHEMY_DATABASE_URI"])
        root_uri = URL(db_uri.drivername,
                       root_name,
                       root_pass,
                       db_uri.host,
                       db_uri.port,
                       db_uri.database)

        if not sqlalchemy_utils.database_exists(root_uri):
            sqlalchemy_utils.functions.create_database(root_uri)

        engine = create_engine(root_uri)
        conn = engine.connect()
        conn.execute("commit")
        # conn.execute(("CREATE USER IF NOT EXISTS '{}'@'{}' IDENTIFIED BY '{}';").
        #              format(db_uri.username, db_uri.host, db_uri.password))
        conn.execute(("GRANT ALL ON {}.* TO '{}'@'{}' IDENTIFIED BY '{}';").format(
            db_uri.database, db_uri.username, db_uri.host, db_uri.password))
        conn.close()

        return
    click.echo("Database seems to be working OK.")


@cli.command("populate-db")
def run_populate_db():
    """Run the populate_db.py script.
    """
    populate_db.setup_db()

if __name__ == '__main__':
    cli()
