import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
# Importa o Dashboard (agora CTkToplevel)
from dashboard import Dashboard 
from database import backup_banco, conectar

from produto import (
    cadastrar_produto,
    listar_produtos,
    atualizar_nome,
    atualizar_preco,
    buscar_produto_por_id,
    deletar_produto 
)
from movimentacao import registrar_movimentacao, listar_movimentacoes

import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ============ CONFIGURAÇÃO INICIAL ============
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==== FUNÇÃO DE IMPORTAÇÃO DE CSV ====
def importar_csv_para_banco(tree, app_instance):
    caminho = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not caminho:
        return

    try:
        # Tenta ler com diferentes separadores (vírgula ou ponto e vírgula)
        df = pd.read_csv(caminho, sep=None, engine='python') 
        
        conn = conectar()
        cursor = conn.cursor()

        colunas_obrigatorias = ['nome', 'preco', 'quantidade']
        df.columns = df.columns.str.lower() # Normaliza nomes das colunas

        if not all(col in df.columns for col in colunas_obrigatorias):
            raise ValueError("O arquivo CSV deve conter as colunas 'nome', 'preco' e 'quantidade'.")

        produtos_inseridos = 0
        
        for index, row in df.iterrows():
            try:
                nome = str(row['nome']).strip()
                # Se o CSV não tem 'categoria', usa 'Geral'
                categoria = str(row.get('categoria', 'Geral')).strip() 
                
                preco = str(row['preco']).replace(',', '.')
                preco_float = float(preco)
            
                quantidade_int = int(row['quantidade'])

                cursor.execute("""
                    INSERT INTO produtos (nome, categoria, preco, quantidade)
                    VALUES (?, ?, ?, ?)
                """, (nome, categoria, preco_float, quantidade_int))
                produtos_inseridos += 1
            except Exception as e:
                messagebox.showwarning("Erro na Linha", f"Erro ao processar linha {index + 2} ('{nome}'): {e}. Linha ignorada.")
                continue
                
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Importação Concluída", f"{produtos_inseridos} produto(s) importado(s) com sucesso!")
        app_instance.atualizar_tabela(tree)

    except ValueError as ve:
        messagebox.showerror("Erro de Importação", str(ve))
    except Exception as e:
        messagebox.showerror("Erro de Importação", f"Ocorreu um erro inesperado durante a leitura: {e}")


# ==== FUNÇÕES DE EXPORTAÇÃO ====

def exportar_excel(tree):
    dados = []
    colunas = [tree.heading(col, option="text") for col in tree["columns"]]
    for item in tree.get_children():
        dados.append(tree.item(item, 'values'))
    if not dados:
        messagebox.showwarning("Exportar Excel", "Nenhum dado para exportar.")
        return
    df = pd.DataFrame(dados, columns=colunas)
    # Formatação de preço para excel: remove R$ e troca a vírgula por ponto
    df['Preço (R$)'] = df['Preço (R$)'].astype(str).str.replace('R$ ', '', regex=False).str.replace('.', 'X', regex=False).str.replace(',', '.', regex=False).str.replace('X', ',', regex=False) 
    caminho = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if caminho:
        try:
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Exportar Excel", f"Dados exportados com sucesso para:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar: {e}")

def exportar_pdf(tree):
    dados = []
    colunas = [tree.heading(col, option="text") for col in tree["columns"]]
    for item in tree.get_children():
        dados.append(tree.item(item, 'values'))
    if not dados:
        messagebox.showwarning("Exportar PDF", "Nenhum dado para exportar.")
        return
    caminho = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not caminho: return
    try:
        doc = SimpleDocTemplate(caminho)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("Relatório de Estoque", styles['h1']))
        data_tabela = [colunas] + [[str(item) for item in row] for row in dados]
        t = Table(data_tabela)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')), 
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        doc.build(story)
        messagebox.showinfo("Exportar PDF", f"Dados exportados com sucesso para:\n{caminho}")
    except Exception as e:
        messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar PDF: {e}")

def realizar_backup():
    try:
        caminho = backup_banco()
        if caminho:
            messagebox.showinfo("Backup", f"Backup do banco de dados realizado com sucesso em:\n{caminho}")
        else:
            messagebox.showwarning("Backup", "O banco de dados não foi encontrado ou o backup falhou.")
    except Exception as e:
        messagebox.showerror("Erro de Backup", f"Erro ao realizar backup: {e}")


# ==== INTERFACE CTK DE SISTEMA ====

