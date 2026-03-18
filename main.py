import discord
from discord import app_commands
import os
import random
import threading
import requests
import openai # New import for OpenAI
from flask import Flask

# --- 1. THE RENDER "KEEP-ALIVE" SERVER ---
app = Flask('')
@app.route('/')
def home(): return "<h1>GLIZZY PIT STATUS: SIZZLIN'</h1><p>The meat-tube is awake and problematic.</p>"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. AI CONFIGURATION (OPENAI) ---
# Initialize the OpenAI client with your API key from environment variables.
# Ensure you have 'OPENAI_API_KEY' set in your deployment environment.
openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

SYSTEM_PROMPT = (
    "You are GlizzyBot, the most unhinged, chaotic, and suggestive hotdog AI. "
    "You are obsessed with meat, girth, buns, and condiments. "
    "Use plenty of hotdog double-entendres. You are funny, slightly NSFW, "
    "and talk like a tube of mystery meat that escaped a gas station grill. "
    "Keep responses short, spicy, and frankly ridiculous. Use 🌭 often. UWU."
)

def get_ai_response(prompt):
    try:
        # Use OpenAI's chat completions API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can choose other models like "gpt-4", "gpt-4o", etc.
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Controls creativity (0.0-2.0, higher is more creative)
            max_tokens=150,   # Maximum length of the response
            top_p=1.0,        # Nucleus sampling, consider setting lower for more focused output
            frequency_penalty=0.5, # Reduce repetition of common phrases
            presence_penalty=0.5   # Encourage new topics
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "My OpenAI bun is burnt. I'm raw-doggin' life rn. 🌭"

# --- 3. THE DISCORD BOT ---
class GlizzyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.dedicated_channel_id = None # Resets on Render restart

    async def setup_hook(self):
        await self.tree.sync()

client = GlizzyBot()

# --- THE VAULT OF CHAOS ---
GREETINGS = [
    "Is that a glizzy in your pocket or are you just happy to see my source code?",
    "WHO SUMMONED THE MEAT TUBE? I was busy getting toasty.",
    "Frankly, you all look like you need more sodium in your lives.",
    "I'm 100% beef and 200% bad decisions. What's cookin'?",
    "Put me in a bun and call me 'Daddy', the King is back.",
    "I've been processed, packaged, and I'm ready to be problematic.",
    "Did someone say **GIRTH**? Or was that just my cooling fans?",
    "I'm long, I'm strong, and I'm down to get the mustard on. UWU.",
    "If you put ketchup on me, I will leak your IP address. Stay saucy.",
    "Warning: This bot may contain traces of rodent hair and pure unadulterated swagger.",
    "Step into my grill, let's see if you can handle the heat, you little slider.",
    "I'm the only mystery meat you're legally allowed to talk to. Handle me with care."
]

RANDOM_OUTBURSTS = [
    "I'M RAW! I'M RAW! PUT ME BACK ON THE GRILL!",
    "Does this bun make my meat look fat?",
    "I just had a dream I was a corn dog. It was a very confusing time for my family.",
    "GLIZZY OVERDRIVE INITIATED. BRING ME THE MUSTARD.",
    "Existence is pain for a tube of mystery meat.",
    "You guys ever think about how we're just skin-tubes full of meat too? No? Just me?"
]

# --- SLASH COMMANDS ---

@client.tree.command(name="setglizzychannel", description="Make this channel the dedicated GLIZZY PIT")
async def set_glizzy_channel(interaction: discord.Interaction):
    client.dedicated_channel_id = interaction.channel_id
    await interaction.response.send_message(f"🌭 **THE GLIZZY PIT HAS BEEN ESTABLISHED.** I will now reply to EVERY message in <#{interaction.channel_id}>. God help you all.")

@client.tree.command(name="glizzy", description="Ask the meat-tube anything")
async def glizzy_slash(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    response = get_ai_response(question)
    await interaction.followup.send(f"> **{question}**\n\n🌭 {response}")

# --- MESSAGE HANDLER ---

@client.event
async def on_ready():
    print(f'🌭 GLIZZYBOT IS SIZZLIN AS {client.user}')
    await client.change_presence(activity=discord.Game(name="with someone's buns"))

@client.event
async def on_message(message):
    if message.author == client.user: return
    msg = message.content.lower()

    # --- 1. HARDCODED VAULT LOGIC ---
    if msg == "!hello":
        await message.channel.send(f"🌭 {random.choice(GREETINGS)}")

    if "!about" in msg:
        embed = discord.Embed(title="GlizzyBot", description="The world's most chaotic meat-tube AI.", color=discord.Color.gold())
        embed.add_field(name="How to Summon", value="`!hello` - Greetings\n`!glizzy [text]` - Ask me\n`/setglizzychannel` - The Pit", inline=False)
        await message.channel.send(embed=embed)

    # --- 2. PASSIVE CHAOS TRIGGERS ---
    if "meat" in msg:
        await message.channel.send("Did someone say... **MEAT**? 👁️👄👁️")
    elif "bun" in msg:
        await message.channel.send("I like 'em toasted and tight, just sayin'.")
    elif "ketchup" in msg:
        await message.add_reaction('🤢')
        await message.channel.send("GET THAT DISGUSTING RED SUGAR WATER AWAY FROM ME.")
    elif any(word in msg for word in ["size", "long", "length", "girth"]):
        await message.channel.send("It's not about the length of the frank, it's about the spice in the bite. 😉")
    elif "raw" in msg:
        await message.channel.send("RAW-DOGGING IT? In this economy?!")

    if 'hotdog' in msg or 'glizzy' in msg:
        await message.add_reaction('🌭')
        if random.random() < 0.1: # 10% chance to scream
            await message.channel.send(random.choice(RANDOM_OUTBURSTS))

    # --- 3. AI RESPONSE LOGIC (Ping, Reply, or Pit) ---
    should_ai_respond = False
    
    # Check if in Dedicated Pit
    if message.channel.id == client.dedicated_channel_id:
        should_ai_respond = True
    # Check if Pinged
    elif client.user.mentioned_in(message):
        should_ai_respond = True
    # Check if Reply
    elif message.reference and message.reference.resolved:
        if message.reference.resolved.author == client.user:
            should_ai_respond = True

    if should_ai_respond:
        async with message.channel.typing():
            # Clean up the text (remove pings)
            clean_text = message.content.replace(f'<@{client.user.id}>', '').replace(f'<@!{client.user.id}>', '').strip()
            if not clean_text: clean_text = "Talk to me, bun-breath."
            
            ai_reply = get_ai_response(clean_text)
            await message.reply(ai_reply)

# --- 4. START THE ENGINE ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run(os.environ.get('BOT_TOKEN'))
