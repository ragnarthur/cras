from flask import Flask, render_template, request, redirect, url_for, session, g
from datetime import datetime, timedelta
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

# Função para garantir que a coluna 'observacoes' seja adicionada
def alterar_tabela():
    with g.db:
        cursor = g.db.cursor()
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN observacoes TEXT")
            g.db.commit()
        except sqlite3.OperationalError:
            pass  # Ignorar se a coluna já existir

# Garantir que a tabela é alterada quando necessário
@app.before_request
def check_table():
    alterar_tabela()

# Depois de cada requisição, fechar a conexão com o banco de dados
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.template_filter('format_telefone')
def format_telefone(telefone):
    telefone = ''.join([num for num in telefone if num.isdigit()])
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        return telefone
    

@app.template_filter('format_data')
def format_data(data_str):
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except ValueError:
        return data_str

# Rota de login
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('password')

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
        data_nascimento = request.form['data_nascimento']
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        endereco = f"{rua}, {numero}, {bairro}, {cidade}"
        telefone = request.form['telefone']
        filhos = request.form.get('filhos', 'não')
        conjuge = request.form.get('conjuge', 'não')
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']

        cursor = g.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, data_nascimento, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, data_nascimento, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta)
        )
        usuario_id = cursor.lastrowid  # Pegamos o ID do usuário recém-criado
        g.db.commit()

        # Redirecionamento condicional
        if filhos == 'sim':
            return redirect(url_for('cadastro_filho', usuario_id=usuario_id))
        elif conjuge == 'sim':
            return redirect(url_for('cadastro_conjuge', usuario_id=usuario_id))
        else:
            return redirect(url_for('dashboard'))

    return render_template('cadastro_usuario.html')

