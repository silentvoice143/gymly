from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_restx import Api

api = Api(
    title="Gymly API",
    version="1.0",
    description="API documentation for the Gymly backend",
    doc="/docs" 
    
)
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
