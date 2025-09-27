import sqlite3
from datetime import datetime

# =========================
# Registrar Movimentação
# =========================
def registrar_movimentacao(produto_id, quantidade, tipo): 
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    # Inserir movimentação
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, quantidade, tipo, data) VALUES (?, ?, ?, ?)",
        (produto_id, quantidade, tipo, data)
    )

    # Atualizar estoque
    if tipo == "entrada":
        cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?", (quantidade, produto_id))
    elif tipo == "saida":
        cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, produto_id))

    conn.commit()
    conn.close()


# =========================
# Listar Movimentações
# =========================
def listar_movimentacoes():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimentacoes ORDER BY data DESC")
    movimentacoes = cursor.fetchall()
    conn.close()
    return movimentacoes
