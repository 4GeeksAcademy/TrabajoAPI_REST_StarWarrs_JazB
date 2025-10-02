from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///starwars.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Modelos
#Modelo de Usuario
class User(db.Model):
    __tablename__ = "users"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def serialize(self):
        return {"id": self.id, "name": self.name}

#Modelo de Personajes
class People(db.Model):
    __tablename__ = "people"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def serialize(self):
        return {"id": self.id, "name": self.name}

#Modelo de planetas
class Planet(db.Model):
    __tablename__ = "planets"
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def serialize(self):
        return {"id": self.id, "name": self.name}

#Modelo de los Personajes favoritos
class FavoritePeople(db.Model):
    __tablename__ = "favorite_people"
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)

    def serialize(self):
        return {"id": self.id, "user_id": self.user_id, "people_id": self.people_id}

#Modelo de los Planetas favoritos
class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planets"
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planets.id"), nullable=False)

    def serialize(self):
        return {"id": self.id, "user_id": self.user_id, "planet_id": self.planet_id}



# Helpers

def current_user_id():
    """Simula el usuario actual, por defecto el id=1"""
    return int(request.args.get("user_id", 1))



# Endpoints

# People
@app.route("/people", methods=["GET"])
def list_people():
    return jsonify([p.serialize() for p in People.query.all()])

@app.route("/people/<int:people_id>", methods=["GET"])
def get_person(people_id):
    person = People.query.get_or_404(people_id)
    return jsonify(person.serialize())


# Planets
@app.route("/planets", methods=["GET"])
def list_planets():
    return jsonify([p.serialize() for p in Planet.query.all()])

@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize())


# Users
@app.route("/users", methods=["GET"])
def list_users():
    return jsonify([u.serialize() for u in User.query.all()])


# Favorites del usuario actual
@app.route("/users/favorites", methods=["GET"])
def list_favorites():
    uid = current_user_id()
    fav_people  = [f.serialize() for f in FavoritePeople.query.filter_by(user_id=uid)]
    fav_planets = [f.serialize() for f in FavoritePlanet.query.filter_by(user_id=uid)]
    return jsonify({"people": fav_people, "planets": fav_planets})


# Añadir favoritos
@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_fav_person(people_id):
    uid = current_user_id()
    fav = FavoritePeople(user_id=uid, people_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_fav_planet(planet_id):
    uid = current_user_id()
    fav = FavoritePlanet(user_id=uid, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.serialize()), 201


# Eliminar favoritos
@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def delete_fav_person(people_id):
    uid = current_user_id()
    fav = FavoritePeople.query.filter_by(user_id=uid, people_id=people_id).first()
    if not fav:
        abort(404, "Favorito no encontrado")
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Eliminado"}), 200

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_fav_planet(planet_id):
    uid = current_user_id()
    fav = FavoritePlanet.query.filter_by(user_id=uid, planet_id=planet_id).first()
    if not fav:
        abort(404, "Favorito no encontrado")
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Eliminado"}), 200



# Inicialización

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Datos iniciales de ejemplo
        if User.query.count() == 0:
            db.session.add_all([User(name="Jazmin"), User(name="Pablo")])
        if People.query.count() == 0:
            db.session.add_all([People(name="Luke Skywalker"), People(name="Darth Vader")])
        if Planet.query.count() == 0:
            db.session.add_all([Planet(name="Tatooine"), Planet(name="Alderaan")])
        db.session.commit()

    app.run(debug=True)
