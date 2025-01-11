import customtkinter as ctk
from Telas.tela_menu import MenuFrame
from PIL import Image, ImageTk
from db import inicializar_banco
from Util.path import get_resource_path
import sys
import os

# Inicializar o banco de dados
inicializar_banco()

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def iniciar():
    frame_atual.mostrar_menu()

def fechar():
    app.destroy()

# Configuração principal
ctk.set_appearance_mode("dark")  # Tema escuro
ctk.set_default_color_theme("blue")  # Tema de cores

app = ctk.CTk()
app.title("Apresentação")

app.state('zoomed')

app.configure(fg_color="white")  # Define o fundo do sistema como branco

class TelaInicial(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="white")  # Define o fundo do frame como branco
        self.pack(fill="both", expand=True)

        # Cria o frame do menu, mas não o exibe ainda
        self.menu_frame = MenuFrame(master=master, voltar_callback=self.mostrar_tela_inicial)
        self.menu_frame.pack_forget()

        self.criar_tela_inicial()

    def criar_tela_inicial(self):
        # Limpa a tela antes de criar novos widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Carrega a imagem da capa
        image_path = get_resource_path("Imgs/capa.png")
        image = Image.open(image_path)
        screen_width = self.winfo_screenwidth()
        original_width, original_height = image.size
        aspect_ratio = original_height / original_width
        new_width = screen_width
        new_height = int(new_width * aspect_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image)
        label_img = ctk.CTkLabel(self, image=img_tk, text="")
        label_img.image = img_tk  # Mantém a referência da imagem
        label_img.pack(pady=20)

        # Ícones FontAwesome para os botões
        from tkfontawesome import icon_to_image  # Importa suporte para ícones FontAwesome
        icon_start = icon_to_image("power-off", fill="#fcb333", scale_to_width=24)
        icon_exit = icon_to_image("times", fill="red", scale_to_width=24)

        # Botões
        btn_iniciar = ctk.CTkButton(
            self,
            text=" Iniciar",
            image=icon_start,
            corner_radius=30,
            width=150,
            height=50,
            fg_color="transparent",
            border_color="#fcb333",
            border_width=2,
            text_color="#fcb333",
            hover_color="#fcb333",
            font=("Verdana", 20),
            compound="left",
            command=iniciar
        )
        btn_iniciar.pack(pady=10)

        btn_fechar = ctk.CTkButton(
            self,
            text=" Fechar",
            image=icon_exit,
            corner_radius=30,
            width=150,
            height=50,
            fg_color="transparent",
            border_color="red",
            border_width=2,
            text_color="red",
            hover_color="red",
            font=("Verdana", 20),
            compound="left",
            command=fechar
        )
        btn_fechar.pack(pady=10)

        # Centraliza os botões na tela
        self.pack_propagate(False)
        self.pack(expand=True)

    def mostrar_menu(self):
        self.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def mostrar_tela_inicial(self):
        self.menu_frame.pack_forget()
        self.pack(fill="both", expand=True)

frame_atual = TelaInicial(master=app)

# Executar a aplicação
app.mainloop()
