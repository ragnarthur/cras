import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criação da tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    telefone TEXT NOT NULL,
    filhos TEXT,
    conjuge TEXT,
    bolsa_familia TEXT NOT NULL,
    data_cesta DATE
)
''')

# Criação da tabela de filhos
cursor.execute('''
CREATE TABLE IF NOT EXISTS filhos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER NOT NULL,
    usuario_id INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

# Criação da tabela de cônjuge
cursor.execute('''
CREATE TABLE IF NOT EXISTS conjuge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    usuario_id INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

conn.commit()
conn.close()

print("Banco de dados inicializado com sucesso!")
