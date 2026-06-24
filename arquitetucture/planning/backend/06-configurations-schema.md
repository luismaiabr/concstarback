# 06 - Modelagem e Integração de Configurações (Configurations Schema)

Para gerenciar parâmetros do sistema de forma dinâmica (como `CHECKINTIME`, `STARTTIME`, `MIN_WORD_REGISTER_QUESTIONS`), sem a necessidade de novos deploys ou reinicializações do servidor, adotamos uma tabela genérica de chave-valor baseada no tipo `JSONB` do PostgreSQL. Isso possibilita armazenar diferentes tipos de dados de forma nativa e segura.

---

## 1. Modelagem do Banco de Dados (Supabase/PostgreSQL)

### Tabela: `configurations`
Armazena chaves de configuração globais do sistema.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `key` | `varchar(100)` | **Primary Key** |
| `value` | `jsonb` | **Not Null** (Valores nativos como strings, inteiros, booleanos ou objetos complexos) |
| `description` | `text` | Nullable (Explicação do propósito da configuração) |
| `created_at` | `timestamptz` | Default: `now()` |
| `updated_at` | `timestamptz` | Default: `now()` |

### DDL e Migrations (SQL)
```sql
-- Criação da tabela
CREATE TABLE configurations (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Habilitar Row Level Security (RLS)
ALTER TABLE configurations ENABLE ROW LEVEL SECURITY;

-- Trigger para atualização automática do updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_configurations_updated_at
    BEFORE UPDATE ON configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Políticas de Segurança (RLS)
- **Leitura (SELECT):** Permitida para todos os usuários autenticados (ou anônimos se exposto publicamente):
  ```sql
  CREATE POLICY "Allow public read access to configurations" 
      ON configurations FOR SELECT 
      USING (true);
  ```
- **Escrita (INSERT/UPDATE/DELETE):** Restrita a administradores do sistema:
  ```sql
  CREATE POLICY "Allow admin write access to configurations" 
      ON configurations FOR ALL 
      TO authenticated 
      USING (auth.jwt() ->> 'role' = 'admin');
  ```

---

## 2. Exemplos de Configurações no Banco de Dados

| `key` | `name` | `value` (JSONB) | Tipo Interpretado | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `CHECKINTIME` | `"Horário Limite de Check-in"` | `"09:55:00"` | String (Time) | Horário limite para a realização do Check-in no sistema |
| `STARTTIME` | `"Horário de Início"` | `"09:56:00"` | String (Time) | Horário de início do processamento/evento |
| `MIN_WORD_REGISTER_QUESTIONS` | `"Mínimo de Palavras para Perguntas"` | `5` | Integer | Quantidade mínima de palavras exigidas nas perguntas de cadastro |
| `MAINTENANCE_MODE` | `"Modo de Manutenção"` | `false` | Boolean | Define se o sistema está em manutenção |

---

## 3. Implementação no Front-end (TypeScript)

No front-end Angular/TypeScript, as configurações devem ser mapeadas de forma fortemente tipada com suporte para parse automático do `jsonb`.

### Interfaces de Tipo (`types/configuration.ts`)
```typescript
export type ConfigKey = 'CHECKINTIME' | 'STARTTIME' | 'MIN_WORD_REGISTER_QUESTIONS' | string;

export interface Configuration {
  key: ConfigKey;
  name: string; // Nome legível de exibição
  value: any; // jsonb vindo do Supabase
  description?: string;
  created_at: string;
  updated_at: string;
}

// Estrutura tipada para consumo da aplicação
export interface AppConfig {
  CHECKINTIME: string; // Ex: "09:55:00"
  STARTTIME: string;   // Ex: "09:56:00"
  MIN_WORD_REGISTER_QUESTIONS: number; // Ex: 5
}
```

### Serviço do Supabase no Front-end
```typescript
import { Injectable } from '@angular/core';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { AppConfig, ConfigKey } from './types/configuration';

@Injectable({
  providedIn: 'root'
})
export class ConfigurationService {
  private supabase: SupabaseClient;

