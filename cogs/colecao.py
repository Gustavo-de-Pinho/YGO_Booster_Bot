import discord
from discord.ext import commands
import database
import json
import os

class ColecaoPaginator(discord.ui.View):
    def __init__(self, ctx, paginas, usuario_nome):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.paginas = paginas
        self.usuario_nome = usuario_nome
        self.indice_atual = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message("Esta coleção não é sua!", ephemeral=True)
        return False

    def criar_embed(self):
        total_paginas = len(self.paginas)
        embed = discord.Embed(
            title=f"🃏 Coleção de {self.usuario_nome}",
            description=self.paginas[self.indice_atual],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Página {self.indice_atual + 1} de {total_paginas}")
        return embed

    @discord.ui.button(label="◀ Voltar", style=discord.ButtonStyle.primary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.indice_atual > 0:
            self.indice_atual -= 1
        else:
            self.indice_atual = len(self.paginas) - 1  # Vai para a última
        await interaction.response.edit_message(embed=self.criar_embed(), view=self)

    @discord.ui.button(label="Próxima ▶", style=discord.ButtonStyle.primary)
    async def proxima(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.indice_atual < len(self.paginas) - 1:
            self.indice_atual += 1
        else:
            self.indice_atual = 0
        await interaction.response.edit_message(embed=self.criar_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


class Colecao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def buscar_detalhes_carta(self, card_id):
        for arquivo in os.listdir("."):
            if arquivo.startswith("caixa_") and arquivo.endswith(".json"):
                with open(arquivo, "r", encoding="utf-8") as f:
                    cartas = json.load(f)
                    for carta in cartas:
                        if str(carta["id"]) == str(card_id):
                            return {
                                "nome": carta.get("nome", "Carta Desconhecida"),
                                "tipo": carta.get("tipo", "Desconhecido"),
                                "raridade": carta.get("raridade", "Comum")
                            }
        return {"nome": "Carta Desconhecida", "tipo": "Desconhecido", "raridade": "Comum"}

    @commands.command(name="cards", aliases=["collection"])
    async def cartas(self, ctx):
        discord_id = str(ctx.author.id)
        
        conn = database.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT card_id, quantidade FROM inventario WHERE discord_id = ? AND quantidade > 0", (discord_id,))
        minhas_cartas = cursor.fetchall()
        conn.close()
        
        if not minhas_cartas:
            embed = discord.Embed(
                title=f"🃏 Coleção de {ctx.author.name}",
                description="Você ainda não possui nenhuma carta. Abra pacotes usando `!open`!",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)

        lista_completa = []
        for card_id, quantidade in minhas_cartas:
            detalhes = self.buscar_detalhes_carta(card_id)
            lista_completa.append({
                "quantidade": quantidade,
                "nome": detalhes["nome"],
                "tipo": detalhes["tipo"],
                "raridade": detalhes["raridade"]
            })

        hierarquia_raridade = {
            "Secret Rara": 1,
            "Ultra Rara": 2,
            "Super Rara": 3,
            "Rara": 4,
            "Comum": 5
        }

        lista_completa.sort(key=lambda x: (
            hierarquia_raridade.get(x["raridade"], 99), 
            x["nome"].lower()
        ))

        itens_por_pagina = 15
        paginas = []
        bloco_atual = ""
        
        for i, item in enumerate(lista_completa):
            bloco_atual += f"**{item['quantidade']}x** | {item['nome']} — *{item['tipo']}* `({item['raridade']})`\n"
            
            if (i + 1) % itens_por_pagina == 0 or (i + 1) == len(lista_completa):
                paginas.append(bloco_atual)
                bloco_atual = ""

        if len(paginas) == 1:
            embed = discord.Embed(
                title=f"🃏 Coleção de {ctx.author.name}",
                description=paginas[0],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Total de cartas únicas: {len(lista_completa)}")
            await ctx.send(embed=embed)
        else:
            view = ColecaoPaginator(ctx, paginas, ctx.author.name)
            embed = view.criar_embed()
            embed.set_footer(text=f"Total de cartas únicas: {len(lista_completa)} | Página 1 de {len(paginas)}")
            
            message = await ctx.send(embed=embed, view=view)
            view.message = message

async def setup(bot):
    await bot.add_cog(Colecao(bot))