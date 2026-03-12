# 🕐 FlowRP — Bot de Bate-Ponto

Bot de Discord desenvolvido em Python para controle de ponto (entrada/saída) dos servidores da cidade de roleplay **FlowRP**.

O bot funciona em **múltiplos servidores** simultaneamente — cada servidor possui sua própria configuração de canais e seus próprios registros de ponto independentes.

---

## ✨ Funcionalidades

- **Painel interativo** com botão integrado ao embed (layout V2 do Discord)
- **Registro de entrada/saída** com um único clique
- **Log em tempo real** de entradas e saídas em canal dedicado
- **Relatório diário automático** enviado às 23:59 (horário de Brasília)
- **Relatório por período** via comando, com filtro opcional por membro
- **Comando `/emservico`** para ver quem está com ponto aberto no momento
- Todos os embeds em **cor roxa** com identidade visual FlowRP
- Dados persistidos em **arquivos JSON** (sem necessidade de banco externo)

---

## 📦 Requisitos

- **Python 3.11** ou superior
- **discord.py 2.5+** (necessário para layout V2)

---

## 🚀 Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

**Ativar:**
```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar o token

Copie o arquivo de exemplo e preencha com o token do seu bot:

```bash
copy .env.example .env
```

Edite o `.env`:
```
BOT_TOKEN=seu_token_aqui
```

> 💡 O token é obtido no [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications), na seção **Bot** da sua aplicação.

### 4. Iniciar o bot

```bash
python bot.py
```

---

## ⚙️ Configuração dos Canais

Antes de o bot funcionar em um servidor, um **administrador** precisa configurar dois canais obrigatórios:

### Canal de Registro

Canal onde o **relatório diário automático** será enviado todos os dias às 23:59.

```
/configurar registro #canal-de-registro
```

### Canal de Log

Canal onde cada **entrada e saída** de ponto será registrada em tempo real com detalhes do membro, horário e duração.

```
/configurar log #canal-de-log
```

### Enviar o Painel

Depois de configurar os dois canais, envie o painel de bate-ponto no canal desejado:

```
/painel
```

Isso cria uma mensagem fixa com o botão **⏰ Bater Ponto** que os membros usam para registrar entrada e saída. O painel sobrevive a reinícios do bot.

> ⚠️ O comando `/painel` só funciona após os dois canais estarem configurados.

---

## 📋 Comandos

| Comando | Permissão | Descrição |
|---|---|---|
| `/configurar registro #canal` | Administrador | Define o canal de relatório diário |
| `/configurar log #canal` | Administrador | Define o canal de log de entradas/saídas |
| `/painel` | Administrador | Envia o painel com botão de bater ponto |
| `/relatorio inicio:DD/MM/AAAA fim:DD/MM/AAAA` | Administrador | Gera relatório de ponto por período |
| `/relatorio inicio:DD/MM/AAAA fim:DD/MM/AAAA membro:@user` | Administrador | Relatório filtrado por membro |
| `/emservico` | Todos | Mostra quem está com ponto aberto no momento |

---

## 🔄 Como Funciona

1. O membro clica no botão **⏰ Bater Ponto** no painel
2. Se **não está em serviço** → registra **entrada** (inicia contagem)
3. Se **já está em serviço** → registra **saída** (calcula duração)
4. A cada ação, uma notificação é enviada no **canal de log** com os detalhes
5. Às **23:59** (Brasília), um resumo do dia é enviado automaticamente no **canal de registro**

---

## 🔐 Permissões Necessárias do Bot

No [Portal de Desenvolvedores](https://discord.com/developers/applications):

**Bot Permissions:**
- Ler mensagens / Ver canais
- Enviar mensagens
- Incorporar links (Embeds)
- Usar comandos de aplicação (Slash Commands)

**Privileged Intents (ativar no portal):**
- ✅ Server Members Intent

---

## 📁 Estrutura do Projeto

```
flow bate-ponto/
├── bot.py                  # Ponto de entrada do bot
├── config.py               # Carregamento de variáveis de ambiente
├── requirements.txt        # Dependências Python
├── .env.example            # Modelo para o arquivo .env
├── README.md               # Este arquivo
├── cogs/
│   ├── configuracao.py     # Comandos /configurar e /painel
│   ├── ponto.py            # View persistente + /emservico
│   └── relatorio.py        # Relatório diário automático + /relatorio
├── database/
│   └── manager.py          # Leitura/escrita de dados em JSON
├── utils/
│   ├── constants.py        # Cor padrão, fuso horário, nome do bot
│   ├── embeds.py           # Construtores de todos os embeds
│   └── views.py            # PainelPontoView (layout V2 com Container)
└── data/                   # Criado automaticamente
    ├── config/             # Configurações por servidor (guild_id.json)
    └── pontos/             # Registros de ponto por servidor (guild_id.json)
```
