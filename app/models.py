from app import db

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.String(64))
    time = db.Column(db.String(64))
    temperature = db.Column(db.String(64))

    def __repr__(self):
        return '<Recipe for {}>'.format(self.food)