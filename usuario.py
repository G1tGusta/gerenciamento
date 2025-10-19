# usuario.py
from database import conectar

def cadastrar_usuario(nome, usuario, senha, nivel="operador"):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, usuario, senha, nivel)
            VALUES (?, ?, ?, ?)
        """, (nome, usuario, senha, nivel))
        conn.commit()
    except Exception as e:
        print("Erro ao cadastrar usuário:", e)
    conn.close()

def autenticar(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, nivel FROM usuarios
        WHERE usuario = ? AND senha = ?
    """, (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    return user  # retorna (id, nome, nivel) se válido, senão None