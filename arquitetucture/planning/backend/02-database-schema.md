# 02 - Modelagem do Banco de Dados (Supabase/PostgreSQL)

## 1. Visão Geral
O banco de dados será hospedado no Supabase. O uso do PostgreSQL permite alta integridade relacional, Foreign Keys (FKs), segurança via Row Level Security (RLS) e performance otimizada para o nosso front-end TypeScript.

## 2. Definição das Entidades (Tabelas)

### Tabela: `users`
Armazena os perfis dos usuários que interagem com o sistema (criando sessões, votando, etc.).
* **Requisito Crítico Atendido:** Atributo `isActive` incluído obrigatoriamente.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key, `uuid_generate_v4()` |
| `email` | `varchar(255)` | Unique, Not Null |
| `name` | `varchar(150)` | Not Null |
| `color` | `varchar(7)` | Default: '#000000' (Para uso no frontend) |
| `isActive` | `boolean` | **Not Null, Default: true** |
| `role` | `varchar(50)` | Default: 'user' |
| `created_at` | `timestamptz` | Default: `now()` |
| `updated_at` | `timestamptz` | Default: `now()` |

---

### Tabela: `constancy_days`
Representa um dia de constância/estudo.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key, `uuid_generate_v4()` |
| `date` | `date` | Unique, Not Null |
| `created_at` | `timestamptz` | Default: `now()` |

---

### Tabela: `check_ins`
Registra os check-ins feitos pelos usuários em um determinado dia de constância.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `id` | `uuid` | Primary Key, `uuid_generate_v4()` |
| `constancy_day_id` | `uuid` | Foreign Key (`constancy_days.id` on Delete Cascade), Not Null |
| `user_id` | `uuid` | Foreign Key (`users.id` on Delete Cascade), Not Null |
| `checked_in` | `boolean` | Not Null, Default: true |
| `cumulative_y` | `int` | Not Null, Default: 0 |
| `cancelled` | `boolean` | Not Null, Default: false |
| `cancel_reason` | `text` | Nullable (Preenchido em caso de cancelamento) |
| `created_at` | `timestamptz` | Default: `now()` |

> **Nota de Integridade:** O check-in deve ser único por usuário por dia: `UNIQUE (constancy_day_id, user_id)`.

---

### Tabela: `questions`
Armazena as perguntas enviadas pelos usuários.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `id` | `serial` | Primary Key |
| `user_id` | `uuid` | Foreign Key (`users.id` on Delete Cascade), Not Null |
| `amount` | `numeric` | Not Null (ex: valor associado à pergunta) |
| `description` | `text` | Not Null |
| `date` | `timestamptz` | Default: `now()` |

---

### Tabela: `configurations`
Armazena parâmetros dinâmicos do sistema (ex: `CHECKINTIME`, `STARTTIME`, `MIN_WORD_REGISTER_QUESTIONS`) em formato JSONB.

| Coluna | Tipo (Postgres) | Restrições / Regras |
| :--- | :--- | :--- |
| `key` | `varchar(100)` | **Primary Key** |
| `value` | `jsonb` | **Not Null** |
| `description` | `text` | Nullable |
| `created_at` | `timestamptz` | Default: `now()` |
| `updated_at` | `timestamptz` | Default: `now()` |

> **Nota Detalhada:** Consulte o documento [06 - Modelagem e Integração de Configurações](file:///root/CONCSTAR_CTAN/frontend/planning/backend/06-configurations-schema.md) para ver a modelagem detalhada, políticas de RLS, exemplos práticos e código de integração.

## 3. Relacionamentos (Diagrama Lógico - ER)
- Um **User** (1) tem (N) **Check-ins**.
- Um **Constancy Day** (1) tem (N) **Check-ins**.
- Um **User** (1) tem (N) **Questions**.

## 4. Políticas de Segurança (Row Level Security - RLS)
Sempre que possível, alocar regras básicas no DB para defesa profunda:
- **Users**: Read aberto para autenticados; Update/Delete restrito ao próprio `id`.
- **Constancy Days**: Read aberto; Criação de dias automática.
- **Check-ins**: Insert/Update/Delete restrito ao próprio dono (`user_id`).
- **Questions**: Insert restrito ao próprio dono (`user_id`); Read aberto para autenticados.
- **Configurations**: Read aberto para todos; Insert/Update/Delete restrito a administradores (ex: `role = 'admin'`).
