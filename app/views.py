# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os

# Flask modules
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from jinja2 import TemplateNotFound

# App modules
from app import app, lm, db, bc
from app.models import User, SuperHero, Bookmarks
from app.forms import LoginForm, RegisterForm
from app.api import get_superhero, search_hero


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Logout user
@app.route('/logout.html')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search')
        return redirect(f'/index?search={search_term}')

    return render_template('search.html')


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        id1 = request.form.get('hero1')
        id2 = request.form.get('hero2')
        return redirect(f'/compare?id1={id1}&id2={id2}')

    tab_options = ['Powerstats', 'Biography', 'Appearance', 'Work', 'Connections']

    id1 = request.args.get('hero1')
    id2 = request.args.get('hero2')
    tab = request.args.get('tab', tab_options[0])

    super_hero1 = get_superhero(id=id1)
    super_hero2 = get_superhero(id=id2)
    tab_data1 = {}
    tab_data2 = {}

    if tab == tab_options[0]:
        tab_data1 = super_hero1.get('powerstats', {})
        tab_data2 = super_hero2.get('powerstats', {})
    elif tab == tab_options[1]:
        tab_data1 = super_hero1.get('biography', {})
        tab_data2 = super_hero2.get('biography', {})
    elif tab == tab_options[2]:
        tab_data1 = super_hero1.get('appearance', {})
        tab_data2 = super_hero2.get('appearance', {})
    elif tab == tab_options[3]:
        tab_data1 = super_hero1.get('work', {})
        tab_data2 = super_hero2.get('work', {})
    elif tab == tab_options[4]:
        tab_data1 = super_hero1.get('connections', {})
        tab_data2 = super_hero2.get('connections', {})

    super_heroes = SuperHero.get_all(current_user)

    return render_template('compare.html',
                           super_heroes=super_heroes,
                           tabs=tab_options,
                           tab=tab if tab is not None else tab_options[0],
                           superhero1=super_hero1,
                           superhero2=super_hero2,
                           tab_data1=tab_data1,
                           tab_data2=tab_data2)


# Register a new user
@app.route('/register.html', methods=['GET', 'POST'])
def register():

    # declare the Registration Form
    form = RegisterForm(request.form)

    msg = None
    success = False

    if request.method == 'GET':
        return render_template('accounts/register.html', form=form, msg=msg)

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():
        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 
        email = request.form.get('email', '', type=str)

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        # filter User out of database through username
        user_by_email = User.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = 'Error: User exists!'
        
        else:         

            pw_hash = bc.generate_password_hash(password)

            user = User(username, email, pw_hash)

            user.save()

            msg = 'User created, please <a href="' + url_for('login') + '">login</a>'
            success = True

    else:
        msg = 'Input error'     

    return render_template('accounts/register.html', form=form, msg=msg, success=success)


# Authenticate user
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    
    # Declare the login form
    form = LoginForm(request.form)

    # Flask message injected into the page, in case of any errors
    msg = None

    # check if both http method is POST and form is valid on submit
    if form.validate_on_submit():

        # assign form data to variables
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str) 

        # filter User out of database through username
        user = User.query.filter_by(user=username).first()

        if user:
            if bc.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template('accounts/login.html', form=form, msg=msg)


@app.route('/bookmark')
def bookmark(path=None):
    id = request.args.get('path')
    search_term = request.args.get('search')

    bookmark = Bookmarks.query.filter_by(user_id=current_user.id, superhero_id=id).all()

    if len(bookmark) == 0:
        bookmark = Bookmarks(user_id=current_user.id, superhero_id=id, value=True)
        bookmark.save()
    else:
        bookmark[0].value = not bookmark[0].value
        bookmark[0].save()

    if search_term is not None:
        return redirect(f'/{id}?search={search_term}')
    return redirect(f'/{id}')


# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    try:
        tab = request.args.get('tab')
        search_term = request.args.get('search')
        super_heroes = SuperHero.get_all(current_user)

        if search_term is not None:
            searched_ids = search_hero(search_term)
            if len(searched_ids) > 0:
                super_heroes = list(filter(lambda x: x['id'] in searched_ids, super_heroes))

        tab_options = ['Powerstats', 'Biography', 'Appearance', 'Work', 'Connections']
        if path == 'index.html' or path == 'index':
            path = super_heroes[0]['id']
        if tab is None:
            tab = tab_options[0]

        super_hero = get_superhero(id=path)
        tab_data = {}

        if tab == tab_options[0]:
            tab_data = super_hero.get('powerstats', {})
        elif tab == tab_options[1]:
            tab_data = super_hero.get('biography', {})
        elif tab == tab_options[2]:
            tab_data = super_hero.get('appearance', {})
        elif tab == tab_options[3]:
            tab_data = super_hero.get('work', {})
        elif tab == tab_options[4]:
            tab_data = super_hero.get('connections', {})

        return render_template('index.html',
                               heroes=super_heroes,
                               id=int(path),
                               tabs=tab_options,
                               tab=tab if tab is not None else tab_options[0],
                               superhero=super_hero,
                               tab_data=tab_data,
                               search_term=search_term)
    
    except:
        return render_template('index.html', heroes=super_heroes, id=1, tabs=tab_options, tab=tab if tab is not None else tab_options[0])


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
