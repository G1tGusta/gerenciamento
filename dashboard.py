import customtkinter as ctk
import sqlite3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel de Indicadores")
        self.geometry("850x500")
        self.resizable(False, False)

        self.conexao = sqlite3.connect("estoque.db")
        self.cursor = self.conexao.cursor()

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.criar_cards()
        self.criar_busca()

    def criar_cards(self):
        # Card 1: Estoque total
        total_qtd = self.cursor.execute("SELECT SUM(quantidade) FROM produtos").fetchone()[0] or 0
        card1 = ctk.CTkFrame(self, corner_radius=10, fg_color="#2E8B57")
        card1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(card1, text="📦 Total em Estoque", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card1, text=f"{total_qtd} unidades", font=("Arial", 20)).pack()

        # Card 2: Valor total
        total_valor = self.cursor.execute("SELECT SUM(quantidade * preco) FROM produtos").fetchone()[0] or 0
        card2 = ctk.CTkFrame(self, corner_radius=10, fg_color="#4682B4")
        card2.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(card2, text="💰 Valor Total", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card2, text=f"R$ {total_valor:.2f}", font=("Arial", 20)).pack()

        # Card 3: Produtos em falta
        produtos_falta = self.cursor.execute("SELECT nome FROM produtos WHERE quantidade <= 1").fetchall()
        nomes = ", ".join([p[0] for p in produtos_falta])
        card3 = ctk.CTkFrame(self, corner_radius=10, fg_color="#B22222")
        card3.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")
        ctk.CTkLabel(card3, text="⚠️ Estoque Baixo", font=("Arial", 16, "bold")).pack(pady=5)
        ctk.CTkLabel(card3, text=nomes if nomes else "Tudo ok!", font=("Arial", 14)).pack()

    def criar_busca(self):
        card_busca = ctk.CTkFrame(self, corner_radius=10)
        card_busca.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        ctk.CTkLabel(card_busca, text="🔍 Buscar Produto", font=("Arial", 16, "bold")).pack(pady=5)
        self.entry_busca = ctk.CTkEntry(card_busca, placeholder_text="Digite o nome do produto")
        self.entry_busca.pack(pady=10)
        self.entry_busca.bind("<Return>", self.buscar_produto)

        self.label_resultado = ctk.CTkLabel(card_busca, text="", font=("Arial", 14))
        self.label_resultado.pack(pady=5)

    def buscar_produto(self, event):
        nome = self.entry_busca.get()
        resultado = self.cursor.execute("SELECT nome, categoria, preco, quantidade FROM produtos WHERE nome LIKE ?", (f"%{nome}%",)).fetchall()

        if resultado:
            texto = "\n".join([f"{r[0]} | {r[1]} | R$ {r[2]:.2f} | Est: {r[3]}" for r in resultado])
            self.label_resultado.configure(text=texto)
        else:
            self.label_resultado.configure(text="Produto não encontrado.")

if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
