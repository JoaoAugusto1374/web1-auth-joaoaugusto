# Autenticação + Gerenciamento de Usuários (Flask)

## Visão Geral
Sistema Flask com:  
- Login por **JWT** (somente JWT).  
- Gerenciamento de usuários via arquivo `users.json`.  
- Páginas protegidas e controle de acesso por **role** (`admin` ou `user`).  
- Admin consegue acessar o **dashboard** e realizar CRUD de usuários diretamente na página.  
- Usuários comuns recebem apenas **token JWT** em JSON após login.

## Estrutura do Projeto
/web1-auth-joao
│
├─ src/
│ ├─ app.py
│ ├─ config.py
│ ├─ helper.py
│ └─ users.json
│
├─ templates/
│ ├─ index.html
│ ├─ login.html
│ └─ dashboard.html
│
├─ static/
│ 
│
├─ .env.example
├─ .gitignore
├─ README.md
└─ requirements.txt



## Configuração
- Criar arquivo `.env` a partir do `.env.example` com variáveis como:
SECRET_KEY=uma_chave_secreta
LOG_LEVEL=DEBUG
JWT_EXPIRATION=3600



- O arquivo `users.json` inicial deve ter estrutura:

```json
[
  {
    "id": 1,
    "username": "admin",
    "password": "1234",
    "role": "admin"
  },
  {
    "id": 2,
    "username": "user",
    "password": "abcd",
    "role": "user"
  }
]
Como Executar:


git clone <repo-url>
cd web1-auth-joao
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask run
Acesse o sistema em: http://127.0.0.1:5000/

Funcionalidades
Página Inicial (/)
Link para login.

Login (/login)
Formulário HTML normal (sem JS/fetch).

Admin:

Redirecionado automaticamente para o dashboard.

JWT enviado como cookie HttpOnly.

Usuário comum:

Recebe token JWT em JSON.

Dashboard (/dashboard) – Somente Admin
Lista todos os usuários.

Permite adicionar e remover usuários.

Protegido por JWT (admin_only=True).

Logout (/logout)
Remove cookie JWT.

Logs de Debug
Ativado pelo LOG_LEVEL no .env.

Mostra:

Tentativas de login (senha mascarada).

Resultado do login.

Payload do JWT (sem chave secreta).

Acesso a rotas protegidas.

Autores:
Ana Júlia

João Augusto

Halina

