from flask import Flask, render_template, request, redirect, url_for, session, g
from datetime import datetime
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
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        endereco = f"{rua}, {numero}, {bairro}, {cidade}"  # Concatenando os campos de endereço
        telefone = request.form['telefone']
        filhos = request.form.get('filhos', 'não')
        conjuge = request.form.get('conjuge', 'não')
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']

        cursor = g.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta)
        )
        usuario_id = cursor.lastrowid  # Armazena o ID do novo usuário
        g.db.commit()

        # Lógica de redirecionamento: Se tem filhos, vai para o cadastro de filhos. Depois de filhos, vai para cônjuge se necessário.
        if filhos == 'sim':
            # Redireciona para o cadastro de filhos e após cadastro de filhos vai para cônjuge, se aplicável
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
            # Após cadastrar o(s) filho(s), verificar se tem cônjuge. Se sim, redirecionar para o cadastro de cônjuge.
            cursor.execute("SELECT conjuge FROM usuarios WHERE id = ?", (usuario_id,))
            conjuge = cursor.fetchone()['conjuge']
            if conjuge == 'sim':
                return redirect(url_for('cadastro_conjuge', usuario_id=usuario_id))
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

@app.template_filter('format_telefone')
def format_telefone(telefone):
    # Remove tudo que não for número
    telefone = ''.join([num for num in telefone if num.isdigit()])
    # Formata para o padrão (XX)XXXXX-XXXX
    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        return telefone

# Filtro para formatar a data no formato DD/MM/AAAA
@app.template_filter('format_data')
def format_data(data_str):
    try:
        # Tentar converter a string de data para um objeto datetime
        data = datetime.strptime(data_str, '%Y-%m-%d')
        # Retornar a data no formato DD/MM/AAAA
        return data.strftime('%d/%m/%Y')
    except ValueError:
        return data_str  # Se houver erro, retornar a string original

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

        # Pesquisa o usuário baseado no nome ou telefone
        cursor.execute("SELECT * FROM usuarios WHERE nome LIKE ? OR telefone LIKE ?", 
                       ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        usuarios_rows = cursor.fetchall()

        # Converta cada resultado para um dicionário e adicione informações extras
        for usuario_row in usuarios_rows:
            usuario = dict(usuario_row)  # Converte o sqlite3.Row para dict
            
            usuario_id = usuario['id']

            # Buscar filhos do usuário
            cursor.execute("SELECT nome, idade FROM filhos WHERE usuario_id = ?", (usuario_id,))
            filhos = cursor.fetchall()
            # Forçar nome dos filhos para uppercase
            usuario['filhos'] = [{"nome": filho['nome'].upper(), "idade": filho['idade']} for filho in filhos]

            # Buscar cônjuge do usuário
            cursor.execute("SELECT nome FROM conjuge WHERE usuario_id = ?", (usuario_id,))
            conjuge = cursor.fetchone()
            # Forçar nome do cônjuge para uppercase se existir
            usuario['conjuge_nome'] = conjuge['nome'].upper() if conjuge else None

            usuarios.append(usuario)

    return render_template('pesquisar_usuario.html', usuarios=usuarios)


if __name__ == '__main__':
    app.run(debug=True)
