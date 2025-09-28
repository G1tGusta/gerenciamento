import tkinter as tk
from tkinter import ttk, messagebox
from dashboard import Dashboard

from produto import (
    cadastrar_produto,
    listar_produtos,
    atualizar_nome,
    atualizar_preco
)
from movimentacao import registrar_movimentacao, listar_movimentacoes

# ==== FUNÇÕES DE INTERFACE ====

def atualizar_tabela(tree, alertar=True):
    for item in tree.get_children():
        tree.delete(item)
    produtos = listar_produtos()

    produtos_baixo = []

    for p in produtos:
        id_prod, nome, categoria, preco, qtd = p
        tag = ""
        if qtd < 3:
            tag = "baixo"
            produtos_baixo.append((nome, qtd))
        elif qtd < 6:
            tag = "medio"
        tree.insert("", "end", values=p, tags=(tag,))

    tree.tag_configure("baixo", background="red", foreground="white")
    tree.tag_configure("medio", background="yellow", foreground="black")

    if alertar and produtos_baixo:
        msg = "\n".join([f"{nome} (qtd: {qtd})" for nome, qtd in produtos_baixo])
        messagebox.showwarning("Atenção! Estoque baixo", f"Os seguintes produtos estão acabando:\n\n{msg}")

def cadastrar(tree, entry_nome, entry_categoria, entry_preco, entry_quantidade):
    nome = entry_nome.get()
    categoria = entry_categoria.get()
    preco = entry_preco.get()
    quantidade = entry_quantidade.get()

    if not (nome and categoria and preco and quantidade):
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return

    try:
        cadastrar_produto(nome, categoria, preco, int(quantidade))
        messagebox.showinfo("Sucesso", "Produto cadastrado!")
        atualizar_tabela(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def movimentar(tree, entry_id, entry_qtd, tipo):
    produto_id = entry_id.get()
    qtd = entry_qtd.get()

    if not (produto_id and qtd):
        messagebox.showerror("Erro", "Preencha todos os campos de movimentação!")
        return

    try:
        registrar_movimentacao(int(produto_id), int(qtd), tipo)
        messagebox.showinfo("Sucesso", f"{tipo.capitalize()} registrada!")
        atualizar_tabela(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def abrir_relatorio_movimentacoes():
    movimentos = listar_movimentacoes()

    relatorio = tk.Toplevel()
    relatorio.title("Relatório de Movimentações")
    relatorio.geometry("600x400")

    colunas = ("ID", "Produto", "Tipo", "Quantidade", "Data")
    tree_mov = ttk.Treeview(relatorio, columns=colunas, show="headings")
    for col in colunas:
        tree_mov.heading(col, text=col)
    tree_mov.pack(fill="both", expand=True)

    for m in movimentos:
        tree_mov.insert("", "end", values=m)

def abrir_dashboard_completo():
    janela = Dashboard()
    janela.mainloop()

def atualizar_nome_interface(entry_id, entry_nome, tree):
    try:
        produto_id = int(entry_id.get())
        novo_nome = entry_nome.get()
        if not novo_nome:
            raise ValueError("Novo nome não pode estar vazio.")
        atualizar_nome(produto_id, novo_nome)
        messagebox.showinfo("Sucesso", "Nome atualizado!")
        atualizar_tabela(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def atualizar_preco_interface(entry_id, entry_preco, tree):
    try:
        produto_id = int(entry_id.get())
        novo_preco = entry_preco.get()
        atualizar_preco(produto_id, novo_preco)
        messagebox.showinfo("Sucesso", "Preço atualizado!")
        atualizar_tabela(tree)
    except Exception as e:
        messagebox.showerror("Erro", str(e))

# ==== INTERFACE PRINCIPAL ====

def iniciar_interface(user_id, nome, nivel):
    root = tk.Tk()
    root.title(f"Sistema de Estoque - Usuário: {nome} ({nivel})")
    root.geometry("950x700")

    # Frame Cadastro
    frame_cadastro = tk.LabelFrame(root, text="Cadastrar Produto")
    frame_cadastro.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0)
    entry_nome = tk.Entry(frame_cadastro)
    entry_nome.grid(row=0, column=1)

    tk.Label(frame_cadastro, text="Categoria:").grid(row=1, column=0)
    entry_categoria = tk.Entry(frame_cadastro)
    entry_categoria.grid(row=1, column=1)

    tk.Label(frame_cadastro, text="Preço:").grid(row=0, column=2)
    entry_preco = tk.Entry(frame_cadastro)
    entry_preco.grid(row=0, column=3)

    tk.Label(frame_cadastro, text="Quantidade:").grid(row=1, column=2)
    entry_quantidade = tk.Entry(frame_cadastro)
    entry_quantidade.grid(row=1, column=3)

    btn_cadastrar = tk.Button(frame_cadastro, text="Cadastrar Produto",
                              command=lambda: cadastrar(tree, entry_nome, entry_categoria, entry_preco, entry_quantidade))
    btn_cadastrar.grid(row=2, column=0, columnspan=4, pady=5)

    if nivel != "admin":
        for widget in frame_cadastro.winfo_children():
            widget.configure(state="disabled")

    # Frame Movimentação
    frame_mov = tk.LabelFrame(root, text="Movimentações")
    frame_mov.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_mov, text="ID Produto:").grid(row=0, column=0)
    entry_id = tk.Entry(frame_mov)
    entry_id.grid(row=0, column=1)

    tk.Label(frame_mov, text="Quantidade:").grid(row=0, column=2)
    entry_qtd = tk.Entry(frame_mov)
    entry_qtd.grid(row=0, column=3)

    btn_entrada = tk.Button(frame_mov, text="Registrar Entrada", bg="green", fg="white",
                            command=lambda: movimentar(tree, entry_id, entry_qtd, "entrada"))
    btn_entrada.grid(row=0, column=4, padx=5)

    btn_saida = tk.Button(frame_mov, text="Registrar Saída", bg="red", fg="white",
                          command=lambda: movimentar(tree, entry_id, entry_qtd, "saida"))
    btn_saida.grid(row=0, column=5, padx=5)

    # Frame Edição
    frame_editar = tk.LabelFrame(root, text="Editar Produto")
    frame_editar.pack(fill="x", padx=10, pady=5)

    tk.Label(frame_editar, text="ID Produto:").grid(row=0, column=0)
    entry_edit_id = tk.Entry(frame_editar)
    entry_edit_id.grid(row=0, column=1)

    tk.Label(frame_editar, text="Novo Nome:").grid(row=0, column=2)
    entry_edit_nome = tk.Entry(frame_editar)
    entry_edit_nome.grid(row=0, column=3)

    tk.Label(frame_editar, text="Novo Preço:").grid(row=1, column=0)
    entry_edit_preco = tk.Entry(frame_editar)
    entry_edit_preco.grid(row=1, column=1)

    btn_nome = tk.Button(frame_editar, text="Atualizar Nome",
                         command=lambda: atualizar_nome_interface(entry_edit_id, entry_edit_nome, tree))
    btn_nome.grid(row=1, column=2, padx=5)

    btn_preco = tk.Button(frame_editar, text="Atualizar Preço",
                          command=lambda: atualizar_preco_interface(entry_edit_id, entry_edit_preco, tree))
    btn_preco.grid(row=1, column=3, padx=5)

    # Frame Estoque
    frame_estoque = tk.LabelFrame(root, text="Estoque Atual")
    frame_estoque.pack(fill="both", expand=True, padx=10, pady=5)

    colunas = ("ID", "Nome", "Categoria", "Preço", "Quantidade")
    tree = ttk.Treeview(frame_estoque, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    # Botões extras no rodapé
    frame_botoes = tk.Frame(root)
    frame_botoes.pack(side="bottom", fill="x", pady=10)

    btn_atualizar = tk.Button(frame_botoes, text="Atualizar Estoque",
                              command=lambda: atualizar_tabela(tree))
    btn_atualizar.pack(side="left", padx=10)

    btn_relatorio = tk.Button(frame_botoes, text="Relatório de Movimentações",
                              command=abrir_relatorio_movimentacoes)
    btn_relatorio.pack(side="left", padx=10)

    btn_dashboard = tk.Button(frame_botoes, text="Dashboard",
                              command=abrir_dashboard_completo)
    btn_dashboard.pack(side="left", padx=10)

    # Carrega estoque inicial + alerta
    atualizar_tabela(tree, alertar=True)

    root.mainloop()
