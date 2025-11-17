import click
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db

@click.command("start")
@with_appcontext
def start_server():
    """Run development server"""
    import os
    os.system("python run.py")

@click.command("create-admin")
@with_appcontext
def create_admin():
    """Create an admin user"""
    from app.models.user import User
    admin = User(name="Admin", email="admin@gymly.com", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    click.echo("Admin created!")
