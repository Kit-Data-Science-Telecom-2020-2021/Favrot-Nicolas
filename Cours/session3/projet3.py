# coding: utf-8

import unittest
import requests
#from bs4 import beautifulsoup

URL_PAGE2 = "https://kim.fspot.org/cours/page2.html"
URL_PAGE3 = "https://kim.fspot.org/cours/page3.html"

# 1) Ecrire une fonction get_prices_from_url() qui extrait des informations à partir des 2 pages ci-dessus.
# Exemple get_prices_from_url(URL_PAGE2) doit retourner :
# {'Personal': {'price': '$5', 'storage': '1GB', 'databases': 1},
#  'Small Business': {'price': '$25', 'storage': '10GB', 'databases': 5},
#  'Enterprise': {'price': '$45', 'storage': '100GB', 'databases': 25}}

def get_prices_from_url(url):
    prices = {}
    r = requests.get(url)
    content = r.content.decode('utf-8')
    soup = BeautifulSoup(content)
    for i in range(len(soup.find_all('h2'))):
        prix = soup.find_all('span', {'class': "pricing-table-price"})[i].text
        tab = soup.find_all('ul', {'class': "pricing-table-list"})[i]
        stor = tab.find_all('li')[3].text
        data = tab.find_all('li')[4].text        
        
        prices[soup.find_all('h2')[i].text] = {'price': re.findall('[0-9$]+', prix)[0],
                                               'storage':re.findall('[0-9A-Z]+', stor)[0],
                                              'databases': int(re.findall('[0-9]+', data)[0])}
    return prices


# 2) Ecrire une fonction qui extrait des informations sur une bière de beowulf
# Exemple URL: https://www.beerwulf.com/fr-fr/p/bieres/brouwerij-t-verzet-super-noah.33

def extract_beer_infos(url):
    r = requests.get(url)
    content = r.content.decode('utf-8')
    soup = BeautifulSoup(content)
       
    infos = {
        'name': soup.find_all('h1')[0].text,
        'note': soup.find_all('div', {'class' : "stars"})[0]['data-percent'],
        'price': re.findall('[0-9,]+',soup.find_all('span', {'class' : "price"})[0].text)[0],
        'volume': int(re.findall('[0-9]+',soup.find_all('div', {'class' : "product-subtext"})[0].text)[-1]),
    }
    return infos


import json
from multiprocessing import Pool
# Cette URL retourne un JSON avec une liste de bières
URL_BEERLIST_AUTRICHE = "https://www.beerwulf.com/fr-FR/api/search/searchProducts?country=Autriche&container=Bouteille"

# 3) Ecrire une fonction qui prend l'argument "url" retourne les informations sur une liste de bière via l'API de beowulf.
# Cette fonction doit retourner la liste des informations obtenues par la fonction extract_beer_infos() définie ci-dessus.
# Chercher comment optimiser cette fonction en utilisant multiprocessing.Pool pour paralléliser les accès web.
#
# Exemple de retour :
# [{'name': 'Engelszell Benno', 'note': 70, 'price': 4.29, 'volume': 33},
#  {'name': 'Engelszell Trappisten Weiße', 'note': 70, 'price': 3.39, 'volume': 33}
#  {'name': 'Engelszell Gregorius', 'note': 70, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Rudeen Black IPA', 'note': 80, 'price': 4.49, 'volume': 33}
#  {'name': 'Bevog Tak Pale Ale', 'note': 70, 'price': 2.79, 'volume': 33}
#  {'name': 'Brew Age Affenkönig', 'note': 70, 'price': 3.49, 'volume': 33}
#  {'name': 'Stiegl Goldbraü', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Stiegl Columbus 1492', 'note': 70, 'price': 2.49, 'volume': 33}
#  {'name': 'Brew Age Hopfenauflauf', 'note': 70, 'price': 2.99, 'volume': 33}]

def extract_beer_list_infos(url):
    data = requests.get(url)
    data = data.json()
    
    # API JSON
    #response = requests.get(f'https://api.deezer.com/artist/{artist}')
    #data = response.json()
    #data
    
    # Collecter les pages de bières à partir du JSON
    beer_pages = []
    for i in range(len(data['items'])):
        beer_pages.append('https://www.beerwulf.com' + data['items'][i]['contentReference'])
    
    # Sequential version (slow):
    #beers = []
    #for page in beer_pages:
    #    beers.append(extract_beer_infos(page))

    # Parallel version (faster):
    beers = []
    with Pool(processes=9) as pool:
        beers = pool.map(extract_beer_infos, beer_pages)
    

    return beers


class Lesson3Tests(unittest.TestCase):
    def test_01_get_prices_from_url_page2(self):
        prices = get_prices_from_url(URL_PAGE2)
        # We should have found 3 products:
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 3)
        self.assertIn('Personal', prices)
        self.assertIn('Small Business', prices)
        self.assertIn('Enterprise', prices)

        personal = prices['Personal']
        self.assertIn('price', personal)
        self.assertIn('storage', personal)
        self.assertIn('databases', personal)
        self.assertEqual(personal['price'], '$5')
        self.assertEqual(personal['storage'], '1GB')
        self.assertEqual(personal['databases'], 1)

    def test_02_get_prices_from_url_page3(self):
        prices = get_prices_from_url(URL_PAGE3)
        self.assertIsInstance(prices, dict)
        self.assertEqual(len(prices), 4)
        self.assertEqual(
            prices['Privilege'],
            {'databases': 100, 'price': '$99', 'storage': '1TB'}
        )

    def test_03_extract_beer_list_infos(self):
        infos = extract_beer_list_infos(URL_BEERLIST_AUTRICHE)
        # >Il y a 9 bières autrichiennes :
        self.assertIsInstance(infos, list)
        self.assertEqual(len(infos), 9)
        # toutes ont 33cl :
        for beer in infos:
            self.assertEqual(beer['volume'], 33)


def run_tests():
    test_suite = unittest.makeSuite(Lesson3Tests)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


if __name__ == '__main__':
    run_tests()
