import customtkinter as ctk
from PIL import Image, ImageTk, ImageEnhance
from Telas.tela_produtos import ProdutoFrame


class MenuFrame(ctk.CTkFrame):
    def __init__(self, master, voltar_callback):
        super().__init__(master)
        self.configure(fg_color="white")  # Define o fundo como branco
        self.voltar_callback = voltar_callback

        # Configurar o layout para centralizar os widgets
        self.grid_rowconfigure(0, weight=1)  # Espaço antes
        self.grid_rowconfigure(2, weight=1)  # Espaço depois
        self.grid_columnconfigure(0, weight=1)  # Centralização horizontal

        self.criar_menu()

    def criar_menu(self):
        # Frame central para os elementos
        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Lista de botões do menu com textos e comandos
        buttons = [
            ("Produtos", self.abrir_produtos),
            ("Vendas", self.abrir_vendas),
            ("Gráficos", self.abrir_graficos),
            ("Ajuda", self.abrir_ajuda),
        ]

        # Carregar as imagens e criar versões escurecidas para hover
        images = {}
        for text, _ in buttons:
            # Caminho da imagem original
            image_path = f"Imgs/{text.lower()}.png"
            original_image = Image.open(image_path)

            # Manter proporção original com largura máxima de 200
            max_width = 200
            ratio = max_width / original_image.width
            new_size = (int(original_image.width * ratio), int(original_image.height * ratio))
            resized_image = original_image.resize(new_size, Image.Resampling.LANCZOS)

            # Criar versões normal e hover
            images[text] = {
                "normal": ImageTk.PhotoImage(resized_image),
                "hover": ImageTk.PhotoImage(ImageEnhance.Brightness(resized_image).enhance(0.7)),
            }

        # Adicionar título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Menu Principal",
            font=("Verdana", 48, "bold"),
            text_color="#fcb333",  # Cor amarela correspondente
        )
        title_label.pack(pady=20)

        # Adicionar botões com imagens
        button_frame = ctk.CTkFrame(main_frame, fg_color="white")
        button_frame.pack(pady=20)

        for i, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,  # Adiciona o texto do botão
                width=images[text]["normal"].width(),  # Largura da imagem
                height=images[text]["normal"].height() + 40,  # Altura ajustada para incluir o texto
                font=("Verdana", 14, "bold"),  # Fonte maior e em negrito
                image=images[text]["normal"],  # Imagem normal
                compound="top",  # Texto abaixo da imagem
                command=command,
            )
            btn.image = images[text]["normal"]  # Evitar garbage collection
            btn.grid(row=0, column=i, padx=10, pady=10)

            # Adicionar comportamento de hover
            btn.bind(
                "<Enter>",
                self._hover_handler(btn, images[text]["hover"]),
            )
            btn.bind(
                "<Leave>",
                self._hover_handler(btn, images[text]["normal"]),
            )

        # Botão para voltar
        btn_voltar = ctk.CTkButton(
            main_frame,
            text="Voltar",
            width=150,
            height=40,
            font=("Verdana", 16),
            fg_color="gray",
            command=self.voltar_callback,
        )
        btn_voltar.pack(pady=20)

    def _hover_handler(self, btn, img):
        """Retorna uma função para lidar com o hover."""
        def on_hover(event):
            btn.configure(image=img)
        return on_hover

    def mostrar_menu(self):
        if hasattr(self, 'tela_produtos'):
            self.tela_produtos.pack_forget()
        self.pack(fill="both", expand=True)

    def abrir_produtos(self):
        self.pack_forget()  # Esconde o menu atual
        self.tela_produtos = ProdutoFrame(master=self.master, voltar_callback=self.mostrar_menu)
        self.tela_produtos.pack(fill="both", expand=True)

    def abrir_vendas(self):
        print("Abrindo Vendas...")

    def abrir_graficos(self):
        print("Abrindo Gráficos...")

    def abrir_ajuda(self):
        print("Abrindo Ajuda...")
