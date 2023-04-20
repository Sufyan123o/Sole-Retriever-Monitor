import os
import discord
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()
TOKEN = "Token"
CHANNEL_ID = "ChannelID"

intents = discord.Intents.default()
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


@tasks.loop(minutes=2)
async def check_raffles():
    channel = bot.get_channel(CHANNEL_ID)
    new_raffles = await fetch_raffles()
    
    for product in new_raffles:
        product_name = product["name"]
        brand_slug = product["shoeBrand"]["slug"]
        model_slug = product["shoeModel"]["slug"]
        product_slug = product["slug"]
        product_url = f"https://www.soleretriever.com/sneaker-release-dates/{brand_slug}/{model_slug}/{product_slug}"

        for raffle in product["raffle"]:
            raffle_id = raffle["id"]
            print(raffle_id)
            if raffle_id not in raffle_ids:
                raffle_ids.add(raffle_id)
                await channel.send(f"New raffle added for {product_name}: Raffle ID {raffle_id}. URL: {product_url}")


check_raffles.before_loop
async def before_check_raffles():
    await bot.wait_until_ready()

bot.run(TOKEN)
