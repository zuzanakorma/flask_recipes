import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'something'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3

"""
The SQLALCHEMY_TRACK_MODIFICATIONS configuration option is set to False 
to disable a feature of Flask-SQLAlchemy that I do not need, 
which is to signal the application every time a change is about to be made 
in the database.
"""