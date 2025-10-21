# movimentacao.py

from database import conectar
from produto import buscar_produto_por_id, atualizar_estoque
from datetime import datetime # Importação adicionada para obter a data/hora atual

def registrar_movimentacao(produto_id, quantidade, tipo):
    """
    Registra uma movimentação de estoque (entrada ou saida) e atualiza a quantidade do produto.
    Lança ValueError se o produto não for encontrado ou se o estoque for insuficiente para uma 'saida'.
    
    Args:
        produto_id (int): ID do produto a ser movimentado.
        quantidade (int): Quantidade a ser movimentada.
        tipo (str): 'entrada' ou 'saida'.
    """
    
    # Busca o produto para obter o estoque atual
    produto = buscar_produto_por_id(produto_id)
    
    # Verifica se o produto existe
    if not produto:
        # Se o produto não for encontrado, lança um erro que é capturado pela interface.
        raise ValueError("Produto não encontrado.") 

    # A tupla de produtos é: (ID, Nome, Categoria, Preco, Quantidade)
    id_produto, nome, categoria, preco, qtd_atual, codigo_barras = produto

    if tipo == "entrada":
        nova_quantidade = qtd_atual + quantidade
    elif tipo == "saida":
        if quantidade > qtd_atual:
            # Lança o erro específico de estoque insuficiente
            raise ValueError(f"Estoque insuficiente! Estoque atual: {qtd_atual}")
        nova_quantidade = qtd_atual - quantidade
    else:
        # Lança erro se o tipo de movimento for inválido
        raise ValueError("Tipo inválido. Use 'entrada' ou 'saida'.")

    # 1. Atualiza o estoque na tabela 'produtos'
    atualizar_estoque(produto_id, nova_quantidade)

    # 2. Registra o histórico na tabela 'movimentacoes'
    conn = conectar()
    cursor = conn.cursor()
    
    # Captura a data/hora atual no formato ISO (CRÍTICO para o Giro de Estoque)
    # Ex: '2025-10-18 21:00:00'
    data_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    
    # Instrução SQL que insere explicitamente o valor da data
    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, data)
        VALUES (?, ?, ?, ?)
    """, (produto_id, tipo, quantidade, data_registro)) 
    
    conn.commit()
    conn.close()

def listar_movimentacoes():
    """
    Lista todas as movimentações de estoque, cruzando com o nome do produto.
    Inclui a data formatada.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    # SQL para listar as movimentações com o nome do produto e data formatada
    cursor.execute("""
        SELECT 
            m.id, 
            p.nome, 
            m.tipo, 
            m.quantidade, 
            STRFTIME('%d/%m/%Y %H:%M', m.data, 'localtime') AS data_formatada
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        ORDER BY m.data DESC
    """)
    movimentacoes = cursor.fetchall()
    conn.close()
    return movimentacoes