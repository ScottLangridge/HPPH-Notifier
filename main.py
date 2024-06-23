from bs4 import BeautifulSoup
import requests
import re
from time import sleep

from secrets import secrets


def get_film_links():
    content = requests.get(secrets["url"]).content
    soup = BeautifulSoup(content, 'html.parser')
    film_links = [i.attrs["href"] for i in soup.find_all('a', href=re.compile(r'https:\/\/hpph\.co\.uk\/films\/.+'))]

    return set(film_links)


def notify(film_link):
    content = requests.get(film_link, 'html.parser').content
    soup = BeautifulSoup(content, 'html.parser')

    film_title = clean_text(soup.find('h1').contents[0].text)
    film_desc_main = clean_text(soup.find('h3', class_="type-xs-mono", string="Details").find_previous('div', class_='bg-yellow').find('div', class_="type-regular").text)

    title = "New at HPPH: '" + film_title + "'"
    msg = film_desc_main + "\n\n" + film_link

    url = 'https://api.pushover.net/1/messages.json'
    post_data = {'user': secrets["user_token"], 'token': secrets["api_token"], 'title': title, 'message': msg}

    response = requests.post(url, data=post_data)
    print(response)

def clean_text(text):
    return text.replace('&nbsp', '').strip()


def main_loop():
    seen_films = set()

    while True:
        try:
            fetched_films = get_film_links()
            unseen_films = fetched_films - seen_films
            seen_films.update(unseen_films)
            while unseen_films:
                notify(unseen_films.pop())

        except:
            pass

            sleep(60)


main_loop()
