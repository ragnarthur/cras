from flask import Flask, render_template, request, redirect, url_for, session, g, flash
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

# Depois de cada requisição, fechar a conexão com o banco de dados
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Filtros de template
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

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
    return value.strftime(format)

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

# Rotas de CRUD de Usuários, Filhos e Cônjuges

@app.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']  # CPF adicionado
        rg = request.form['rg']  # RG adicionado
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
            "INSERT INTO usuarios (nome, data_nascimento, cpf, rg, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, data_nascimento, cpf, rg, endereco, telefone, filhos, conjuge, bolsa_familia, data_cesta)
        )
        usuario_id = cursor.lastrowid
        g.db.commit()

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
            return redirect(url_for('cadastro_filho', usuario_id=usuario_id))
        elif usuario['conjuge'] == 'sim':
            return redirect(url_for('cadastro_conjuge', usuario_id=usuario_id))
        else:
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

# Rota de edição do usuário
@app.route('/editar_usuario/<nome_usuario>', methods=['GET', 'POST'])
def editar_usuario(nome_usuario):
    if 'username' not in session:
        return redirect(url_for('index'))

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        return redirect(url_for('pesquisar_usuario'))

    if request.method == 'POST':
        # Atualizar dados do usuário
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']
        rg = request.form['rg']
        endereco = f"{request.form['rua']}, {request.form['numero']}, {request.form['bairro']}, {request.form['cidade']}"
        telefone = request.form['telefone']
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']

        # Adicionar observação, se existir
        nova_observacao = request.form.get('nova_observacao')
        if nova_observacao:
            cursor.execute("""
                INSERT INTO observacoes (usuario_id, observacao, data_observacao, data_atualizacao) 
                VALUES (?, ?, ?, ?)
            """, (usuario['id'], nova_observacao, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))

        # Atualizar usuário
        cursor.execute("""
            UPDATE usuarios SET nome = ?, data_nascimento = ?, cpf = ?, rg = ?, endereco = ?, telefone = ?, 
            bolsa_familia = ?, data_cesta = ? WHERE nome = ?
        """, (
            nome, data_nascimento, cpf, rg, endereco, telefone,
            bolsa_familia, data_cesta, nome_usuario
        ))

        # Verificar se adicionar filho foi marcado
        if request.form.get('adicionar_filho'):
            nome_filho = request.form['nome_filho']
            cpf_filho = request.form['cpf_filho']
            rg_filho = request.form['rg_filho']
            data_nascimento_filho = request.form['data_nascimento_filho']

            # Inserir novo filho no banco de dados
            cursor.execute("""
                INSERT INTO filhos (nome, cpf, rg, data_nascimento, usuario_id)
                VALUES (?, ?, ?, ?, ?)
            """, (nome_filho, cpf_filho, rg_filho, data_nascimento_filho, usuario['id']))

        # Consultar o cônjuge antes de verificar se o formulário está tentando adicioná-lo
        cursor.execute("SELECT * FROM conjuge WHERE usuario_id = ?", (usuario['id'],))
        conjuge = cursor.fetchone()

        # Verificar se adicionar cônjuge foi marcado
        if request.form.get('adicionar_conjuge'):
            nome_conjuge = request.form['nome_conjuge']
            cpf_conjuge = request.form['cpf_conjuge']
            rg_conjuge = request.form['rg_conjuge']
            data_nascimento_conjuge = request.form['data_nascimento_conjuge']

            # Inserir ou atualizar o cônjuge no banco de dados
            if conjuge:
                # Atualizar cônjuge existente
                cursor.execute("""
                    UPDATE conjuge SET nome = ?, cpf = ?, rg = ?, data_nascimento = ?
                    WHERE usuario_id = ?
                """, (nome_conjuge, cpf_conjuge, rg_conjuge, data_nascimento_conjuge, usuario['id']))
            else:
                # Inserir novo cônjuge
                cursor.execute("""
                    INSERT INTO conjuge (nome, cpf, rg, data_nascimento, usuario_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome_conjuge, cpf_conjuge, rg_conjuge, data_nascimento_conjuge, usuario['id']))

        g.db.commit()

        # Adicionar mensagem flash de sucesso
        flash("Alterações salvas com sucesso!", "success")

        # Redirecionar para o dashboard após salvar
        return redirect(url_for('dashboard'))

    # Carregar filhos, cônjuge e observações
    cursor.execute("SELECT * FROM filhos WHERE usuario_id = ?", (usuario['id'],))
    filhos = cursor.fetchall()

    cursor.execute("SELECT * FROM conjuge WHERE usuario_id = ?", (usuario['id'],))
    conjuge = cursor.fetchone()

    # Adicionando 'id' à query de observações para permitir exclusão
    cursor.execute("SELECT id, observacao, data_observacao, data_atualizacao FROM observacoes WHERE usuario_id = ?", (usuario['id'],))
    observacoes = cursor.fetchall()

    observacoes_corrigidas = []
    for observacao in observacoes:
        observacao_dict = dict(observacao)

        # Verificar se a data_observacao e data_atualizacao são válidas antes de formatar
        if observacao_dict['data_observacao']:
            observacao_dict['data_observacao'] = datetime.strptime(observacao_dict['data_observacao'], '%Y-%m-%d')
        if observacao_dict['data_atualizacao']:
            observacao_dict['data_atualizacao'] = datetime.strptime(observacao_dict['data_atualizacao'], '%Y-%m-%d')

        observacoes_corrigidas.append(observacao_dict)

    return render_template('editar_usuario.html', 
                           usuario=usuario, 
                           filhos=filhos, 
                           conjuge=conjuge, 
                           observacoes=observacoes_corrigidas)

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

        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (filho['usuario_id'],))
        usuario = cursor.fetchone()
        return redirect(url_for('editar_usuario', nome_usuario=usuario['nome']))

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

        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = cursor.fetchone()
        return redirect(url_for('editar_usuario', nome_usuario=usuario['nome']))

    return render_template('editar_conjuge.html', conjuge=conjuge)

# Rotas de CRUD de Gestantes

@app.route('/cadastro_gestante', methods=['GET', 'POST'])
def cadastro_gestante():
    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']  # CPF adicionado
        rg = request.form['rg']  # RG adicionado
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        endereco = f"{rua}, {numero}, {bairro}, {cidade}"
        telefone = request.form['telefone']
        data_parto = request.form['data_parto']
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']
        possui_filhos = request.form.get('filhos', 'não')
        possui_conjuge = request.form.get('conjuge', 'não')

        cursor = g.db.cursor()
        cursor.execute("""
            INSERT INTO gestantes (nome, data_nascimento, cpf, rg, endereco, telefone, data_parto, bolsa_familia, data_cesta) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, data_nascimento, cpf, rg, endereco, telefone, data_parto, bolsa_familia, data_cesta))
        gestante_id = cursor.lastrowid
        g.db.commit()

        if possui_filhos == 'sim':
            return redirect(url_for('cadastro_filho', usuario_id=gestante_id))
        elif possui_conjuge == 'sim':
            return redirect(url_for('cadastro_conjuge', usuario_id=gestante_id))
        else:
            return redirect(url_for('dashboard'))

    return render_template('cadastro_gestante.html')

