
import requests
from bs4 import BeautifulSoup

def obtener_tarifas():
    url = 'https://www.mk-group.co.jp/osaka/hire/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    tarifas = {
        "sedan": 6500,
        "alphard": 0,
        "hiace": 0,
        "bus": 0
    }
    return tarifas
