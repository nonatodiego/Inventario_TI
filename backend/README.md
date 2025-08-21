# Backend - Inventário de Ativos de TI

API REST completa para gerenciamento de inventário de ativos de TI.

## Tecnologias Utilizadas

- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **JWT**: Autenticação via tokens
- **SQLite**: Banco de dados (desenvolvimento)
- **openpyxl**: Exportação para Excel
- **ReportLab**: Exportação para PDF

## Instalação e Configuração

### 1. Criar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
Edite o arquivo `.env` com suas configurações:
```
DATABASE_URL=sqlite:///inventory.db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

### 4. Executar a aplicação
```bash
python app.py
```

A API estará disponível em `http://localhost:5000`

## Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login do usuário
- `GET /api/auth/verify` - Verificar token
- `POST /api/auth/register` - Registrar usuário (admin)

### Usuários do Inventário
- `GET /api/users` - Listar usuários (com filtros)
- `POST /api/users` - Criar usuário (admin)
- `PUT /api/users/<id>` - Atualizar usuário (admin)
- `DELETE /api/users/<id>` - Deletar usuário (admin)
- `GET /api/setores` - Listar setores únicos
- `GET /api/gestores` - Listar gestores únicos

### Exportação
- `GET /api/export/excel` - Exportar para Excel
- `GET /api/export/pdf` - Exportar para PDF

### Saúde da API
- `GET /api/health` - Status da API

## Usuário Padrão

Ao executar pela primeira vez, será criado um usuário administrador:
- **Username**: admin
- **Password**: admin123

## Estrutura do Banco de Dados

### Tabela `auth_users`
- Usuários do sistema (login)
- Roles: admin/user

### Tabela `users`
- Usuários do inventário
- Informações pessoais e profissionais

### Tabela `assets`
- Ativos associados aos usuários
- Equipamentos e periféricos

## Filtros Disponíveis

### Parâmetros de Query para `/api/users`:
- `search`: Busca por nome, matrícula ou setor
- `setor`: Filtrar por setor específico
- `gestor`: Filtrar por gestor específico

Exemplo: `GET /api/users?search=joão&setor=TI`

## Autenticação

Todas as rotas (exceto login) requerem token JWT no header:
```
Authorization: Bearer <seu_token_aqui>
```

## Permissões

- **Admin**: Acesso completo (CRUD)
- **User**: Apenas leitura

## Exportação

### Excel
- Formato .xlsx
- Todas as colunas do inventário
- Formatação profissional

### PDF
- Relatório formatado
- Informações resumidas
- Data de geração

## Desenvolvimento

### Adicionar novos endpoints:
1. Criar arquivo em `routes/`
2. Registrar blueprint em `app.py`
3. Implementar validações e permissões

### Modificar modelos:
1. Editar `models.py`
2. Gerar migração: `flask db migrate`
3. Aplicar: `flask db upgrade`

## Produção

Para produção, altere:
1. `DATABASE_URL` para PostgreSQL
2. `JWT_SECRET_KEY` para chave segura
3. `FLASK_ENV=production`
4. Configure HTTPS
5. Use servidor WSGI (Gunicorn)
