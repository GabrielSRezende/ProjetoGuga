import sqlite3

def inicializar_banco(nome_banco="dados.db"):
    """Inicializa o banco SQLite e cria as tabelas necessárias."""
    conexao = sqlite3.connect(nome_banco)
    cursor = conexao.cursor()

    # Criar tabela de produtos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1
        )
    """)

    conexao.commit()
    conexao.close()
