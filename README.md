# SisChamados (SISTEMA DE CHAMADOS V2 - Versão Web)

Aplicação web para abertura e gerenciamento de chamados de suporte técnico (TI), migrada de um sistema original em terminal (Python + MySQL) para uma aplicação Flask completa, com banco de dados na nuvem e deploy público.
Vale lembrar que desenvolvi tudo sozinho! O intuito desse sistema Flask foi migrar o meu sistema que funcionava apenas no terminal para poder ficar na web, disponível principalmente para o meu currículo.

🔗 **Acesse a aplicação:** https://sischamados.onrender.com

## Sobre o projeto

O sistema simula um fluxo real de suporte técnico interno: usuários abrem chamados relatando problemas (hardware, software, rede, impressora), e a equipe de TI gerencia esses chamados através de um painel próprio, podendo atender, fechar ou reabrir cada um, além de acompanhar métricas gerais em um dashboard.

Existem dois perfis de acesso:

- **Usuário** — abre chamados e acompanha o andamento dos seus próprios chamados.
- **TI** — visualiza todos os chamados do sistema, gerencia o status de cada um, cadastra novos usuários e acessa o dashboard com métricas gerais.

## Funcionalidades

- Autenticação por matrícula, com controle de sessão
- Controle de acesso por perfil (Usuário / TI)
- Abertura de chamados (título, descrição, categoria e prioridade)
- Listagem de chamados por usuário (Meus Chamados)
- Listagem geral de chamados (exclusivo TI)
- Mudança de status de chamados: Atender, Fechar e Reabrir (exclusivo TI)
- Cadastro de novos usuários, com escolha de perfil (exclusivo TI)
- Dashboard com métricas gerais: total de usuários, total de chamados, chamados abertos e fechados
- Layout responsivo, adaptado para desktop e celular

## Tecnologias utilizadas

- **Python** + **Flask** — aplicação web e rotas, organizadas em Blueprints
- **MySQL** — banco de dados relacional
- **Jinja2** — templates HTML dinâmicos
- **HTML/CSS** — interface, com design responsivo (mobile-first)
- **python-dotenv** — gerenciamento de variáveis de ambiente
- **Gunicorn** — servidor de produção
- **Aiven** — hospedagem do banco de dados MySQL na nuvem
- **Render** — hospedagem da aplicação Flask

## Estrutura do projeto

```
SISTEMA-DE-CHAMADOS-V2/
├── app.py                  # Ponto de entrada da aplicação
├── banco/
│   └── conexao.py          # Conexão com o banco de dados MySQL
├── routes/                 # Rotas organizadas por assunto (Blueprints)
│   ├── autenticacao.py     # Login, logout, painel
│   ├── chamados.py         # Abrir, listar e gerenciar chamados
│   ├── usuarios.py         # Cadastro de usuários
│   └── dashboard.py        # Métricas gerais
├── static/
│   └── css/
│       └── style.css       # Estilos compartilhados (responsivo)
├── templates/               # Páginas HTML (Jinja2)
├── requirements.txt         # Dependências do projeto
└── .env                     # Variáveis de ambiente (não versionado)
```

## Como rodar localmente

### Pré-requisitos

- Python 3.10+
- MySQL instalado localmente (ou acesso a um banco MySQL na nuvem)

### Passo a passo

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd SISTEMA-DE-CHAMADOS-V2
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=nome_do_banco
DB_SSL_DISABLED=true
FLASK_SECRET_KEY=uma_chave_aleatoria_gerada
```

> A `FLASK_SECRET_KEY` pode ser gerada com o comando:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

4. Crie as tabelas `usuarios` e `chamados` no seu banco de dados (script SQL disponível em [caminho, se aplicável]).

5. Rode a aplicação:
```bash
python app.py
```

6. Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estrutura do banco de dados

**usuarios**
| Campo | Tipo |
|---|---|
| id | INT, chave primária |
| nome | VARCHAR(100) |
| email | VARCHAR(100), único |
| matricula | VARCHAR(4), único |
| perfil | VARCHAR(20) — "Usuario" ou "TI" |

**chamados**
| Campo | Tipo |
|---|---|
| id | INT, chave primária |
| titulo | VARCHAR(50) |
| descricao | TEXT |
| categoria | ENUM — Hardware, Software, Rede, Impressora |
| prioridade | ENUM — Baixa, Media, Alta |
| status | ENUM — Aberto, Em andamento, Fechado |
| data_abertura | DATETIME |
| data_fechamento | DATETIME |
| id_usuario | INT, chave estrangeira → usuarios.id |

## Segurança

- Senhas e credenciais sensíveis nunca ficam expostas no código-fonte, sendo lidas via variáveis de ambiente (`.env` local / variáveis de ambiente no Render)
- Conexão criptografada (SSL) com o banco de dados em produção
- Rotas protegidas por autenticação e verificação de perfil

## Autor

Gabriel Barbosa Souza, 2026
