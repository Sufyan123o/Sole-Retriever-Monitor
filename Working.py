import os
import discord
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import Webhook, Embed
from bs4 import BeautifulSoup

WEBHOOK_URL = 'https://discord.com/api/webhooks/1048945739549646868/6ElsmKgDBq8gAMtZbE4iNg3CK72riIZeemwzvSFHLjUyMCAnOKeF87khtbqJRXhRqEZK'
load_dotenv()
TOKEN = "MTA5ODUxNDExNDk0MDI1NjMxNg.GlNzHh.Nk6LG1wI_oMxi72nelCT1tS6AJo_jMDoV9xg64" #token
# CHANNEL_ID = 692518598241026139

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

raffle_ids = set()

async def initialize_raffle_ids():
    initial_raffles = await fetch_raffles()
    for product in initial_raffles:
        for raffle in product["raffle"]:
            raffle_id = raffle["id"]
            raffle_ids.add(raffle_id)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await initialize_raffle_ids() 
    check_raffles.start()

def get_retailer_name(raffle_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134"
    }
    response = requests.get(raffle_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch raffle page at {raffle_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    retailer_name_element = soup.find('a', class_="flex items-center")

    if retailer_name_element is not None:
        retailer_name = retailer_name_element.find('h2').text.replace("Raffle by ", "").strip()
        return retailer_name
    else:
        print("Failed to find retailer name.")
        return None



async def fetch_raffles():
    url = "https://www.soleretriever.com/api/products/raffles?term=&from=0&limit=24&locales=&types=&isHideEntered=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    try:
        response.raise_for_status()
        if response.text:
            data = json.loads(response.text)
            products = data["products"]
            return products
        else:
            print("Error fetching raffles: Empty response.")
            return []
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching raffles: {e}")
        return []

async def send_embedded_message(title, url, image_url, raffle_id, raffle_url, retailer_name):
    embed = Embed(title=title, url=url, color=0x68CD89)
    embed.set_thumbnail(url=image_url)
    embed.add_field(name="Link to Raffle", value=f"[Click Here]({raffle_url})", inline=False)
    
    if retailer_name:
        retailer_json_url = f"https://www.soleretriever.com/_next/data/Z0fVbS63e3_w88fKhphiU/retailers/{retailer_name.lower().replace(' ', '-')}.json?slug={retailer_name.lower().replace(' ', '-')}"
        embed.add_field(name="Retailer", value=f"{retailer_name} - [Retailer JSON URL]({retailer_json_url})", inline=False)
    else:
        embed.add_field(name="Retailer", value="Not found", inline=False)
    
    webhook_payload = {
        "embeds": [embed.to_dict()]
    }
    response = requests.post(WEBHOOK_URL, json=webhook_payload)
    response.raise_for_status()


@tasks.loop(minutes=1)
async def check_raffles():
    new_raffles = await fetch_raffles()
    count = 0
    for product in new_raffles:
        product_name = product["name"]
        brand_slug = product["shoeBrand"]["slug"]
        model_slug = product["shoeModel"]["slug"] if product["shoeModel"] is not None else None
        product_slug = product["slug"]
        product_url = f"https://www.soleretriever.com/sneaker-release-dates/{brand_slug}/{model_slug}/{product_slug}" if model_slug is not None else None
        product_image_url = product["imageUrl"]

        for raffle in product["raffle"]:
            raffle_id = raffle["id"]
            count +=1
            print(f"Raffle ID's Scraped, {count}")
            if raffle_id not in raffle_ids:
                raffle_ids.add(raffle_id)
                raffle_url = f"https://www.soleretriever.com/raffles/{product_slug}/raffle/{raffle_id}" if model_slug is not None else None
                retailer_name = get_retailer_name(raffle_url) if raffle_url is not None else None
                await send_embedded_message(f"New raffle added for {product_name}:", product_url, product_image_url, raffle_id, raffle_url, retailer_name)


@bot.command()
async def test(ctx):
    test_raffle_url = "https://www.soleretriever.com/raffles/air-jordan-1-retro-high-og-washed-pink-denim-w-fd2596-600/raffle/81393"

    test_retailer_name = get_retailer_name(test_raffle_url)

    # Get product details from fetch_raffles()
    products = await fetch_raffles()
    test_product = None
    for product in products:
        if "air-jordan-1-retro-high-og-washed-pink-denim-w-fd2596-600" in product["slug"]:
            test_product = product
            break

    if test_product:
        test_product_name = test_product["name"]
        test_product_url = f"https://www.soleretriever.com/sneaker-release-dates/{test_product['shoeBrand']['slug']}/{test_product['shoeModel']['slug']}/{test_product['slug']}"
        test_image_url = test_product["imageUrl"]
        test_raffle_id = 12345

        title = f"{test_product_name} - Retailer: {test_retailer_name}"
        await send_embedded_message(title, test_product_url, test_image_url, test_raffle_id, test_raffle_url, test_retailer_name)
        await ctx.send("Test webhook sent.")
    else:
        await ctx.send("Test failed.")



@check_raffles.before_loop
async def before_check_raffles():
    await bot.wait_until_ready()

bot.run(TOKEN)