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
    data_nascimento DATE,  -- Adicionado campo para data de nascimento
    data_cesta DATE
)
''')

# Criação da tabela de filhos
cursor.execute('''
CREATE TABLE IF NOT EXISTS filhos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    idade INTEGER NOT NULL,
    data_nascimento DATE,  -- Adicionado campo para data de nascimento
    usuario_id INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')

# Criação da tabela de cônjuge
cursor.execute('''
CREATE TABLE IF NOT EXISTS conjuge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE,  -- Adicionado campo para data de nascimento
    usuario_id INTEGER,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    telefone TEXT NOT NULL,
    filhos TEXT,
    conjuge TEXT,
    bolsa_familia TEXT NOT NULL,
    data_nascimento DATE,
    data_cesta DATE,
    observacoes_visita TEXT
)
''')


# Criação da tabela de secretárias
cursor.execute('''
CREATE TABLE IF NOT EXISTS secretarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL CHECK (is_admin IN (0, 1))
)
''')

# Inserção das secretárias com uma senha padrão e Maria Silva como administradora
cursor.execute('''
INSERT OR IGNORE INTO secretarias (nome, username, senha, is_admin) VALUES 
('Maria Silva', 'Maria', 'senha123', 1),
('Roseane Vieira', 'Roseane', 'senha123', 0),
('Aline Resende', 'Aline', 'senha123', 0),
('Meire Castro', 'Meire', 'senha123', 0)
''')

conn.commit()
conn.close()

print("Banco de dados inicializado com sucesso!")
