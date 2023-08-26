from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return f'<User: {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    url = db.Column(db.String(400), unique=False, nullable=False)

    def __repr__(self):
        return f'<Planets: {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    url = db.Column(db.String(400), unique=False, nullable=False)
    
    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
        }


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    people = db.relationship('People')

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    planets = db.relationship('Planets')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    def __repr__(self):
        return '<Favorites %r>' % self.id

    def serialize(self):
        return {
    # Como estoy obteniendo las propiedades de objetos ya serializados, no es posible serializaros a JSON, su lugar, debe serializar los atributos del objet asi:
            "id": self.id,
            "people": {
                "id": self.people.id,
                "name": self.people.name
            },
            "planet": {
                "id": self.planets.id, 
                "name": self.planets.name
            },
            "user": {
                "id": self.user.id,
                "email": self.user.email,
            }
        }
