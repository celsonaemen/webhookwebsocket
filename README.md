# 🚀 Webhooks & WebSockets - Laboratório Prático

## 📚 Sobre o Projeto

Este projeto é uma aplicação educacional completa que demonstra na prática os conceitos de **Webhooks** e **WebSockets** explicados pelo Guto Galego, utilizando FastAPI como framework backend.

### 🎯 Conceitos Implementados

#### 1️⃣ Webhook (API Invertida)
- ✅ Endpoint que **recebe** notificações de eventos externos
- ✅ Validação de assinatura HMAC para segurança
- ✅ Processamento de eventos de pagamento
- ✅ Logs detalhados do fluxo completo

#### 2️⃣ WebSocket (Comunicação Bidirecional)
- ✅ Conexão persistente full-duplex
- ✅ Comunicação em tempo real
- ✅ Demonstração de latência baixa
- ✅ Gerenciamento de múltiplas conexões

---

#### 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.8+** ([Download aqui](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes do Python - já vem com Python)

Para verificar se você tem Python instalado:
```bash
python --version
# ou
python3 --version
```

---

## 🔧 Instalação

### Passo 1: Criar ambiente virtual (recomendado)

```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**Por que usar ambiente virtual?**
- Isola as dependências do projeto
- Evita conflitos com outros projetos Python
- Facilita o gerenciamento de versões

### Passo 2: Instalar dependências

```bash
pip install fastapi uvicorn
```

**O que cada pacote faz?**
- `fastapi`: Framework web moderno e rápido para construir APIs
- `uvicorn`: Servidor ASGI de alta performance para rodar o FastAPI

### Passo 3: Organizar arquivos

Crie a seguinte estrutura de pastas:

```
projeto/
│
├── main.py          (código Python do servidor)
├── index.html       (interface de teste)
└── README.md        (este arquivo)
```

---

## 🚀 Como Executar

### Método 1: Executar diretamente

```bash
python main.py
```

### Método 2: Usar uvicorn (mais controle)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Parâmetros explicados:**
- `main:app` → arquivo `main.py`, variável `app`
- `--reload` → reinicia automaticamente ao salvar código (desenvolvimento)
- `--host 0.0.0.0` → aceita conexões de qualquer IP
- `--port 8000` → porta do servidor

### Método 3: Produção (múltiplos workers)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🌐 Acessando a Aplicação

Após iniciar o servidor, você verá no terminal:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using statreload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Abra seu navegador e acesse:

- **Interface de teste:** http://localhost:8000
- **Documentação automática (Swagger):** http://localhost:8000/docs
- **Documentação alternativa (ReDoc):** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

---

## 🧪 Como Testar

### 🔹 Testando o Webhook

1. Na interface web, vá até o módulo **"Webhook (API Invertida)"**
2. Preencha os campos:
   - **Tipo de Evento:** Pagamento Aprovado
   - **Status:** Aprovado
   - **Valor:** 150.00
   - **ID do Pedido:** PED-12345
3. Clique em **"Disparar Webhook"**
4. Observe:
   - Os logs na interface web
   - Os logs no terminal do servidor
   - A resposta JSON retornada

**O que está acontecendo nos bastidores:**
```
Cliente (navegador) → POST /webhook/pagamento → Servidor FastAPI
                      [JSON + Assinatura HMAC]
                                ↓
                      Valida assinatura
                                ↓
                      Processa pagamento
                                ↓
                      Retorna confirmação
