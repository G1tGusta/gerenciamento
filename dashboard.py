# dashboard.py (Versão Final com Novo Layout de Gráficos)

import customtkinter as ctk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np 
from tkinter import ttk 
from kpi_calculator import calcular_kpis 
from database import conectar 

class Dashboard(ctk.CTkToplevel): 
    def __init__(self):
        super().__init__()
        self.title("Painel de Indicadores de Estoque (Final)")
        self.geometry("1400x1000") 
        self.resizable(True, True) 
        
        self.grab_set() 
        self.focus_set()

        # Configuração do Grid principal (5 colunas para os 5 cards)
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) 
        
        # --- Distribuição Vertical Otimizada ---
        # Linha 0: Cards (altura fixa)
        
        # Linha 1: Gráficos (Rosca + Barras) - Lado a Lado
        self.grid_rowconfigure(1, weight=1) 
        
        # Linha 2: Tabela de Resumo (Ocupa o maior espaço vertical)
        self.grid_rowconfigure(2, weight=2) 
        # Linha 3 (Antiga) foi removida, o peso 2 foi para a nova Linha 2
        
        self.criar_cards() # Linha 0
        self.criar_graficos_linha1() # Linha 1 (Rosca + Barras)
        # self.criar_grafico_barras_centralizado() # REMOVIDO
        self.criar_tabela_movimentacoes() # Linha 2 (Tabela)

    def calcular_kpis(self):
        return calcular_kpis()

    # =========================================================
    # Linha 0: CARDS SCORECARD
    # =========================================================
    def criar_cards(self):
        # Frame que contém todos os cards na linha 0
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=0, column=0, columnspan=5, padx=20, pady=(20, 10), sticky="new")
        cards_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        kpis = self.calcular_kpis()
        
        def criar_card(pai, coluna, titulo, valor, descricao, cor):
            card = ctk.CTkFrame(pai, corner_radius=10, fg_color="white")
            card.grid(row=0, column=coluna, padx=10, sticky="nsew")
            
            ctk.CTkFrame(card, height=5, fg_color=cor).pack(fill="x")
            
            ctk.CTkLabel(card, text=titulo, font=("Arial", 12, "bold"), text_color="gray").pack(pady=(10, 0))
            ctk.CTkLabel(card, text=valor, font=("Arial", 26, "bold"), text_color="black").pack(pady=(5, 5))
            ctk.CTkLabel(card, text=descricao, font=("Arial", 8), text_color="gray").pack(pady=(0, 10))

        # 1. Estoque Total
        criar_card(cards_frame, 0, "📦 Estoque Total (Unidades)", 
                   f"{kpis['total_qtd']} un.", "Contagem total de itens no armazém.", "#2E8B57")
        # 2. Valor Total
        valor_formatado = f"R$ {kpis['valor_total_estoque']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        criar_card(cards_frame, 1, "💸 Valor Total de Estoque", 
                   valor_formatado, "Valor monetário de todo o estoque.", "#4682B4")
        # 3. Estoque Baixo
        num_baixo = len(kpis['produtos_baixo'])
        cor_alerta = "#C0392B" if num_baixo > 0 else "#2ECC71" 
        descricao_baixo = f"{num_baixo} item(ns) requer atenção." if num_baixo > 0 else "Nenhum alerta crítico."
        criar_card(cards_frame, 2, "⚠️ Itens em Estoque Baixo", 
                   f"{num_baixo} itens", descricao_baixo, cor_alerta)
        # 4. Giro de Estoque
        giro_formatado = f"{kpis['giro']:.1f}x"
        giro_desc = "Quanto maior o valor, melhor." if kpis['giro'] >= 1.0 else "Baixa ou moderada movimentação."
        criar_card(cards_frame, 3, "🔄 Giro de Estoque (30d)", 
                   giro_formatado, giro_desc, "#F39C12")
        # 5. Custo de Manutenção
        custo_manutencao = kpis['custo_manutencao']
        custo_formatado = f"R$ {custo_manutencao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        criar_card(cards_frame, 4, "💰 Custo de Manutenção (Anual)", 
                   custo_formatado, "Estimativa de 15% do valor total.", "#8E44AD")

    # =========================================================
    # GRÁFICO A: DISTRIBUIÇÃO ESTOQUE NORMAL vs. BAIXO (ROSCA)
    # =========================================================
    def plotar_distribuicao_estoque(self, frame_pai):
        kpis = self.calcular_kpis()
        total_qtd = kpis['total_qtd']
        itens_baixo_qtd = sum(q for _, q in kpis['produtos_baixo']) 
        
        if total_qtd <= 0:
            ctk.CTkLabel(frame_pai, text="Estoque Vazio.", text_color="#E67E22").pack(pady=20)
            return

        estoque_normal = total_qtd - itens_baixo_qtd
        
        valores = [itens_baixo_qtd, estoque_normal]
        cores = ['#C0392B', '#2ECC71'] 

        # Tamanho reduzido para centralizar
        fig, ax = plt.subplots(figsize=(3.5, 3.5)) 
        
        # Fundo Cinza Claro para contraste
        fig.patch.set_facecolor('#F0F0F0') 
        ax.set_facecolor('#F0F0F0') 
        
        ax.pie(valores, 
               autopct=lambda pct: f"{pct:.1f}%" if pct > 0 else '',
               textprops=dict(color="black", fontsize=8, fontweight='bold'), 
               colors=cores,
               startangle=90,
               wedgeprops=dict(width=0.4, edgecolor='#292727'))

        # Título superior centralizado
        ax.set_title('Distribuição de Estoque por Unidades', color='black', fontdict={'fontsize': 10, 'fontweight': 'bold'}) 
        
        # Legenda horizontal centralizada abaixo
        legenda_texto = f'  ● Baixo ({itens_baixo_qtd} un) | ● Normal ({estoque_normal} un)'
        ax.text(0.5, -0.1, legenda_texto, 
                ha='center', 
                transform=ax.transAxes, 
                fontsize=7, 
                color='gray')
        
        ax.axis('equal') 
        
        self._embed_matplotlib(fig, frame_pai)

    # =========================================================
    # GRÁFICO B: COMPOSIÇÃO POR CATEGORIA (BARRAS VERTICAIS)
    # =========================================================
    def plotar_composicao_categoria(self, frame_pai):
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COALESCE(categoria, 'Sem Categoria') AS cat, SUM(quantidade) 
            FROM produtos 
            GROUP BY cat 
            ORDER BY SUM(quantidade) DESC
        """)
        dados_categoria = cursor.fetchall()
        conn.close()

        if not dados_categoria:
            ctk.CTkLabel(frame_pai, text="Não há dados de categorias no estoque.", text_color="gray").pack(pady=20)
            return
            
        categorias = [d[0] for d in dados_categoria]
        quantidades = [d[1] for d in dados_categoria]
        
        # Tamanho ajustado para ser quadrado (4x4) para caber ao lado do rosca
        fig, ax = plt.subplots(figsize=(4, 4)) 
        fig.patch.set_facecolor("#F0F0F0") 
        ax.set_facecolor("#F0F0F0") 

        # Barras Verticais (bar)
        ax.bar(categorias, quantidades, color='#3498DB')
        
        ax.set_title('Composição do Estoque (Unidades)', color='black', fontdict={'fontsize': 10, 'fontweight': 'bold'})
        ax.set_ylabel('Quantidade (Unidades)', color='black', fontsize=9) 
        
        # Ajuste de rotação para rótulos X (categorias)
        plt.xticks(rotation=45, ha='right', fontsize=8) 
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', colors='black')
        ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray') # Grid no eixo Y
        
        fig.tight_layout()
        
        self._embed_matplotlib(fig, frame_pai)

    # =========================================================
    # FUNÇÕES DE LAYOUT GERAIS
    # =========================================================
    def _embed_matplotlib(self, fig, frame_pai):
        for widget in frame_pai.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_pai)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)
        canvas.draw()


    def criar_graficos_linha1(self): # NOVO NOME para o agrupamento
        # Linha 1: Rosca Distribuição (Esquerda) e Barras Categoria (Direita)
        graficos_frame = ctk.CTkFrame(self, fg_color="transparent")
        graficos_frame.grid(row=1, column=0, columnspan=5, padx=20, pady=10, sticky="nsew")
        
        graficos_frame.grid_columnconfigure(0, weight=1) # Rosca
        graficos_frame.grid_columnconfigure(1, weight=1) # Barras
        
        # Gráfico 1: Rosca (Distribuição)
        card_distribuicao = ctk.CTkFrame(graficos_frame, fg_color="white", corner_radius=10)
        card_distribuicao.grid(row=0, column=0, padx=10, sticky="nsew")
        self.plotar_distribuicao_estoque(card_distribuicao) 
        
        # Gráfico 2: Barras (Composição)
        card_composicao = ctk.CTkFrame(graficos_frame, fg_color="white", corner_radius=10)
        card_composicao.grid(row=0, column=1, padx=10, sticky="nsew")
        self.plotar_composicao_categoria(card_composicao)
        
    
    # Função removida: criar_grafico_barras_centralizado (pois o gráfico foi movido)


    # =========================================================
    # Linha 2: TABELA DE MOVIMENTAÇÕES (HISTÓRICO)
    # =========================================================
    def criar_tabela_movimentacoes(self):
        # Frame da Tabela (Linha 2 - Antiga Linha 3)
        tabela_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        tabela_frame.grid(row=2, column=0, columnspan=5, padx=20, pady=(10, 20), sticky="nsew")
        
        ctk.CTkLabel(tabela_frame, text="Últimas Movimentações (Histórico)", font=("Arial", 16, "bold"), text_color="black").pack(pady=(10, 5))

        style = ttk.Style()
        style.theme_use("default") 
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), foreground='white', background='#4682B4') 
        style.configure("Treeview", font=('Arial', 10), rowheight=25, background='white', foreground='black')
        style.map("Treeview", background=[('selected', '#F0F0F0')]) 

        self.tree = ttk.Treeview(tabela_frame, columns=("ID", "Produto", "Tipo", "Quantidade", "Data"), show='headings')

        self.tree.heading("ID", text="ID Mov.")
        self.tree.heading("Produto", text="Produto")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Quantidade", text="Quantidade")
        self.tree.heading("Data", text="Data/Hora")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Produto", width=400, anchor="w")
        self.tree.column("Tipo", width=120, anchor="center")
        self.tree.column("Quantidade", width=120, anchor="center")
        self.tree.column("Data", width=200, anchor="center")

        scrollbar = ctk.CTkScrollbar(tabela_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))
        
        self.carregar_movimentacoes_resumo()

    def carregar_movimentacoes_resumo(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                m.id, 
                p.nome, 
                m.tipo, 
                m.quantidade, 
                STRFTIME('%d/%m/%Y %H:%M', m.data)
            FROM movimentacoes m
            JOIN produtos p ON m.produto_id = p.id
            ORDER BY m.id DESC 
            LIMIT 20
        """)
        movimentacoes = cursor.fetchall()
        conn.close()
        
        for mov in movimentacoes:
            cor_tag = 'entrada' if mov[2] == 'entrada' else 'saida'
            self.tree.tag_configure('entrada', foreground='#2E8B57') 
            self.tree.tag_configure('saida', foreground='#C0392B') 
            
            self.tree.insert("", "end", values=mov, tags=(cor_tag,))