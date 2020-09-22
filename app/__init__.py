from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

"""
-creates the application object as an instance of class Flask
imported from the flask package,
-The __name__ variable passed to the Flask class 
is a Python predefined variable, 
which is set to the name of the module in which it is used
-passing __name__ is almost always going to configure Flask in the correct way.
-bottom import is a workaround to circular imports
"""
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models