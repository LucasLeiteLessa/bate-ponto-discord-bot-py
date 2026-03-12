import asyncio
import discord
from discord.ext import commands

from config import BOT_TOKEN
from database.sqlite import SQLiteManager

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    description="FlowRP — Sistema de Bate-Ponto",
)

bot.db = SQLiteManager()

COGS = [
    "cogs.configuracao",
    "cogs.ponto",
    "cogs.relatorio",
]


@bot.event
async def on_ready():
    print(f"[FlowRP] Bot conectado como {bot.user} ({bot.user.id})")
    print(f"[FlowRP] Servidores: {len(bot.guilds)}")

    try:
        synced = await bot.tree.sync()
        print(f"[FlowRP] {len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        print(f"[FlowRP] Erro ao sincronizar comandos: {e}")


async def main():
    async with bot:
        for cog in COGS:
            await bot.load_extension(cog)
            print(f"[FlowRP] Cog carregada: {cog}")
        await bot.start(BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
