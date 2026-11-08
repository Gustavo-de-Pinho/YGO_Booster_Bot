import discord
from discord.ext import commands
import asyncio
import database
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    database.configurar_banco()
    print(f"Bot conectado como {bot.user} e Banco de Dados pronto!")

async def main():
    async with bot:
        # Carrega os comandos da pasta cogs/
        await bot.load_extension("cogs.economia")
        await bot.load_extension("cogs.loja")
        await bot.load_extension("cogs.inventario")
        await bot.load_extension("cogs.abrir")
        await bot.load_extension("cogs.colecao")
        await bot.load_extension("cogs.info_card") 

        if os.path.exists("token.txt"):
            with open("token.txt", "r", encoding="utf-8") as f:
                TOKEN = f.read().strip()
        else:
            TOKEN = "COLE_O_TOKEN_AQUI_APENAS_PARA_LOCAL_OU_USE_ENV"
    
        await bot.start("TOKEN")

# Inicia o loop assíncrono
if __name__ == "__main__":
    asyncio.run(main())