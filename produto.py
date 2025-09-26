from database import conectar

def cadastrar_produto(nome, categoria, preco, quantidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, categoria, preco, quantidade) VALUES (?, ?, ?, ?)",
                   (nome, categoria, preco, quantidade))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def atualizar_quantidade(produto_id, quantidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (quantidade, produto_id))
    conn.commit()
    conn.close()

def buscar_quantidade(produto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
    qtd = cursor.fetchone()
    conn.close()
    return qtd[0] if qtd else None
