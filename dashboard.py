# dashboard.py

import customtkinter as ctk
import sqlite3
# Importa o calculador de KPIs
from kpi_calculator import calcular_kpis 
from database import conectar 

# Importante: Classe herda de CTkToplevel para abrir como janela secundária
class Dashboard(ctk.CTkToplevel): 
    def __init__(self):
        super().__init__()
        self.title("Painel de Indicadores")
        self.geometry("1200x600") 
        self.resizable(True, True) 
        
        self.grab_set() 
        self.focus_set()

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) 
        self.grid_rowconfigure(1, weight=1) 
        
        self.criar_cards()
        self.criar_busca()

    # Função para buscar e calcular todos os KPIs
    def calcular_kpis(self):
        # Chama a função que agora está em kpi_calculator.py
        return calcular_kpis()

    def criar_cards(self):
        # Frame que contém todos os cards na linha 0
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=0, column=0, columnspan=5, padx=20, pady=(20, 10), sticky="new")
        cards_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        kpis = self.calcular_kpis()
        
        # --- CARD 1: SOMA TOTAL DE UNIDADES ---
        card1 = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#2E8B57") 
        card1.grid(row=0, column=0, padx=10, sticky="nsew")
        ctk.CTkLabel(card1, text="📦 Soma Total de Unidades", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card1, text=f"{kpis['total_qtd']} unidades", font=("Arial", 22)).pack(pady=10)
        ctk.CTkLabel(card1, text="", font=("Arial", 10)).pack(pady=(0, 5)) 


        # --- CARD 2: PREÇO TOTAL EM PRODUTOS (Valor Monetário) ---
        valor_formatado = f"R$ {kpis['valor_total_estoque']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        card2 = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#4682B4") 
        card2.grid(row=0, column=1, padx=10, sticky="nsew")
        ctk.CTkLabel(card2, text="💸 Preço Total em Produtos", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card2, text=valor_formatado, font=("Arial", 22)).pack(pady=10)
        ctk.CTkLabel(card2, text="Valor monetário de todo o estoque.", font=("Arial", 8)).pack(pady=(0, 5)) 


        # --- CARD 3: ESTOQUE BAIXO ---
        num_baixo = len(kpis['produtos_baixo'])
        nomes_baixo = ", ".join([f"{n} ({q})" for n, q in kpis['produtos_baixo'][:2]]) 
        cor_alerta = "#C0392B" if num_baixo > 0 else "#2ECC71" 
        
        card3 = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color=cor_alerta) 
        card3.grid(row=0, column=2, padx=10, sticky="nsew")
        ctk.CTkLabel(card3, text="⚠️ Itens em Estoque Baixo", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card3, text=f"{num_baixo} itens", font=("Arial", 22)).pack(pady=10)
        ctk.CTkLabel(card3, text=nomes_baixo if nomes_baixo else "Tudo ok!", font=("Arial", 10)).pack(pady=(0, 5))


        # --- CARD 4: Giro de Estoque ---
        giro_formatado = f"{kpis['giro']:.1f}x"
        card4 = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#F39C12") 
        card4.grid(row=0, column=3, padx=10, sticky="nsew")
        ctk.CTkLabel(card4, text="🔄 Giro de Estoque (30d)", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card4, text=giro_formatado, font=("Arial", 22)).pack(pady=10)
        ctk.CTkLabel(card4, text="Quantas vezes o estoque 'girou' no mês.", font=("Arial", 8)).pack(pady=(0, 5))


        # --- CARD 5: Custo de Manutenção ---
        custo_formatado = f"R$ {kpis['custo_manutencao']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        card5 = ctk.CTkFrame(cards_frame, corner_radius=10, fg_color="#8E44AD") 
        card5.grid(row=0, column=4, padx=10, sticky="nsew")
        ctk.CTkLabel(card5, text="💰 Custo de Manutenção (15% anual)", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(card5, text=custo_formatado, font=("Arial", 22)).pack(pady=10)
        ctk.CTkLabel(card5, text="", font=("Arial", 10)).pack(pady=(0, 5)) 


    def criar_busca(self):
        # Card de Busca (Ocupa a linha 1 inteira, abaixo dos cards)
        card_busca = ctk.CTkFrame(self, corner_radius=10, fg_color="#34495E")
        card_busca.grid(row=1, column=0, columnspan=5, padx=20, pady=(10, 20), sticky="nsew") 
        
        card_busca.grid_columnconfigure(0, weight=1)
        card_busca.grid_columnconfigure(1, weight=3)
        card_busca.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(card_busca, text="🔍 Buscar Produto:", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.entry_busca = ctk.CTkEntry(card_busca, placeholder_text="Digite o nome ou ID do produto", width=300)
        self.entry_busca.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entry_busca.bind("<Return>", self.buscar_produto)

        self.label_resultado = ctk.CTkLabel(card_busca, text="Resultado:", font=("Arial", 14), justify="left")
        self.label_resultado.grid(row=1, column=0, columnspan=3, padx=20, pady=(5, 10), sticky="w")

    def buscar_produto(self, event=None):
        termo = self.entry_busca.get()
        if not termo:
            self.label_resultado.configure(text="Resultado: Digite um termo de busca.")
            return
        
        # Usa a função conectar() do database.py
        conn = conectar() 
        cursor = conn.cursor()
        
        try:
            produto_id = int(termo)
            cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE id = ?", (produto_id,))
        except ValueError:
            cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE nome LIKE ?", ('%' + termo + '%',))
            
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            nome, preco, quantidade = resultado
            preco_formatado = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            texto = f"Resultado: {nome} | Preço: {preco_formatado} | Estoque: {quantidade}"
            self.label_resultado.configure(text=texto, text_color="#2ECC71")
        else:
            self.label_resultado.configure(text=f"Resultado: Nenhum produto encontrado para '{termo}'.", text_color="#E74C3C")