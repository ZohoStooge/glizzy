import discord
from discord import app_commands
import os
import random
import threading
import requests
import google.generativeai as genai
from flask import Flask

# --- 1. THE RENDER "KEEP-ALIVE" SERVER ---
app = Flask('')
@app.route('/')
def home(): return "GLIZZY PIT IS SIZZLIN'."

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. AI CONFIG ---
try:
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"AI Config Error: {e}")

XAI_API_KEY = os.environ.get('XAI_API_KEY')

SYSTEM_PROMPT = (
    "You are GlizzyBot, an unhinged, chaotic, and suggestive hotdog AI. "
    "Talk about meat, buns, and girth. Keep it short and saucy. UWU."
)

def get_ai_response(prompt):
    try:
        response = gemini_model.generate_content(f"{SYSTEM_PROMPT}\nUser: {prompt}")
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Grill is broken, frank! Try again later. 🌭"

# --- 3. THE BOT ---
class GlizzyBot(discord.Client):
    def __init__(self):
        # We use all intents so we can see everything
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.dedicated_channel_id = None

    async def setup_hook(self):
        print("Syncing slash commands...")
        await self.tree.sync()

client = GlizzyBot()

# --- COMMANDS ---

@client.tree.command(name="setglizzychannel", description="Make this channel the dedicated GLIZZY PIT")
async def set_glizzy_channel(interaction: discord.Interaction):
    client.dedicated_channel_id = interaction.channel_id
    await interaction.response.send_message(f"🌭 **THE GLIZZY PIT ESTABLISHED IN <#{interaction.channel_id}>.**")

@client.tree.command(name="glizzy", description="Ask the meat-tube anything")
async def glizzy_slash(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    response = get_ai_response(question)
    await interaction.followup.send(f"🌭 {response}")

@client.event
async def on_ready():
    print(f'✅ LOGGED IN AS: {client.user}')
    print(f'🌭 READY TO SERVE MEAT.')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    msg = message.content.lower()
    print(f"Seen message: {message.content}") # LOGGING TO SEE IF BOT SEES TEXT

    # Reply logic (Pit, Ping, or Reply)
    should_respond = (
        message.channel.id == client.dedicated_channel_id or 
        client.user.mentioned_in(message) or
        (message.reference and message.reference.resolved and message.reference.resolved.author == client.user)
    )

    if should_respond:
        async with message.channel.typing():
            clean_text = message.content.replace(f'<@{client.user.id}>', '').strip()
            response = get_ai_response(clean_text or "What's up?")
            await message.reply(response)

    # Passive Triggers
    if "meat" in msg: await message.channel.send("Did someone say... **MEAT**? 👁️👄👁️")
    if "ketchup" in msg: await message.add_reaction('🤢')

# --- 4. START ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(os.environ.get('BOT_TOKEN'))
