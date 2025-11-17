from flask import Flask
from .config.settings import Config
from .extensions import db, migrate
from app.extensions import ma
from app.extensions import api

# Import namespaces
from app.routes.auth_routes import auth_ns

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    api.init_app(app)

    # Register CLI commands
    from .commands import start_server, create_admin
    app.cli.add_command(start_server)
    app.cli.add_command(create_admin)

    # register apis
    api.add_namespace(auth_ns, path="/auth")
    
    

    return app
