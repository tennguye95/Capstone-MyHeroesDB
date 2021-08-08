import requests

TOKEN = '5539203276150659'
BASE_URL = f'https://www.superheroapi.com/api/{TOKEN}'


def get_all_superhero_data(SuperHero):
    # 1-731
    id_ = 90
    while id_ <= 731:
        data = requests.get(BASE_URL + '/' + str(id_))
        superhero = data.json()
        superhero = SuperHero(id=superhero['id'], name=superhero['name'])
        superhero.save()

        print(id_)
        id_ += 1


def get_superhero(id):
    data = requests.get(BASE_URL + '/' + str(id))
    superhero = data.json()
    if superhero.get('error'):
        return {}

    return superhero


def get_powerstats(id_):

    data = requests.get(BASE_URL + '/' + str(id_) + '/powerstats')
    powerstats = data.json()
    return powerstats


def search_hero(name):
    data = requests.get(BASE_URL + '/search/' + str(name))
    superhereos = data.json()
    if superhereos.get('results') is None:
        return []
    ids = list(map(lambda x: int(x['id']), superhereos['results']))
    return ids
