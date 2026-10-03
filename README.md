# Email Personal Manager

Sistema que atua como um **gerenciador pessoal de e-mail** do usuário: conecta-se à conta **Gmail** dele via **OAuth2**, permite **agendar e enviar mensagens a partir da própria conta**, e expõe **estatísticas simples da caixa de entrada** (não lidos, volume, remetentes frequentes). Construído com **Domain-Driven Design (DDD)** e **Clean Architecture** sobre **FastAPI** + **Advanced Alchemy / SQLAlchemy Async**.

![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)
![FastAPI](https://img.shields.io/badge/fastapi-async-009688)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

**Decisões de escopo da v1:** apenas Gmail (multi-provedor fica para depois); estatísticas de inbox são contagens simples, sem IA (classificação/resumo com IA fica para depois, ver Roadmap).

---

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Stack Tecnológico](#stack-tecnológico)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Entidades do Domínio](#entidades-do-domínio)
- [Casos de Uso](#casos-de-uso)
- [Endpoints da API](#endpoints-da-api)
- [Banco de Dados](#banco-de-dados)
- [Autenticação](#autenticação)
- [Conexão com o Gmail (OAuth2)](#conexão-com-o-gmail-oauth2)
- [Agendamento (APScheduler)](#agendamento-apscheduler)
- [Instalação e Configuração](#instalação-e-configuração)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Roadmap](#roadmap)
- [Contato](#contato)

---

## Sobre o Projeto

A ideia central do sistema é o usuário conectar sua conta Gmail uma vez, e a partir daí o sistema passa a agir **em nome dele** — agenda e-mails para serem enviados no horário certo a partir do endereço dele, e oferece uma visão rápida do estado da caixa de entrada (quantos não lidos, quem mais escreve para ele, volume por dia). Não é um serviço de disparo em massa pois atualmente é um assistente pessoal com autonomia limitada e revogável sobre a própria conta do usuário.

Essa autonomia é dada via **OAuth2** para segurança onde o usuário autoriza explicitamente o sistema, escopo por escopo (ler e enviar), e pode revogar esse acesso a qualquer momento direto no Google, sem depender do seu sistema. O núcleo do negócio (o que é uma mensagem agendada, quando ela deve ser enviada, o que conta como "estatística de inbox") continua isolado no domínio, independente de FastAPI ou da API do Google — a infraestrutura é que sabe falar com o Gmail.

Três frentes resolvidas:

1. **Conexão delegada** — o usuário autoriza o sistema a agir na própria conta Gmail, sem nunca entregar a senha.
2. **Agendamento e envio** — uma mensagem agendada (`pending`) é entregue no horário certo, a partir do endereço real do usuário.
3. **Visão da caixa de entrada** — estatísticas simples e sob demanda, sem persistir o conteúdo dos e-mails do usuário.

---

## Arquitetura

```
┌─────────────────────┐
│   API (HTTP)          │  ← Schemas: MessageInSchema, EmailAccountSchema
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│ Application Layer     │  ← Use Cases: ScheduleMessageUseCase, GetInboxStatsUseCase
│ (Casos de Uso)        │  ← DTOs: MessageInDTO → MessageOutDTO
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│  Domain Layer          │  ← Entities: MessageEntity, EmailAccountEntity, UserEntity
│ (Regras de Negócio)    │  ← Contratos: IEmailProviderAdapter, IUserRepository...
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│ Infrastructure         │  ← GmailProviderAdapter (OAuth2 + Gmail API)
│ (Persistência/Gmail)   │  ← Repositórios, models ORM, TokenEncryptor
└──────────┬───────────┘
           │
           ▼
┌─────────────────────┐
│   SQLite → PostgreSQL  │
└─────────────────────┘
```

### Padrões Arquiteturais

| Padrão | Descrição | Implementação |
|---|---|---|
| **DDD / Clean Architecture** | Domínio isolado de framework e de provedor externo | `domain/` não conhece Gmail API nem FastAPI |
| **Repository Pattern** | Abstração de persistência | `IUserRepository`, `IMessageRepository`, `IEmailAccountRepository` |
| **Adapter Pattern** | Integração com serviço externo | `IEmailProviderAdapter` → `GmailProviderAdapter` |
| **DTO Pattern** | Transporte entre camadas | `MessageInDTO`, `InboxStatsDTO` |
| **OAuth2 Authorization Code Flow** | Autorização delegada, sem senha do usuário | `ConnectEmailAccountUseCase` + `GmailOAuthCallbackUseCase` |
| **Encryption at Rest** | Tokens nunca ficam em texto puro no banco | `TokenEncryptor` (Fernet) na infraestrutura |
| **Background Scheduler** | Disparo assíncrono das mensagens agendadas | `APScheduler` (`AsyncIOScheduler`) no lifespan do FastAPI |

---

## Stack Tecnológico

| Categoria | Tecnologia | Propósito |
|---|---|---|
| Framework Web | FastAPI | API REST assíncrona |
| ORM / Data Mapper | Advanced Alchemy | Repositórios e models sobre SQLAlchemy |
| Banco de Dados | SQLite (dev) → PostgreSQL (produção) | Persistência |
| Validação | Pydantic | Schemas de entrada/saída |
| Integração Gmail | `google-api-python-client`, `google-auth`, `google-auth-oauthlib` | OAuth2 + Gmail API (ler, enviar, contar) |
| Criptografia de tokens | `cryptography` (Fernet) | Tokens OAuth nunca em texto puro no banco |
| Agendamento | APScheduler | Verificação periódica de mensagens pendentes |
| Autenticação da API | PyJWT | Login do usuário no seu sistema (distinto do OAuth do Gmail) |
| Hash de senha | Passlib (bcrypt) | `HashService`, já existente |
| Gerenciador de pacotes | uv | Ambiente e lockfile |

> **Requisitos:** Python ≥ 3.12
>
> **OBS(Importante):** existem dois "logins" diferentes e não devem ser confundidos — o **login no seu sistema** (e-mail/senha própria, gera JWT) e a **conexão OAuth com o Gmail** (autoriza o sistema a agir na conta de e-mail do usuário). Um usuário pode estar logado no sistema sem ter conectado o Gmail ainda.

---

## Estrutura do Projeto

```
FastAdvancedAlchemy/
├── app/
│   ├── api/
│   │   ├── handlers/
│   │   │   ├── auth/auth_api_route_handler.py            # login do sistema (JWT)
│   │   │   ├── user/user_api_route_handler.py             
│   │   │   ├── email_account/
│   │   │   │   └── email_account_api_route_handler.py     #  connect/callback/disconnect
│   │   │   ├── message/message_api_route_handler.py        
│   │   │   └── inbox/inbox_api_route_handler.py            #  estatísticas
│   │   └── schemas/
│   │       ├── user_schemas.py            
│   │       ├── auth_schemas.py             
│   │       ├── email_account_schemas.py    
│   │       ├── message_schemas.py          
│   │       └── inbox_schemas.py            
│   │
│   ├── application/
│   │   ├── dtos/
│   │   │   ├── user_dtos.py               
│   │   │   ├── email_account_dtos.py       
│   │   │   ├── message_dtos.py             
│   │   │   └── inbox_stats_dtos.py         
│   │   └── use_cases/
│   │       ├── user_use_cases.py           
│   │       ├── auth_use_cases.py           
│   │       ├── email_account_use_cases.py  
│   │       ├── message_use_cases.py        
│   │       └── inbox_use_cases.py          
│   │
│   ├── domain/
│   │   ├── contracts/
│   │   │   ├── user/                       
│   │   │   ├── email_account/
│   │   │   │   ├── repositories.py         
│   │   │   │   └── provider_adapter.py     #  IEmailProviderAdapter
│   │   │   └── message/                    
│   │   ├── entities/
│   │   │   ├── user_entities.py            
│   │   │   ├── email_account_entities.py   
│   │   │   └── message_entities.py         
│   │   ├── value_objects/
│   │   │   └── scheduled_at_time.py        
│   │   └── exceptions/                    
│   │
│   └── infrastructure/
│       ├── database/
│       │   ├── repository.py                
│       │   └── sqlite/database.py          
│       ├── models/
│       │   ├── user_models.py              
│       │   ├── email_account_models.py     
│       │   └── message_models.py           
│       ├── gmail/
│       │   ├── gmail_oauth_client.py       #  fluxo OAuth2 (gera URL, troca code por tokens)
│       │   └── gmail_provider_adapter.py   #  implementa IEmailProviderAdapter
│       ├── security/
│       │   └── token_encryptor.py          #  Fernet — criptografa tokens antes de salvar
│       └── scheduler/
│           └── scheduler.py                #  AsyncIOScheduler + job de verificação
│
├── config/
│   └── exception.py         
├── Dockerfile
├── docker-compose.yaml               
├── main.py                               
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## Entidades do Domínio

### `UserEntity` 

```python
@dataclass
class UserEntity:
    id: UUID
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
```

Continua sendo a identidade do usuário **no seu sistema** — não tem relação direta com a conta Gmail dele.

### `EmailAccountEntity`

```python
@dataclass
class EmailAccountEntity:
    id: UUID
    user_id: UUID
    provider: str              # "gmail" (único suportado na v1)
    email_address: str
    access_token: str          # sempre criptografado antes de persistir
    refresh_token: str         # sempre criptografado antes de persistir
    token_expires_at: datetime
    scopes: list[str]
    connected: bool
    connected_at: datetime
```

**Métodos:** `refresh(new_access_token, new_expiry)`, `disconnect()`
**Invariante:** um `user_id` só pode ter **uma** `EmailAccountEntity` com `provider="gmail"` ativa por vez (reconectar substitui a anterior).

### `MessageEntity`

```python
@dataclass
class MessageEntity:
    id: UUID
    user_id: UUID
    email_account_id: UUID
    to_address: str
    subject: str
    body: str
    scheduled_at: ScheduledAtTime
    status: str                # pending | processing | sent | failed | cancelled
    attempts: int
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None
```

**Métodos:** `mark_as_processing()`, `mark_as_sent()`, `mark_as_failed(reason)`, `cancel()`
**Regra:** só pode ser criada se `email_account_id` referenciar uma conta `connected = True` do mesmo `user_id`.

### `ScheduledAtTime` *(Value Object)*

Encapsula a regra "não agendar no passado" — igual ao desenho anterior.

---
 
## Casos de Uso
 
Casos de uso descritos em formato resumido (estilo Cockburn): ator, objetivo, pré-condição, cenário de sucesso principal e extensões relevantes.
 
### Módulo de Conta de E-mail (Gmail)
 
#### UC01 · Iniciar Conexão — `ConnectEmailAccountUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Obter a URL de autorização do Google para iniciar a conexão da conta Gmail
- **Pré-condição:** Usuário autenticado no sistema
- **Cenário principal:**
  1. Usuário solicita o início da conexão com o Gmail
  2. Sistema monta a URL de autorização OAuth2 com `client_id`, `redirect_uri` e os escopos necessários (`gmail.readonly`, `gmail.send`)
  3. Sistema retorna a URL para o usuário abrir e autorizar
- **Extensões:** *1a.* Usuário já possui uma conta Gmail conectada → sistema informa que uma reconexão substituirá a conta atual

#### UC02 · Confirmar Conexão — `GmailOAuthCallbackUseCase`
- **Ator:** Sistema (callback do Google)
- **Objetivo:** Concluir a conexão da conta Gmail após a autorização do usuário
- **Pré-condição:** Google redirecionou a requisição com um `authorization_code` válido
- **Cenário principal:**
  1. Sistema recebe o `authorization_code` enviado pelo Google
  2. Sistema troca o código por `access_token` e `refresh_token` junto à API do Google
  3. Sistema criptografa os tokens recebidos
  4. Sistema cria ou atualiza a `EmailAccountEntity` do usuário com `connected = true`
- **Extensões:** *1a.* Usuário nega a autorização → nenhuma conta é criada, sistema retorna erro tratado de forma amigável

#### UC03 · Desconectar Conta — `DisconnectEmailAccountUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Revogar o acesso do sistema à conta Gmail do usuário
- **Pré-condição:** Usuário possui uma `EmailAccountEntity` conectada
- **Cenário principal:**
  1. Usuário solicita a desconexão da conta Gmail
  2. Sistema revoga o token junto ao Google
  3. Sistema marca a `EmailAccountEntity` como `connected = false`
- **Extensões:** *1a.* Nenhuma conta conectada → `EmailAccountNotConnectedException`
### Módulo de Mensagens
 
#### UC04 · Agendar Mensagem — `ScheduleMessageUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Agendar o envio futuro de uma mensagem a partir da conta Gmail conectada
- **Pré-condição:** Usuário possui `EmailAccountEntity` conectada
- **Cenário principal:**
  1. Usuário informa destinatário, assunto, corpo e data/hora de envio
  2. Sistema valida que o usuário possui uma conta Gmail conectada
  3. Sistema cria o `ScheduledAtTime` a partir da data informada
  4. Sistema cria a mensagem com status `pending`, vinculada à conta de e-mail do usuário
  5. Sistema persiste a mensagem e confirma o agendamento
- **Extensões:** *2a.* Sem conta Gmail conectada → `EmailAccountNotConnectedException` · *3a.* Data informada no passado → `InvalidScheduleTimeException`

#### UC05 · Listar Mensagens Pendentes — `ListMessagesToSendUseCase`
- **Ator:** Sistema (job do APScheduler)
- **Objetivo:** Identificar mensagens que já atingiram o horário de envio
- **Pré-condição:** Existem mensagens com status `pending`
- **Cenário principal:**
  1. Sistema consulta mensagens com `scheduled_at <= agora`
  2. Sistema filtra apenas as mensagens com status `pending`
  3. Sistema retorna a lista para processamento

#### UC06 · Enviar Mensagem — `SendMessageUseCase`
- **Ator:** Sistema (job do APScheduler)
- **Objetivo:** Entregar a mensagem agendada a partir da conta Gmail do usuário
- **Pré-condição:** Mensagem existe e está com status `pending`, identificada pelo UC05
- **Cenário principal:**
  1. Sistema marca a mensagem como `processing`
  2. Sistema obtém a `EmailAccountEntity` vinculada à mensagem, renovando o token via `refresh_token` se necessário
  3. Sistema solicita o envio ao `GmailProviderAdapter`
  4. Sistema atualiza o status da mensagem para `sent`
- **Extensões:** *2a.* Token não pôde ser renovado → `EmailAccountNotConnectedException`, mensagem marcada como `failed` · *3a.* Falha no envio → mensagem marcada como `failed`, `attempts` incrementado e `error_message` registrado

#### UC07 · Consultar Mensagem por ID — `ResponseMessageByIDUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Obter os dados atuais de uma mensagem agendada
- **Cenário principal:**
  1. Usuário informa o ID da mensagem
  2. Sistema busca a mensagem e valida que pertence ao usuário autenticado
  3. Sistema retorna os dados da mensagem
- **Extensões:** *2a.* Mensagem não encontrada ou pertence a outro usuário → `MessageNotFoundException`

#### UC08 · Listar Mensagens do Usuário — `ListMessagesByUserUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Consultar o histórico de mensagens agendadas pelo usuário
- **Cenário principal:**
  1. Usuário solicita a lista de suas mensagens, com filtro opcional por status
  2. Sistema busca todas as mensagens associadas ao usuário autenticado
  3. Sistema retorna a lista de mensagens

#### UC09 · Cancelar Mensagem — `CancelMessageUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Impedir o envio de uma mensagem ainda não processada
- **Pré-condição:** Mensagem existe, pertence ao usuário e está com status `pending`
- **Cenário principal:**
  1. Usuário solicita o cancelamento de uma mensagem agendada
  2. Sistema valida que a mensagem pertence ao usuário e está com status `pending`
  3. Sistema marca a mensagem como `cancelled`
  4. Sistema persiste a alteração
- **Extensões:** *2a.* Mensagem não encontrada → `MessageNotFoundException` · *2b.* Mensagem já enviada, em processamento ou já cancelada → `MessageCannotBeCancelledException`
### Módulo de Estatísticas de Inbox
 
#### UC10 · Obter Estatísticas da Caixa de Entrada — `GetInboxStatsUseCase`
- **Ator:** Usuário autenticado
- **Objetivo:** Obter uma visão rápida do estado atual da caixa de entrada
- **Pré-condição:** Usuário possui `EmailAccountEntity` conectada com escopo `gmail.readonly`
- **Cenário principal:**
  1. Usuário solicita as estatísticas da caixa de entrada, informando o período desejado
  2. Sistema chama a Gmail API (`users.messages.list`) filtrando mensagens pelo período informado
  3. Sistema conta o total de mensagens e quantas possuem o label `UNREAD`
  4. Sistema agrupa as mensagens por remetente (`From`) e identifica os mais frequentes
  5. Sistema retorna os dados calculados em um `InboxStatsDTO`, sem persistir conteúdo de e-mail no banco
- **Extensões:** *1a.* Sem conta Gmail conectada → `EmailAccountNotConnectedException`

```python
@dataclass
class InboxStatsDTO:
    total_messages: int
    unread_count: int
    top_senders: list[tuple[str, int]]   # [(email, contagem), ...]
    period_days: int
```

# Módulo de Autenticação
 
#### UC11 · Autenticar Usuário — `LoginUseCase`
- **Ator:** Visitante com conta registrada
- **Objetivo:** Obter acesso autenticado ao sistema
- **Pré-condição:** Usuário possui conta ativa (não deletada)
- **Cenário principal:**
  1. Usuário informa e-mail e senha
  2. Sistema localiza o usuário pelo e-mail
  3. Sistema valida a senha informada via `HashService.verify`
  4. Sistema gera `access_token` (30 min) e `refresh_token` (7 dias)
  5. Sistema retorna ambos os tokens para serem definidos como cookies `HttpOnly` na resposta
- **Extensões:** *2a.* Usuário não encontrado → `UserNotFoundException` · *3a.* Senha inválida → `InvalidCredentialsException`

#### UC12 · Renovar Access Token — `RefreshTokenUseCase`
- **Ator:** Usuário com sessão válida
- **Objetivo:** Renovar o `access_token` sem exigir novo login, usando o `refresh_token` vigente
- **Pré-condição:** Cookie `refresh_token` presente e com assinatura/expiração válidas
- **Cenário principal:**
  1. Sistema lê o `refresh_token` do cookie
  2. Sistema valida a assinatura e a expiração do token
  3. Sistema gera um novo `access_token`
  4. Sistema retorna o novo `access_token` para ser definido como cookie na resposta
- **Extensões:** *2a.* `refresh_token` ausente, expirado ou inválido → `InvalidRefreshTokenException`, usuário precisa fazer login novamente

---

## Endpoints da API

**Base URL:** `/api/v1` · **Documentação:** `/api/v1/docs`

### Auth (`/auth`)
 
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/auth/login` | ❌ | Login no sistema, define os cookies `access_token` e `refresh_token` |
| POST | `/auth/refresh` | ✅ Cookie (`refresh_token`) | Renova o `access_token` a partir do `refresh_token` válido |
| POST | `/auth/logout` | ✅ Cookie | Invalida a sessão, limpa os cookies `access_token` e `refresh_token` |
 
### Usuários (`/users`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/users/` | ❌ | Registrar novo usuário |
| GET | `/users/me` | ✅ Bearer | Dados do usuário autenticado |

### Conta de E-mail (`/email-accounts`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/email-accounts/connect` | ✅ Bearer | Retorna a URL de autorização do Google |
| GET | `/email-accounts/callback` | ❌ (chamado pelo Google) | Troca `code` por tokens, ativa a conexão |
| GET | `/email-accounts/me` | ✅ Bearer | Status da conexão (conectado? qual e-mail?) |
| DELETE | `/email-accounts/me` | ✅ Bearer | Desconectar Gmail |

### Mensagens (`/messages`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/messages/` | ✅ Bearer | Agendar mensagem a partir da conta conectada |
| GET | `/messages/` | ✅ Bearer | Listar mensagens do usuário |
| GET | `/messages/{id}` | ✅ Bearer | Consultar mensagem por ID |
| DELETE | `/messages/{id}` | ✅ Bearer | Cancelar mensagem pendente |

### Inbox (`/inbox`)

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| GET | `/inbox/stats?days=7` | ✅ Bearer | Estatísticas da caixa de entrada (não lidos, volume, top remetentes) |

### Exemplo — `GET /inbox/stats?days=7`

```json
// Header: Authorization: Bearer <access_token>
// Response 200
{
  "total_messages": 214,
  "unread_count": 38,
  "top_senders": [
    ["notificacoes@banco.com", 21],
    ["equipe@trabalho.com", 14],
    ["newsletter@servico.com", 9]
  ],
  "period_days": 7
}
```

### Exemplo — `POST /messages/`

```json
// Request
// Header: Authorization: Bearer <access_token>
{
  "to_address": "cliente@example.com",
  "subject": "Follow-up da proposta",
  "body": "Olá! Passando para saber se conseguiu revisar a proposta.",
  "scheduled_at": "2026-09-26T09:00:00"
}

// Response 201
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "to_address": "cliente@example.com",
  "subject": "Follow-up da proposta",
  "status": "pending",
  "scheduled_at": "2026-09-26T09:00:00"
}
```

---

## Banco de Dados

### `users`

| Campo | Tipo | Null | Chave | Descrição |
|---|---|---|---|---|
| `id` | UUID | ❌ | PK | Identificador único |
| `name` | VARCHAR(100) | ❌ | - | Nome do usuário |
| `email` | VARCHAR(255) | ❌ | UNIQUE | E-mail de login no sistema |
| `password` | VARCHAR(120) | ❌ | - | Senha hasheada (bcrypt) |
| `created_at` | DATETIME | ❌ | - | Data de criação |
| `deleted_at` | DATETIME | ✅ | - | Soft delete |

### `email_accounts`

| Campo | Tipo | Null | Chave | Descrição |
|---|---|---|---|---|
| `id` | UUID | ❌ | PK | Identificador único |
| `user_id` | UUID | ❌ | FK → users.id, UNIQUE | Um usuário, uma conta Gmail ativa |
| `provider` | VARCHAR(20) | ❌ | - | `"gmail"` |
| `email_address` | VARCHAR(255) | ❌ | - | Endereço Gmail conectado |
| `access_token_encrypted` | TEXT | ❌ | - | Token de acesso, criptografado |
| `refresh_token_encrypted` | TEXT | ❌ | - | Token de renovação, criptografado |
| `token_expires_at` | DATETIME | ❌ | - | Expiração do access token |
| `scopes` | VARCHAR(255) | ❌ | - | Escopos autorizados, separados por vírgula |
| `connected` | BOOLEAN | ❌ | - | Conexão ativa |
| `connected_at` | DATETIME | ❌ | - | Data da conexão |

### `messages`

| Campo | Tipo | Null | Chave | Descrição |
|---|---|---|---|---|
| `id` | UUID | ❌ | PK | Identificador único |
| `user_id` | UUID | ❌ | FK → users.id | Autor do agendamento |
| `email_account_id` | UUID | ❌ | FK → email_accounts.id | Conta Gmail usada para envio |
| `to_address` | VARCHAR(255) | ❌ | - | Destinatário |
| `subject` | VARCHAR(200) | ❌ | - | Assunto |
| `body` | TEXT | ❌ | - | Corpo do e-mail |
| `scheduled_at` | DATETIME | ❌ | - | Data/hora de envio |
| `status` | VARCHAR(20) | ❌ | - | `pending` \| `processing` \| `sent` \| `failed` \| `cancelled` |
| `attempts` | INTEGER | ❌ | - | Tentativas de envio |
| `error_message` | TEXT | ✅ | - | Motivo da última falha |
| `created_at` | DATETIME | ❌ | - | Data de criação |
| `sent_at` | DATETIME | ✅ | - | Data efetiva de envio |

> Não existe tabela de e-mails da inbox — estatísticas são calculadas sob demanda direto na Gmail API, nada do conteúdo dos e-mails do usuário é armazenado no seu banco.

---

## Autenticação

Login **no sistema** via JWT entregue em **cookies httpOnly** — não em header `Authorization: Bearer` (distinto da conexão Gmail, ver seção seguinte). A utilização de cookies é uma decisão de segurança: um token em `Authorization` normalmente é guardado em `localStorage`/`sessionStorage` pelo frontend, o que fica exposto a roubo via XSS; um cookie `HttpOnly` não pode ser lido por JavaScript, reduzindo essa superfície de ataque.
 
| Tipo | Validade | Formato | Nome do cookie |
|---|---|---|---|
| Access Token | 30 minutos | JWT (HS256) | `access_token` |
| Refresh Token | 7 dias | JWT (HS256) | `refresh_token` |
 
**Atributos do cookie `access_token`:**
 
| Atributo | Valor | Por quê |
|---|---|---|
| `HttpOnly` | `true` | Impede leitura via JavaScript no navegador (mitiga XSS) |
| `Secure` | `true` | Cookie só trafega em conexões HTTPS |
| `SameSite` | `Lax` | Bloqueia o envio automático do cookie em requisições cross-site (mitiga CSRF básico) |
| `Path` | `/` | Cookie válido para toda a API |
| `Max-Age` | `1800` (30 min) | Expira junto com a validade do access token |
 
**Atributos do cookie `refresh_token`:**
 
Mesma base do `access_token` (`HttpOnly`, `Secure`, `SameSite=Lax`), com duas diferenças recomendadas:
 
| Atributo | Valor | Por quê |
|---|---|---|
| `Path` | `/auth/refresh` | O navegador só envia esse cookie para a própria rota de renovação — reduz a exposição do token de maior validade nas demais requisições |
| `Max-Age` | `604800` (7 dias) | Expira junto com a validade do refresh token |
 
**Fluxo:**
 
1. `POST /auth/login` valida e-mail/senha e define **dois cookies** na resposta: `access_token` (30 min) e `refresh_token` (7 dias), via `Set-Cookie`.
2. O navegador envia `access_token` automaticamente em toda requisição para o domínio da API, e `refresh_token` apenas em requisições para `/auth/refresh`.
3. Um `dependency` do FastAPI (`get_current_user`) lê o JWT de `request.cookies.get("access_token")`, valida assinatura/expiração e injeta o usuário autenticado na rota.
4. Quando o `access_token` expira, o frontend chama `POST /auth/refresh`: o sistema lê o `refresh_token` do cookie, valida, e responde definindo um novo `access_token` (e, idealmente, rotacionando também o `refresh_token`, para limitar o tempo de vida útil de um token vazado).
5. `POST /auth/logout` responde definindo `access_token` e `refresh_token` com `Max-Age=0`, instruindo o navegador a descartar ambos.

---

## Conexão com o Gmail (OAuth2)

Fluxo completo de autorização delegada — o sistema nunca vê a senha do usuário:

1. Usuário autenticado chama `GET /email-accounts/connect` → recebe a URL de autorização do Google (com `client_id`, `redirect_uri`, escopos `gmail.readonly` + `gmail.send`).
2. Usuário abre a URL, faz login no Google e aceita os escopos pedidos.
3. Google redireciona para `GET /email-accounts/callback` com um `authorization_code`.
4. Sistema troca o `code` por `access_token` + `refresh_token` (chamada servidor-a-servidor ao Google).
5. `ConnectEmailAccountUseCase` cria a `EmailAccountEntity`, **criptografando** os tokens com `TokenEncryptor` (Fernet) antes de persistir, e marca `connected = True`.
6. Em toda ação futura (`SendMessageUseCase`, `GetInboxStatsUseCase`), o `GmailProviderAdapter` descriptografa o token, renova via `refresh_token` se necessário, e chama a Gmail API.

**Pré-requisito de configuração:** criar um projeto no [Google Cloud Console](https://console.cloud.google.com/), configurar a tela de consentimento OAuth (modo "Teste" é suficiente para desenvolvimento pessoal) e gerar credenciais OAuth 2.0 (`client_id` / `client_secret`), com `redirect_uri` apontando para `/email-accounts/callback`.

**Escopos usados:**
- `https://www.googleapis.com/auth/gmail.readonly` — leitura para estatísticas
- `https://www.googleapis.com/auth/gmail.send` — envio de mensagens agendadas

---

## Agendamento (APScheduler)

```
APScheduler (a cada 60s)
  └─ check_and_send_messages()
       ├─ ListMessagesToSendUseCase → mensagens pending vencidas
       └─ Para cada mensagem:
             SendMessageUseCase
               ├─ status → "processing"
               ├─ GmailProviderAdapter.send(email_account, to, subject, body)
               ├─ sucesso → status "sent", sent_at = agora
               └─ falha → status "failed", attempts += 1, error_message registrado
```

---

## Instalação e Configuração

### Pré-requisitos

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado
- Um projeto no Google Cloud Console com a Gmail API habilitada e credenciais OAuth2 geradas

### Rodando com uv

```bash
git clone <url-do-repositorio>
cd FastAdvancedAlchemy

cp .env.example .env
uv sync
uv run uvicorn main:app --reload
```

Documentação interativa em `http://localhost:8000/docs`.

---

## Variáveis de Ambiente

```bash
# App
SECRET_KEY=sua-chave-secreta
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Database
DATABASE_URL=sqlite+aiosqlite:///my_db.sqlite3

# Google OAuth / Gmail API
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/email-accounts/callback
GOOGLE_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send

# Criptografia de tokens (gerar com Fernet.generate_key())
TOKEN_ENCRYPTION_KEY=

# Scheduler
SCHEDULER_INTERVAL_SECONDS=60
```

---

## Roadmap

###  Fase 0 — Base herdada (parcial)
- [✅] `UserEntity` e contratos de usuário
- [✅] `HashService` (bcrypt)
- [✅] Configuração de banco assíncrono

###  Fase 1 — Login no sistema
- [✅] Corrigir bugs herdados da Fase 0
- [✅] `RegisterUserUseCase`, `LoginUseCase` (JWT)

###  Fase 2 — Conexão Gmail (OAuth2)
- [✅] Projeto no Google Cloud Console + credenciais OAuth2
- [✅] `EmailAccountEntity`, model, repositório
- [✅] `TokenEncryptor` (Fernet)
- [] `ConnectEmailAccountUseCase`, `GmailOAuthCallbackUseCase`, `DisconnectEmailAccountUseCase`
- [✅] Endpoints `/email-accounts`

###  Fase 3 — Mensagens agendadas
- [✅] `MessageEntity`, `ScheduledAtTime`, model, repositório
- [✅] `GmailProviderAdapter.send()` (Gmail API `users.messages.send`)
- [ ] `ScheduleMessageUseCase`, `SendMessageUseCase`, `CancelMessageUseCase`
- [ ] Job do APScheduler

###  Fase 4 — Estatísticas de inbox
- [ ] `GmailProviderAdapter.list_messages()` (Gmail API `users.messages.list`)
- [ ] `GetInboxStatsUseCase` (contagem, não lidos, top remetentes)
- [ ] Endpoint `/inbox/stats`

###  Próximos Passos (pós-MVP)
- [ ] Suporte a Outlook (Microsoft Graph API) via novo `IEmailProviderAdapter`
- [ ] Análises com IA (resumo de e-mails, priorização, classificação automática)
- [ ] Testes unitários e de integração
- [ ] Retry com backoff em falhas de envio
- [ ] Migração para PostgreSQL
- [ ] Migração de scheduler in-process para Celery + Redis

---

## Licença

Este projeto está sob a licença **MIT**.


---

## Contato

- **Autor** — Arthur França Silva
- **E-mail** — arthurfranca.dev@gmail.com
- **GitHub** — [@Thurzinfs](https://github.com/Thurzinfs)

---

<div align="center">
  Desenvolvido com ❤️ por <a href="https://github.com/Thurzinfs">Arthur França Silva</a>
</div>