@app.route('/editar_gestante/<int:gestante_id>', methods=['GET', 'POST'])
def editar_gestante(gestante_id):
    if 'username' not in session:
        return redirect(url_for('index'))

    cursor = g.db.cursor()
    cursor.execute("SELECT * FROM gestantes WHERE id = ?", (gestante_id,))
    gestante = cursor.fetchone()

    if not gestante:
        return redirect(url_for('pesquisar_gestantes'))

    if request.method == 'POST':
        # Atualizar dados da gestante
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        cpf = request.form['cpf']
        rg = request.form['rg']
        endereco = f"{request.form['rua']}, {request.form['numero']}, {request.form['bairro']}, {request.form['cidade']}"
        telefone = request.form['telefone']
        data_parto = request.form['data_parto']
        bolsa_familia = request.form['bolsa_familia']
        data_cesta = request.form['data_cesta']

        nova_observacao = request.form.get('nova_observacao')
        if nova_observacao:
            cursor.execute("""
                INSERT INTO observacoes (usuario_id, observacao, data_observacao, data_atualizacao) 
                VALUES (?, ?, ?, ?)
            """, (gestante['id'], nova_observacao, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%Y-%m-%d')))

        cursor.execute("""
            UPDATE gestantes SET nome = ?, data_nascimento = ?, cpf = ?, rg = ?, endereco = ?, telefone = ?, 
            data_parto = ?, bolsa_familia = ?, data_cesta = ? WHERE id = ?
        """, (nome, data_nascimento, cpf, rg, endereco, telefone, data_parto, bolsa_familia, data_cesta, gestante_id))

        # Verificar e adicionar filho, cônjuge se necessário
        if request.form.get('adicionar_filho'):
            nome_filho = request.form['nome_filho']
            cpf_filho = request.form['cpf_filho']
            rg_filho = request.form['rg_filho']
            data_nascimento_filho = request.form['data_nascimento_filho']

            cursor.execute("""
                INSERT INTO filhos (usuario_id, nome, cpf, rg, data_nascimento) 
                VALUES (?, ?, ?, ?, ?)
            """, (gestante_id, nome_filho, cpf_filho, rg_filho, data_nascimento_filho))

        if request.form.get('adicionar_conjuge'):
            nome_conjuge = request.form['nome_conjuge']
            cpf_conjuge = request.form['cpf_conjuge']
            rg_conjuge = request.form['rg_conjuge']
            data_nascimento_conjuge = request.form['data_nascimento_conjuge']

            cursor.execute("""
                INSERT INTO conjuge (usuario_id, nome, cpf, rg, data_nascimento) 
                VALUES (?, ?, ?, ?, ?)
            """, (gestante_id, nome_conjuge, cpf_conjuge, rg_conjuge, data_nascimento_conjuge))

        g.db.commit()

        # Exibir a mensagem de sucesso e redirecionar para o dashboard
        flash("Alterações realizadas com sucesso!", "success")
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM filhos WHERE usuario_id = ?", (gestante_id,))
    filhos = cursor.fetchall()

    cursor.execute("SELECT * FROM conjuge WHERE usuario_id = ?", (gestante_id,))
    conjuge = cursor.fetchone()

    cursor.execute("SELECT * FROM observacoes WHERE usuario_id = ?", (gestante_id,))
    observacoes = cursor.fetchall()

    return render_template('editar_gestante.html', 
                           gestante=gestante, 
                           filhos=filhos, 
                           conjuge=conjuge, 
                           observacoes=observacoes)

# Rotas de Pesquisa de Usuários e Gestantes
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

            if usuario['data_cesta']:
                ultima_data = datetime.strptime(usuario['data_cesta'], '%Y-%m-%d')
                proxima_data = ultima_data + timedelta(days=90)
                usuario['data_proxima_retirada'] = proxima_data.strftime('%Y-%m-%d')
            else:
                usuario['data_proxima_retirada'] = None

            cursor.execute("SELECT nome, idade, data_nascimento FROM filhos WHERE usuario_id = ?", (usuario_id,))
            filhos = cursor.fetchall()
            usuario['filhos'] = [{"nome": filho['nome'].upper(), "idade": filho['idade'], "data_nascimento": filho['data_nascimento']} for filho in filhos]

            cursor.execute("SELECT nome, data_nascimento FROM conjuge WHERE usuario_id = ?", (usuario_id,))
            conjuge = cursor.fetchone()
            usuario['conjuge_nome'] = conjuge['nome'].upper() if conjuge else None
            usuario['conjuge_data_nascimento'] = conjuge['data_nascimento'] if conjuge else None

            usuarios.append(usuario)

    return render_template('pesquisar_usuario.html', usuarios=usuarios)

@app.route('/pesquisar_gestantes', methods=['GET', 'POST'])
def pesquisar_gestantes():
    if 'username' not in session:
        return redirect(url_for('index'))

    gestantes = []
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM gestantes WHERE nome LIKE ? OR telefone LIKE ?", 
                       ('%' + pesquisa + '%', '%' + pesquisa + '%'))
        gestantes_rows = cursor.fetchall()

        for gestante_row in gestantes_rows:
            gestante = dict(gestante_row)
            gestantes.append(gestante)

    return render_template('pesquisar_gestantes.html', gestantes=gestantes, datetime=datetime, timedelta=timedelta)

# Rota de Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Rota de Adicionar Secretárias (apenas para administradores)
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
