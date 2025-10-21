import sqlite3
import os
import shutil
from datetime import datetime

# ============================================================
# FUNÇÃO PRINCIPAL DE CONEXÃO
# ============================================================
def conectar():
    """
    Estabelece a conexão com o banco de dados 'estoque.db'.
    Configura PARSE_DECLTYPES e PARSE_COLNAMES para correto
    reconhecimento de tipos de data/hora (TIMESTAMP).
    """
    conn = sqlite3.connect(
        "estoque.db",
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    # Garante que as chaves estrangeiras estejam ativas
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================
# CRIAÇÃO DE TABELAS PRINCIPAIS
# ============================================================
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # -------------------------------
    # Tabela de Produtos
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    # -------------------------------
    # Tabela de Movimentações
    # -------------------------------
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

    # -------------------------------
    # Tabela de Usuários
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nivel TEXT NOT NULL CHECK(nivel IN ('admin', 'operador'))
    )
    """)

    # -------------------------------
    # Usuário padrão (Admin)
    # -------------------------------
    cursor.execute("""
    INSERT OR IGNORE INTO usuarios (nome, usuario, senha, nivel)
    VALUES ('Administrador Master', 'admin', '1234', 'admin')
    """)

    conn.commit()

    # Corrige colunas antigas (adiciona se não existirem)
    checar_e_corrigir_coluna()            # garante coluna 'data' em movimentações
    checar_e_corrigir_codigo_barras()     # garante coluna 'codigo_barras' em produtos

    conn.close()


# ============================================================
# CORREÇÃO DE COLUNAS ANTIGAS
# ============================================================
def checar_e_corrigir_coluna():
    """
    Verifica se a coluna 'data' existe na tabela 'movimentacoes' e a adiciona se necessário.
    Utilizado para corrigir bancos criados antes da implementação da coluna 'data'.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movimentacoes'")
    if not cursor.fetchone():
        conn.close()
        return

    try:
        cursor.execute("SELECT data FROM movimentacoes LIMIT 1")
    except sqlite3.OperationalError:
        print("Coluna 'data' faltando na tabela movimentacoes. Corrigindo com ALTER TABLE.")
        try:
            cursor.execute("ALTER TABLE movimentacoes ADD COLUMN data TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("Coluna 'data' adicionada com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar adicionar coluna 'data': {e}")

    conn.close()


def checar_e_corrigir_codigo_barras():
    """
    Verifica se a coluna 'codigo_barras' existe na tabela 'produtos'
    e a adiciona automaticamente se estiver ausente.
    """
    conn = conectar()
    cursor = conn.cursor()

    # Verifica se a tabela 'produtos' existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
    if not cursor.fetchone():
        conn.close()
        return

    try:
        cursor.execute("SELECT codigo_barras FROM produtos LIMIT 1")
    except sqlite3.OperationalError:
        print("Coluna 'codigo_barras' não encontrada. Adicionando automaticamente...")
        try:
            cursor.execute("ALTER TABLE produtos ADD COLUMN codigo_barras TEXT")
            conn.commit()
            print("Coluna 'codigo_barras' adicionada com sucesso!")
        except Exception as e:
            print(f"Erro ao adicionar coluna 'codigo_barras': {e}")

    conn.close()


# ============================================================
# BACKUP AUTOMÁTICO DO BANCO
# ============================================================
def backup_banco():
    """Cria uma cópia do banco estoque.db na pasta 'backups/'"""
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


# ============================================================
# EXECUÇÃO DIRETA (TESTE)
# ============================================================
if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados verificado/criado com sucesso!")
