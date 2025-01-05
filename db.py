import sqlite3

def inicializar_banco(nome_banco="dados.db"):
    """Inicializa o banco SQLite e cria as tabelas necessárias."""
    conexao = sqlite3.connect(nome_banco)
    cursor = conexao.cursor()

    # Criar tabela de servicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_servico INTEGER NOT NULL,
            valor REAL NOT NULL,
            desconto REAL DEFAULT 0,
            valor_trabalho REAL DEFAULT 0,
            valor_material REAL DEFAULT 0,
            valor_adicional REAL DEFAULT 0,
            possui_nota BOOLEAN DEFAULT 0,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1,
            observacao TEXT,
            FOREIGN KEY (id_servico) REFERENCES servicos(id)
        )
    """)

    conexao.commit()
    conexao.close()
