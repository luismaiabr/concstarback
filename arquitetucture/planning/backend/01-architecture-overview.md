# 01 - Visão Geral da Arquitetura (Architecture Overview)

## 1. Introdução
Esta documentação define a arquitetura do backend para a aplicação, utilizando Python moderno, FastAPI e o **cliente oficial do Supabase** como única camada de acesso a dados. O objetivo é criar um sistema escalável, tipado de ponta a ponta e orientado pelo padrão MVC (Model-View-Controller) adaptado para o ecossistema de APIs RESTful com persistência gerenciada pelo Supabase.

## 2. Padrão Arquitetural: MVC Adaptado para API

Em um contexto de API construída com FastAPI e cliente Supabase, o MVC é mapeado da seguinte forma:
- **Model (M):** Composto pelos contratos de validação e tipagem de entrada/saída (Schemas Pydantic). Não há ORM; as entidades são représentadas exclusivamente por modelos Pydantic que espelham o schema do Supabase.
- **View/Router (V):** Representada pelos endpoints (Rotas do FastAPI). A camada View não renderiza HTML, mas sim expõe contratos JSON (Request/Response) e lida com o roteamento, métodos HTTP e documentação OpenAPI.
- **Controller (C):** Camada responsável pela regra de negócio. Recebe os dados validados das rotas (View), processa a lógica de domínio, chama o **cliente Supabase** (`supabase-py`) para interagir com o banco de dados e retorna o resultado.

### Fluxo de Dados
1. O Front-end (Cliente) faz uma requisição HTTP.
2. A **View/Router** intercepta a requisição, e o FastAPI valida automaticamente os dados com base nos **Schemas Pydantic**.
3. A rota delega a execução para o **Controller** correspondente, passando os dados validados.
4. O **Controller** aplica as regras de negócio (ex: verificações, autorização contextual) e interage com o **Supabase** via `supabase-py` (PostgREST API).
5. O resultado é processado e mapeado para um **Schema Pydantic (Response)** pelo Controller.
6. A **View/Router** retorna a resposta REST serializada para o cliente.

## 3. Estrutura de Diretórios Proposta

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada da aplicação FastAPI
│   ├── core/                   # Configurações globais e infraestrutura
│   │   ├── config.py           # Gerenciamento de env vars (Pydantic Settings)
│   │   ├── security.py         # Middlewares de Autenticação, validação JWT
│   │   └── exceptions.py       # Handlers globais de tratamento de erro
│   ├── db/                     # Infraestrutura de acesso ao Supabase
│   │   └── supabase.py         # Instanciação e export do cliente Supabase
│   ├── models/                 # MODEL LAYER: Pydantic Schemas (Request/Response)
│   │   ├── user.py
│   │   ├── constancy.py
│   │   ├── question.py
│   │   └── configuration.py
│   ├── controllers/            # CONTROLLER LAYER: Lógicas de negócio
│   │   ├── user_controller.py
│   │   ├── constancy_controller.py
│   │   ├── question_controller.py
│   │   └── configuration_controller.py
│   ├── routers/                # VIEW LAYER: Rotas FastAPI
│   │   ├── user_router.py
│   │   ├── constancy_router.py
│   │   ├── question_router.py
│   │   └── configuration_router.py
├── tests/                      # Suite de Testes (Pytest)
├── pyproject.toml              # Gestão de dependências (Poetry)
├── .env                        # Variáveis locais de desenvolvimento
└── README.md
```

## 4. Tecnologias Core e Stack
- **Framework Web:** FastAPI (Assíncrono, performático, documentação auto-gerada).
- **Banco de Dados:** Supabase (PostgreSQL gerenciado, com PostgREST API, Auth e Storage nativos). **Não há ORM local.**
- **Cliente DB:** `supabase-py` (SDK oficial do Supabase para Python, opera sobre a PostgREST API do projeto).
- **Validação & Contratos:** Pydantic V2 (Type Hints rigorosos, Schemas e Serialização rápida).
- **Servidor ASGI:** Uvicorn.
