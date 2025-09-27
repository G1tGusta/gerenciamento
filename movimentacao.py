# movimentacao.py
from database import conectar
from produto import buscar_produto_por_id, atualizar_estoque

def registrar_movimentacao(produto_id, quantidade, tipo):
    """
    tipo: 'entrada' ou 'saida'
    """
    produto = buscar_produto_por_id(produto_id)
    if not produto:
        raise ValueError("Produto não encontrado.")

    id_produto, nome, categoria, preco, qtd_atual = produto

    if tipo == "entrada":
        nova_quantidade = qtd_atual + quantidade
    elif tipo == "saida":
        if quantidade > qtd_atual:
            raise ValueError(f"Estoque insuficiente! Estoque atual: {qtd_atual}")
        nova_quantidade = qtd_atual - quantidade
    else:
        raise ValueError("Tipo inválido. Use 'entrada' ou 'saida'.")

    # Atualiza estoque
    atualizar_estoque(produto_id, nova_quantidade)

    # Registra histórico
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade)
        VALUES (?, ?, ?)
    """, (produto_id, tipo, quantidade))
    conn.commit()
    conn.close()

def listar_movimentacoes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, p.nome, m.tipo, m.quantidade, m.data
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        ORDER BY m.data DESC
    """)
    movimentos = cursor.fetchall()
    conn.close()
    return movimentos
