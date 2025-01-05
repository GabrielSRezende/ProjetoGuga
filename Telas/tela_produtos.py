import customtkinter as ctk
from tkinter import messagebox, Toplevel
import sqlite3


class ProdutoFrame(ctk.CTkFrame):
    def __init__(self, master, voltar_callback):
        super().__init__(master)
        self.configure(fg_color="white")
        self.voltar_callback = voltar_callback

        # Variáveis para controle de página
        self.current_page = 0
        self.page_size = 5

        self.is_form_visible = False
        self.editing_product = None

        self.grid_rowconfigure(0, weight=0)  # Linha do título
        self.grid_rowconfigure(1, weight=0)  # Linha do botão "Adicionar Produto"
        self.grid_rowconfigure(2, weight=0)  # Linha da lista de produtos
        self.grid_rowconfigure(3, weight=0)  # Linha da navegação de página
        self.grid_rowconfigure(4, weight=1)  # Linha vazia para ocupar o restante do espaço
        self.grid_rowconfigure(5, weight=0)  # Linha do botão "Voltar"

        self.grid_columnconfigure(0, weight=1)  # Garantir que a coluna ocupe toda a largura

        self.criar_tela_produto()

    def criar_tela_produto(self):
        title_label = ctk.CTkLabel(
            self,
            text="Gerenciamento de Produtos",
            font=("Verdana", 36, "bold"),
            text_color="#fcb333",
        )
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

        btn_adicionar = ctk.CTkButton(
            self,
            text="Adicionar Produto",
            width=200,
            height=40,
            font=("Verdana", 14),
            fg_color="#4CAF50",
            command=self.toggle_form,
        )
        btn_adicionar.grid(row=1, column=0, pady=(50, 5), sticky="n")

        # Agora a lista ficará mais acima
        self.lista_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.lista_frame.grid(row=2, column=0, padx=10, pady=(5, 5),
                              sticky="nsew")  # A tabela começa logo abaixo do botão
        self.lista_frame.grid_rowconfigure(0, weight=1)

        # Ajustando os pesos das colunas para melhor proporção
        self.lista_frame.grid_columnconfigure(0, weight=1)  # ID
        self.lista_frame.grid_columnconfigure(1, weight=3)  # Nome
        self.lista_frame.grid_columnconfigure(2, weight=3)  # Descrição
        self.lista_frame.grid_columnconfigure(3, weight=2)  # Data Cadastro
        self.lista_frame.grid_columnconfigure(4, weight=2)  # Ações

        # Configurando a parte de navegação de página
        self.pagination_frame = ctk.CTkFrame(self, fg_color="white")
        self.pagination_frame.grid(row=3, column=0, pady=10)

        btn_prev = ctk.CTkButton(
            self.pagination_frame,
            text="Página Anterior",
            command=self.prev_page,
            width=150,
            height=40,
            font=("Verdana", 12),
            fg_color="#4CAF50"
        )
        btn_prev.pack(side="left", padx=10)

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Página 1",
            font=("Verdana", 12)
        )
        self.page_label.pack(side="left", padx=10)

        btn_next = ctk.CTkButton(
            self.pagination_frame,
            text="Próxima Página",
            command=self.next_page,
            width=150,
            height=40,
            font=("Verdana", 12),
            fg_color="#4CAF50"
        )
        btn_next.pack(side="left", padx=10)

        btn_voltar = ctk.CTkButton(
            self,
            text="Voltar",
            width=150,
            height=40,
            font=("Verdana", 16),
            fg_color="gray",
            command=self.voltar_callback,
        )
        btn_voltar.grid(row=5, column=0, pady=30, sticky="se", padx=20)

        # Criar o formulário de produto (inicialmente invisível)
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)

        # Ajustar o formulário para centralizar
        self.form_frame.grid_rowconfigure(0, weight=1)
        self.form_frame.grid_rowconfigure(1, weight=1)
        self.form_frame.grid_rowconfigure(2, weight=1)
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=3)

        # Configuração do grid do form_frame para centralizar
        self.form_frame.grid_columnconfigure(0, weight=1)  # Ajusta a coluna 0 para ter peso
        self.form_frame.grid_columnconfigure(1, weight=1)  # Ajusta a coluna 1 para ter peso
        self.form_frame.grid_rowconfigure(0, weight=1)  # Ajusta a linha 0 para ter peso
        self.form_frame.grid_rowconfigure(1, weight=1)  # Ajusta a linha 1 para ter peso
        self.form_frame.grid_rowconfigure(2, weight=1)  # Ajusta a linha 2 para ter peso

        # Label para o nome
        self.entry_nome_label = ctk.CTkLabel(self.form_frame, text="Nome", font=("Verdana", 14), text_color="black")
        self.entry_nome_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input de nome com a mesma largura do Textbox
        self.entry_nome = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_nome.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para a descrição
        self.entry_descricao_label = ctk.CTkLabel(self.form_frame, text="Descrição", font=("Verdana", 14),
                                                  text_color="black")
        self.entry_descricao_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")

        # Campo de texto maior para a descrição
        self.entry_descricao = ctk.CTkTextbox(self.form_frame, width=400, height=100, font=("Verdana", 14))
        self.entry_descricao.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="w")

        # Botão de salvar
        btn_salvar = ctk.CTkButton(self.form_frame, text="Salvar", width=150, height=40, font=("Verdana", 14),
                                   fg_color="#4CAF50", command=self.salvar_produto)
        btn_salvar.grid(row=2, column=0, pady=10, padx=5, columnspan=2)

        # Botão de cancelar
        btn_cancelar = ctk.CTkButton(self.form_frame, text="Cancelar", width=150, height=40, font=("Verdana", 14),
                                     fg_color="#FF6347", command=self.cancelar_formulario)
        btn_cancelar.grid(row=3, column=0, pady=10, padx=5, columnspan=2)

        # Agora, o formulário começa invisível, e será mostrado somente quando necessário
        self.form_frame.grid_remove()  # O formulário começa invisível

        self.carregar_produtos()

    def cancelar_formulario(self):
        """Função para cancelar e fechar o formulário"""
        self.form_frame.grid_remove()  # Esconde o formulário
        self.is_form_visible = False
        self.editing_product = None
        self.limpar_campos()

    def limpar_campos(self):
        """Função para limpar os campos de entrada"""
        self.entry_nome.delete(0, ctk.END)
        self.entry_descricao.delete(0, ctk.END)

    def carregar_produtos(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, descricao, data_cadastro FROM produtos WHERE status = 1")
        produtos = cursor.fetchall()
        conexao.close()

        headers = ["ID", "Nome", "Descrição", "Data Cadastro", "Ações"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.lista_frame, fg_color="#4CAF50", corner_radius=5)
            header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            lbl = ctk.CTkLabel(header_frame, text=header, font=("Verdana", 12, "bold"), text_color="white")
            lbl.pack(padx=5, pady=5)

        self.produtos = produtos
        self.update_table()

    def update_table(self):
        for widget in self.lista_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.grid_info()['row'] != 0:
                widget.destroy()

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.produtos[start_idx:end_idx]

        for i, produto in enumerate(page_data, start=1):
            for col, valor in enumerate(produto):
                cell_frame = ctk.CTkFrame(self.lista_frame, fg_color="white", corner_radius=5, border_width=1,
                                          border_color="gray")
                cell_frame.grid(row=i, column=col, padx=5, pady=5, sticky="nsew")
                lbl = ctk.CTkLabel(cell_frame, text=valor, font=("Verdana", 10), text_color="black")
                lbl.pack(padx=5, pady=5)

            action_frame = ctk.CTkFrame(self.lista_frame, fg_color="white", corner_radius=5, border_width=1,
                                        border_color="gray")
            action_frame.grid(row=i, column=len(produto), padx=5, pady=5, sticky="nsew")

            # Frame interno para centralizar os botões
            buttons_frame = ctk.CTkFrame(action_frame, fg_color="white")
            buttons_frame.pack(anchor="center", pady=5)

            btn_editar = ctk.CTkButton(
                buttons_frame,
                text="Editar",
                width=80,
                command=lambda p=produto: self.toggle_form(p),
            )
            btn_editar.pack(side="left", padx=2)

            btn_inativar = ctk.CTkButton(
                buttons_frame,
                text="Inativar",
                width=80,
                fg_color="red",
                command=lambda p=produto: self.inativar_produto(p[0]),
            )
            btn_inativar.pack(side="left", padx=2)

        self.page_label.configure(text=f"Página {self.current_page + 1}")

    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.produtos):
            self.current_page += 1
            self.update_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def inativar_produto(self, produto_id):
        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()
        cursor.execute("UPDATE produtos SET status = 0 WHERE id = ?", (produto_id,))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Produto inativado com sucesso!")
        self.carregar_produtos()

    def toggle_form(self, produto=None):
        if self.is_form_visible:
            self.form_frame.grid_remove()  # Esconde o formulário
            self.is_form_visible = False
            self.editing_product = None
        else:
            self.form_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")  # Exibe o formulário
            self.is_form_visible = True
            if produto:
                self.editing_product = produto
                self.entry_nome.delete(0, ctk.END)
                self.entry_descricao.delete("1.0", ctk.END)  # Corrigido aqui
                self.entry_nome.insert(0, produto[1])
                self.entry_descricao.insert("1.0", produto[2])

    def salvar_produto(self):
        nome = self.entry_nome.get()
        descricao = self.entry_descricao.get("1.0", "end-1c")  # Pega o conteúdo do campo de texto

        if nome == "" or descricao == "":
            messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
            return

        if self.editing_product:
            conexao = sqlite3.connect("dados.db")
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE produtos SET nome = ?, descricao = ? WHERE id = ?",
                (nome, descricao, self.editing_product[0]),
            )
            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            self.toggle_form()  # Fecha o formulário após salvar
        else:
            conexao = sqlite3.connect("dados.db")
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO produtos (nome, descricao, status) VALUES (?, ?, 1)",
                (nome, descricao),
            )
            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            self.toggle_form()  # Fecha o formulário após salvar

        self.carregar_produtos()
