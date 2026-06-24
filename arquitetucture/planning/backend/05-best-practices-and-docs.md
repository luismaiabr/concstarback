# 05 - Melhores Práticas, Padrões e Documentação (Best Practices)

Para que o backend seja robusto e "enterprise-ready", todo o desenvolvimento deve seguir as diretrizes rigorosas descritas abaixo.

## 1. Padrões de Tipagem (Type Hints e Mypy)
- **Obrigatoriedade:** Todo parâmetro e retorno de método/função DEVE ser tipado.
- Evitar ao máximo a importação e o uso de `Any`.
- Classes Pydantic resolvem parte da validação em Runtime, mas o Type Hint (Mypy) garante segurança em tempo de desenvolvimento.
```python
# BOM:
async def get_active_users(limit: int = 10) -> List[UserResponse]: ...

# RUIM:
async def get_active_users(limit): ...
```

## 2. Arquitetura "Thin Views, Fat Controllers"
- **Views (Routers) são burras:** A Rota no FastAPI é responsável apenas por injeção de dependência (`Depends`), receber o HTTP Request, validar via Pydantic e retornar HTTP Response correspondente.
- **Controllers contêm o negócio:** Nenhuma regra de banco, validações cruzadas ou `if` de negócio complexo deve viver na rota. Se a rota tem mais de 10 linhas, algo está errado.

## 3. Rich Documentation com FastAPI/OpenAPI nativos
O Swagger UI (`/docs`) gerado deve ser a única fonte de verdade para o Front-end.
Para garantir isso:
1. **Agrupamento (Tags):** Todas as rotas devem estar sob a respectiva `tag` no decorator do Router.
2. **Descrições de Campo (Pydantic):** O uso do parâmetro `Field(..., description="...", example="...")` é obrigatório em modelos Request/Response.
3. **Responses Documentadas:** Explicitamente documente o que acontece quando ocorre um erro.
```python
@router.post(
    "/",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma nova sessão de evento",
    responses={
        400: {"description": "Dados da sessão inconsistentes."},
        403: {"description": "Usuário não tem permissão de host."}
    }
)
async def create_session(...):
```

## 4. Padronização Global de Tratamento de Erros (Exception Handling)
Nunca exponha Stack Traces para o cliente, nem erros nativos do Supabase/PostgreSQL soltos.
Implemente um handler customizado no `app/main.py`:

```python
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the real error to external tools (Sentry, Datadog etc)
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_SERVER_ERROR", "message": "Um erro inesperado ocorreu."}
    )

@app.exception_handler(CustomBusinessException)
async def business_exception_handler(request: Request, exc: CustomBusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message}
    )
```

## 5. Integração com Supabase (Segurança e Isolamento)
- O backend atua em ambiente de servidor (Server-Side), portanto deve utilizar a chave `SUPABASE_SERVICE_ROLE_KEY` para as lógicas internas caso ele atue de maneira autoritativa ("Bypassing RLS") *OU* se valer de Tokens JWT gerados pelo front-end para invocar em nome do usuário.
- Se o backend for a única forma de acessar o DB para escritas (recomendado), utilize o Service Role e gerencie a permissão (AuthZ) diretamente nos Controllers, não deixando o banco à mercê de chamadas anônimas diretas no Client do Supabase.

## 6. Padronização e Estilo de Código (Linting)
- Use **Ruff** ou o conjunto **Black + Flake8** para formatação automática.
- Use **Isort** para ordenação de imports (módulos nativos > libs de terceiros > imports locais).
- Adote o uso de **Docstrings** no formato Google ou Sphinx para todos os Controllers críticos, explicando os side-effects e exceções que podem ser levantadas.
