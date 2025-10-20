# kpi_calculator.py

from database import conectar
from datetime import datetime, timedelta # O 'timedelta' pode ser removido, mas vou mantê-lo por segurança

def calcular_kpis():
    """Calcula todos os indicadores (KPIs) de estoque."""
    kpis = {}
    
    conn = conectar() 
    cursor = conn.cursor()
    
    # CRÍTICO: LINHA REMOVIDA/IGNORADA!
    # data_30_dias_atras = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

    # 1. SOMA TOTAL DE UNIDADES (CORREÇÃO APLICADA)
    # COALESCE garante que, se o resultado de SUM for NULL (tabela vazia), ele retornará 0.
    total_qtd = cursor.execute("SELECT COALESCE(SUM(quantidade), 0) FROM produtos").fetchone()[0]
    kpis['total_qtd'] = total_qtd
    
    # 2. PREÇO TOTAL EM PRODUTOS (COALESCE também aplicado)
    cursor.execute("SELECT COALESCE(SUM(preco * quantidade), 0) FROM produtos")
    valor_total_estoque = cursor.fetchone()[0]
    kpis['valor_total_estoque'] = valor_total_estoque
    
    # 3. ESTOQUE BAIXO
    produtos_baixo = cursor.execute("SELECT nome, quantidade FROM produtos WHERE quantidade < 3").fetchall()
    kpis['produtos_baixo'] = produtos_baixo
    
    # 4. GIRO DE ESTOQUE (ALTERAÇÃO CRÍTICA AQUI)
    
    # Busca o total de saídas (vendas/movimentações) nos últimos 30 dias
    # Usando DATETIME('now', '-30 days') do SQLite para garantir formato e comparação corretos.
    cursor.execute("""
        SELECT COALESCE(SUM(M.quantidade), 0)
        FROM movimentacoes M
        WHERE M.tipo = 'saida' AND M.data >= DATETIME('now', '-30 days') 
    """)
    
    total_saidas_30d = cursor.fetchone()[0]
    
    estoque_atual = total_qtd # USA O VALOR CALCULADO ANTERIORMENTE
    
    giro_calculado = 0
    
    # Lógica de cálculo: Se Saídas > 0 e Estoque Atual > 0
    if total_saidas_30d > 0 and estoque_atual > 0:
        giro_calculado = total_saidas_30d / estoque_atual
        
        # DEBUG: Se quiser ver o cálculo na console (opcional)
        # print(f"DEBUG: Saídas (30d) = {total_saidas_30d}, Estoque Atual = {estoque_atual}, Giro = {giro_calculado}")
    
    kpis['giro'] = giro_calculado

    # 5. Custo de Manutenção
    TAXA_CUSTO_MANUTENCAO = 0.15 
    custo_manutencao = valor_total_estoque * TAXA_CUSTO_MANUTENCAO
    kpis['custo_manutencao'] = custo_manutencao
    
    conn.close() 
    return kpis

# O diagnóstico_giro() permanece como antes e é opcional agora.
# ...