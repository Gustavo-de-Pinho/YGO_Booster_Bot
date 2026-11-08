import discord
from discord.ext import commands
import database
import json
import random
import os

class BoosterPaginator(discord.ui.View):
    def __init__(self, ctx, cartas_tiradas, caixa_id):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.cartas_tiradas = cartas_tiradas
        self.caixa_id = caixa_id
        self.indice_atual = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message("Estes botões não são seus!", ephemeral=True)
        return False

    def criar_embed(self):
        carta = self.cartas_tiradas[self.indice_atual]
        total = len(self.cartas_tiradas)
        
        imagem_url = f"https://images.ygoprodeck.com/images/cards/{carta['id']}.jpg"
        
        embed = discord.Embed(
            title=f"📦 Pacote - Coleção {self.caixa_id} ({self.indice_atual + 1}/{total})",
            color=discord.Color.gold()
        )
        embed.description = (
            f"**#{self.indice_atual + 1} Carta**\n"
            f"**Nome:** {carta['nome']}\n"
            f"**Raridade:** {carta.get('raridade', 'Comum')}\n"
            f"**Tipo:** {carta.get('tipo', 'Desconhecido')}"
        )
        embed.set_image(url=imagem_url)
        embed.set_footer(text=f"Solicitado por {self.ctx.author.name}")
        return embed

    @discord.ui.button(label="◀ Voltar", style=discord.ButtonStyle.primary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.indice_atual > 0:
            self.indice_atual -= 1
        else:
            self.indice_atual = len(self.cartas_tiradas) - 1
        await interaction.response.edit_message(embed=self.criar_embed(), view=self)

    @discord.ui.button(label="Próxima ▶", style=discord.ButtonStyle.primary)
    async def proxima(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.indice_atual < len(self.cartas_tiradas) - 1:
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


class AbrirPacotes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def carregar_dados_caixa(self, caixa_id):
        caminho = f"caixa_{caixa_id}.json"
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def sortear_cartas(self, todas_cartas, quantidade=5):
        if not todas_cartas:
            return []

        # 1. Separa as cartas em grupos por raridade
        comuns = [c for c in todas_cartas if "Comum" in c.get("raridade", "Comum")]
        raras = [c for c in todas_cartas if "Rara" in c.get("raridade", "") and "Super" not in c.get("raridade", "") and "Ultra" not in c.get("raridade", "") and "Secret" not in c.get("raridade", "")]
        supers = [c for c in todas_cartas if "Super Rara" in c.get("raridade", "")]
        ultras = [c for c in todas_cartas if "Ultra Rara" in c.get("raridade", "")]
        secrets = [c for c in todas_cartas if "Secret Rara" in c.get("raridade", "")]

        # Fallbacks de segurança caso a caixa não possua alguma raridade específica
        if not comuns: comuns = todas_cartas
        if not raras: raras = comuns
        if not supers: supers = raras
        if not ultras: ultras = supers
        if not secrets: secrets = ultras

        cartas_sorteadas = []
        
        # 2. As primeiras cartas (quantidade - 1) são sempre Comuns
        for _ in range(quantidade - 1):
            cartas_sorteadas.append(random.choice(comuns))
            
        # 3. A última carta (5ª) rola uma chance especial para Rara ou superior
        chance_especial = random.random()
        
        if chance_especial < 0.55:      # 55% de chance da carta garantida ser Rara
            filtro = raras
        elif chance_especial < 0.85:    # 30% de chance de ser Super Rara
            filtro = supers
        elif chance_especial < 0.95:    # 10% de chance de ser Ultra Rara
            filtro = ultras
        else:                           # 5% de chance de ser Secret Rara
            filtro = secrets
            
        cartas_sorteadas.append(random.choice(filtro))
            
        return cartas_sorteadas

    @commands.command(name="open")
    async def open_pack(self, ctx, caixa_id: str = None):
        if caixa_id is None:
            return await ctx.send("❌ Você precisa dizer qual caixa quer abrir! Exemplo: `!open 1`")

        try:
            discord_id = str(ctx.author.id)
            
            conn = database.conectar_banco()
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantidade FROM boosters WHERE discord_id = ? AND caixa_id = ? AND quantidade > 0", (discord_id, caixa_id))
            resultado = cursor.fetchone()
            
            if not resultado:
                conn.close()
                return await ctx.send("❌ Você não tem nenhum booster dessa caixa! Compre na `!shop`.")
                
            todas_cartas = self.carregar_dados_caixa(caixa_id)
            if not todas_cartas:
                conn.close()
                return await ctx.send(f"❌ Erro: O arquivo `caixa_{caixa_id}.json` não foi encontrado ou está vazio.")

            # Sorteia com a nova mecânica de garantida
            cartas_tiradas = self.sortear_cartas(todas_cartas, quantidade=5)
            
            cursor.execute("UPDATE boosters SET quantidade = quantidade - 1 WHERE discord_id = ? AND caixa_id = ?", (discord_id, caixa_id))
            
            for carta in cartas_tiradas:
                card_id = str(carta["id"])
                cursor.execute("SELECT quantidade FROM inventario WHERE discord_id = ? AND card_id = ?", (discord_id, card_id))
                if cursor.fetchone():
                    cursor.execute("UPDATE inventario SET quantidade = quantidade + 1 WHERE discord_id = ? AND card_id = ?", (discord_id, card_id))
                else:
                    cursor.execute("INSERT INTO inventario (discord_id, card_id, quantidade) VALUES (?, ?, ?)", (discord_id, card_id, 1))
                    
            conn.commit()
            conn.close()

            view = BoosterPaginator(ctx, cartas_tiradas, caixa_id)
            embed = view.criar_embed()
            
            message = await ctx.send(embed=embed, view=view)
            view.message = message

        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao abrir o pacote: `{e}`")
            print(f"Erro no !open: {e}")

async def setup(bot):
    await bot.add_cog(AbrirPacotes(bot))