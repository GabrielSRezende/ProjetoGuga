import tkinter as tk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GraficoFrame(tk.Frame):
    def __init__(self, master=None, voltar_callback=None):
        super().__init__(master)
        self.master = master
        self.voltar_callback = voltar_callback
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

    def criar_widgets(self):
        df = self.obter_dados_vendas()  # Obtém os dados processados

        # Cálculo dos totais
        total_lucro = df['receita_liquida'].sum()
        total_material = df['total_material'].sum()

        # Filtrando para o mês atual
        mes_atual = pd.Timestamp.now().month
        total_vendas_mes = df[df['data_cadastro'].dt.month == mes_atual]['total_receita'].sum()

        # Labels de Resumo
        lbl_total_lucro = tk.Label(self, text=f"Total de Lucro: R${total_lucro:.2f}", font=("Arial", 12, "bold"))
        lbl_total_lucro.pack()

        lbl_total_material = tk.Label(self, text=f"Total Gasto com Material: R${total_material:.2f}",
                                      font=("Arial", 12, "bold"))
        lbl_total_material.pack()

        lbl_total_vendas_mes = tk.Label(self, text=f"Total de Vendas no Mês: R${total_vendas_mes:.2f}",
                                        font=("Arial", 12, "bold"))
        lbl_total_vendas_mes.pack()

        # Criar frame para os gráficos
        frame_graficos = tk.Frame(self)
        frame_graficos.pack(pady=10)

        # Dividir o frame em duas linhas
        frame_topo = tk.Frame(frame_graficos)
        frame_topo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        frame_base = tk.Frame(frame_graficos)
        frame_base.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Primeiro Gráfico: Serviços Mais Vendidos
        fig1, ax1 = plt.subplots()
        servicos_vendidos = df.groupby('servico')['total_vendas'].sum().sort_values(ascending=False)
        servicos_vendidos.plot(kind='bar', ax=ax1, title='Serviços Mais Vendidos', ylabel='Quantidade de Vendas')

        canvas1 = FigureCanvasTkAgg(fig1, frame_topo)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Segundo Gráfico: Projeção de Lucros Acumulados
        fig2, ax2 = plt.subplots()
        df['lucro_estimado'] = df['receita_liquida'] - (
                df['total_trabalho'] + df['total_material'] + df['total_adicional']
        )
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])
        df.set_index('data_cadastro', inplace=True)
        lucro_acumulado = df.groupby(pd.Grouper(freq='M'))['lucro_estimado'].sum().cumsum()
        lucro_acumulado.plot(ax=ax2, title='Projeção de Lucro Acumulado', ylabel='Lucro Acumulado', xlabel='Data')
        ax2.xaxis.set_major_locator(mdates.MonthLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)

        canvas2 = FigureCanvasTkAgg(fig2, frame_topo)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Terceiro Gráfico: Serviços com Mais Mão de Obra (Pizza)
        fig3, ax3 = plt.subplots()
        mao_de_obra = df.groupby('servico')['total_trabalho'].sum().sort_values(ascending=False)
        mao_de_obra.plot(kind='pie', ax=ax3, title='Serviços com Mais Mão de Obra', autopct='%1.1f%%')
        ax3.set_ylabel('')

        canvas3 = FigureCanvasTkAgg(fig3, frame_base)
        canvas3.draw()
        canvas3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Quarto Gráfico: Custo Adicional e Material (Barras Horizontais)
        fig4, ax4 = plt.subplots()
        custo_adicional = df.groupby('servico')['total_adicional'].sum()
        custo_material = df.groupby('servico')['total_material'].sum()
        custo_combined = pd.DataFrame({'Adicional': custo_adicional, 'Material': custo_material})
        custo_combined.plot(kind='barh', ax=ax4, title='Custo Adicional e de Material', stacked=True)
        ax4.set_xlabel('Custo Total')

        canvas4 = FigureCanvasTkAgg(fig4, frame_base)
        canvas4.draw()
        canvas4.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Botão de voltar para o menu
        btn_voltar = tk.Button(self, text="Voltar", command=self.voltar)
        btn_voltar.pack(pady=5)

    def voltar(self):
        if self.voltar_callback:
            self.voltar_callback()
