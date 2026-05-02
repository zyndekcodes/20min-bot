import discord
from dotenv import load_dotenv
import os

from storage import load_data, save_data
from commands import handle_command

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

state = load_data()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith("!"):
        return

    conteudo = message.content.removeprefix("!")
    parts = conteudo.split()

    cmd = parts[0].lower()
    args = parts[1:]

    user = str(message.author.id)

    result = handle_command(cmd, args, state, user)

    if result:
        save_data(state)
        await message.channel.send(result)


client.run(token)