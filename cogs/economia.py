import random

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import database

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx):
        discord_id = str(ctx.author.id)
        database.registrar_usuario_se_necessario(discord_id)
        
        conn = database.conectar_banco()
        cursor = conn.cursor()
        cursor.execute("SELECT yg_coins FROM usuarios WHERE discord_id = ?", (discord_id,))
        moedas = cursor.fetchone()[0]
        conn.close()
        
        await ctx.send(f"👤 **Perfil de {ctx.author.name}**\n💰 Saldo: **{moedas} YGcoins**")

    @commands.command()
    async def daily(self, ctx):
        discord_id = str(ctx.author.id)
        database.registrar_usuario_se_necessario(discord_id)
        
        conn = database.conectar_banco()
        cursor = conn.cursor()
        
        # Busca a data do último daily
        cursor.execute("SELECT last_daily FROM usuarios WHERE discord_id = ?", (discord_id,))
        resultado = cursor.fetchone()
        last_daily_str = resultado[0]
        
        agora = datetime.now()
        pode_coletar = False
        tempo_restante = None
        
        # Verifica se é a primeira vez ou se já passaram 12h
        if last_daily_str is None:
            pode_coletar = True
        else:
            last_daily = datetime.fromisoformat(last_daily_str)
            diferenca = agora - last_daily
            
            if diferenca >= timedelta(hours=12):
                pode_coletar = True
            else:
                tempo_restante = timedelta(hours=12) - diferenca
        
        # Ação baseada na verificação de tempo
        if pode_coletar:
            ganho = random.randint(150, 750) # Moedas recebidas por dia para comprar boosters[cite: 1]
            
            cursor.execute('''
                UPDATE usuarios 
                SET yg_coins = yg_coins + ?, last_daily = ? 
                WHERE discord_id = ?
            ''', (ganho, agora.isoformat(), discord_id))
            conn.commit()
            
            await ctx.send(f"🎁 **{ctx.author.name}**, você coletou suas **{ganho} YGcoins** diárias!")
        else:
            # Calcula horas e minutos restantes
            horas, resto = divmod(tempo_restante.seconds, 3600)
            minutos, _ = divmod(resto, 60)
            await ctx.send(f"⏳ **{ctx.author.name}**, você já pegou seu daily hoje! Volte em **{horas}h e {minutos}m**.")
            
        conn.close()

# Função obrigatória para o discord.py carregar o arquivo
async def setup(bot):
    await bot.add_cog(Economia(bot))