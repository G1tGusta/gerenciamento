# database.py
import sqlite3
import os
import shutil
from datetime import datetime

def conectar():
    """
    Estabelece a conexão com o banco de dados 'estoque.db'.
    Configura PARSE_DECLTYPES e PARSE_COLNAMES para correto reconhecimento de tipos de data/hora (TIMESTAMP).
    """
    conn = sqlite3.connect(
        "estoque.db", 
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    # Garante que as chaves estrangeiras estejam ativas
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

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


def checar_e_corrigir_coluna():
    """
    Verifica se a coluna 'data' existe na tabela 'movimentacoes' e a adiciona se necessário.
    Utilizado para corrigir bancos de dados criados antes da implementação da coluna 'data'.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Checa se a tabela 'movimentacoes' existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movimentacoes'")
    if not cursor.fetchone():
        conn.close()
        return

    # 2. Checa se a coluna 'data' existe na tabela 'movimentacoes'
    try:
        # Tenta selecionar a coluna 'data'. Se ela não existir, lança um erro.
        cursor.execute("SELECT data FROM movimentacoes LIMIT 1")
    except sqlite3.OperationalError:
        # Se cair aqui, a coluna 'data' está faltando ou foi removida.
        print("Coluna 'data' faltando na tabela movimentacoes. Corrigindo com ALTER TABLE.")
        try:
            # Adiciona a coluna 'data' sem perder dados existentes!
            cursor.execute("ALTER TABLE movimentacoes ADD COLUMN data TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("Coluna 'data' adicionada com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar adicionar coluna 'data': {e}")
            
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