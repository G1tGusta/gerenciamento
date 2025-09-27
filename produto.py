# produto.py
from database import conectar

def cadastrar_produto(nome, categoria, preco, quantidade):
    preco = str(preco).replace(",", ".")  # corrige vírgula para ponto
    try:
        preco = float(preco)
    except ValueError:
        raise ValueError("Preço inválido. Use números, exemplo: 1800.00")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, categoria, preco, quantidade)
        VALUES (?, ?, ?, ?)
    """, (nome, categoria, preco, quantidade))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def buscar_produto_por_id(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    conn.close()
    return produto

def buscar_produto_por_nome(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", ('%' + nome + '%',))
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