```

### 🔹 Testando o WebSocket

1. Na interface web, vá até o módulo **"WebSocket (Tempo Real)"**
2. Clique em **"Conectar WebSocket"**
3. Aguarde a confirmação de conexão
4. Digite uma mensagem no campo de texto
5. Clique em **"Enviar Mensagem"** ou pressione **Enter**
6. Observe a resposta instantânea com:
   - Mensagem original
   - Mensagem processada (invertida)
   - Latência em milissegundos
   - Timestamp

**O que está acontecendo nos bastidores:**
```
Cliente ←→ WebSocket (ws://localhost:8000/ws) ←→ Servidor
   ↓                                                    ↓
Envia: "Olá mundo"                           Recebe: "Olá mundo"
   ↓                                                    ↓
                                              Processa: "odnum álO"
   ↓                                                    ↓
Recebe: JSON com resposta                    Envia: JSON
```

---

## 🧪 Testes com Ferramentas Externas

### Testando Webhook com cURL

```bash
# Enviar webhook simulado
curl -X POST http://localhost:8000/webhook/pagamento \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: assinatura_teste_123" \
  -d '{
    "evento": "pagamento.aprovado",
    "status": "aprovado",
    "valor": 250.50,
    "pedido_id": "PED-99999",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Testando WebSocket com wscat

Instale o wscat (Node.js necessário):
```bash
npm install -g wscat
```

Conecte e envie mensagens:
```bash
wscat -c ws://localhost:8000/ws
> Olá servidor!
< {"tipo":"resposta","mensagem_original":"Olá servidor!","mensagem_processada":"!rodivre álO"...}
```

### Testando com Postman

1. Importe a coleção de endpoints
2. Configure variável `base_url` = `http://localhost:8000`
3. Teste os endpoints:
   - POST `/webhook/pagamento`
   - WebSocket `/ws`

---

## 📊 Logs e Monitoramento

### Logs do Servidor

O servidor exibe logs detalhados no terminal:

```
====================================================================
🎉 WEBHOOK RECEBIDO!
====================================================================
⏰ Timestamp: 2024-01-15 10:30:45
📦 Dados recebidos: {
  "evento": "pagamento.aprovado",
  "status": "aprovado",
  "valor": 150.0,
  "pedido_id": "PED-12345"
}

✅ Assinatura válida - Webhook autêntico

📊 PROCESSANDO EVENTO:
   • Tipo: pagamento.aprovado
   • Status: aprovado
   • Valor: R$ 150.00
   • Pedido: PED-12345

✅ Pagamento aprovado - liberando pedido...
====================================================================
```

### Logs do WebSocket

```
====================================================================
🔌 NOVA CONEXÃO WEBSOCKET
====================================================================
   • Cliente ID: 140234567890
   • Conexões ativas: 1
   • Timestamp: 2024-01-15 10:31:00
====================================================================

📨 Mensagem recebida do cliente 140234567890: Olá servidor!
📤 Resposta enviada para cliente 140234567890
   • Latência: 0.45ms
   • Processamento: !rodivre álO
```

---

## 🔐 Segurança

### Validação de Assinatura HMAC

O código implementa validação de assinatura para garantir autenticidade:

```python
# Chave secreta compartilhada (em produção, use variável de ambiente)
WEBHOOK_SECRET = "minha_chave_secreta_super_segura_123"

# Gera assinatura HMAC-SHA256
expected_signature = hmac.new(
    key=WEBHOOK_SECRET.encode('utf-8'),
    msg=body_bytes,
    digestmod=hashlib.sha256
).hexdigest()

# Compara de forma segura (evita timing attacks)
is_valid = hmac.compare_digest(signature_header, expected_signature)
```

**⚠️ IMPORTANTE:** Em produção:
- Use variáveis de ambiente para chaves secretas
- Nunca commite chaves no Git
- Use HTTPS (wss:// para WebSocket)
- Implemente rate limiting

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'fastapi'"
**Solução:**
```bash
pip install fastapi uvicorn
```

### Problema: "Address already in use"
**Solução:** A porta 8000 já está em uso
```bash
# Use outra porta
uvicorn main:app --port 8001

# Ou mate o processo usando a porta
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Problema: WebSocket não conecta
**Soluções:**
1. Verifique se o servidor está rodando
2. Confirme a URL: `ws://localhost:8000/ws` (não `http://`)
3. Desabilite extensões de navegador (ad blockers)
4. Teste em modo anônimo

### Problema: CORS errors
**Solução:** Adicione CORS ao FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Recursos para Estudo

### Documentação Oficial
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [WebSocket RFC 6455](https://tools.ietf.org/html/rfc6455)
- [Webhook Best Practices](https://webhook.site/blog/webhook-best-practices)

### Tutoriais Recomendados
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [WebSockets - MDN](https://developer.mozilla.org/pt-BR/docs/Web/API/WebSockets_API)
- [HMAC Authentication](https://en.wikipedia.org/wiki/HMAC)

---

## 🎓 Exercícios Práticos

Para fixar o aprendizado, tente implementar:

### Nível Iniciante
1. ✅ Adicionar novo tipo de evento de webhook (ex: "reembolso")
2. ✅ Modificar o processamento do WebSocket para contar palavras
3. ✅ Adicionar timestamp visual na interface

### Nível Intermediário
4. ⚡ Implementar broadcast (enviar para todos os clientes conectados)
5. ⚡ Criar sistema de "salas" no WebSocket (chat por grupos)
6. ⚡ Adicionar autenticação JWT no WebSocket

### Nível Avançado
7. 🚀 Persistir mensagens em banco de dados (SQLite/PostgreSQL)
8. 🚀 Implementar fila de processamento assíncrono (Celery/RQ)
9. 🚀 Deploy em produção com Docker + Nginx

---

## 🤝 Contribuindo

Melhorias são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir features
- Enviar pull requests
- Compartilhar seu aprendizado

---

## 📄 Licença

Este projeto é open-source e está disponível para fins educacionais.

---

## 🙏 Agradecimentos

- **Augusto Galego (Guto Galego)** - Pelos excelentes tutoriais no YouTube
- **FastAPI** - Framework incrível para APIs modernas
- Comunidade Python - Pelo suporte e documentação

---

## 💬 Dúvidas?

Se tiver alguma dúvida:
1. Revise os comentários no código (`main.py`)
2. Consulte a documentação do FastAPI
3. Teste os exemplos passo a passo
4. Experimente modificar o código!

**Lembre-se:** A melhor forma de aprender é fazendo! 🚀

---

**Bons estudos!** 📚✨