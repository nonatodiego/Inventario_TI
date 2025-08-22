# API Reference

Base URL (dev via Vite proxy): `http://localhost:3000/api`

Base URL (backend direto): `http://localhost:5000/api`

Observação: Apenas rotas registradas em `backend/app.py` estão documentadas aqui.

## Health

GET `/health`

Resposta 200:
```json
{ "status": "healthy", "timestamp": "2025-01-01T00:00:00Z" }
```

## Users

### Listar usuários
GET `/users`

Query params opcionais:
- `search`: termo para buscar por `nome_usuario`, `matricula` (quando existir) e `setor`.
- `setor`: filtra por setor exato.
- `gestor`: filtra por nome do gestor exato.

Exemplo:
```
GET /api/users?search=joao&setor=TI
```

Resposta 200 (lista):
```json
[
  {
    "id": 1,
    "nome_usuario": "João Silva",
    "matricula": "12345",
    "setor": "TI",
    "nome_gestor": "Maria Santos",
    "localizacao": "São Paulo",
    "desktop_notebook": "Notebook",
    "segunda_tela": true,
    "licenca_office": "O365 E3",
    "assets": [
      {
        "id": 10,
        "user_id": 1,
        "celular_corporativo": true,
        "headset": true,
        "mouse_sem_fio": false,
        "teclado_sem_fio": true
      }
    ]
  }
]
```

### Criar usuário
POST `/users`

Body JSON:
- `nome_usuario` (string) — obrigatório
- `matricula` (string|null) — opcional; se vazio, será tratado como `null`
- `setor`, `nome_gestor`, `localizacao`, `desktop_notebook`, `segunda_tela`, `licenca_office` — opcionais

Regras:
- Unicidade de `matricula` é verificada apenas quando fornecida.

Exemplo:
```json
{
  "nome_usuario": "Ana Costa",
  "matricula": null,
  "setor": "Financeiro",
  "nome_gestor": "Carlos Lima",
  "localizacao": "Rio de Janeiro",
  "desktop_notebook": "Desktop",
  "segunda_tela": false,
  "licenca_office": "O365 E1"
}
```

Resposta 201:
```json
{ "message": "Usuário criado com sucesso", "user_id": 2 }
```

Erros comuns:
- 400 `{ "message": "Nome é obrigatório" }`
- 400 `{ "message": "Matrícula já existe" }` (quando enviada duplicada)

### Atualizar usuário
PUT `/users/{id}`

Body JSON (parcial): mesmos campos de criação. Para limpar a matrícula, envie `"matricula": ""` ou `null`.

Resposta 200:
```json
{ "message": "Usuário atualizado com sucesso" }
```

Erros comuns:
- 404 quando `id` não existe
- 400 `{ "message": "Matrícula já existe" }` (quando nova matrícula conflita)

### Deletar usuário
DELETE `/users/{id}`

Resposta 200:
```json
{ "message": "Usuário deletado com sucesso" }
```

### Listar setores únicos
GET `/setores`

Resposta 200:
```json
["TI", "Financeiro", "Vendas"]
```

### Listar gestores únicos
GET `/gestores`

Resposta 200:
```json
["Maria Santos", "Carlos Lima"]
```

## Exportação

Os filtros aceitos replicam os de `/users` (`search`, `setor`, `gestor`).

### Excel
GET `/export/excel`

- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Download com nome: `inventario_ativos_YYYYMMDD_HHMMSS.xlsx`

Exemplo:
```
GET /api/export/excel?setor=TI
```

### PDF
GET `/export/pdf`

- Content-Type: `application/pdf`
- Download com nome: `inventario_ativos_YYYYMMDD_HHMMSS.pdf`

Exemplo:
```
GET /api/export/pdf?search=joao&gestor=Maria%20Santos
```
