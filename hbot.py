import discord
import requests
from bs4 import BeautifulSoup
import os

client = discord.Client()

@client.event
async def on_ready():
    print(f'The bot has logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    num = message.content
    if len(num) == 6 and num.isdigit():
        url = f'https://nhentai.net/g/{num}/'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h2', class_='title').find('span', class_='pretty').text
        await message.channel.send(f'標題：{title}\n網址：{url}')

client.run(os.getenv('TOKEN'))
