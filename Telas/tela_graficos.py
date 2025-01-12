import tkinter as tk
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import sqlite3
import pandas as pd
import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraficoFrame(tk.Frame):
    def __init__(self, master=None, voltar_callback=None):
        super().__init__(master)
        self.master = master
        self.voltar_callback = voltar_callback
        self.configure(bg="white")
        self.criar_widgets()

    @staticmethod
    def obter_dados_vendas(nome_banco="dados.db"):
        """Extrai os dados de vendas e serviços do banco de dados."""
        conexao = sqlite3.connect(nome_banco)
        query = """
        SELECT s.nome AS servico, 
               COUNT(v.id) AS total_vendas, 
               SUM(v.valor) AS total_receita,
               SUM(v.valor_trabalho) AS total_trabalho,
               SUM(v.valor_material) AS total_material,
               SUM(v.valor_adicional) AS total_adicional,
               SUM(v.valor - v.desconto) AS receita_liquida,
               v.data_cadastro,
               v.parcelas
        FROM vendas v
        JOIN servicos s ON v.id_servico = s.id
        WHERE v.status = 1
        GROUP BY s.nome, v.data_cadastro
        """
        df = pd.read_sql_query(query, conexao)
        conexao.close()

        # Garantir que 'data_cadastro' seja do tipo datetime
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce')
        return df

    def exportar_relatorio(self):
        try:
            # Ocultar a janela principal do Tkinter
            Tk().withdraw()

            # Abrir janela para o usuário escolher o local para salvar o arquivo
            caminho_arquivo = asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
                title="Salvar Relatório"
            )

            # Verificar se o usuário escolheu um local ou cancelou a operação
            if not caminho_arquivo:
                print("Exportação cancelada pelo usuário.")
                return

            # Obter os dados das vendas
            df = self.obter_dados_vendas()

            # Garantir que a coluna 'data_cadastro' seja datetime
            df['data_cadastro'] = pd.to_datetime(df['data_cadastro'], errors='coerce')

            # Configurar o índice para a coluna 'data_cadastro'
            df.set_index('data_cadastro', inplace=True)

            # Dados adicionais para exportar
            servicos_vendidos = df.groupby('servico')['total_vendas'].sum().sort_values(ascending=False)
            lucro_acumulado = df.groupby(pd.Grouper(freq='M'))['receita_liquida'].sum().cumsum()
            mao_de_obra = df.groupby('servico')['total_trabalho'].sum().sort_values(ascending=False)
            custo_adicional = df.groupby('servico')['total_adicional'].sum()
            custo_material = df.groupby('servico')['total_material'].sum()

            # Criar o arquivo Excel no local escolhido pelo usuário
            with pd.ExcelWriter(caminho_arquivo, engine="xlsxwriter") as writer:
                # Planilha com os dados gerais das vendas
                df.reset_index().to_excel(writer, sheet_name="Dados Gerais", index=False)

                # Planilha com os serviços mais vendidos
                servicos_vendidos.to_frame(name="Quantidade de Vendas").to_excel(writer, sheet_name="Serviços Vendidos")

                # Planilha com a projeção de lucros acumulados
                lucro_acumulado.to_frame(name="Lucro Acumulado").to_excel(writer, sheet_name="Lucro Acumulado")

                # Planilha com serviços e mão de obra
                mao_de_obra.to_frame(name="Custo de Mão de Obra").to_excel(writer, sheet_name="Mão de Obra")

                # Planilha com custos adicionais e de material
                custo_combined = pd.DataFrame({
                    "Custo Adicional": custo_adicional,
                    "Custo Material": custo_material
                })
                custo_combined.to_excel(writer, sheet_name="Custos")

            # Mensagem de sucesso
            print(f"Relatório exportado com sucesso para: {caminho_arquivo}")

        except Exception as e:
            print(f"Ocorreu um erro ao exportar o relatório: {e}")

    # Criar função para construir caixas
    def criar_caixa(self, frame, texto, valor, cor):
        caixa = ctk.CTkFrame(frame, width=300, height=150, corner_radius=15, fg_color=cor)
        caixa.grid_propagate(False)

        # Adicionando padding interno
        lbl_texto = tk.Label(caixa, text=texto, font=("Arial", 14, "bold"), bg=cor, fg="white")
        lbl_texto.pack(side=tk.TOP, pady=10, padx=20)  # Mais padding lateral (padx)

        lbl_valor = tk.Label(caixa, text=f"R${valor:.2f}", font=("Arial", 20, "bold"), bg=cor, fg="white")
        lbl_valor.pack(expand=True, padx=20, pady=10)  # Padding para o valor também

        return caixa

    def criar_widgets(self):
        df = self.obter_dados_vendas()  # Obtém os dados processados

        # Cálculo dos totais
        total_lucro = df['receita_liquida'].sum()
        total_material = df['total_material'].sum()
        mes_atual = pd.Timestamp.now().month
        total_vendas_mes = df[df['data_cadastro'].dt.month == mes_atual]['total_receita'].sum()

        # Frame para os totais
        frame_totais = tk.Frame(self, bg="white")
        frame_totais.pack(pady=20)

        # Adicionando as caixas ao frame
        self.criar_caixa(frame_totais, "Total de Lucro", total_lucro, "#4CAF50").grid(row=0, column=0, padx=15, pady=15)
        self.criar_caixa(frame_totais, "Gasto com Material", total_material, "#FF9800").grid(row=0, column=1, padx=15,
                                                                                             pady=15)
        self.criar_caixa(frame_totais, "Vendas no Mês", total_vendas_mes, "#2196F3").grid(row=0, column=2, padx=15,
                                                                                          pady=15)

        # Ajustando o grid para as caixas ficarem responsivas
        frame_totais.grid_columnconfigure(0, weight=1)
        frame_totais.grid_columnconfigure(1, weight=1)
        frame_totais.grid_columnconfigure(2, weight=1)

        # Criar frame para os gráficos
        canvas_frame = tk.Frame(self, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Dividir o frame em duas linhas dentro do canvas_frame
        frame_topo = tk.Frame(canvas_frame, bg="white")
        frame_topo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        frame_base = tk.Frame(canvas_frame, bg="white")
        frame_base.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Primeiro Gráfico: Serviços Mais Vendidos
        fig1, ax1 = plt.subplots(figsize=(5, 3))  # Tamanho maior para as legendas
        fig1.patch.set_facecolor('white')
        servicos_vendidos = df.groupby('servico')['total_vendas'].sum().sort_values(ascending=False)
        servicos_vendidos.plot(kind='bar', ax=ax1, title='Serviços Mais Vendidos', ylabel='Quantidade de Vendas')
        ax1.set_xlabel('Serviços')
        plt.xticks(rotation=45, ha='right')  # Ajusta os rótulos do eixo X
        fig1.tight_layout()  # Garante que o conteúdo caiba

        # Segundo Gráfico: Projeção de Lucros Acumulados
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor('white')
        df['lucro_estimado'] = df['receita_liquida'] - (
                df['total_trabalho'] + df['total_material'] + df['total_adicional']
        )
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])
        df.set_index('data_cadastro', inplace=True)
        lucro_acumulado = df.groupby(pd.Grouper(freq='M'))['lucro_estimado'].sum().cumsum()
        lucro_acumulado.plot(ax=ax2, title='Projeção de Lucro Acumulado', ylabel='Lucro Acumulado', xlabel='Data')
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')
        fig2.tight_layout()

        # Terceiro Gráfico: Serviços com Mais Mão de Obra (Pizza)
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        fig3.patch.set_facecolor('white')
        mao_de_obra = df.groupby('servico')['total_trabalho'].sum().sort_values(ascending=False)
        mao_de_obra.plot(kind='pie', ax=ax3, title='Serviços com Mais Mão de Obra', autopct='%1.1f%%')
        ax3.set_ylabel('')
        ax3.legend(loc='upper right', bbox_to_anchor=(1.2, 1))  # Move a legenda para fora do gráfico
        fig3.tight_layout()

        # Quarto Gráfico: Custo Adicional e Material (Barras Horizontais)
        fig4, ax4 = plt.subplots(figsize=(5, 3))
        fig4.patch.set_facecolor('white')
        custo_adicional = df.groupby('servico')['total_adicional'].sum()
        custo_material = df.groupby('servico')['total_material'].sum()
        custo_combined = pd.DataFrame({'Adicional': custo_adicional, 'Material': custo_material})
        custo_combined.plot(kind='barh', ax=ax4, title='Custo Adicional e de Material', stacked=True)
        ax4.set_xlabel('Custo Total')
        fig4.tight_layout()

        # Adicionar os gráficos ao frame_base
        canvas1 = FigureCanvasTkAgg(fig1, frame_topo)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        canvas2 = FigureCanvasTkAgg(fig2, frame_topo)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        canvas3 = FigureCanvasTkAgg(fig3, frame_base)
        canvas3.draw()
        canvas3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        canvas4 = FigureCanvasTkAgg(fig4, frame_base)
        canvas4.draw()
        canvas4.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para os botões
        frame_botoes = tk.Frame(self, bg="white")
        frame_botoes.pack(side=tk.BOTTOM, pady=20, anchor='e')

        # Botão de Exportar Relatório
        btn_exportar = ctk.CTkButton(
            frame_botoes,
            text="Exportar Relatório",
            width=150,
            height=40,
            font=("Verdana", 16),
            fg_color="green",
            command=self.exportar_relatorio,
        )
        btn_exportar.pack(side=tk.LEFT, padx=10)

        # Botão de Voltar
        btn_voltar = ctk.CTkButton(
            frame_botoes,
            text="Voltar",
            width=150,
            height=40,
            font=("Verdana", 16),
            fg_color="gray",
            command=self.voltar_callback,
        )
        btn_voltar.pack(side=tk.LEFT, padx=10)

