# database.py
import sqlite3
import os
import shutil
from datetime import datetime

def conectar():
    return sqlite3.connect("estoque.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    # Movimentações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        tipo TEXT,
        quantidade INTEGER,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )
    """)

    # Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT NOT NULL CHECK(nivel IN ('admin', 'operador'))
    )
    """)

    # Admin Default
    cursor.execute("""
    INSERT OR IGNORE INTO usuarios (nome, usuario, senha, nivel)
    VALUES ('Administrador Master', 'admin', '1234', 'admin')
    """)

    conn.commit()
    conn.close()

def backup_banco():
    """Cria uma cópia do banco estoque.db na pasta backups/"""
    if not os.path.exists("estoque.db"):
        print("Banco de dados não encontrado para backup.")
        return None

    if not os.path.exists("backups"):
        os.makedirs("backups")

    datahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join("backups", f"estoque_{datahora}.db")
    shutil.copyfile("estoque.db", destino)
    print(f"Backup criado em {destino}")
    return destino
