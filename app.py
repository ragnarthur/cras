from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo-super-seguro'

# Função para conectar ao banco de dados
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acessar as colunas pelo nome
    return conn

# Antes de cada requisição, abrir a conexão com o banco de dados
@app.before_request
def before_request():
    g.db = connect_db()

# Depois de cada requisição, fechar a conexão com o banco de dados
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Rota de login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']

        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM secretarias WHERE username = ? AND senha = ?", (username, senha))
        secretaria = cursor.fetchone()

        if secretaria:
            session['username'] = secretaria['username']
            session['is_admin'] = bool(secretaria['is_admin'])
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Usuário ou senha incorretos!")
    
    return render_template('index.html')

# Rota do dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', is_admin=session.get('is_admin'))

# Rota para cadastro de usuário
@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        filhos = request.form['filhos']
        conjuge = request.form['conjuge']
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']

        cursor = g.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta))
        usuario_id = cursor.lastrowid
        g.db.commit()

        if filhos == 'sim':
            return redirect(url_for('cadastro_filho', usuario_id=usuario_id))
        elif conjuge == 'sim':
            return redirect(url_for('cadastro_conjuge', usuario_id=usuario_id))
        else:
            return redirect(url_for('dashboard'))

    return render_template('cadastro_usuario.html')

# Rota para cadastro de filho
@app.route('/cadastro_filho/<int:usuario_id>', methods=['GET', 'POST'])
def cadastro_filho(usuario_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome_filho = request.form['nome_filho']
        idade_filho = request.form['idade_filho']
        cadastrar_outro = request.form.get('cadastrar_outro')

        cursor = g.db.cursor()
        cursor.execute("INSERT INTO filhos (nome, idade, usuario_id) VALUES (?, ?, ?)",
                       (nome_filho, idade_filho, usuario_id))
        g.db.commit()

        if cadastrar_outro == 'sim':
            return redirect(url_for('cadastro_filho', usuario_id=usuario_id))
        else:
            return redirect(url_for('dashboard'))

    return render_template('cadastro_filho.html', usuario_id=usuario_id)

# Rota para cadastro de cônjuge
@app.route('/cadastro_conjuge/<int:usuario_id>', methods=['GET', 'POST'])
def cadastro_conjuge(usuario_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome_conjuge = request.form['nome_conjuge']

        cursor = g.db.cursor()
        cursor.execute("INSERT INTO conjuge (nome, usuario_id) VALUES (?, ?)",
                       (nome_conjuge, usuario_id))
        g.db.commit()

        return redirect(url_for('dashboard'))

    return render_template('cadastro_conjuge.html', usuario_id=usuario_id)

# Rota para adicionar novas secretárias (apenas administradores)
@app.route('/admin/add_secretaria', methods=['GET', 'POST'])
def add_secretaria():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        senha = request.form['senha']
        is_admin = request.form.get('is_admin') == 'on'

        cursor = g.db.cursor()
        try:
            cursor.execute("INSERT INTO secretarias (nome, username, senha, is_admin) VALUES (?, ?, ?, ?)",
                           (nome, username, senha, int(is_admin)))
            g.db.commit()
        except sqlite3.IntegrityError:
            return render_template('add_secretaria.html', error="Nome de usuário já existe!")

        return redirect(url_for('dashboard'))

    return render_template('add_secretaria.html')

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Rota para pesquisar usuários
@app.route('/pesquisar_usuario', methods=['GET', 'POST'])
def pesquisar_usuario():
    if 'username' not in session:
        return redirect(url_for('index'))

    usuarios = []
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nome LIKE ? OR telefone LIKE ?", 
                       ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        usuarios = cursor.fetchall()

    return render_template('pesquisar_usuario.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
