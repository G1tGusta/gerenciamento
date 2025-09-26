import sqlite3

def conectar():
    return sqlite3.connect("estoque.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        preco REAL,
        quantidade INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        tipo TEXT,
        quantidade INTEGER,
        data TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos (id)
    )
    """)
    conn.commit()
    conn.close()
