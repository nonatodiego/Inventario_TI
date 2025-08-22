# Inventory Dashboard (Frontend + Backend)

Sistema de inventário de ativos de TI com painel React (Vite) e API Flask. Permite gerenciar usuários do inventário, registrar ativos, filtrar por setor/gestor, e exportar dados em Excel e PDF.

## Stack

- Frontend: React 18 + Vite + TailwindCSS
- Backend: Flask + SQLAlchemy + Flask-Migrate + CORS
- Exportação: openpyxl (Excel) e ReportLab (PDF)
- Deploy: Netlify (frontend) + Render (backend) — configurável

## Estrutura do projeto

```
.
├─ backend/
│  ├─ app.py               # Inicialização Flask e registro de blueprints
│  ├─ models.py            # Modelos SQLAlchemy (User, Asset)
│  ├─ routes/
│  │  ├─ users.py          # CRUD de usuários do inventário
│  │  └─ export.py         # Exportação Excel/PDF
│  ├─ requirements.txt     # Dependências do backend
│  ├─ Procfile             # Execução com gunicorn (produção)
│  └─ README.md            # Docs específicas da API backend
├─ src/                    # Código do frontend (React)
│  ├─ App.jsx              # App principal
│  ├─ components/          # Componentes reutilizáveis (UI e Login)
│  └─ ...
├─ public/_redirects       # Redirecionamentos (Netlify)
├─ netlify.toml            # Build e proxy do frontend
├─ package.json            # Scripts e dependências do frontend
├─ vite.config.js          # Proxy local /api -> http://localhost:5000
└─ README.md               # Este arquivo
```

## Pré-requisitos

- Node.js 18+
- Python 3.10+
- Pip e virtualenv (recomendado)

## Configuração e execução local

### 1) Backend

1. Criar e ativar venv
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # Linux/Mac
   ```
2. Instalar dependências
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Criar `.env` no diretório `backend/` (opcional)
   ```env
   DATABASE_URL=sqlite:///inventory.db
   # JWT_SECRET_KEY=defina_se_usar_auth
   ```
4. Rodar a API
   ```bash
   # dentro de backend/
   python app.py
   # API em http://localhost:5000
   ```

Observação importante (migração de schema): o campo `matricula` em `users` é opcional (NULL). Se já existe um banco criado antes dessa alteração, aplique migração (Flask-Migrate) ou recrie o banco local.

### 2) Frontend

1. Instalar dependências
   ```bash
   npm install
   ```
2. Rodar em desenvolvimento
   ```bash
   npm run dev
   # App em http://localhost:3000
   ```

O Vite já está configurado para proxyar `/api` para `http://localhost:5000` (veja `vite.config.js`).

## Funcionalidades principais

- Listagem, filtro e busca de usuários do inventário
- Criação/Edição/Exclusão de usuários (permissão admin no app)
- Campo de matrícula é opcional (não obrigatório)
- Exportação:
  - Excel: `GET /api/export/excel`
  - PDF: `GET /api/export/pdf` (frontend possui botão “Exportar PDF” usando filtros ativos)

## Documentação da API

Veja documentação detalhada em `docs/API.md` e também o arquivo `backend/README.md`.

Atalhos:
- Saúde: `GET /api/health`
- Usuários: `GET /api/users`, `POST /api/users`, `PUT /api/users/:id`, `DELETE /api/users/:id`
- Export: `GET /api/export/excel`, `GET /api/export/pdf`

## Build e Deploy

### Frontend (Netlify)
- O arquivo `netlify.toml` publica `dist` e inclui proxy para `/api/*` apontando para sua URL do backend (Render). Ajuste a URL conforme seu backend.
- Build: `npm run build`

### Backend (Render ou outro)
- `backend/Procfile` contém `web: gunicorn app:app`
- Defina `DATABASE_URL` e outras variáveis no provedor

## Troubleshooting

- CORS: já habilitado no backend via `flask_cors`.
- PDF não baixa: verifique se o frontend aponta para o backend correto (proxy local ou `netlify.toml` em produção).
- Campo matrícula: como é opcional, as buscas por matrícula no frontend já consideram ausência (`user.matricula && ...`).

## Licença

Uso interno. Adapte conforme sua necessidade.
