import discord
import os
import random
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Set up the bot with necessary intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# A list of hotdog-themed greetings
GREETINGS = [
    "GlizzyBot is in the house! What's cookin'?",
    "The grill is hot and the dogs are ready. GlizzyBot at your service!",
    "Who dares to summon the Glizzy Gladiator?",
    "Bun-believably good to see you all!",
    "Frankly, I'm the best bot in this server.",
]

@client.event
async def on_ready():
    """Prints a confirmation message to the console when the bot is online."""
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    """
    This function is called whenever a message is sent in a channel the bot can see.
    """
    if message.author == client.user:
        return

    # A friendly greeting
    if message.content.lower() == '!hello':
        await message.channel.send(random.choice(GREETINGS))

    # Responds with a hotdog emoji
    if 'hotdog' in message.content.lower() or 'glizzy' in message.content.lower():
        await message.add_reaction('🌭')

    # A fun "about" command
    if message.content.lower() == '!about':
        embed = discord.Embed(
            title="GlizzyBot",
            description="The finest hotdog-flavored AI in all of Discord.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Commands", value="!hello - Say hi to the GlizzyBot\n!about - Learn more about me", inline=False)
        embed.set_footer(text="Keep it saucy!")
        await message.channel.send(embed=embed)

# Run the bot
client.run(TOKEN)
