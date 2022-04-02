import requests
from time import sleep

while True:
    sleep(10*60*60)
    requests.get('https://hentaibot-discord.herokuapp.com/')
