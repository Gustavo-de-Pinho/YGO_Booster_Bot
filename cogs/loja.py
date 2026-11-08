import discord
from discord.ext import commands
import database
import json
import os

# Metadados das caixas disponíveis na loja
CAIXAS_METADADOS = {
    "1": {"nome": "Legend of Blue Eyes White Dragon", "emoji": "📦", "preco": 100}
}

class CaixaInfoPaginator(discord.ui.View):
    def __init__(self, ctx, paginas, caixa_nome, emoji):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.paginas = paginas
        self.caixa_nome = caixa_nome
        self.emoji = emoji
        self.indice_atual = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message("Esta interação não é sua!", ephemeral=True)
        return False

    def criar_embed(self):
        total_paginas = len(self.paginas)
        embed = discord.Embed(
            title=f"{self.emoji} {self.caixa_nome}",
            description=self.paginas[self.indice_atual],
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Página {self.indice_atual + 1} de {total_paginas}")
        return embed

    @discord.ui.button(label="◀ Voltar", style=discord.ButtonStyle.primary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.indice_atual > 0:
            self.indice_atual -= 1
        else:
            self.indice_atual = len(self.paginas) - 1
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

class ConfirmacaoCompra(discord.ui.View):
    def __init__(self, ctx, caixa_id, quantidade, preco_total):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.caixa_id = caixa_id
        self.quantidade = quantidade
        self.preco_total = preco_total

    @discord.ui.button(label="Sim, comprar", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Esta compra não é sua!", ephemeral=True)

        try:
            discord_id = str(self.ctx.author.id)
            conn = database.conectar_banco()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET yg_coins = yg_coins - ? WHERE discord_id = ?", (self.preco_total, discord_id))
            conn.commit()
            conn.close()
            
            database.adicionar_booster(discord_id, self.caixa_id, self.quantidade)
            
            for child in self.children:
                child.disabled = True
                
            embed = discord.Embed(
                title="✅ Compra Aprovada!",
                description=f"Você comprou **{self.quantidade}x pacotes**.\nUse `!open {self.caixa_id}` para abrir!",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Ocorreu um erro no banco de dados: {e}", ephemeral=True)

    @discord.ui.button(label="Não, cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Esta compra não é sua!", ephemeral=True)
            
        for child in self.children:
            child.disabled = True
            
        embed = discord.Embed(title="❌ Compra Cancelada", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=self)

class Loja(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop")
    async def shop(self, ctx):
        database.registrar_usuario_se_necessario(ctx.author.id)
        
        embed = discord.Embed(title="🛒 Loja de Boosters", color=discord.Color.gold())
        for cid, dados in CAIXAS_METADADOS.items():
            embed.add_field(
                name=f"ID: {cid} | {dados['emoji']} {dados['nome']}", 
                value=f"Preço: **{dados['preco']} YGcoins**", 
                inline=False
            )
        embed.set_footer(text="Use !buy <id> <qtd> para comprar ou !info-box <id> para ver a lista de cartas.")
        
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, caixa_id: str, quantidade: int):
        if quantidade <= 0:
            return await ctx.send("❌ A quantidade deve ser maior que zero.")
            
        if caixa_id not in CAIXAS_METADADOS:
            return await ctx.send("❌ Caixa não encontrada na loja.")
            
        database.registrar_usuario_se_necessario(ctx.author.id)
        preco_total = CAIXAS_METADADOS[caixa_id]["preco"] * quantidade
        
        conn = database.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT yg_coins FROM usuarios WHERE discord_id = ?", (str(ctx.author.id),))
        saldo = cursor.fetchone()[0]
        conn.close()
        
        if saldo < preco_total:
            return await ctx.send(f"❌ Saldo insuficiente. Você precisa de **{preco_total} YGcoins**, mas tem apenas **{saldo}**.")
            
        embed = discord.Embed(
            title="Confirmação de Compra",
            description=f"Deseja comprar **{quantidade}x {CAIXAS_METADADOS[caixa_id]['nome']}** por **{preco_total} YGcoins**?",
            color=discord.Color.blue()
        )
        
        view = ConfirmacaoCompra(ctx, caixa_id, quantidade, preco_total)
        await ctx.send(embed=embed, view=view)

    # Renomeado para info-box
    @commands.command(name="info-box", aliases=["infobox"])
    async def info_box(self, ctx, caixa_id: str = None):
        if caixa_id is None:
            return await ctx.send("❌ Você precisa informar o ID da caixa! Exemplo: `!info-box 1`")
            
        if caixa_id not in CAIXAS_METADADOS:
            return await ctx.send("❌ Caixa não encontrada.")
            
        caminho = f"caixa_{caixa_id}.json"
        if not os.path.exists(caminho):
            return await ctx.send(f"❌ O arquivo de cartas `{caminho}` não foi encontrado.")

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                todas_cartas = json.load(f)

            hierarquia_raridade = {
                "Secret Rara": 1,
                "Ultra Rara": 2,
                "Super Rara": 3,
                "Rara": 4,
                "Comum": 5
            }

            todas_cartas.sort(key=lambda x: (
                hierarquia_raridade.get(x.get("raridade", "Comum"), 99), 
                x.get("nome", "").lower()
            ))

            itens_por_pagina = 10
            paginas = []
            bloco_atual = ""
            
            for i, carta in enumerate(todas_cartas):
                nome = carta.get("nome", "Desconhecida")
                tipo = carta.get("tipo", "Desconhecido")
                raridade = carta.get("raridade", "Comum")
                
                bloco_atual += f"• **{nome}** — *{tipo}* `({raridade})`\n"
                
                if (i + 1) % itens_por_pagina == 0 or (i + 1) == len(todas_cartas):
                    paginas.append(bloco_atual)
                    bloco_atual = ""

            caixa_nome = CAIXAS_METADADOS[caixa_id]['nome']
            emoji = CAIXAS_METADADOS[caixa_id]['emoji']

            if len(paginas) == 1:
                embed = discord.Embed(
                    title=f"{emoji} {caixa_nome}",
                    description=paginas[0],
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"Total de cartas na caixa: {len(todas_cartas)}")
                await ctx.send(embed=embed)
            else:
                view = CaixaInfoPaginator(ctx, paginas, caixa_nome, emoji)
                embed = view.criar_embed()
                embed.set_footer(text=f"Total de cartas na caixa: {len(todas_cartas)} | Página 1 de {len(paginas)}")
                
                message = await ctx.send(embed=embed, view=view)
                view.message = message
            
        except Exception as e:
            await ctx.send(f"❌ Erro ao ler o arquivo JSON da caixa: `{e}`")

async def setup(bot):
    await bot.add_cog(Loja(bot))