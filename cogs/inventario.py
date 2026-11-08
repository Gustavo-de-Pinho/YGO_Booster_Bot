import discord
from discord.ext import commands
import database

# Importamos os metadados da loja para pegar o nome e emoji das caixas
from cogs.loja import CAIXAS_METADADOS

class Inventario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inventory", aliases=["boosters"])
    async def inventario(self, ctx):
        discord_id = str(ctx.author.id)
        database.registrar_usuario_se_necessario(discord_id)
        
        # Busca no banco apenas os boosters que o usuário tem mais de 0
        conn = database.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT caixa_id, quantidade FROM boosters WHERE discord_id = ? AND quantidade > 0", (discord_id,))
        meus_boosters = cursor.fetchall()
        conn.close()
        
        embed = discord.Embed(
            title=f"🎒 Inventário de {ctx.author.name}",
            description="Aqui estão seus pacotes fechados prontos para abrir!",
            color=discord.Color.orange()
        )
        
        if not meus_boosters:
            embed.add_field(
                name="Vazio", 
                value="Você não possui nenhum booster. Compre alguns na `!shop`!", 
                inline=False
            )
        else:
            for caixa_id, quantidade in meus_boosters:
                # Tenta pegar os dados da caixa na loja; se for uma caixa antiga/removida, usa dados genéricos
                caixa_info = CAIXAS_METADADOS.get(caixa_id, {"nome": "Coleção Desconhecida", "emoji": "📦"})
                
                embed.add_field(
                    name=f"{caixa_info['emoji']} {caixa_info['nome']} (ID: {caixa_id})",
                    value=f"Quantidade: **{quantidade}x** pacotes",
                    inline=False
                )
                
        embed.set_footer(text="Use !open <id> para abrir um pacote.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventario(bot))