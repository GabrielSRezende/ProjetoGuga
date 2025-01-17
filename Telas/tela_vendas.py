import customtkinter as ctk
from tkinter import messagebox, Toplevel
import sqlite3
from Util.formatacao import formatar_para_moeda, remover_formatacao_monetaria

class VendaFrame(ctk.CTkFrame):
    def __init__(self, master, voltar_callback):
        self.servicos_dict = {}
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
        self.grid_rowconfigure(2, weight=0)  # Linha da lista de vendas
        self.grid_rowconfigure(3, weight=0)  # Linha da navegação de página
        self.grid_rowconfigure(4, weight=1)  # Linha vazia para ocupar o restante do espaço
        self.grid_rowconfigure(5, weight=0)  # Linha do botão "Voltar"

        self.grid_columnconfigure(0, weight=1)  # Garantir que a coluna ocupe toda a largura

        self.criar_tela_produto()

    def criar_tela_produto(self):
        title_label = ctk.CTkLabel(
            self,
            text="Gerenciamento de Vendas",
            font=("Verdana", 36, "bold"),
            text_color="#fcb333",
        )
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="n")

        btn_adicionar = ctk.CTkButton(
            self,
            text="Adicionar Venda",
            width=200,
            height=40,
            font=("Verdana", 14),
            fg_color="#03c6fc",
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
        self.lista_frame.grid_columnconfigure(1, weight=2)  # Serviço
        self.lista_frame.grid_columnconfigure(2, weight=2)  # Valor
        self.lista_frame.grid_columnconfigure(3, weight=2)  # Desconto
        self.lista_frame.grid_columnconfigure(4, weight=2)  # Valor Trabalho
        self.lista_frame.grid_columnconfigure(5, weight=2)  # Valor Material
        self.lista_frame.grid_columnconfigure(6, weight=2)  # Valor Adicional
        self.lista_frame.grid_columnconfigure(6, weight=1)  # Parcelas
        self.lista_frame.grid_columnconfigure(7, weight=1)  # Possui Nota
        self.lista_frame.grid_columnconfigure(8, weight=1)  # Data Cadastro
        self.lista_frame.grid_columnconfigure(9, weight=3)  # Observação
        self.lista_frame.grid_columnconfigure(10, weight=2)  # Ações

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
            fg_color="#03c6fc"
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
            fg_color="#03c6fc"
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

        # Label para o serviço
        self.entry_servico_label = ctk.CTkLabel(self.form_frame, text="Serviço", font=("Verdana", 14),
                                                text_color="black")
        self.entry_servico_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")

        # Obter a lista de serviços da tabela servicos
        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM servicos WHERE status = 1")
        servicos = cursor.fetchall()

        # Lista de serviços para o ComboBox (apenas os nomes)
        servicos_lista = [servico[1] for servico in servicos]  # Lista com os nomes dos serviços

        # Dicionário para mapear o nome do serviço ao seu ID
        self.servicos_dict = {servico[1]: servico[0] for servico in servicos}  # {nome: id}

        # ComboBox para selecionar o serviço
        self.entry_servico = ctk.CTkOptionMenu(self.form_frame, values=servicos_lista, font=("Verdana", 14), width=400)
        self.entry_servico.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o valor
        self.entry_valor_label = ctk.CTkLabel(self.form_frame, text="Valor", font=("Verdana", 14), text_color="black")
        self.entry_valor_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o valor com máscara
        self.entry_valor = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_valor.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o desconto
        self.entry_desconto_label = ctk.CTkLabel(self.form_frame, text="Desconto", font=("Verdana", 14),
                                                 text_color="black")
        self.entry_desconto_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o desconto
        self.entry_desconto = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_desconto.grid(row=2, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o valor do trabalho
        self.entry_valor_trabalho_label = ctk.CTkLabel(self.form_frame, text="Valor do Trabalho", font=("Verdana", 14),
                                                       text_color="black")
        self.entry_valor_trabalho_label.grid(row=3, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o valor do trabalho
        self.entry_valor_trabalho = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_valor_trabalho.grid(row=3, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o valor do material
        self.entry_valor_material_label = ctk.CTkLabel(self.form_frame, text="Valor do Material", font=("Verdana", 14),
                                                       text_color="black")
        self.entry_valor_material_label.grid(row=4, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o valor do material
        self.entry_valor_material = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_valor_material.grid(row=4, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o valor adicional
        self.entry_valor_adicional_label = ctk.CTkLabel(self.form_frame, text="Valor Adicional", font=("Verdana", 14),
                                                        text_color="black")
        self.entry_valor_adicional_label.grid(row=5, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o valor adicional
        self.entry_valor_adicional = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_valor_adicional.grid(row=5, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o parcelas
        self.entry_parcelas_label = ctk.CTkLabel(self.form_frame, text="Quantidade de Parcelas", font=("Verdana", 14),
                                                       text_color="black")
        self.entry_parcelas_label.grid(row=6, column=0, padx=(10, 5), pady=10, sticky="e")

        # Input para o parcelas
        self.entry_parcelas = ctk.CTkEntry(self.form_frame, font=("Verdana", 14), width=400)
        self.entry_parcelas.grid(row=6, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para o campo "Possui Nota"
        self.entry_possui_nota_label = ctk.CTkLabel(self.form_frame, text="Possui Nota", font=("Verdana", 14),
                                                    text_color="black")
        self.entry_possui_nota_label.grid(row=7, column=0, padx=(10, 5), pady=10, sticky="e")

        # Campo para "Possui Nota" (checkbox)
        self.entry_possui_nota = ctk.CTkCheckBox(self.form_frame, font=("Verdana", 14))
        self.entry_possui_nota.grid(row=7, column=1, padx=(5, 10), pady=10, sticky="w")

        # Label para a observação
        self.entry_observacao_label = ctk.CTkLabel(self.form_frame, text="Observação", font=("Verdana", 14),
                                                   text_color="black")
        self.entry_observacao_label.grid(row=8, column=0, padx=(10, 5), pady=10, sticky="e")

        # Campo de texto maior para a observação
        self.entry_observacao = ctk.CTkTextbox(self.form_frame, width=400, height=100, font=("Verdana", 14))
        self.entry_observacao.grid(row=8, column=1, padx=(5, 10), pady=10, sticky="w")

        # Vincular evento para formatar como moeda
        self.entry_valor.bind("<KeyRelease>", formatar_para_moeda)
        self.entry_valor_trabalho.bind("<KeyRelease>", formatar_para_moeda)
        self.entry_valor_material.bind("<KeyRelease>", formatar_para_moeda)
        self.entry_valor_adicional.bind("<KeyRelease>", formatar_para_moeda)

        # Botão de salvar
        btn_salvar = ctk.CTkButton(self.form_frame, text="Salvar", width=150, height=40, font=("Verdana", 14),
                                   fg_color="#03c6fc", command=self.salvar_venda)
        btn_salvar.grid(row=9, column=0, pady=10, padx=5, columnspan=2)

        # Botão de cancelar
        btn_cancelar = ctk.CTkButton(self.form_frame, text="Cancelar", width=150, height=40, font=("Verdana", 14),
                                     fg_color="#FF6347", command=self.cancelar_formulario)
        btn_cancelar.grid(row=10, column=0, pady=10, padx=5, columnspan=2)

        # Agora, o formulário começa invisível, e será mostrado somente quando necessário
        self.form_frame.grid_remove()  # O formulário começa invisível

        self.carregar_vendas()

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

    def carregar_vendas(self):
        # Limpar os widgets existentes
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        # Conexão com o banco de dados
        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()

        # Atualizar a consulta SQL para incluir todos os campos relevantes
        cursor.execute("""
                    SELECT v.id, s.nome, v.valor, v.desconto, v.valor_trabalho, v.valor_material, 
                           v.valor_adicional, v.parcelas, v.possui_nota, v.data_cadastro, v.observacao
                    FROM vendas v
                    INNER JOIN servicos s ON v.id_servico = s.id
                    WHERE v.status = 1
                """)
        vendas = cursor.fetchall()
        conexao.close()

        # Cabeçalhos da tabela
        headers = ["ID", "Serviço", "Valor", "Desconto", "Valor Trabalho", "Valor Material",
                   "Valor Adicional", "Parcelas", "Possui Nota", "Data Cadastro", "Observação", "Ações"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.lista_frame, fg_color="#03c6fc", corner_radius=5)
            header_frame.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            lbl = ctk.CTkLabel(header_frame, text=header, font=("Verdana", 12, "bold"), text_color="white")
            lbl.pack(padx=5, pady=5)

        # Atualizar a referência de vendas para uso posterior
        self.vendas = vendas
        self.update_table()

    def update_table(self):
        # Limpar widgets existentes (exceto o cabeçalho)
        for widget in self.lista_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.grid_info()['row'] != 0:
                widget.destroy()

        # Paginação
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.vendas[start_idx:end_idx]

        for i, produto in enumerate(page_data, start=1):
            id_venda, id_servico, valor, desconto, valor_trabalho, valor_material, valor_adicional, parcelas, possui_nota, data_cadastro, observacao = produto

            # Aplicar formatações
            valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            desconto_formatado = f"R$ {desconto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valor_trabalho_formatado = f"R$ {valor_trabalho:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valor_material_formatado = f"R$ {valor_material:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valor_adicional_formatado = f"R$ {valor_adicional:,.2f}".replace(",", "X").replace(".", ",").replace("X",
                                                                                                                 ".")
            possui_nota_formatado = "Sim" if possui_nota == 1 else "Não"
            data_formatada = "/".join(reversed(data_cadastro.split(" ")[0].split("-")))

            # Montar valores formatados para exibição
            valores = [
                id_venda, id_servico, valor_formatado, desconto_formatado, valor_trabalho_formatado,
                valor_material_formatado, valor_adicional_formatado, parcelas, possui_nota_formatado,
                data_formatada, observacao
            ]

            # Exibir dados na tabela
            for col, valor in enumerate(valores):
                cell_frame = ctk.CTkFrame(self.lista_frame, fg_color="white", corner_radius=5, border_width=1,
                                          border_color="gray")
                cell_frame.grid(row=i, column=col, padx=5, pady=5, sticky="nsew")
                lbl = ctk.CTkLabel(cell_frame, text=str(valor), font=("Verdana", 10), text_color="black")
                lbl.pack(padx=5, pady=5)

            # Adicionar botões de ação
            action_frame = ctk.CTkFrame(self.lista_frame, fg_color="white", corner_radius=5, border_width=1,
                                        border_color="gray")
            action_frame.grid(row=i, column=len(valores), padx=5, pady=5, sticky="nsew")

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

        # Atualizar o texto da página
        self.page_label.configure(text=f"Página {self.current_page + 1}")

    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.vendas):
            self.current_page += 1
            self.update_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def inativar_produto(self, produto_id):
        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()
        cursor.execute("UPDATE vendas SET status = 0 WHERE id = ?", (produto_id,))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Produto inativado com sucesso!")
        self.carregar_vendas()

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

                # Acessa os elementos da tupla por índice
                self.entry_servico.set(produto[1])  # Índice 1: servico_nome
                self.entry_valor.delete(0, ctk.END)
                self.entry_valor.insert(0, produto[2])  # Índice 2: valor

                self.entry_desconto.delete(0, ctk.END)
                self.entry_desconto.insert(0, produto[3])  # Índice 3: desconto

                self.entry_valor_trabalho.delete(0, ctk.END)
                self.entry_valor_trabalho.insert(0, produto[4])  # Índice 4: valor_trabalho

                self.entry_valor_material.delete(0, ctk.END)
                self.entry_valor_material.insert(0, produto[5])  # Índice 5: valor_material

                self.entry_valor_adicional.delete(0, ctk.END)
                self.entry_valor_adicional.insert(0, produto[6])  # Índice 6: valor_adicional

                self.entry_parcelas.delete(0, ctk.END)
                self.entry_parcelas.insert(0, produto[7])  # Índice 7: parcelas

                # Checkbox "Possui Nota"
                if produto[8]:  # Índice 8: possui_nota
                    self.entry_possui_nota.select()
                else:
                    self.entry_possui_nota.deselect()

                # Observação
                self.entry_observacao.delete("1.0", ctk.END)
                self.entry_observacao.insert("1.0", produto[10])  # Índice 9: observacao

    def salvar_venda(self):
        conexao = sqlite3.connect("dados.db")
        cursor = conexao.cursor()

        # Coletando os valores dos campos
        servico_nome = self.entry_servico.get()  # Nome do serviço selecionado

        # Verificando se o serviço foi selecionado
        if not servico_nome:
            messagebox.showerror("Erro", "Por favor, selecione um serviço.")
            return

        # Obter o ID do serviço selecionado usando o dicionário servicos_dict
        servico_id = self.servicos_dict.get(servico_nome)

        # Coletando outros valores e removendo a formatação monetária
        valor = remover_formatacao_monetaria(self.entry_valor.get())
        desconto = remover_formatacao_monetaria(self.entry_desconto.get())
        valor_trabalho = remover_formatacao_monetaria(self.entry_valor_trabalho.get())
        valor_material = remover_formatacao_monetaria(self.entry_valor_material.get())
        valor_adicional = remover_formatacao_monetaria(self.entry_valor_adicional.get())
        parcelas = self.entry_parcelas.get()
        possui_nota = self.entry_possui_nota.get()  # Esse campo é um checkbox
        observacao = self.entry_observacao.get("1.0", "end-1c")  # Pega o conteúdo do campo de texto

        # Verificando se algum campo obrigatório está vazio
        if not servico_id or valor == 0 or desconto == 0 or valor_trabalho == 0 or valor_material == 0 or valor_adicional == 0:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
            return

        # Validação adicional para campos numéricos
        try:
            valor = float(valor)
            desconto = float(desconto)
            valor_trabalho = float(valor_trabalho)
            valor_material = float(valor_material)
            valor_adicional = float(valor_adicional)
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para os campos de valor.")
            return

        # Salvando ou atualizando no banco de dados
        if self.editing_product:
            cursor.execute(
                """UPDATE vendas
                SET id_servico = ?, valor = ?, desconto = ?, valor_trabalho = ?, valor_material = ?, valor_adicional = ?, 
                    parcelas = ?, possui_nota = ?, observacao = ?
                WHERE id = ?""",
                (servico_id, valor, desconto, valor_trabalho, valor_material, valor_adicional, parcelas, possui_nota,
                 observacao,
                 self.editing_product[0])
            )
            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", "Venda atualizada com sucesso!")
        else:
            cursor.execute(
                """INSERT INTO vendas (id_servico, valor, desconto, valor_trabalho, valor_material, valor_adicional, 
                                        parcelas, possui_nota, observacao, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (servico_id, valor, desconto, valor_trabalho, valor_material, valor_adicional, parcelas, possui_nota,
                 observacao)
            )
            conexao.commit()
            conexao.close()

            messagebox.showinfo("Sucesso", "Venda adicionada com sucesso!")

        self.toggle_form()  # Fecha o formulário após salvar
        self.carregar_vendas()  # Carrega as vendas novamente



