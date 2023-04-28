import json, os, time, discord, threading, datetime, requests
from discord_webhook import DiscordEmbed, DiscordWebhook

intents = discord.Intents().all()
client = discord.Bot(intents = intents)

with open(os.getcwd() + '/Config.json') as f:
    data = json.load(f)
    region_list = data['region_list']
    bot_token = data['bot_token']
    embed_footer_text = data['embed_footer_text']
    embed_author_url = data['embed_author_url']
    embed_color = data['embed_color']
    webhook_url = data['webhook_url']
    delay = data['monitor_delay']

with open(os.getcwd() + '/Region_emoji.json') as f:
    region_emoji = json.load(f)

def get_raffles(region):
    product_data = []
    headers = {
        'Pragma': 'no-cache',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Host': 'www.soleretriever.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    }

    params = {
        'term': '',
        'from': '0',
        'limit': '24',
        'locales': region.upper(),
        'types': '',
        'isHideEntered': 'true',
    }

    response = requests.get('https://www.soleretriever.com/api/products/raffles', params=params, headers=headers)
    if response.status_code == 200:
        data_json = json.loads(response.text)
        for product in data_json['products']:
            product_slug = product['slug']
            for raffle in product['raffle']:
                product_raffle = str(raffle['id'])
                product_data.append([product_slug, product_raffle])
    
    return product_data

def get_raffle_details(product_data, region_data):
    headers = {
        'Pragma': 'no-cache',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'Host': 'www.soleretriever.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
    }

    response = requests.get(
        f'https://www.soleretriever.com/raffles/{str(product_data[0])}/raffle/{str(product_data[1])}',
        headers=headers,
    )

    if response.status_code == 200:
        response_data = response.text.split('<script id="__NEXT_DATA__" type="application/json">')[1].split('</script>')[0]
        data_json = json.loads(response_data)['props']['pageProps']['raffleData']

        raffle_url = data_json['url']
        raffle_type = data_json['type']
        raffle_pickup = data_json['isPickup']
        raffle_shipping = data_json['hasPostage']
        raffle_end = data_json['endDate']
        product_sku = data_json['product']['pid']
        product_name = data_json['product']['name']
        product_image = data_json['product']['imageUrl']
        raffle_store= data_json['retailer']['name']

        webhook = DiscordWebhook(url = webhook_url)
        embed = DiscordEmbed(title = f'{str(product_name)}', url = f'https://www.soleretriever.com/raffles/{str(product_data[0])}/raffle/{str(product_data[1])}', color = int(embed_color), description=f'> New Raffle Live For {str(region_emoji[region_data]["name"])} :{str(region_emoji[region_data]["flag"])}:')
        embed.set_thumbnail(url = product_image)
        embed.set_footer(text = f'SoleRetriever Monitor by {embed_footer_text} \U000000B7 {datetime.datetime.now()}')
        embed.add_embed_field(name = 'Product SKU: ', value = f'`{product_sku}`')

        if raffle_type == 'In app':
            embed.add_embed_field(name = 'Raffle Type: ', value = 'In App :mobile_phone:')
        elif raffle_type == 'Online':
            embed.add_embed_field(name = 'Raffle Type: ', value = 'Online :desktop:')
        elif raffle_type == 'In store':
            embed.add_embed_field(name = 'Raffle Type: ', value = 'Instore :shopping_cart:')
        
        if raffle_pickup == True:
            embed.add_embed_field(name = 'Delivery:', value = 'Instore Pickup :door:')
        if raffle_shipping == True:
            embed.add_embed_field(name = 'Delivery:', value = 'Shipping :package:')

        embed.add_embed_field(name = 'Store:', value = raffle_store)
        embed.add_embed_field(name = 'Closing: ', value = f'<t:{str(int(datetime.datetime.fromisoformat(raffle_end).timestamp())).split(".")[0]}>')
        embed.add_embed_field(name = 'Entry:', value = f'[ENTER HERE]({raffle_url})')
        embed.add_embed_field(name = 'Links:', value = f'[Restocks](https://restocks.net/en/shop/?q={product_sku}) | [StockX](https://stockx.com/search?s={product_sku}) | [Goat](https://www.goat.com/search?query={product_sku}) | [FlightClub](https://www.flightclub.com/catalogsearch/result?query={product_sku})', inline=False)
        webhook.add_embed(embed)
        webhook.execute()

        return

@client.event
async def on_ready():
    print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f] Bot Is Ready"))

    for region in region_list:
        print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f | Region: {region}] Starting..."))
        with open(os.getcwd() + '/Region_emoji.json') as f:
            region_emoji = json.load(f)
        region_data = region_emoji[region]
        t1 = threading.Thread(target=main, args=(region,region_data)).start()

def main(region,region_data):
    initial_data = get_raffles(region)
    while True:
        monitor_data = get_raffles(region)

        if monitor_data != initial_data:
            for raffle in monitor_data:
                if raffle not in initial_data:
                    get_raffle_details(raffle, region_data)
                    print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f | Region: {region}] New Raffle Live: {raffle[0]}"))
                
                time.sleep(3)
                    
            initial_data = monitor_data
            
        else:
            print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f | Region: {region}] Waiting For New Raffles"))

        time.sleep(delay)

@client.slash_command(description = 'Command To Test Webhook')
async def webhook_test(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    try:
        raffle = get_raffles(region_list[0])
        get_raffle_details(raffle[0], region_list[0])
        await ctx.respond('Testing Succesful', ephemeral=True)
        print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f | Region: {region_list[0]}] Successfully Send Testing Webhook"))
    
    except Exception as e:
        await ctx.respond(f'Error: {str(e)}', ephemeral=True)
        print(datetime.datetime.now().strftime(f"[%d %B %Y %H:%M:%S.%f | Region: {region_list[0]}] Error Sending Testing Webhook. Error: {str(e)}"))

@client.event
async def on_message(message: discord.Message):
    if message.channel.id == 1100043271503351858:
        try:
            await message.add_reaction("✅")
        except:
            pass
    else:
        pass

client.run(data['bot_token'])
