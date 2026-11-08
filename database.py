import sqlite3

def conectar_banco():
    return sqlite3.connect("database.db")

def configurar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            discord_id TEXT PRIMARY KEY,
            yg_coins INTEGER DEFAULT 0,
            last_daily TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT,
            card_id TEXT,
            quantidade INTEGER DEFAULT 1,
            FOREIGN KEY(discord_id) REFERENCES usuarios(discord_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boosters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT,
            caixa_id TEXT,
            quantidade INTEGER DEFAULT 0,
            FOREIGN KEY(discord_id) REFERENCES usuarios(discord_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def registrar_usuario_se_necessario(discord_id):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT discord_id FROM usuarios WHERE discord_id = ?", (str(discord_id),))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO usuarios (discord_id, yg_coins) VALUES (?, ?)", (str(discord_id), 500))
        conn.commit()
        
    conn.close()

def adicionar_booster(discord_id, caixa_id, quantidade):
    """Adiciona pacotes fechados ao inventário do usuário."""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantidade FROM boosters WHERE discord_id = ? AND caixa_id = ?", (str(discord_id), str(caixa_id)))
    resultado = cursor.fetchone()
    
    if resultado:
        cursor.execute("UPDATE boosters SET quantidade = quantidade + ? WHERE discord_id = ? AND caixa_id = ?", 
                       (quantidade, str(discord_id), str(caixa_id)))
    else:
        cursor.execute("INSERT INTO boosters (discord_id, caixa_id, quantidade) VALUES (?, ?, ?)", 
                       (str(discord_id), str(caixa_id), quantidade))
        
    conn.commit()
    conn.close()