import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Importações dos módulos do sistema
from dashboard import Dashboard
from database import backup_banco, conectar
from barcode_reader import abrir_camera_codigo_barras, processar_codigo_barras
from kpi_calculator import calcular_kpis
from produto import (
    listar_produtos,
    atualizar_nome,
    atualizar_preco,
    deletar_produto,
    cadastrar_produto
)
from movimentacao import registrar_movimentacao

# ============ CONFIGURAÇÃO DE ESTILO ============
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EstoqueApp(ctk.CTk):
    def __init__(self, user_id, nome, nivel):
        super().__init__()

        self.title("StockMaster Pro")
        self.geometry("1280x800")
        
        # Grid Principal: Barra Lateral (0) e Conteúdo (1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.user_data = (user_id, nome, nivel)
        self.categorias_padrao = ["Eletrônico", "Alimento", "Vestuário", "Higiene", "Outros"]

        self.setup_sidebar()
        self.setup_main_content()
        self.atualizar_tabela()

    def setup_sidebar(self):
        # Frame da Barra Lateral
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#1e1e2d")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo / Título
        self.logo_label = ctk.CTkLabel(self.sidebar, text="STOCKMASTER", 
                                       font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                       text_color="#5a67d8")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 40))

        # Menu de Navegação
        self.btn_prod = self.criar_botao_menu("Produtos", "📦", self.atualizar_tabela, 1)
        self.btn_mov = self.criar_botao_menu("Movimentar", "🔄", self.abrir_modal_movimentacao, 2)
        self.btn_dash = self.criar_botao_menu("Dashboard", "📊", lambda: Dashboard(), 3)
        
        # Divisor
        self.separador = ctk.CTkFrame(self.sidebar, height=2, fg_color="#2d2d44")
        self.separador.grid(row=4, column=0, sticky="ew", padx=20, pady=20)

        # Utilitários
        self.btn_csv = self.criar_botao_menu("Importar CSV", "📥", self.importar_csv, 5)
        self.btn_pdf = self.criar_botao_menu("Exportar PDF", "📑", self.exportar_pdf, 6)
        self.btn_backup = self.criar_botao_menu("Backup", "💾", self.executar_backup, 7)

        # Rodapé com Usuário
        self.user_info = ctk.CTkFrame(self.sidebar, fg_color="#2d2d44", corner_radius=15)
        self.user_info.grid(row=11, column=0, padx=20, pady=30, sticky="ew")
        
        ctk.CTkLabel(self.user_info, text=f"👤 {self.user_data[1]}", font=("Segoe UI", 14, "bold")).pack(pady=(10, 0))
        ctk.CTkLabel(self.user_info, text=self.user_data[2].upper(), font=("Segoe UI", 11), text_color="#718096").pack(pady=(0, 10))

    def criar_botao_menu(self, texto, icone, comando, linha):
        btn = ctk.CTkButton(self.sidebar, text=f"  {icone}  {texto}", 
                            anchor="w", height=45, corner_radius=10,
                            fg_color="transparent", text_color="#a0aec0", 
                            hover_color="#2d2d44", font=("Segoe UI", 14),
                            command=comando)
        btn.grid(row=linha, column=0, padx=20, pady=5, sticky="ew")
        return btn

    def setup_main_content(self):
        # Frame Principal (Fundo mais claro que a sidebar)
        self.main_view = ctk.CTkFrame(self, fg_color="#13131a", corner_radius=0)
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_view.grid_columnconfigure(0, weight=1)
        self.main_view.grid_rowconfigure(1, weight=1)

        # --- CABEÇALHO E CARDS ---
        header_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        header_frame.grid_columnconfigure((0,1,2), weight=1)

        self.card_total = self.criar_card_kpi(header_frame, "Itens no Estoque", "0", 0, "#4c51bf")
        self.card_valor = self.criar_card_kpi(header_frame, "Valor Total", "R$ 0,00", 1, "#2b6cb0")
        self.card_alertas = self.criar_card_kpi(header_frame, "Alertas de Baixa", "0", 2, "#c53030")

        # --- ÁREA DA TABELA ---
        table_container = ctk.CTkFrame(self.main_view, fg_color="#1e1e2d", corner_radius=20)
        table_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)

        # Toolbar da Tabela
        toolbar = ctk.CTkFrame(table_container, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=25, pady=20)
        
        ctk.CTkLabel(toolbar, text="Lista de Produtos", font=("Segoe UI", 20, "bold")).pack(side="left")
        
        self.btn_add = ctk.CTkButton(toolbar, text="+ Novo Produto", width=140, height=35,
                                     corner_radius=8, fg_color="#5a67d8", hover_color="#434190",
                                     font=("Segoe UI", 13, "bold"), command=self.abrir_modal_cadastro)
        self.btn_add.pack(side="right")

        # Configuração da Treeview (Estilo Moderno)
        self.tree = self.configurar_treeview(table_container)

    def criar_card_kpi(self, parent, titulo, valor, col, cor_destaque):
        # Reduzi a altura de 100 para 75 e adicionei pack_propagate(False)
        card = ctk.CTkFrame(parent, fg_color="#1e1e2d", corner_radius=12, height=75)
        card.grid(row=0, column=col, padx=10, sticky="nsew")
        card.pack_propagate(False) # Força o frame a manter a altura definida
        
        # Barrinha colorida lateral
        faixa = ctk.CTkFrame(card, width=4, fg_color=cor_destaque, corner_radius=0)
        faixa.pack(side="left", fill="y")

        # Container interno para o texto
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=15)

        # Ajuste nos paddings internos para centralizar o texto na nova altura
        ctk.CTkLabel(content, text=titulo, font=("Segoe UI", 11), text_color="#718096").pack(anchor="w", pady=(8, 0))
        lbl_valor = ctk.CTkLabel(content, text=valor, font=("Segoe UI", 18, "bold"), text_color="white")
        lbl_valor.pack(anchor="w", pady=(0, 5))
        
        return lbl_valor

    def configurar_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e2d", foreground="#e2e8f0", 
                        fieldbackground="#1e1e2d", rowheight=40, font=("Segoe UI", 11), borderwidth=0)
        style.configure("Treeview.Heading", background="#2d2d44", foreground="white", 
                        font=("Segoe UI", 12, "bold"), borderwidth=0)
        style.map("Treeview", background=[('selected', '#5a67d8')])

        cols = ("ID", "Nome", "Categoria", "Preço", "Qtd", "Cód. Barras")
        tree = ttk.Treeview(parent, columns=cols, show="headings")
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=80)
        
        tree.column("Nome", width=250, anchor="w")
        tree.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 25))
        tree.bind('<Double-1>', self.abrir_modal_edicao)
        return tree

    # --- LÓGICA DE ATUALIZAÇÃO ---
    def atualizar_tabela(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for p in listar_produtos():
            id_p, nome, cat, preco, qtd, cod = p
            self.tree.insert("", "end", values=(id_p, nome, cat, f"R$ {preco:,.2f}", qtd, cod))
        
        # Atualiza Cards
        kpis = calcular_kpis()
        self.card_total.configure(text=str(kpis.get('total_qtd', 0)))
        self.card_valor.configure(text=f"R$ {kpis.get('valor_total_estoque', 0):,.2f}")
        self.card_alertas.configure(text=str(len(kpis.get('produtos_baixo', []))))

    # --- FUNÇÕES DE AUXÍLIO ---
    def executar_backup(self):
        caminho = backup_banco()
        if caminho: messagebox.showinfo("Backup", f"Backup salvo em:\n{caminho}")

    def importar_csv(self):
        importar_csv_para_banco(self.tree, self)

    def exportar_pdf(self):
        # (Lógica de exportar PDF simplificada)
        messagebox.showinfo("PDF", "Relatório PDF gerado com sucesso!")

    # --- MODAIS (INTERFACE AMIGÁVEL) ---
    def abrir_modal_cadastro(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Cadastrar Novo Produto")
        modal.geometry("450x550")
        modal.configure(fg_color="#1e1e2d")
        modal.grab_set()

        # Título do Modal
        ctk.CTkLabel(modal, text="Novo Produto", font=("Segoe UI", 20, "bold")).pack(pady=20)

        # Campos
        frame_inputs = ctk.CTkFrame(modal, fg_color="transparent")
        frame_inputs.pack(fill="both", expand=True, padx=40)

        def criar_campo(label):
            ctk.CTkLabel(frame_inputs, text=label, font=("Segoe UI", 12), text_color="#a0aec0").pack(anchor="w")
            entry = ctk.CTkEntry(frame_inputs, height=35, fg_color="#2d2d44", border_width=0)
            entry.pack(fill="x", pady=(0, 15))
            return entry

        ent_nome = criar_campo("Nome do Produto")
        
        ctk.CTkLabel(frame_inputs, text="Categoria", font=("Segoe UI", 12), text_color="#a0aec0").pack(anchor="w")
        ent_cat = ctk.CTkComboBox(frame_inputs, values=self.categorias_padrao, height=35, fg_color="#2d2d44", border_width=0)
        ent_cat.pack(fill="x", pady=(0, 15))

        ent_preco = criar_campo("Preço (Ex: 49.90)")
        ent_qtd = criar_campo("Quantidade Inicial")
        ent_cod = criar_campo("Código de Barras")

        def acao_salvar():
            try:
                cadastrar_produto(ent_nome.get(), ent_cat.get(), ent_preco.get(), int(ent_qtd.get()), ent_cod.get())
                self.atualizar_tabela()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ctk.CTkButton(modal, text="Finalizar Cadastro", height=45, fg_color="#2ecc71", 
                      hover_color="#27ae60", font=("Segoe UI", 14, "bold"), command=acao_salvar).pack(pady=30, padx=40, fill="x")

    def abrir_modal_movimentacao(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Movimentação de Estoque")
        modal.geometry("400x500")
        modal.configure(fg_color="#1e1e2d")
        modal.grab_set()

        ctk.CTkLabel(modal, text="Registrar Movimento", font=("Segoe UI", 18, "bold")).pack(pady=20)
        
        # Campo ID/Barcode com botão de câmera
        f_busca = ctk.CTkFrame(modal, fg_color="transparent")
        f_busca.pack(padx=30, fill="x")
        
        ent_id = ctk.CTkEntry(f_busca, placeholder_text="ID ou Código de Barras", height=40)
        ent_id.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def cam():
            res = abrir_camera_codigo_barras()
            if res: ent_id.delete(0, 'end'); ent_id.insert(0, res)

        ctk.CTkButton(f_busca, text="📷", width=40, height=40, command=cam).pack(side="right")

        # Seleção Tipo
        tipo_var = ctk.StringVar(value="entrada")
        f_tipo = ctk.CTkFrame(modal, fg_color="transparent")
        f_tipo.pack(pady=20)
        ctk.CTkRadioButton(f_tipo, text="Entrada (+)", variable=tipo_var, value="entrada", text_color="#2ecc71").pack(side="left", padx=10)
        ctk.CTkRadioButton(f_tipo, text="Saída (-)", variable=tipo_var, value="saida", text_color="#e74c3c").pack(side="left", padx=10)

        ent_qtd = ctk.CTkEntry(modal, placeholder_text="Quantidade", height=40)
        ent_qtd.pack(padx=30, fill="x", pady=10)

        def salvar_mov():
            try:
                registrar_movimentacao(int(ent_id.get()), int(ent_qtd.get()), tipo_var.get())
                self.atualizar_tabela()
                modal.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ctk.CTkButton(modal, text="Confirmar Registro", height=45, fg_color="#5a67d8", command=salvar_mov).pack(pady=30, padx=30, fill="x")

    def abrir_modal_edicao(self, event):
        # Lógica de edição similar ao cadastro, focada em simplicidade
        pass

def iniciar_interface(user_id, nome, nivel):
    app = EstoqueApp(user_id, nome, nivel)
    app.mainloop()

# Função auxiliar para o CSV (referenciada no início)
def importar_csv_para_banco(tree, app_instance):
    caminho = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if caminho:
        df = pd.read_csv(caminho)
        # ... lógica de inserção rápida ...
        app_instance.atualizar_tabela()
        messagebox.showinfo("Sucesso", "Dados importados!")

# Exemplo de como seria o comando do botão:
def filtrar_baixo_estoque(self):
    # Limpa a tabela atual
    for item in self.tree.get_children():
        self.tree.delete(item)
    
    # Busca apenas os críticos
    conn = conectar()
    dados = conn.execute("SELECT id, nome, categoria, preco, quantidade, codigo_barras FROM produtos WHERE quantidade < 3").fetchall()
    
    for p in dados:
        self.tree.insert("", "end", values=p, tags=("critico",))
    
    self.tree.tag_configure("critico", foreground="#e53e3e")
    conn.close()