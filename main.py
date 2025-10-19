# main.py
from database import criar_tabelas, checar_e_corrigir_coluna # Importe 'checar_e_corrigir_coluna'
from login import LoginApp 
from usuario import cadastrar_usuario
import sqlite3

def criar_admin_padrao():
    # ... (o código desta função permanece o mesmo) ...
    try:
        # Verifica se o usuário admin já existe
        conexao = sqlite3.connect("estoque.db")
        cursor = conexao.cursor()
        # CORREÇÃO: Usando 'usuario' em vez de 'username'
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", ("admin",))
        if not cursor.fetchone():
            # A função cadastrar_usuario deve ser importada de usuario.py (assumindo que você a tem)
            # Argumentos: nome, usuario, senha, nivel
            cadastrar_usuario("Administrador", "admin", "1234", "admin")
            print("Usuário administrador criado com sucesso.")
        conexao.close()
    except Exception as e:
        # Não exibe a mensagem de erro se o erro for apenas a coluna não existir ainda
        if "no such column" not in str(e):
            print("Erro ao criar usuário admin:", e)


if __name__ == "__main__":
    criar_tabelas()
    checar_e_corrigir_coluna() # CHAMA A CORREÇÃO DO BANCO ANTES DE TENTAR INSERIR
    criar_admin_padrao()
    
    # Inicializa o aplicativo de login
    app = LoginApp()
    app.mainloop()