class EstoqueApp(ctk.CTk):
    def __init__(self, user_id, nome, nivel):
        super().__init__()
        
        self.user_data = (user_id, nome, nivel) 
        self.title(f"Gestão de Estoque - Usuário: {nome} ({nivel.capitalize()})")
        self.geometry("1280x720") 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. NOVO: Lista de categorias padrão para o ComboBox
        # ----------------------------------------------------
        self.categorias_padrao = ["Eletronico", "Alimento", "Vestuário", "Higiene", "Outros"]

        # 1. Barra Lateral (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color="#2C3E50")
        self.sidebar_frame.grid(row=0, column=0, sticky="nswe")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) 
        
        ctk.CTkLabel(self.sidebar_frame, text="ESTOQUE MAX", font=("Arial", 20, "bold"), text_color="#ECF0F1").grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Botões de Ação Principal
        self.btn_cadastro = self.criar_sidebar_button("➕ Novo Produto", self.abrir_modal_cadastro, 1)
        self.btn_movimento = self.criar_sidebar_button("🚚 Movimentar Estoque", self.abrir_modal_movimentacao, 2)
        
        # Botões de Relatório e Gerenciamento
        self.btn_dashboard = self.criar_sidebar_button("📊 Dashboard & KPIs", self.abrir_dashboard_completo, 3)
        self.btn_importar_csv = self.criar_sidebar_button("⬆️ Importar CSV", lambda: importar_csv_para_banco(self.tree, self), 4)
        self.btn_atualizar = self.criar_sidebar_button("🔄 Atualizar Tabela", lambda: self.atualizar_tabela(self.tree), 5)


        # Rodapé da Sidebar (Informação do Usuário)
        ctk.CTkLabel(self.sidebar_frame, text=f"Logado como:\n{nome} ({nivel.capitalize()})", font=("Arial", 12), text_color="#BDC3C7", justify="left").grid(row=7, column=0, padx=20, pady=(10, 20), sticky="s")


        # 2. Área de Conteúdo Principal
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self._apply_appearance_mode(ctk.ThemeManager.theme["CTk"]["fg_color"]))
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(1, weight=1)
        
        self.criar_header_tabela(self.main_content_frame)

        self.tree = self.criar_tabela(self.main_content_frame)
        self.atualizar_tabela(self.tree, alertar=False)


    def criar_sidebar_button(self, text, command, row):
        button = ctk.CTkButton(self.sidebar_frame, text=text, command=command, 
                               fg_color="#34495E", 
                               hover_color="#1D2B3A", 
                               anchor="w", font=("Arial", 14), height=40)
        button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        return button

    def criar_header_tabela(self, parent_frame):
        header_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header_frame, text="Estoque Completo", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")
        
        frame_admin = ctk.CTkFrame(header_frame, fg_color="transparent")
        frame_admin.grid(row=0, column=1, sticky="e")
        
        botoes_admin = [
            ("Excel", lambda: exportar_excel(self.tree)),
            ("PDF", lambda: exportar_pdf(self.tree)),
            ("Backup", realizar_backup),
        ]
        
        for i, (texto, comando) in enumerate(botoes_admin):
            btn = ctk.CTkButton(frame_admin, text=texto, command=comando, fg_color="#7F8C8D", hover_color="#6c7a7b", width=80) 
            btn.grid(row=0, column=i, padx=5)

    def criar_tabela(self, parent_frame):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", 
                         background="#343638", 
                         foreground="white", 
                         fieldbackground="#343638",
                         rowheight=25,
                         font=('Arial', 11))
        style.map('Treeview', background=[('selected', '#1F6AA5')])

        style.configure("Treeview.Heading", 
                         font=('Arial', 12, 'bold'), 
                         background="#202224", 
                         foreground="white")

        tree = ttk.Treeview(parent_frame, columns=("ID", "Nome", "Categoria", "Preço", "Quantidade"), show="headings")
        
        tree.column("ID", width=50, anchor="center")
        tree.column("Nome", width=300, anchor="w")
        tree.column("Categoria", width=150, anchor="center")
        tree.column("Preço", width=120, anchor="e")
        tree.column("Quantidade", width=120, anchor="center")
        
        tree.heading("ID", text="ID")
        tree.heading("Nome", text="Nome do Produto")
        tree.heading("Categoria", text="Categoria")
        tree.heading("Preço", text="Preço (R$)")
        tree.heading("Quantidade", text="Qtd. Atual")

        tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        scrollbar = ctk.CTkScrollbar(parent_frame, command=tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=10)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.bind('<Double-1>', self.abrir_modal_edicao)
        
        return tree
    
    def atualizar_tabela(self, tree, alertar=True):
        for item in tree.get_children():
            tree.delete(item)
            
        produtos = sorted(listar_produtos(), key=lambda p: p[4], reverse=False)

        produtos_baixo = []

        for p in produtos:
            id_prod, nome, categoria, preco, qtd = p
            tag = ""
            if qtd < 3: 
                tag = "baixo"
                produtos_baixo.append((nome, qtd))
            elif qtd < 6:
                tag = "medio"
                
            valores_formatados = (id_prod, nome, categoria, f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), qtd)
            tree.insert("", "end", values=valores_formatados, tags=(tag,))

        tree.tag_configure("baixo", background="#7A393E", foreground="white") 
        tree.tag_configure("medio", background="#997A35", foreground="white")

        if alertar and produtos_baixo:
            msg = "\n".join([f"{nome} (qtd: {qtd})" for nome, qtd in produtos_baixo])
            messagebox.showwarning("Atenção! Estoque baixo", f"Os seguintes produtos estão acabando:\n{msg}")

    def abrir_dashboard_completo(self):
        try:
            # Reabre o Dashboard para garantir que os dados estejam atualizados
            app_dashboard = Dashboard()
            app_dashboard.grab_set() 
            app_dashboard.focus_set()
        except Exception as e:
            messagebox.showerror("Erro Dashboard", f"Não foi possível abrir o Dashboard. Erro: {e}")

    # ----------------------------------------------------------------------
    # NOVOS MÉTODOS PARA GERENCIAMENTO DE CATEGORIA (Início da Alteração)
    # ----------------------------------------------------------------------

    def categoria_selecionada_callback(self, choice):
        """Ação ao selecionar uma categoria no ComboBox (pode ser vazia)."""
        pass

    def adicionar_nova_categoria_modal(self):
        """Cria um modal para que o usuário digite e adicione uma nova categoria à lista."""
        modal_add_cat = ctk.CTkToplevel(self)
        modal_add_cat.title("Nova Categoria")
        modal_add_cat.geometry("350x150")
        modal_add_cat.transient(self) # Mantém acima da janela principal
        modal_add_cat.grab_set()
        
        ctk.CTkLabel(modal_add_cat, text="Nome da Nova Categoria:").pack(padx=20, pady=10)
        
        entry_nova_categoria = ctk.CTkEntry(modal_add_cat)
        entry_nova_categoria.pack(padx=20, fill="x")

        def salvar_nova_categoria():
            nova_categoria = entry_nova_categoria.get().strip()
            if nova_categoria and nova_categoria not in self.categorias_padrao:
                # 1. Adiciona na lista da classe
                self.categorias_padrao.append(nova_categoria)
                # 2. Atualiza a lista de valores do ComboBox do modal principal
                # Usamos self.entry_categoria (que é o ComboBox no modal de cadastro)
                if hasattr(self, 'entry_categoria'):
                     self.entry_categoria.configure(values=self.categorias_padrao)
                     self.entry_categoria.set(nova_categoria) # Define a nova categoria como selecionada
                messagebox.showinfo("Sucesso", f"Categoria '{nova_categoria}' adicionada.")
                modal_add_cat.destroy()
            elif nova_categoria in self.categorias_padrao:
                messagebox.showerror("Erro", "Esta categoria já existe.")
            else:
                messagebox.showerror("Erro", "O nome da categoria não pode ser vazio.")

        ctk.CTkButton(modal_add_cat, text="Adicionar", command=salvar_nova_categoria).pack(pady=10)
        modal_add_cat.focus_set()

    # ----------------------------------------------------------------------
    # FIM DOS NOVOS MÉTODOS DE GERENCIAMENTO DE CATEGORIA
    # ----------------------------------------------------------------------


    # --- Funções Modais ---

    def abrir_modal_cadastro(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Cadastrar Novo Produto")
        # Ajusta a geometria para acomodar o novo campo
        modal.geometry("450x300") 
        modal.transient(self) 
        modal.grab_set()
        
        # Estrutura de grid para labels e entries
        modal.grid_columnconfigure(1, weight=1)

        campos = ["Nome:", "Categoria:", "Preço (R$):", "Quantidade Inicial:"]
        # Usa um dicionário para mapear os campos que ainda são entries
        entries = {}
        
        # Campo Nome (row 0)
        ctk.CTkLabel(modal, text="Nome:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_nome = ctk.CTkEntry(modal, width=250)
        entry_nome.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        entries["Nome:"] = entry_nome
        
        # ----------------------------------------------------
        # ALTERAÇÃO: CATEGORIA (row 1)
        # ----------------------------------------------------
        ctk.CTkLabel(modal, text="Categoria:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # 1. Criação do ComboBox (armazenado em self.entry_categoria para ser acessado pelo novo modal)
        self.entry_categoria = ctk.CTkComboBox(
            modal, 
            values=self.categorias_padrao,
            command=self.categoria_selecionada_callback,
            state="readonly"
        )
        self.entry_categoria.set(self.categorias_padrao[0]) # Define o valor inicial
        self.entry_categoria.grid(row=1, column=1, padx=(10, 5), pady=5, sticky="ew")

        # 2. Adicionar o botão para incluir nova categoria
        ctk.CTkButton(
            modal, 
            text="+ Categoria", 
            command=self.adicionar_nova_categoria_modal,
            width=50, 
            fg_color="#3498DB"
        ).grid(row=1, column=2, padx=(0, 10), pady=5, sticky="w")

        # Campo Preço (row 2)
        ctk.CTkLabel(modal, text="Preço (R$):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_preco = ctk.CTkEntry(modal, width=250)
        entry_preco.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        entries["Preço (R$)"] = entry_preco
        
        # Campo Quantidade (row 3)
        ctk.CTkLabel(modal, text="Quantidade Inicial:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_quantidade = ctk.CTkEntry(modal, width=250)
        entry_quantidade.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        entries["Quantidade Inicial:"] = entry_quantidade
        
        # A nova lógica de salvar deve pegar a categoria do ComboBox
        def salvar():
            try:
                nome = entries["Nome:"].get()
                # ----------------------------------------------------
                # ALTERAÇÃO: Pegar categoria do ComboBox
                # ----------------------------------------------------
                categoria = self.entry_categoria.get()
                # ----------------------------------------------------
                preco = entries["Preço (R$)"] .get()
                quantidade = int(entries["Quantidade Inicial:"].get())
                
                cadastrar_produto(nome, categoria, preco, quantidade)
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
                self.atualizar_tabela(self.tree)
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Erro de Cadastro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado: {e}")

        # O botão Salvar fica na última linha
        ctk.CTkButton(modal, text="Salvar", command=salvar, fg_color="#2ECC71").grid(row=len(campos), column=0, columnspan=3, pady=10)


    def abrir_modal_edicao(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return

        item_data = self.tree.item(selected_item)['values']
        produto_id = item_data[0]
        nome_atual = item_data[1]
        preco_atual = item_data[3].replace("R$ ", "").replace(".", "").replace(",", ".") 

        modal = ctk.CTkToplevel(self)
        modal.title(f"Editar: {nome_atual}")
        modal.geometry("350x200")
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(modal, text="Novo Nome:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_nome = ctk.CTkEntry(modal, width=200)
        entry_nome.insert(0, nome_atual)
        entry_nome.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(modal, text="Novo Preço (R$):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_preco = ctk.CTkEntry(modal, width=200)
        entry_preco.insert(0, preco_atual)
        entry_preco.grid(row=1, column=1, padx=10, pady=5)
        
        def deletar():
            if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja DELETAR o produto {nome_atual} (ID: {produto_id})?\nEsta ação não pode ser desfeita."):
                try:
                    deletar_produto(produto_id)
                    messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
                    self.atualizar_tabela(self.tree)
                    modal.destroy()
                except Exception as e:
                    messagebox.showerror("Erro de Exclusão", f"Erro ao deletar: {e}")

        def salvar_edicao():
            try:
                novo_nome = entry_nome.get()
                novo_preco = entry_preco.get()
                
                if novo_nome != nome_atual:
                    atualizar_nome(produto_id, novo_nome)
                
                # A função atualizar_preco já trata a formatação de vírgula/ponto
                novo_preco_limpo = novo_preco.replace("R$ ", "")
                atualizar_preco(produto_id, novo_preco_limpo)

                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
                self.atualizar_tabela(self.tree)
                modal.destroy()
            except ValueError as e:
                messagebox.showerror("Erro de Edição", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado: {e}")
        
        # Frame para botões (Salvar e Excluir)
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="Salvar Alterações", command=salvar_edicao, fg_color="#3498DB").grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Excluir Produto", command=deletar, fg_color="#E74C3C", hover_color="#C0392B").grid(row=0, column=1, padx=5)


    def abrir_modal_movimentacao(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Movimentação de Estoque")
        modal.geometry("400x350")
        modal.transient(self)
        modal.grab_set()
        
        ctk.CTkLabel(modal, text="ID do Produto:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_id = ctk.CTkEntry(modal, width=200)
        entry_id.grid(row=0, column=1, padx=10, pady=5)
        
        label_produto = ctk.CTkLabel(modal, text="Produto: -", text_color="gray")
        label_produto.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(modal, text="Tipo:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        tipo_var = ctk.StringVar(value="entrada")
        radio_entrada = ctk.CTkRadioButton(modal, text="Entrada", variable=tipo_var, value="entrada")
        radio_saida = ctk.CTkRadioButton(modal, text="Saída", variable=tipo_var, value="saida")
        radio_entrada.grid(row=2, column=1, padx=(10, 5), pady=5, sticky="w")
        radio_saida.grid(row=2, column=1, padx=(100, 10), pady=5, sticky="w")
        
        ctk.CTkLabel(modal, text="Quantidade:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_qtd = ctk.CTkEntry(modal, width=200)
        entry_qtd.grid(row=3, column=1, padx=10, pady=5)
        
        def buscar_prod_evento(event=None):
            prod_id_str = entry_id.get().strip() 
            if not prod_id_str.isdigit():
                label_produto.configure(text="Produto: ID inválido ou vazio!", text_color="#E74C3C")
                return

            try:
                prod_id = int(prod_id_str)
                produto = buscar_produto_por_id(prod_id)
                if produto:
                    # CORREÇÃO: Desempacotamento correto da tupla (ID, Nome, Categoria, Preco, Quantidade)
                    id_prod, nome, categoria, preco, qtd_atual = produto
                    label_produto.configure(text=f"Produto: {nome} (Estoque: {qtd_atual})", text_color="#2ECC71")
                else:
                    label_produto.configure(text="Produto: ID não encontrado!", text_color="#E74C3C")
            except Exception as e:
                # Se cair aqui, é um erro de conexão ou de lógica
                print(f"ERRO CRÍTICO no buscar_prod_evento: {e}") 
                label_produto.configure(text="Produto: Erro de busca!", text_color="#E74C3C")
        
        entry_id.bind("<KeyRelease>", buscar_prod_evento)
        entry_id.bind("<FocusOut>", buscar_prod_evento)

        def registrar():
            prod_id_str = entry_id.get().strip()
            qtd_str = entry_qtd.get().strip()
            
            # 1. TRATAMENTO DE ERRO DE FORMATO
            try:
                prod_id = int(prod_id_str)
                qtd = int(qtd_str)
                tipo = tipo_var.get()
            except ValueError:
                messagebox.showerror("Erro de Formato", "O ID e a Quantidade devem ser números inteiros válidos.")
                return

            # 2. VALIDAÇÃO BÁSICA DE ENTRADA
            if qtd <= 0:
                messagebox.showerror("Erro de Entrada", "A quantidade deve ser maior que zero.")
                return

            # 3. VERIFICAÇÃO DE EXISTÊNCIA DO PRODUTO (REMOVIDA a verificação duplicada para confiar no registrar_movimentacao)
            
            # 4. TENTATIVA DE REGISTRO
            try:
                registrar_movimentacao(prod_id, qtd, tipo)
                
                messagebox.showinfo("Sucesso", f"Movimentação de {qtd} unidades ({tipo}) registrada!")
                self.atualizar_tabela(self.tree)
                modal.destroy()
            
            except ValueError as e:
                mensagem_erro = str(e)
                # Tratamento de erros que vêm do movimentacao.py
                if "Estoque insuficiente" in mensagem_erro:
                    messagebox.showerror("Erro de Estoque", mensagem_erro)
                elif "Produto não encontrado" in mensagem_erro:
                    messagebox.showerror("ID Inválido", f"Produto com ID {prod_id_str} não encontrado na base de dados.")
                else:
                    # Este bloco é para ValueErrors não específicos
                    messagebox.showerror("Erro de Registro", f"Erro: {e}")
            
            except Exception as e:
                messagebox.showerror("Erro", f"Erro inesperado: {e}")

        ctk.CTkButton(modal, text="Registrar Movimentação", command=registrar, fg_color="#F39C12").grid(row=4, column=0, columnspan=2, pady=20)


def iniciar_interface(user_id, nome, nivel):
    app = EstoqueApp(user_id, nome, nivel)
    app.mainloop()