  constructor() {
    // Inicialização do cliente Supabase (usando variáveis de ambiente adequadas)
    this.supabase = createClient('YOUR_SUPABASE_URL', 'YOUR_SUPABASE_ANON_KEY');
  }

  // Busca uma única configuração tipada
  async getConfig<T>(key: ConfigKey): Promise<T | null> {
    const { data, error } = await this.supabase
      .from('configurations')
      .select('value')
      .eq('key', key)
      .single();

    if (error) {
      console.error(`Erro ao buscar configuração ${key}:`, error);
      return null;
    }

    return data?.value as T;
  }

  // Busca todas as configurações e mapeia em um objeto estruturado
  async getAllConfigs(): Promise<Partial<AppConfig>> {
    const { data, error } = await this.supabase
      .from('configurations')
      .select('key, value');

    if (error) {
      console.error('Erro ao listar todas as configurações:', error);
      return {};
    }

    return data.reduce((acc, curr) => {
      acc[curr.key as keyof AppConfig] = curr.value;
      return acc;
    }, {} as any);
  }
}
```

---

## 4. Implementação no Back-end (Python / FastAPI)

No FastAPI, consumimos a tabela `configurations` mapeando o tipo `jsonb` do Postgres diretamente para `Any` ou `Json` no Pydantic, garantindo flexibilidade total de schemas.

### Modelos Pydantic (`app/models/configuration.py`)
```python
from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime

class ConfigurationBase(BaseModel):
    key: str = Field(..., description="Chave identificadora única", example="MIN_WORD_REGISTER_QUESTIONS")
    value: Any = Field(..., description="Valor da configuração (qualquer formato JSON)", example=5)
    description: Optional[str] = Field(None, description="Descrição da funcionalidade do parâmetro")

class ConfigurationCreate(ConfigurationBase):
    pass

class ConfigurationUpdate(BaseModel):
    value: Any = Field(..., description="Novo valor a ser salvo")
    description: Optional[str] = Field(None, description="Descrição atualizada")

class ConfigurationResponse(ConfigurationBase):
    created_at: datetime
    updated_at: datetime
```

### Controller de Configurações (`app/controllers/configuration_controller.py`)
```python
from fastapi import HTTPException, status
from app.db.supabase import get_supabase_client
from app.models.configuration import ConfigurationResponse, ConfigurationUpdate

class ConfigurationController:
    @staticmethod
    async def get_config(key: str) -> ConfigurationResponse:
        client = get_supabase_client()
        response = client.table("configurations").select("*").eq("key", key).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuração '{key}' não localizada no banco de dados."
            )
            
        return ConfigurationResponse(**response.data[0])

    @staticmethod
    async def list_configs() -> list[ConfigurationResponse]:
        client = get_supabase_client()
        response = client.table("configurations").select("*").execute()
        return [ConfigurationResponse(**item) for item in response.data]

    @staticmethod
    async def update_config(key: str, data: ConfigurationUpdate) -> ConfigurationResponse:
        client = get_supabase_client()
        update_payload = data.model_dump(exclude_unset=True)
        
        response = client.table("configurations").update(update_payload).eq("key", key).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Falha ao atualizar configuração '{key}'."
            )
            
        return ConfigurationResponse(**response.data[0])
```

### Rotas do FastAPI (`app/routers/configurations.py`)
```python
from fastapi import APIRouter, status, Depends
from app.models.configuration import ConfigurationResponse, ConfigurationUpdate
from app.controllers.configuration_controller import ConfigurationController

router = APIRouter(prefix="/api/v1/configurations", tags=["Configurations"])

@router.get("/", response_model=list[ConfigurationResponse], summary="Lista todas as configurações globais")
async def list_all():
    return await ConfigurationController.list_configs()

@router.get("/{key}", response_model=ConfigurationResponse, summary="Busca uma configuração por chave")
async def get_by_key(key: str):
    return await ConfigurationController.get_config(key)

@router.patch("/{key}", response_model=ConfigurationResponse, summary="Atualiza o valor de uma configuração")
async def update(key: str, data: ConfigurationUpdate):
    return await ConfigurationController.update_config(key, data)
```
