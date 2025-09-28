# main.py
from database import criar_tabelas
from login import iniciar_login
from usuario import cadastrar_usuario
import sqlite3

def criar_admin_padrao():
    try:
        # Verifica se o usuário admin já existe
        conexao = sqlite3.connect("estoque.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            cadastrar_usuario("Administrador", "admin", "1234", "admin")
            print("Usuário administrador criado com sucesso.")
        conexao.close()
    except Exception as e:
        print("Erro ao criar usuário admin:", e)

if __name__ == "__main__":
    criar_tabelas()
    criar_admin_padrao()
    iniciar_login()
