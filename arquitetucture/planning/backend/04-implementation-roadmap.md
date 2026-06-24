# 04 - Roadmap de Implementação

Um guia cronológico com as etapas necessárias para transcrever esta arquitetura em um projeto real.

## Fase 1: Fundação do Projeto (Setup e Estrutura)
1. **Inicialização:**
   - Criar a pasta raiz `backend`.
   - Inicializar ambiente com Poetry: `poetry init` e `poetry env use python3.11` (ou versão equivalente).
2. **Dependências Base:**
   - Executar: `poetry add fastapi uvicorn pydantic pydantic-settings supabase`.
   - Dependências de dev: `poetry add --group dev pytest ruff black mypy httpx`.
3. **Estrutura de Pastas:**
   - Criar as pastas `app/routers/`, `app/controllers/`, `app/models/`, `app/core/`, `app/db/`.
4. **Variáveis de Ambiente:**
   - Configurar o módulo Pydantic Settings (`core/config.py`) para consumir chaves do `.env` (`SUPABASE_URL` e `SUPABASE_KEY`).

## Fase 2: Integração com o Banco de Dados
1. **Modelagem via MCP (Model Context Protocol):**
   - Utilizar o MCP Server do Supabase (`mcp_supabase`) via IA para automatizar a criação e o gerenciamento das tabelas de acordo com o `02-database-schema.md`.
   - Criar as tabelas `users`, `constancy_days`, `check_ins`, `questions` e `configurations` usando a tool `execute_sql` ou similares.
   - Configurar via MCP as políticas de segurança (Row Level Security - RLS).
2. **Setup do Cliente em Python:**
   - Instanciar em `db/supabase.py` uma função `get_supabase_client()` que forneça a conexão Supabase injetável de modo seguro usando as chaves de configuração.

## Fase 3: Desenvolvimento de Models e Handlers (Core)
1. **Pydantic Schemas:**
   - Criar em `app/models/` os arquivos `user.py`, `constancy.py`, `question.py` e `configuration.py` conforme especificações dos Documentos 03 e 06.
2. **Global Exception Handling:**
   - Em `core/exceptions.py`, configurar manipuladores padrão para capturar exceções HTTP e exceções genéricas, retornando um JSON estruturado padronizado de erros.

## Fase 4: Implementação das Regras de Negócio (Controllers) e Rotas (Views)
1. **Módulo Users:**
   - Criar a classe abstrata/estática `UserController`.
   - Mapear a rota `/api/v1/users` conectando as funções do controller e os schemas Pydantic.
2. **Módulo Constancy:**
   - Desenvolver o Controller garantindo validações de check-ins (impedir check-in duplo no mesmo dia).
   - Criar rota `/api/v1/constancy` e incluir no `main.py`.
3. **Módulo Questions:**
   - Desenvolver lógica especializada para a criação e listagem de perguntas (`/api/v1/questions`).
4. **Módulo de Configurações:**
   - Criar `ConfigurationController` para gerenciar leitura e escrita das configurações globais no Supabase.
   - Mapear rotas em `/api/v1/configurations` para leitura geral, leitura de chave específica e atualizações por admins.
   - Acoplar todas as rotas no router global.

## Fase 5: Refinamento, Tipagem e Testes
1. **Auditoria de Types (Mypy):**
   - Rodar Mypy no código. Adicionar type hints obrigatórios para todos os retornos de função (`-> Model`) e assinaturas.
2. **Testes Base (Pytest + Httpx):**
   - Testar o fluxo feliz e caminhos de erro utilizando o `TestClient` provido pelo FastAPI nas principais lógicas de negócio.
3. **Revisão Swagger/OpenAPI:**
   - Levantar o servidor local (`uvicorn app.main:app --reload`), abrir `http://localhost:8000/docs`.
   - Validar se exemplos, status codes de sucesso e erro e descrições dos campos estão visíveis.

## Fase 6: Preparação para Deploy
1. **Empacotamento:**
   - Criar o `Dockerfile` focando na versão alpine/slim do Python e execução via Uvicorn.
2. **Variáveis de Produção:**
   - Garantir que as URL/Keys do Supabase de produção não sejam versionadas, utilizando um Secrets Manager na nuvem destino.
