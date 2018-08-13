from pymongo import MongoClient
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        client = MongoClient('localhost:27017')
        g.db = client['flaskr']

    return g.db


def init_db():
    db = get_db()
    db.user.drop()
    db.post.drop()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables. """
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    app.cli.add_command(init_db_command)