@app.route('/cadastro_filho/<int:usuario_id>', methods=['GET', 'POST'])
def cadastro_filho(usuario_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    # Busca o status de "conjuge" do usuário
    cursor = g.db.cursor()
    cursor.execute("SELECT conjuge FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()

    if request.method == 'POST':
        nome_filho = request.form['nome_filho']
        idade_filho = request.form['idade_filho']
        data_nascimento_filho = request.form['data_nascimento_filho']
        cadastrar_outro = request.form.get('cadastrar_outro')

        cursor.execute("INSERT INTO filhos (nome, idade, data_nascimento, usuario_id) VALUES (?, ?, ?, ?)",
                       (nome_filho, idade_filho, data_nascimento_filho, usuario_id))
        g.db.commit()

        if cadastrar_outro == 'sim':
            # Redireciona para o cadastro de outro filho
            return redirect(url_for('cadastro_filho', usuario_id=usuario_id))
        elif usuario['conjuge'] == 'sim':
            # Se o cônjuge está marcado, redireciona para o cadastro de cônjuge
            return redirect(url_for('cadastro_conjuge', usuario_id=usuario_id))
        else:
            # Caso contrário, vai para o dashboard
            return redirect(url_for('dashboard'))

    return render_template('cadastro_filho.html', usuario_id=usuario_id)

@app.route('/cadastro_conjuge/<int:usuario_id>', methods=['GET', 'POST'])
def cadastro_conjuge(usuario_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome_conjuge = request.form['nome_conjuge']
        data_nascimento_conjuge = request.form['data_nascimento_conjuge']

        cursor = g.db.cursor()
        cursor.execute("INSERT INTO conjuge (nome, data_nascimento, usuario_id) VALUES (?, ?, ?)",
                       (nome_conjuge, data_nascimento_conjuge, usuario_id))
        g.db.commit()

        return redirect(url_for('dashboard'))

    return render_template('cadastro_conjuge.html', usuario_id=usuario_id)

@app.route('/editar_usuario/<nome_usuario>', methods=['GET', 'POST'])
def editar_usuario(nome_usuario):
    if 'username' not in session:
        return redirect(url_for('index'))

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        return redirect(url_for('pesquisar_usuario'))

    # Atualizar os dados do usuário se o formulário for enviado
    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        telefone = request.form['telefone']
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']
        observacoes = request.form['observacoes']

        # Calcular a próxima data de retirada (3 meses após a data_cesta)
        if data_cesta:
            data_proxima_retirada = datetime.strptime(data_cesta, '%Y-%m-%d') + timedelta(days=90)
        else:
            data_proxima_retirada = None

        cursor.execute("""
            UPDATE usuarios SET nome = ?, data_nascimento = ?, endereco = ?, telefone = ?, 
            bolsa_familia = ?, data_cesta = ?, observacoes = ? WHERE nome = ?
        """, (
            nome, data_nascimento, f"{rua}, {numero}, {bairro}, {cidade}", telefone,
            bolsa_familia, data_cesta, observacoes, nome_usuario
        ))
        g.db.commit()
        return redirect(url_for('pesquisar_usuario'))

    # Buscar os filhos e cônjuge do usuário para exibição na página de edição
    cursor.execute("SELECT * FROM filhos WHERE usuario_id = ?", (usuario['id'],))
    filhos = cursor.fetchall()

    cursor.execute("SELECT * FROM conjuge WHERE usuario_id = ?", (usuario['id'],))
    conjuge = cursor.fetchone()

    # Calcular a próxima data de retirada para exibir na ficha
    if usuario['data_cesta']:
        data_proxima_retirada = datetime.strptime(usuario['data_cesta'], '%Y-%m-%d') + timedelta(days=90)
    else:
        data_proxima_retirada = None

    return render_template('editar_usuario.html', usuario=usuario, filhos=filhos, conjuge=conjuge, data_proxima_retirada=data_proxima_retirada)


@app.route('/editar_filho/<int:filho_id>', methods=['GET', 'POST'])
def editar_filho(filho_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM filhos WHERE id = ?", (filho_id,))
    filho = cursor.fetchone()

    if request.method == 'POST':
        nome_filho = request.form['nome_filho']
        idade_filho = request.form['idade_filho']
        data_nascimento_filho = request.form['data_nascimento_filho']

        cursor.execute("""
            UPDATE filhos SET nome = ?, idade = ?, data_nascimento = ? WHERE id = ?
        """, (nome_filho, idade_filho, data_nascimento_filho, filho_id))
        g.db.commit()

        # Aqui, usamos o usuario_id ao invés de nome_usuario para redirecionar de volta ao editar_usuario
        return redirect(url_for('editar_usuario', nome_usuario=filho['usuario_id']))

    return render_template('editar_filho.html', filho=filho)


@app.route('/editar_conjuge/<int:usuario_id>', methods=['GET', 'POST'])
def editar_conjuge(usuario_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM conjuge WHERE usuario_id = ?", (usuario_id,))
    conjuge = cursor.fetchone()

    if request.method == 'POST':
        nome_conjuge = request.form['nome_conjuge']
        data_nascimento_conjuge = request.form['data_nascimento_conjuge']

        cursor.execute("""
            UPDATE conjuge SET nome = ?, data_nascimento = ? WHERE usuario_id = ?
        """, (nome_conjuge, data_nascimento_conjuge, usuario_id))
        g.db.commit()

        # Redirecionando de volta para a edição do usuário usando usuario_id
        return redirect(url_for('editar_usuario', nome_usuario=usuario_id))

    return render_template('editar_conjuge.html', conjuge=conjuge)


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
        usuarios_rows = cursor.fetchall()

        for usuario_row in usuarios_rows:
            usuario = dict(usuario_row)
            usuario_id = usuario['id']

            cursor.execute("SELECT nome, idade, data_nascimento FROM filhos WHERE usuario_id = ?", (usuario_id,))
            filhos = cursor.fetchall()
            usuario['filhos'] = [{"nome": filho['nome'].upper(), "idade": filho['idade'], "data_nascimento": filho['data_nascimento']} for filho in filhos]

            cursor.execute("SELECT nome, data_nascimento FROM conjuge WHERE usuario_id = ?", (usuario_id,))
            conjuge = cursor.fetchone()
            usuario['conjuge_nome'] = conjuge['nome'].upper() if conjuge else None
            usuario['conjuge_data_nascimento'] = conjuge['data_nascimento'] if conjuge else None

            usuarios.append(usuario)

    return render_template('pesquisar_usuario.html', usuarios=usuarios)

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

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


if __name__ == '__main__':
    app.run(debug=True)
