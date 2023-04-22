import os
import discord
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import Webhook, Embed
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import cfscrape
import re
import pycountry
from pycountry_convert import country_name_to_country_alpha2
import emoji


WEBHOOK_URL = 'https://discord.com/api/webhooks/1098704908921876653/MarGN7mW0pDiP6ERbJ78OainQSiCLCjj-LuoyuinmAZ0oBbdBjuFDAoFLWX02T61f_r0'
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
    
    # Create a Cloudflare scraper object
    scraper = cfscrape.create_scraper()
    
    # Use the scraper object to get the page content
    response = scraper.get(raffle_url)

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

def extract_raffle_information(soup):
    start_date_label = "Start date"
    close_date_label = "Close date"
    type_label = "Type"
    region_label = "Region"
    retrieval_label = "Retrieval"

    start_date = soup.find("div", string=lambda text: text and text.strip() == start_date_label).find_next_sibling("div").text.strip()
    close_date = soup.find("div", string=lambda text: text and text.strip() == close_date_label).find_next_sibling("div").text.strip()
    raffle_type = soup.find("div", string=lambda text: text and text.strip() == type_label).find_next_sibling("div").text.strip()
    region = soup.find("div", string=lambda text: text and text.strip() == region_label).find_next_sibling("div").text.strip()
    retrieval = soup.find("div", string=lambda text: text and text.strip() == retrieval_label).find_next_sibling("div").text.strip()

    return start_date, close_date, raffle_type, region, retrieval


async def send_embedded_message(title, url, image_url, raffle_id, raffle_url, retailer_name):
    # Create a Cloudflare scraper object
    scraper = cfscrape.create_scraper()
    # Use the scraper object to get the page content
    raffle_response = scraper.get(raffle_url)
    raffle_soup = BeautifulSoup(raffle_response.content, "html.parser")

    # Extract the required information
    start_date, close_date, raffle_type, region, retrieval = extract_raffle_information(raffle_soup)

    embed = Embed(title=title, url=url,description=f"A new raffle for [{title}]({url}) is live!", color=0x68CD89)
    embed.set_thumbnail(url=image_url)
    
    flag_emoji=get_flag_emoji(region)
    
    
    embed.add_field(name="Region", value=f"{flag_emoji} {region}", inline=True)
    embed.add_field(name="Type", value=raffle_type, inline=True)
    embed.add_field(name="Store", value=retailer_name, inline=True)
    embed.add_field(name="Open", value=start_date, inline=True)
    embed.add_field(name="Close", value=close_date, inline=True)
    embed.add_field(name="Delivery", value=get_delivery_emoji(retrieval), inline=True)
    embed.add_field(name="Entry:", value=f"[Enter at {retailer_name}]({raffle_url})", inline=False)

    embed.set_footer(text="Suf Retriever", icon_url="https://cdn.discordapp.com/attachments/692518598241026139/1098991992085696592/download_2.png")
    embed.timestamp = datetime.utcnow()

    webhook_payload = {
        "embeds": [embed.to_dict()],
        "username": "Suf Retriever",
        "avatar_url": "https://cdn.discordapp.com/attachments/692518598241026139/1098991992085696592/download_2.png",
    }
    response = requests.post(WEBHOOK_URL, json=webhook_payload)
    response.raise_for_status()



def get_flag_emoji(region):
    region_flags = {
        "Europe": "🇪🇺",
        "Worldwide": "🌐",
    }

    # Check if the region is in the region_flags dictionary
    if region in region_flags:
        return region_flags[region]

    # If it's a country, find the corresponding flag emoji
    try:
        country_code = country_name_to_country_alpha2(region)
        flag_emoji = emoji.emojize(f":flag_{country_code.lower()}:")
        return flag_emoji
    except KeyError:
        # If the region is not found, return an empty string
        return ""

def get_delivery_emoji(retrieval):
    if retrieval.lower() == "shipping":
        return ":package: " + retrieval
    elif retrieval.lower() == "in store pickup":
        return ":door: " + retrieval
    else:
        return ":white_check_mark: " + retrieval


@tasks.loop(minutes=1)
async def check_raffles():
    new_raffles = await fetch_raffles()
    
    for product in new_raffles:
        product_name = product["name"]
        brand_slug = product["shoeBrand"]["slug"]
        model_slug = product["shoeModel"]["slug"] if product["shoeModel"] is not None else None
        product_slug = product["slug"]
        product_url = f"https://www.soleretriever.com/sneaker-release-dates/{brand_slug}/{model_slug}/{product_slug}" if model_slug is not None else None
        product_image_url = product["imageUrl"]

        for raffle in product["raffle"]:
            raffle_id = raffle["id"]
            print(f"Raffle ID's Scraped")
            if raffle_id not in raffle_ids:
                raffle_ids.add(raffle_id)
                raffle_url = f"https://www.soleretriever.com/raffles/{product_slug}/raffle/{raffle_id}" if model_slug is not None else None
                retailer_name = get_retailer_name(raffle_url) if raffle_url is not None else None
                await send_embedded_message(f"{product_name}:", product_url, product_image_url, raffle_id, raffle_url, retailer_name)


@bot.command()
async def test(ctx):
    #Test only works for Raffle URLs on the first page as those are the only ones on the Json
    test_raffle_url = "https://www.soleretriever.com/raffles/air-jordan-1-retro-high-og-washed-pink-denim-w-fd2596-600/raffle/81393"
    
    # Extract the product slug from the test_raffle_url
    match = re.search(r'raffles/(.+?)/raffle', test_raffle_url)
    if match:
        product_slug = match.group(1)
    else:
        await ctx.send("Invalid URL format.")
        return

    # Get product details from fetch_raffles()
    products = await fetch_raffles()
    test_product = None
    for product in products:
        if product_slug in product["slug"]:
            test_product = product
            break

    if test_product:
        test_product_name = test_product["name"]
        test_product_url = f"https://www.soleretriever.com/sneaker-release-dates/{test_product['shoeBrand']['slug']}/{test_product['shoeModel']['slug']}/{test_product['slug']}"
        test_image_url = test_product["imageUrl"]
        test_raffle_id = 12345

        title = f"{test_product_name}"
        test_retailer_name = get_retailer_name(test_raffle_url)
        await send_embedded_message(title, test_product_url, test_image_url, test_raffle_id, test_raffle_url, test_retailer_name)
        await ctx.send("Test webhook sent.")
    else:
        await ctx.send("Test failed.")




@check_raffles.before_loop
async def before_check_raffles():
    await bot.wait_until_ready()

bot.run(TOKEN)
