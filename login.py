# login.py
import customtkinter as ctk
from usuario import autenticar
from interface import iniciar_interface

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x200")

        ctk.CTkLabel(self, text="Usuário").pack(pady=5)
        self.entry_user = ctk.CTkEntry(self)
        self.entry_user.pack()

        ctk.CTkLabel(self, text="Senha").pack(pady=5)
        self.entry_pass = ctk.CTkEntry(self, show="*")
        self.entry_pass.pack()

        ctk.CTkButton(self, text="Entrar", command=self.verificar_login).pack(pady=10)

        self.label_erro = ctk.CTkLabel(self, text="", text_color="red")
        self.label_erro.pack()

    def verificar_login(self):
        usuario = self.entry_user.get()
        senha = self.entry_pass.get()

        dados = autenticar(usuario, senha)
        if dados:
            user_id, nome, nivel = dados
            self.destroy()  # Fecha a janela de login
            iniciar_interface(user_id, nome, nivel)  # Abre a interface principal
        else:
            self.label_erro.configure(text="Usuário ou senha inválidos.")

def iniciar_login():
    app = LoginApp()
    app.mainloop()
