# reset_data.py
#python reset_data.py - apagar tudo e deixar zerado


from database import conectar
import sqlite3
import os

def resetar_tudo():
    """
    EXCLUI TODOS os produtos e TODAS as movimentações do banco de dados.
    Esta operação é IRREVERSÍVEL.
    """
    # Verifica se o arquivo do banco de dados existe antes de conectar
    if not os.path.exists("estoque.db"):
        print("🚨 ATENÇÃO: O arquivo 'estoque.db' não foi encontrado. Execute o 'main.py' primeiro.")
        return

    print("==============================================")
    print("🚨 INICIANDO OPERAÇÃO DE EXCLUSÃO TOTAL DE DADOS 🚨")
    print("Isso apagará TODOS os produtos e TODOS os registros de movimentação.")
    print("==============================================")

    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # 1. EXCLUI TODAS as movimentações
        cursor.execute("DELETE FROM movimentacoes")
        movimentacoes_deletadas = cursor.rowcount
        print(f"[1/3] [{movimentacoes_deletadas}] Movimentações deletadas do histórico.")

        # 2. EXCLUI TODOS os produtos
        # NOTA: O SQLite apaga os produtos mesmo que haja chaves estrangeiras, 
        # desde que 'FOREIGN KEYS = ON' esteja ativo (o que está no seu database.py) 
        # e as movimentações já tenham sido excluídas.
        cursor.execute("DELETE FROM produtos")
        produtos_deletados = cursor.rowcount
        print(f"[2/3] [{produtos_deletados}] Produtos cadastrados deletados.")
        
        # 3. ZERA O CONTADOR DE ID (CRÍTICO para começar a cadastrar do ID 1)
        cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'produtos'")
        cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'movimentacoes'")
        print("[3/3] Contadores de ID zerados para 'produtos' e 'movimentacoes'.")

        # 4. Confirma as alterações
        conn.commit()
        
        print("\n✅ SUCESSO: O sistema de estoque está completamente limpo.")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"\n❌ ERRO ao tentar resetar os dados: {e}")
        
    finally:
        conn.close()

if __name__ == '__main__':
    # Pergunta para confirmar, já que a ação é CRÍTICA e IRREVERSÍVEL
    confirmacao = input("TEM CERTEZA absoluta que deseja APAGAR TODOS os produtos e movimentações? (s/N): ")
    if confirmacao.lower() == 's':
        resetar_tudo()
    else:
        print("Operação de exclusão de dados cancelada pelo usuário.")