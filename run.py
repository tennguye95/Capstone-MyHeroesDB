from app import app, db
from app.models import SuperHero
from app.api import get_all_superhero_data

get_all_superhero_data(SuperHero)
# SuperHero.get_all()
