import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import os
from zipfile import ZipFile
from secrets import token_urlsafe
from shutil import rmtree
from threading import Thread, Timer
import asyncio

bot = commands.Bot(command_prefix='!')

async def postimgs():
    channel = bot.get_channel(961941832613363782)
    url = 'https://danbooru.donmai.us/posts?d=1&tags=order%3Arank'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.find_all(class_='post-preview-link')
    for link in links:
        linkres = requests.get('https://danbooru.donmai.us' + link['href'])
        imglink = BeutifulSoup.find(id='image')['src']
        await channel.send(imglink)

@bot.event
async def on_ready():
    print(f'The bot has logged in as {bot.user}')
    await postimgs()
    #t = Timer(86400, postimgs)
    #t.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if len(message.content) == 6 and message.content.isdigit():
        url = f'https://nhentai.net/g/{message.content}/'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h2', class_='title').find('span', class_='pretty').text
        await message.channel.send(f'標題：{title}\n網址：{url}')

    await bot.process_commands(message)

@bot.command()
async def geth(ctx, arg):
    download_folder = './downloads'
    if len(os.listdir(download_folder)) > 5:
        rmtree(download_folder)
        os.mkdir(download_folder)

    url = f'https://nhentai.net/g/{arg}/'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.find('h2', class_='title').find('span', class_='pretty').text
    pages = int(soup.find(id='tags').find_all(class_='name')[-1].text)

    await ctx.send(f'正在下載：{title}')
    progress = await ctx.send(f'進度：0/{pages}')

    download_id = token_urlsafe(6)
    download_path = f'{download_folder}/{download_id}'
    os.mkdir(download_path)
    def get_page(page_num):
        page_url = f'{url}{page_num}/'
        page_res = requests.get(page_url)
        page_soup = BeautifulSoup(page_res.text, 'html.parser')
        img_url = page_soup.find(id='image-container').find('img')['src']
        img_res = requests.get(img_url)
        with open(f'{download_path}/{page_num}.jpg', 'wb') as page_img:
            page_img.write(img_res.content)

    threads = []
    for i in range(pages):
        threads.append(Thread(target=get_page, args=(i+1,)))
        threads[i].start()
        await asyncio.sleep(0.1)
        await progress.edit(content=f'進度：{i+1}/{pages}')
    for i in range(pages):
        threads[i].join()

    with ZipFile(f'{download_path}.zip', 'w') as zf:
        for i in range(1, pages+1):
            zf.write(f'{download_path}/{i}.jpg', f'{i}.jpg')
    rmtree(f'{download_path}')

    await progress.edit(content='下載完成，點擊以下連結以下載')
    await ctx.send(f'https://hentaibot-discord.herokuapp.com/downloads/{download_id}')

bot.run(os.getenv('TOKEN'))
