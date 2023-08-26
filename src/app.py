"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ENDPOINTS PEOPLE, PLANETS
@app.route('/people', methods=['GET'])
def get_people():
    people = db.session.execute(db.select(People).order_by(People.name)).scalars()
    results = [person.serialize() for person in people]
    response_body = {
        "msg": "Hello, this is your GET/people response ",
        "result": results
    }
    return response_body, 200

@app.route('/people/<int:id>', methods=['GET'])
def get_people_id(id):
    # Obtener la data
    person = db.get_or_404(People, id)
    response_body= {"Message": "This is the person with id: " + str(id), "result": person.serialize()}
    return response_body, 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = db.session.execute(db.select(Planets).order_by(Planets.name)).scalars()
    results = [planet.serialize() for planet in planets]
    response_body = {
        "msg": "Hello, this is your GET/planet response ",
        "result": results
    }
    return response_body, 200

@app.route('/planets/<int:id>', methods=['GET'])
def get_planets_id(id):
    planet = db.get_or_404(Planets, id)
    response_body = {"Message": "This is the planet with id: " + str(id), "result": planet.serialize()}
    return response_body, 200


# ENDPOINTS USER, FAVORITES
@app.route('/users', methods=['GET'])
def get_user():
    # 1. Obtener todos los usuarios de la base de datos
    users = db.session.execute(db.select(User).order_by(User.email)).scalars()
    # 2. Obtener los datos del serialize
    result =[user.serialize() for user in users]
    # 3. Caputar respuesta
    response_body = {
        "msg": "Hello, this is your GET /user response ",
        "result": result
    }
    return response_body, 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user_id(id):
    user = db.get_or_404(User, id)
    response_body = {"Message": f"This is the user with id: {id} ", "result": user.serialize()}
    return response_body, 200

@app.route('/users/<int:id>/favorites', methods=['GET'])
def get_user_favorites(id):
    # 1. Recuperar todos loss Favoritos asociadas con el usuario cuyas user_id coincidan con el id.
    favorites = Favorites.query.filter_by(user_id=id).all() 
    favorites_serialized = [favorite.serialize() for favorite in favorites]
    return jsonify(favorites_serialized), 200


@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def handle_favorite_planet(user_id, planet_id):
    # Obtener los datos del planeta desde la solicitud JSON
    request_body = request.get_json()
    # Buscar el usuario y el planeta correspondientes en la base de datos
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)

    # Crear un nuevo registro en la tabla Favorites
    new_favorite = Favorites(user_id = user, planet_id = planet.id, name = planet.name, url = planet.url)
    db.session.add(new_favorite)
    db.session.commit()
    return {"message": "Planet added to favorites"}, 200


@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def handle_favorite_people(user_id, people_id):
    # Obtener los datos del planeta desde la solicitud JSON
    request_body = request.get_json()
    # Buscar el usuario y el planeta correspondientes en la base de datos
    user = User.query.get(user_id)
    planet = People.query.get(people_id)

    # Crear un nuevo registro en la tabla Favorites
    new_favorite = Favorites(user_id = user, people_id = people.id, name = people.name, url = people.url)
    db.session.add(new_favorite)
    db.session.commit()
    return {"message": "Planet added to favorites"}, 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # Obtener el ID del usuario actual 
    user_id = 1  # Supongamos que es el usuario con ID 1
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites"}), 200
    else:
        return jsonify({"message": "Favorite not found"}), 404


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    # Obtener el ID del usuario actual 
    user_id = 1  # Supongamos que es el usuario con ID 1
    favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "People removed from favorites"}), 200
    else:
        return jsonify({"message": "Favorite not found"}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
