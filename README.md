# Ecclesia Next

Nova versão moderna e segura da plataforma de gestão eclesiástica.

## Objetivo

Reconstruir as funcionalidades do sistema atual com:

- Arquitetura multi-tenant
- Autorização centralizada por papéis, permissões e escopos
- PostgreSQL, migrações versionadas e testes
- Backend FastAPI e frontend Next.js
- Configuração simples para chaves de IA, e-mail, banco e armazenamento
- Base preparada para finanças, eventos, ministérios, mídia, estudos e área infantil

## Estrutura

```text
ecclesia-next/
├── backend/       API FastAPI, domínio, banco, segurança e serviços
├── frontend/      Aplicação Next.js
├── docs/          Especificação funcional e arquitetura
├── docker-compose.yml
└── .env.example
```

## Execução local

1. Copie o arquivo de variáveis:

```bash
cp .env.example .env
```

2. Preencha as variáveis, especialmente:

```env
SECRET_KEY=
DATABASE_URL=postgresql+psycopg://ecclesia:ecclesia@db:5432/ecclesia
OPENAI_API_KEY=
GOOGLE_AI_API_KEY=
```

3. Suba os serviços:

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs
- Banco PostgreSQL: localhost:5432

## Chaves de IA

O projeto já possui um serviço unificado de IA em `backend/app/services/ai_service.py`.

Você pode usar OpenAI ou Google Gemini apenas definindo a chave no `.env`:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sua-chave
```

Ou:

```env
AI_PROVIDER=gemini
GOOGLE_AI_API_KEY=sua-chave
```

As chaves ficam somente no `.env`, nunca no código ou no repositório.

## Primeiros passos

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

## Segurança

- Nenhuma chave deve ser commitada.
- `SECRET_KEY` é obrigatória em produção.
- Senhas usam hash Argon2/bcrypt por meio do mecanismo configurado.
- Permissões são verificadas no servidor, nunca apenas na interface.
- Toda ação sensível gera registro de auditoria.
