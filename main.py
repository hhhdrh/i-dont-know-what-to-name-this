import discord
import json
from discord.ext import tasks
from discord.ext import commands
import requests
import asyncio
import math

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

data_url = "https://mps.geo-fs.com/map"
geocode_url = "https://nominatim.openstreetmap.org/reverse"

headers = {
    'User-Agent': 'GeoFS-User-Lookup/1.0 email@example.com'  # Replace with your actual email
}

triggers = ["[UTP]", "[U]"]
target_countries = ["România", "Moldova"]

cooldown = False

async def check_utp_users(channel: discord.TextChannel):
    try:
        response = requests.get(data_url)
        data = response.json()
        users = data.get("users", [])

        for user in users:
            cs = user.get("cs", "")

            if any(trigger in cs for trigger in triggers):
                coords = user.get("co", [])
                if len(coords) < 2:
                    continue

                lat, lon = coords[0], coords[1]

                # Reverse geocode
                params = {
                    'format': 'json',
                    'lat': lat,
                    'lon': lon,
                    'zoom': 10,
                    'addressdetails': 1
                }

                geo_response = requests.get(geocode_url, params=params, headers=headers)
                geo_data = geo_response.json()
                address = geo_data.get("address", {})
                country = address.get("country", "Unknown")

                if country in target_countries:
                    cooldown = False
                    if cooldown == False:
                        cooldown = True
                        try:
                            embed = discord.Embed(
                                title="SCRAMBLE SCRAMBLE SCRAMBLE!!",
                                description=f"**``{cs}`` is in ``{country}!!``**",
                                color=discord.Color.blurple()
                            )

                            
                            embed.add_field(name="UTP Information:",
                                            value=f"**Name: ``{user["cs"]}``**\n**Account id: ``{user["acid"]}``**")
                            embed.set_footer(text="Test scramble bot")
                            messageToSend = f"@here SCRAMBLE SCRAMBLE!!"
                            await channel.send(embed=embed)
                            await channel.send(messageToSend)
                        finally:
                            await asyncio.sleep(10)
                            cooldown = False

                await asyncio.sleep(1)  # Respect API limit

    except Exception as e:
        print(e)

@tasks.loop(seconds=5)
async def auto_check_utp():
    channel = bot.get_channel(1412854335481839777) # Set to your channel's id
    await check_utp_users(channel)

@bot.event
async def on_ready():
    auto_check_utp.start()

bot.run("token")
