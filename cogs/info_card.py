import discord
from discord.ext import commands
import json
import os

class InfoCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # O asterisco (*) em `nome_carta` permite que o bot leia nomes com espaços (Ex: Blue-Eyes White Dragon)
    @commands.command(name="info-card", aliases=["infocard"])
    async def info_card(self, ctx, *, nome_carta: str = None):
        if nome_carta is None:
            return await ctx.send("❌ Tem de informar o nome da carta! Exemplo: `!info-card Dark Magician`")
            
        carta_encontrada = None
        
        # Procura a carta em todos os ficheiros de caixa JSON na raiz
        for arquivo in os.listdir("."):
            if arquivo.startswith("caixa_") and arquivo.endswith(".json"):
                try:
                    with open(arquivo, "r", encoding="utf-8") as f:
                        cartas = json.load(f)
                        for carta in cartas:
                            # Busca ignorando maiúsculas/minúsculas e permitindo partes do nome
                            if nome_carta.lower() in carta.get("nome", "").lower():
                                carta_encontrada = carta
                                break
                except Exception:
                    continue
            if carta_encontrada:
                break
                
        if not carta_encontrada:
            return await ctx.send(f"❌ Não encontrei nenhuma carta com o nome `{nome_carta}`.")
            
        # Puxa os dados da carta
        nome = carta_encontrada.get("nome", "Desconhecida")
        raridade = carta_encontrada.get("raridade", "Comum")
        tipo = carta_encontrada.get("tipo", "Desconhecido")
        card_id = str(carta_encontrada.get("id"))
        
        # URL oficial da API do YGOPRODeck baseada no ID
        imagem_url = f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"
        
        embed = discord.Embed(
            title=nome,
            color=discord.Color.dark_theme()
        )
        embed.add_field(name="Raridade", value=f"`{raridade}`", inline=True)
        embed.add_field(name="Tipo", value=f"*{tipo}*", inline=True)
        
        embed.set_image(url=imagem_url)
        embed.set_footer(text=f"ID: {card_id}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoCard(bot))