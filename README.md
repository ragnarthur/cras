
# CRAS App

CRAS App é um sistema de gerenciamento de usuários para o Centro de Referência de Assistência Social (CRAS), desenvolvido com Flask, Python, HTML, CSS e JavaScript. Ele permite que secretárias realizem cadastros de usuários, pesquisem informações e administrem o sistema de forma eficiente.

## Funcionalidades Principais

- **Cadastro de Usuários:** Permite o cadastro de novos usuários no sistema com informações detalhadas como nome, endereço, telefone, dados familiares e data de retirada da cesta básica.
- **Pesquisar Usuários:** Pesquisa usuários já cadastrados com base em seu nome ou número de telefone.
- **Informações Familiares:** Cadastro de filhos e cônjuge, com rotas específicas para essas informações.
- **Sistema de Login:** Login com credenciais específicas para secretárias, com diferentes níveis de acesso.
- **Gestão de Secretárias:** O administrador (Maria Silva) pode adicionar ou remover secretárias do sistema.
- **Saudação Dinâmica:** O sistema exibe uma saudação personalizada com base no horário do dia (Bom dia, Boa tarde, Boa noite).
- **Interface Responsiva e Atraente:** Desenvolvida com Bootstrap para garantir uma experiência amigável em diferentes dispositivos.

## Estrutura do Projeto

O projeto segue a seguinte estrutura de diretórios:

```
CRAS_App/
│
├── app.py                   # Arquivo principal da aplicação Flask
├── database.db               # Banco de dados SQLite
├── static/
│   ├── styles.css            # Estilos CSS personalizados
│   └── script.js             # Scripts JS personalizados
├── templates/
│   ├── base.html             # Template base compartilhado entre todas as páginas
│   ├── cadastro_usuario.html  # Página de cadastro de usuários
│   ├── pesquisar_usuario.html # Página de pesquisa de usuários
│   └── dashboard.html        # Página principal (dashboard)
└── README.md                 # Arquivo README (este documento)
```

## Pré-requisitos

- **Python 3.7+**
- **Flask**
- **SQLite3**
- **Bootstrap 5**

## Como Rodar o Projeto

1. Clone este repositório:

   ```bash
   git clone https://github.com/seu-usuario/CRAS_App.git
   ```

2. Entre no diretório do projeto:

   ```bash
   cd CRAS_App
   ```

3. Crie um ambiente virtual e ative-o:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scriptsctivate
   ```

4. Instale as dependências:

   ```bash
   pip install flask
   ```

5. Inicialize o banco de dados:

   ```bash
   python init_db.py
   ```

6. Rode o servidor Flask:

   ```bash
   flask run
   ```

7. Acesse a aplicação no navegador:

   ```
   http://127.0.0.1:5000
   ```

## Usuários Padrão para Login

- **Maria Silva** (administradora):
  - Usuário: `maria`
  - Senha: `senha123`

- **Outras secretárias**:
  - Roseane Vieira, Aline Resende, Meire Castro (mesma senha).

## Contribuições

Este projeto está aberto a contribuições. Sinta-se à vontade para enviar Pull Requests ou abrir Issues.

## Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.

