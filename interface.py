import tkinter as tk
from tkinter import ttk, messagebox
from produto import cadastrar_produto, listar_produtos
from movimentacao import registrar_movimentacao, listar_movimentacoes
import sqlite3
import matplotlib.pyplot as plt


# =============================
# Atualizar Lista de Produtos
# =============================
def atualizar_lista(tree):
    for item in tree.get_children():
        tree.delete(item)

    produtos = listar_produtos()
    for row in produtos:
        tree.insert("", "end", values=row, tags=("baixo" if row[4] <= 5 else "ok",))


# =============================
# Mostrar Relatório de Movimentações
# =============================
def mostrar_movimentacoes():
    win = tk.Toplevel()
    win.title("Relatório de Movimentações")
    win.geometry("600x400")
    tree_mov = ttk.Treeview(win, columns=("ID", "Produto", "Tipo", "Qtd", "Data"), show="headings")
    tree_mov.pack(fill="both", expand=True)

    for col in ("ID", "Produto", "Tipo", "Qtd", "Data"):
        tree_mov.heading(col, text=col)
        tree_mov.column(col, anchor="center")

    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, p.nome, m.tipo, m.quantidade, m.data
        FROM movimentacoes m
        JOIN produtos p ON m.produto_id = p.id
        ORDER BY m.data DESC
    """)
    for row in cursor.fetchall():
        tree_mov.insert("", "end", values=row)
    conn.close()


# =============================
# Mostrar Dashboard (Gráfico)
# =============================
def mostrar_dashboard():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, quantidade FROM produtos")
    dados = cursor.fetchall()
    conn.close()

    if not dados:
        messagebox.showinfo("Dashboard", "Nenhum produto cadastrado para exibir o gráfico.")
        return

    nomes = [d[0] for d in dados]
    quantidades = [d[1] for d in dados]

    plt.figure(figsize=(8, 5))
    plt.bar(nomes, quantidades, color="skyblue")
    plt.title("📊 Quantidade de Produtos em Estoque")
    plt.xlabel("Produtos")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


# =============================
# Iniciar Interface
# =============================
def iniciar_interface():
    root = tk.Tk()
    root.title("📦 Sistema de Estoque (ERP Básico)")
    root.geometry("900x600")
    root.config(bg="#f4f6f9")

    style = ttk.Style()
    style.theme_use("clam")

    # Cores personalizadas
    style.configure("Treeview", background="#ffffff", foreground="black", rowheight=25, fieldbackground="#ffffff")
    style.map("Treeview", background=[("selected", "#0078D7")])

    # Cadastro de produtos
    frame_cadastro = tk.LabelFrame(root, text="Cadastrar Produto", bg="#f4f6f9", font=("Arial", 12, "bold"))
    frame_cadastro.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_cadastro, text="Nome:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
    entry_nome = tk.Entry(frame_cadastro, width=20)
    entry_nome.grid(row=0, column=1)

    tk.Label(frame_cadastro, text="Categoria:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
    entry_categoria = tk.Entry(frame_cadastro, width=20)
    entry_categoria.grid(row=0, column=3)

    tk.Label(frame_cadastro, text="Preço:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5)
    entry_preco = tk.Entry(frame_cadastro, width=20)
    entry_preco.grid(row=1, column=1)

    tk.Label(frame_cadastro, text="Quantidade:", bg="#f4f6f9", font=("Arial", 10)).grid(row=1, column=2, padx=5, pady=5)
    entry_quantidade = tk.Entry(frame_cadastro, width=20)
    entry_quantidade.grid(row=1, column=3)

    def acao_cadastrar():
        nome = entry_nome.get()
        categoria = entry_categoria.get()
        try:
            preco = float(entry_preco.get())
            quantidade = int(entry_quantidade.get())
        except ValueError:
            messagebox.showerror("Erro", "Preço e quantidade devem ser numéricos!")
            return

        cadastrar_produto(nome, categoria, preco, quantidade)
        messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado!")
        atualizar_lista(tree)

    tk.Button(frame_cadastro, text="Cadastrar Produto", bg="#0078D7", fg="white", font=("Arial", 10, "bold"),
              command=acao_cadastrar).grid(row=2, column=0, columnspan=4, pady=10)

    # Movimentações
    frame_mov = tk.LabelFrame(root, text="Movimentações", bg="#f4f6f9", font=("Arial", 12, "bold"))
    frame_mov.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_mov, text="ID Produto:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(frame_mov, width=10)
    entry_id.grid(row=0, column=1)

    tk.Label(frame_mov, text="Quantidade:", bg="#f4f6f9", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5)
    entry_qtd_mov = tk.Entry(frame_mov, width=10)
    entry_qtd_mov.grid(row=0, column=3)

    def acao_entrada():
        try:
            produto_id = int(entry_id.get())
            quantidade = int(entry_qtd_mov.get())
        except ValueError:
            messagebox.showerror("Erro", "ID e quantidade devem ser numéricos!")
            return
        registrar_movimentacao(produto_id, quantidade, "entrada")
        messagebox.showinfo("Sucesso", "Entrada registrada!")
        atualizar_lista(tree)

    def acao_saida():
        try:
            produto_id = int(entry_id.get())
            quantidade = int(entry_qtd_mov.get())
        except ValueError:
            messagebox.showerror("Erro", "ID e quantidade devem ser numéricos!")
            return
        registrar_movimentacao(produto_id, quantidade, "saida")
        messagebox.showinfo("Sucesso", "Saída registrada!")
        atualizar_lista(tree)

    tk.Button(frame_mov, text="Registrar Entrada", bg="#28a745", fg="white", font=("Arial", 10, "bold"),
              command=acao_entrada).grid(row=1, column=0, columnspan=2, pady=5, padx=5)

    tk.Button(frame_mov, text="Registrar Saída", bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
              command=acao_saida).grid(row=1, column=2, columnspan=2, pady=5, padx=5)

    # Lista de produtos
    frame_lista = tk.LabelFrame(root, text="Estoque Atual", bg="#f4f6f9", font=("Arial", 12, "bold"))
    frame_lista.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(frame_lista, columns=("ID", "Nome", "Categoria", "Preço", "Quantidade"), show="headings")
    tree.pack(fill="both", expand=True)

    for col in ("ID", "Nome", "Categoria", "Preço", "Quantidade"):
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    tree.tag_configure("baixo", background="#f8d7da")
    tree.tag_configure("ok", background="#d4edda")

    # Botões adicionais
    frame_botoes = tk.Frame(root, bg="#f4f6f9")
    frame_botoes.pack(fill="x", pady=10)

    tk.Button(frame_botoes, text="🔄 Atualizar Estoque", bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
          command=lambda: atualizar_lista(tree)).pack(side="left", padx=10)

    tk.Button(frame_botoes, text="📑 Relatório de Movimentações", bg="#6f42c1", fg="white", font=("Arial", 10, "bold"),
          command=mostrar_movimentacoes).pack(side="left", padx=10)

# ✅ Botão do gráfico
    tk.Button(frame_botoes, text="📊 Dashboard", bg="#ff9800", fg="white", font=("Arial", 10, "bold"),
          command=mostrar_dashboard).pack(side="left", padx=10)

    # Inicializa tabela
    atualizar_lista(tree)

    root.mainloop()
