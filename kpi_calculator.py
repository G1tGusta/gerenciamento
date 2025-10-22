# kpi_calculator.py

from database import conectar
from datetime import datetime, timedelta 

def calcular_kpis():
    """Calcula todos os indicadores (KPIs) de estoque."""
    kpis = {}
    
    conn = conectar() 
    cursor = conn.cursor()
    
    # 1. SOMA TOTAL DE UNIDADES
    total_qtd = cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM produtos").fetchone()[0]
    kpis['total_qtd'] = total_qtd
    
    # 2. PREÇO TOTAL EM PRODUTOS (Valor Total do Estoque Atual)
    cursor.execute("SELECT COALESCE(SUM(preco * quantidade), 0) FROM produtos")
    valor_total_estoque = cursor.fetchone()[0]
    kpis['valor_total_estoque'] = valor_total_estoque
    
    # 3. ESTOQUE BAIXO
    produtos_baixo = cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade < 3").fetchall()
    kpis['produtos_baixo'] = produtos_baixo

    # 4. TOTAL DE PRODUTOS DIFERENTES
    cursor.execute("SELECT COUNT(id) FROM produtos")
    total_produtos = cursor.fetchone()[0]
    kpis['total_produtos'] = total_produtos
    
    # =========================================================
    # 5. GIRO DE ESTOQUE (FÓRMULA MONETÁRIA: PROXY CPV / ESTOQUE ATUAL)
    # =========================================================
    
    # Busca o Valor Total de Saídas (Preço x Quantidade) nos últimos 30 dias (PROXY DO CPV)
    # CRÍTICO: Usa M.quantidade * P.preco para obter o valor monetário das saídas.
    cursor.execute("""
        SELECT COALESCE(SUM(M.quantidade * P.preco), 0)
        FROM movimentacoes M
        JOIN produtos P ON M.produto_id = P.id
        WHERE M.tipo = 'saida' AND M.data >= DATETIME('now', '-30 days') 
    """)
    
    valor_total_saidas_30d = cursor.fetchone()[0]
    
    # Usa o Valor Total do Estoque Atual (calculado no passo 2) como proxy para o Estoque Médio
    estoque_atual_valor = valor_total_estoque 
    
    giro_calculado = 0
    
    # O giro só é calculado se houver valor movimentado E estoque
    if valor_total_saidas_30d > 0 and estoque_atual_valor > 0:
        giro_calculado = valor_total_saidas_30d / estoque_atual_valor
        
    kpis['giro'] = giro_calculado

    # 6. Custo de Manutenção
    TAXA_CUSTO_MANUTENCAO = 0.15 
    custo_manutencao = valor_total_estoque * TAXA_CUSTO_MANUTENCAO
    kpis['custo_manutencao'] = custo_manutencao
    
    conn.close() 
    return kpis