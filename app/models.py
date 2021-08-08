# -*- encoding: utf-8 -*-

from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))

    def __init__(self, user, email, password):
        self.user = user
        self.password = password
        self.email = email

    def __repr__(self):
        return str(self.id) + ' - ' + str(self.user)

    def save(self):

        # inject self into db session    
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self 


class SuperHero(db.Model):

    __tablename__ = 'superhero'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def save(self):

        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self

    @staticmethod
    def get_all(user):
        super_heroes = SuperHero.query.all()
        super_heroes_list = []

        bookmarks = Bookmarks.query.filter_by(user_id=user.id, value=True).all()
        bookmark_superheros = []
        if len(bookmarks) > 0:
            bookmark_superheros = list(map(lambda x: x.superhero_id, bookmarks))

        for super_hero in super_heroes:
            if super_hero.id in bookmark_superheros:
                super_heroes_list.append({'id': super_hero.id, 'name': super_hero.name, 'bookmark': True})
            else:
                super_heroes_list.append({'id': super_hero.id, 'name': super_hero.name})

        return super_heroes_list


class Bookmarks(db.Model):

    __tablename__ = 'bookmarks'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    superhero_id = db.Column(db.Integer, db.ForeignKey('superhero.id'), primary_key=True)
    value = db.Column(db.Boolean)

    def __init__(self, user_id, superhero_id, value):
        self.user_id = user_id
        self.superhero_id = superhero_id
        self.value = value

    def save(self):

        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self
