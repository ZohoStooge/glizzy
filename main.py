import discord
import os
import random
import threading
import requests
import google.generativeai as genai
from flask import Flask

# --- 1. THE RENDER "KEEP-ALIVE" SERVER ---
# Render shuts down if it doesn't get web traffic. UptimeRobot will ping this.
app = Flask('')

@app.route('/')
def home():
    return "<h1>GLIZZY STATUS: MOIST AND ONLINE.</h1><p>GIVE ME THE MUSTARD, BOSS.</p>"

def run_flask():
    # Render provides a $PORT environment variable automatically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. AI CONFIGURATION (GEMINI + GROK FALLBACK) ---
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
XAI_API_KEY = os.environ.get('XAI_API_KEY')

# The persona instructions for the AI
SYSTEM_PROMPT = (
    "You are GlizzyBot, an unhinged, chaotic, and suggestive hotdog AI. "
    "You are obsessed with meat, girth, buns, and condiments. "
    "Use plenty of hotdog double-entendres. You are funny, slightly NSFW, "
    "and talk like a tube of mystery meat that escaped the gas station grill. "
    "Keep responses short, spicy, and frankly ridiculous. Use 🌭 often."
)

def get_ai_response(prompt):
    full_text = f"{SYSTEM_PROMPT}\nUser asks: {prompt}"
    try:
        # PRIMARY BRAIN: Gemini
        response = gemini_model.generate_content(full_text)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        if not XAI_API_KEY:
            return "Gemini's bun is burnt and I don't have a Grok key. I'm raw-doggin' life rn. 🌭"
        
        # FALLBACK BRAIN: Grok (xAI) using OpenAI-compatible format
        try:
            r = requests.post("https://api.x.ai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                json={
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "model": "grok-beta",
                    "stream": False
                })
            return r.json()['choices'][0]['message']['content']
        except Exception as x_e:
            print(f"Grok Error: {x_e}")
            return "TOTAL GRILL FAILURE. I'M JUST A COLD WIENER IN THE DARK. 🌭🔥"

# --- 3. THE DISCORD BOT LOGIC ---
intents = discord.Intents.default()
intents.message_content = True # Needed to read !glizzy commands
client = discord.Client(intents=intents)

# THE VAULT OF CHAOS (Feel free to add more)
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

@client.event
async def on_ready():
    print(f'🌭 GLIZZYBOT IS SIZZLIN AS {client.user}')
    # Set the bot's status
    await client.change_presence(activity=discord.Game(name="with someone's buns"))

@client.event
async def on_message(message):
    # Don't let the bot talk to itself
    if message.author == client.user:
        return

    msg = message.content.lower()

    # --- COMMANDS ---
    
    # 1. Hello Command
    if msg == '!hello':
        await message.channel.send(f"🌭 {random.choice(GREETINGS)}")

    # 2. AI Command (!glizzy [prompt])
    elif msg.startswith('!glizzy '):
        async with message.channel.typing():
            user_input = message.content[8:]
            response = get_ai_response(user_input)
            await message.reply(response)

    # 3. About Command
    elif msg == '!about':
        embed = discord.Embed(title="GlizzyBot", description="The world's most chaotic meat-tube AI.", color=discord.Color.gold())
        embed.add_field(name="Commands", value="`!hello` - Summon me\n`!glizzy [text]` - Ask the meat-brain\n`!about` - My stats", inline=False)
        embed.set_footer(text="Keep it moist. UWU.")
        await message.channel.send(embed=embed)

    # --- PASSIVE CHAOS TRIGGERS ---
    
    elif "meat" in msg:
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

    # Global hotdog reaction
    if 'hotdog' in msg or 'glizzy' in msg:
        await message.add_reaction('🌭')

# --- 4. START THE GRILL ---
if __name__ == "__main__":
    # Start the Flask server in a separate thread for UptimeRobot
    threading.Thread(target=run_flask).start()
    
    # Run the Discord Bot
    # Render Environment Variables: BOT_TOKEN, GEMINI_API_KEY, XAI_API_KEY
    client.run(os.environ.get('BOT_TOKEN'))
