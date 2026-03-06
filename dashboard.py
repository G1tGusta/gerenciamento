import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk 
from kpi_calculator import calcular_kpis 
from database import conectar 

class Dashboard(ctk.CTkToplevel): 
    def __init__(self):
        super().__init__()
        self.title("StockMaster Analytics - Central de Controle")
        self.geometry("1300x850") 
        self.configure(fg_color="#13131a")
        
        self.grab_set() 
        self.focus_set()

        # Grid: 2 colunas, 2 linhas de conteúdo principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.setup_estilo_matplotlib()
        self.criar_cards() 
        
        # 1. Gráfico de Saúde (Rosca)
        self.g1 = self.criar_container(1, 0, "SAÚDE DO ESTOQUE")
        # 2. Painel de Alerta (A LISTA QUE VOCÊ QUERIA)
        self.g2 = self.criar_container(1, 1, "⚠️ NECESSITAM DE REPOSIÇÃO (URGENTE)")
        # 3. Gráfico de Valor por Categoria
        self.g3 = self.criar_container(2, 0, "VALOR POR CATEGORIA")
        # 4. Gráfico de Tendência
        self.g4 = self.criar_container(2, 1, "FLUXO DE MOVIMENTAÇÃO (7 DIAS)")

        self.renderizar_conteudo()

    def setup_estilo_matplotlib(self):
        plt.rcParams.update({
            'text.color': 'white', 'axes.labelcolor': '#a0aec0',
            'xtick.color': '#718096', 'ytick.color': '#718096',
            'axes.facecolor': '#1e1e2d', 'figure.facecolor': '#1e1e2d',
            'axes.edgecolor': '#2d2d44', 'font.size': 9
        })

    def criar_container(self, r, c, titulo):
        f = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=15)
        f.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        ctk.CTkLabel(f, text=titulo, font=("Segoe UI", 12, "bold"), text_color="#5a67d8").pack(pady=(10, 5))
        return f

    def criar_cards(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        for i in range(5): frame.grid_columnconfigure(i, weight=1)
        
        k = calcular_kpis()
        self.card(frame, 0, "TOTAL UN.", f"{k['total_qtd']}", "#5a67d8")
        self.card(frame, 1, "VALOR TOTAL", f"R$ {k['valor_total_estoque']:,.0f}", "#38b2ac")
        self.card(frame, 2, "EM FALTA", f"{len(k['produtos_baixo'])}", "#e53e3e")
        self.card(frame, 3, "GIRO", f"{k['giro']:.1f}x", "#f6ad55")
        self.card(frame, 4, "ITENS", f"{k['total_produtos']}", "#9f7aea")

    def card(self, pai, col, tit, val, cor):
        c = ctk.CTkFrame(pai, fg_color="#1e1e2d", corner_radius=12, height=70)
        c.grid(row=0, column=col, padx=5, sticky="nsew")
        c.pack_propagate(False)
        ctk.CTkFrame(c, width=4, fg_color=cor).pack(side="left", fill="y")
        ctk.CTkLabel(c, text=tit, font=("Segoe UI", 9, "bold"), text_color="#718096").pack(anchor="w", padx=12, pady=(8,0))
        ctk.CTkLabel(c, text=val, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=12)

    def renderizar_conteudo(self):
        k = calcular_kpis()
        
        # --- 1. GRÁFICO DE ROSCA ---
        fig1, ax1 = plt.subplots(figsize=(3, 2))
        baixo = sum(q for _, q in k['produtos_baixo'])
        normal = max(0, k['total_qtd'] - baixo)
        ax1.pie([baixo, normal], labels=['Crítico', 'OK'], colors=['#e53e3e', '#38b2ac'], 
                startangle=90, wedgeprops={'width': 0.4})
        self._embed(fig1, self.g1)

        # --- 2. PAINEL DE LISTA DE REPOSIÇÃO (O que você pediu) ---
        self.renderizar_lista_urgente(k['produtos_baixo'])

        # --- 3. BARRAS CATEGORIA ---
        conn = conectar()
        dados_cat = conn.execute("SELECT categoria, SUM(preco * quantidade) FROM produtos GROUP BY 1 LIMIT 5").fetchall()
        fig3, ax3 = plt.subplots(figsize=(4, 2.5))
        if dados_cat:
            cats = [str(d[0])[:8] for d in dados_cat]
            vals = [d[1] for d in dados_cat]
            ax3.bar(cats, vals, color='#38b2ac')
        self._embed(fig3, self.g3)

        # --- 4. LINHA TENDÊNCIA ---
        dados_mov = conn.execute("""
            SELECT STRFTIME('%d/%m', data) as dia, SUM(quantidade) 
            FROM movimentacoes WHERE data >= DATETIME('now', '-7 days')
            GROUP BY dia ORDER BY data ASC
        """).fetchall()
        conn.close()
        fig4, ax4 = plt.subplots(figsize=(4, 2.5))
        if dados_mov:
            dias = [d[0] for d in dados_mov]
            qtds = [d[1] for d in dados_mov]
            ax4.plot(dias, qtds, color='#f6ad55', marker='o')
        self._embed(fig4, self.g4)

    def renderizar_lista_urgente(self, lista_produtos):
        # Container com scroll para não cortar se tiver muitos itens
        scroll_frame = ctk.CTkScrollableFrame(self.g2, fg_color="transparent", height=200)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        if not lista_produtos:
            ctk.CTkLabel(scroll_frame, text="✅ Todo o estoque está normal", text_color="#38b2ac").pack(pady=50)
            return

        for nome, qtd in lista_produtos:
            item = ctk.CTkFrame(scroll_frame, fg_color="#2d2d44", corner_radius=8)
            item.pack(fill="x", pady=3, padx=5)
            
            # Nome do produto
            ctk.CTkLabel(item, text=f"• {nome}", font=("Segoe UI", 11, "bold")).pack(side="left", padx=10, pady=5)
            # Quantidade em destaque
            ctk.CTkLabel(item, text=f"{qtd} un", font=("Segoe UI", 11), text_color="#e53e3e").pack(side="right", padx=10)

    def _embed(self, fig, pai):
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=pai)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)