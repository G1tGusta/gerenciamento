from database import conectar

# Definição dos 6 campos para ser consistente em todas as consultas
COLUNAS_PRODUTO = "id, nome, categoria, preco, quantidade, codigo_barras"

def cadastrar_produto(nome, categoria, preco, quantidade, codigo_barras=""):
    """
    Cadastra um novo produto, agora incluindo o Código de Barras.
    """
    preco = str(preco).replace(",", ".")  # corrige vírgula para ponto
    try:
        preco = float(preco)
    except ValueError:
        raise ValueError("Preço inválido. Use números, exemplo: 1800.00")

    conn = conectar()
    cursor = conn.cursor()
    # CORRIGIDO: Inclui codigo_barras no INSERT
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, preco, quantidade, codigo_barras)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade, codigo_barras))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    # CORRIGIDO: Seleciona explicitamente os 6 campos
    cursor.execute(f"SELECT {COLUNAS_PRODUTO} FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def buscar_produto_por_id(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    # CORRIGIDO: Seleciona explicitamente os 6 campos
    cursor.execute(f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conn.close()
    return produto

def buscar_produto_por_nome(nome):
    conn = conectar()
    cursor = conn.cursor()
    # CORRIGIDO: Seleciona explicitamente os 6 campos
    cursor.execute(f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE nome LIKE ?", ('%' + nome + '%',))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def atualizar_estoque(produto_id, nova_quantidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_quantidade, produto_id))
    conn.commit()
    conn.close()

def deletar_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()

def atualizar_preco(produto_id, novo_preco):
    novo_preco = str(novo_preco).replace(",", ".")
    try:
        novo_preco = float(novo_preco)
    except ValueError:
        raise ValueError("Preço inválido. Use números, exemplo: 1800.00")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET preco = ? WHERE id = ?", (novo_preco, produto_id))
    conn.commit()
    conn.close()

def atualizar_nome(produto_id, novo_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET nome = ? WHERE id = ?", (novo_nome, produto_id))
    conn.commit()
    conn.close()
    
def buscar_produto_por_codigo_barras(codigo):
    """
    Busca um produto pelo código de barras.
    Retorna a tupla completa (6 campos) ou None.
    """
    conn = conectar()
    cursor = conn.cursor()
    # CORRIGIDO: Seleciona explicitamente os 6 campos
    cursor.execute(f"SELECT {COLUNAS_PRODUTO} FROM produtos WHERE codigo_barras = ?", (codigo,))
    produto = cursor.fetchone()
    conn.close()
    return produto