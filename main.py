"""
FastAPI - Demonstração de Webhooks e WebSockets
================================================

Este aplicativo demonstra dois conceitos fundamentais de comunicação:
1. WEBHOOK (API Invertida): O servidor RECEBE notificações de eventos externos
2. WEBSOCKET (Bidirecional): Comunicação em tempo real entre cliente e servidor

Autor: Estudo baseado nas explicações do Guto Galego
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import json
import hmac
import hashlib

# ============================================================================
# INICIALIZAÇÃO DO FASTAPI
# ============================================================================

app = FastAPI(
    title="Webhooks & WebSockets Demo",
    description="Aplicação de estudo sobre comunicação assíncrona",
    version="1.0.0"
)

# ============================================================================
# MÓDULO 1: WEBHOOK - API INVERTIDA
# ============================================================================

"""
CONCEITO DE WEBHOOK:
--------------------
Um webhook é uma "API invertida". Ao invés de VOCÊ fazer requisições para 
obter informações (polling), o SERVIDOR EXTERNO te avisa quando algo acontece.

Exemplo prático:
- Você integra com um gateway de pagamento (Stripe, PagSeguro, etc)
- Quando um pagamento é aprovado, ELES chamam SEU endpoint
- Você não precisa ficar perguntando "o pagamento foi aprovado?"

Vantagens:
✓ Tempo real
✓ Menos requisições desnecessárias
✓ Economia de recursos
"""

# Chave secreta simulada (em produção, vem de variável de ambiente)
WEBHOOK_SECRET = "minha_chave_secreta_super_segura_123"


@app.post("/webhook/pagamento")
async def webhook_pagamento(request: Request):
    """
    Endpoint que RECEBE notificações de pagamento de provedores externos
    
    Fluxo:
    1. Provedor de pagamento (ex: Stripe) processa um pagamento
    2. Ele faz um POST para este endpoint com os dados
    3. Verificamos a autenticidade (assinatura)
    4. Processamos o evento
    
    Args:
        request: Objeto da requisição contendo headers e body
    
    Returns:
        JSON confirmando o recebimento
    """
    
    # ========================================================================
    # PASSO 1: EXTRAIR OS DADOS DO CORPO DA REQUISIÇÃO
    # ========================================================================
    try:
        # Lê o corpo da requisição como bytes (necessário para validação)
        body_bytes = await request.body()
        
        # Converte para string e depois para dicionário Python
        payload = json.loads(body_bytes.decode('utf-8'))
        
        print("\n" + "="*70)
        print("🎉 WEBHOOK RECEBIDO!")
        print("="*70)
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 Dados recebidos: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON do webhook")
        return {"status": "error", "message": "JSON inválido"}
    
    # ========================================================================
    # PASSO 2: VALIDAR A ASSINATURA (SECURITY)
    # ========================================================================
    """
    ⚠️ SEGURANÇA CRÍTICA ⚠️
    
    Em produção, SEMPRE valide se o webhook veio realmente do provedor!
    Caso contrário, qualquer um pode enviar dados falsos para seu endpoint.
    
    Processo de validação típico:
    1. O provedor envia um header com uma assinatura (ex: X-Signature)
    2. Você recalcula a assinatura usando a chave secreta compartilhada
    3. Compara as assinaturas - se baterem, é autêntico
    
    Exemplo de implementação:
    """
    
    # Obtém a assinatura enviada pelo provedor (simulado)
    signature_header = request.headers.get("X-Webhook-Signature", "")
    
    # Calcula a assinatura esperada usando HMAC-SHA256
    # HMAC = Hash-based Message Authentication Code (padrão da indústria)
    expected_signature = hmac.new(
        key=WEBHOOK_SECRET.encode('utf-8'),  # Chave secreta compartilhada
        msg=body_bytes,                       # Corpo original da mensagem
        digestmod=hashlib.sha256              # Algoritmo de hash
    ).hexdigest()
    
    # Compara as assinaturas de forma segura (evita timing attacks)
    is_valid = hmac.compare_digest(signature_header, expected_signature)
    
    if not is_valid:
        print("⚠️ ALERTA: Assinatura inválida! Possível tentativa de fraude.")
        print(f"   Esperado: {expected_signature}")
        print(f"   Recebido: {signature_header}")
        # Em produção, você retornaria 401 Unauthorized aqui
        # return {"status": "error", "message": "Assinatura inválida"}, 401
    else:
        print("✅ Assinatura válida - Webhook autêntico")
    
    # ========================================================================
    # PASSO 3: PROCESSAR O EVENTO DE PAGAMENTO
    # ========================================================================
    
    # Extrai informações relevantes do payload
    evento = payload.get("evento", "desconhecido")
    status = payload.get("status", "pendente")
    valor = payload.get("valor", 0)
    pedido_id = payload.get("pedido_id", "N/A")
    
    print(f"\n📊 PROCESSANDO EVENTO:")
    print(f"   • Tipo: {evento}")
    print(f"   • Status: {status}")
    print(f"   • Valor: R$ {valor:.2f}")
    print(f"   • Pedido: {pedido_id}")
    
    # Aqui você faria a lógica de negócio, por exemplo:
    # - Atualizar status do pedido no banco de dados
    # - Enviar email de confirmação para o cliente
    # - Liberar acesso a um produto digital
    # - Disparar notificação push
    
    if status == "aprovado":
        print("✅ Pagamento aprovado - liberando pedido...")
        # simulate_liberar_pedido(pedido_id)
    elif status == "recusado":
        print("❌ Pagamento recusado - notificando cliente...")
        # simulate_notificar_falha(pedido_id)
    
    print("="*70 + "\n")
    
    # ========================================================================
    # PASSO 4: RESPONDER AO PROVEDOR
    # ========================================================================
    """
    É importante responder rapidamente (< 5 segundos) ao webhook!
    
    Se você demorar muito ou não responder:
    - O provedor pode reenviar o webhook (duplicação)
    - Pode marcar seu endpoint como "down"
    - Pode desabilitar os webhooks
    
    Dica: Faça processamento pesado de forma assíncrona (ex: Celery, RQ)
    """
    
    return {
        "status": "success",
        "message": "Webhook processado com sucesso",
        "evento_recebido": evento,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# MÓDULO 2: WEBSOCKET - COMUNICAÇÃO BIDIRECIONAL
# ============================================================================

"""
CONCEITO DE WEBSOCKET:
----------------------
WebSocket é um protocolo de comunicação FULL-DUPLEX (bidirecional) sobre TCP.

Diferenças principais:

HTTP tradicional:
- Cliente pergunta → Servidor responde → Conexão fecha
- Para cada mensagem, nova conexão (overhead)
- Comunicação HALF-DUPLEX (um fala, outro escuta)

WebSocket:
- Cliente conecta → Canal permanece aberto → Ambos podem enviar a qualquer momento
- Uma única conexão persistente (eficiente)
- Comunicação FULL-DUPLEX (ambos falam simultaneamente)

Casos de uso ideais:
✓ Chat em tempo real
✓ Jogos multiplayer
✓ Atualizações de cotações/bolsa
✓ Notificações push
✓ Colaboração em tempo real (ex: Google Docs)
"""

# Lista de conexões ativas (em produção, use Redis ou similar)
active_connections: list[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket para comunicação em tempo real
    
    O ciclo de vida é:
    1. Cliente solicita upgrade de HTTP para WebSocket
    2. accept() estabelece a conexão
    3. Loop infinito aguardando mensagens
    4. Quando cliente desconecta, remove da lista
    
    Args:
        websocket: Objeto de conexão WebSocket
    """
    
    # ========================================================================
    # FASE 1: ESTABELECER CONEXÃO (HANDSHAKE)
    # ========================================================================
    await websocket.accept()
    active_connections.append(websocket)
    
    client_id = id(websocket)  # ID único para esta conexão
    
    print("\n" + "="*70)
    print(f"🔌 NOVA CONEXÃO WEBSOCKET")
    print("="*70)
    print(f"   • Cliente ID: {client_id}")
    print(f"   • Conexões ativas: {len(active_connections)}")
    print(f"   • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Envia mensagem de boas-vindas
    await websocket.send_json({
        "tipo": "conexao",
        "mensagem": "Conectado ao servidor WebSocket!",
        "client_id": client_id,
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        # ====================================================================
        # FASE 2: LOOP DE COMUNICAÇÃO
        # ====================================================================
        """
        Este loop fica aguardando mensagens do cliente indefinidamente.
        É assíncrono (não bloqueia), então pode gerenciar múltiplas conexões.
        """
        
        while True:
            # Aguarda receber dados do cliente
            # Pode ser: texto, JSON, ou bytes
            data = await websocket.receive_text()
            
            print(f"📨 Mensagem recebida do cliente {client_id}: {data}")
            
            # ==============================================================
            # PROCESSAMENTO DA MENSAGEM
            # ==============================================================
            
            # Adiciona timestamp (demonstra latência baixa)
            timestamp_recebido = datetime.now()
            
            # Transforma a mensagem (exemplo: inverte o texto)
            mensagem_invertida = data[::-1]
            
            # Calcula tempo de processamento (microsegundos)
            timestamp_enviado = datetime.now()
            latencia_ms = (timestamp_enviado - timestamp_recebido).total_seconds() * 1000
            
            # ==============================================================
            # ENVIO DA RESPOSTA
            # ==============================================================
            
            resposta = {
                "tipo": "resposta",
                "mensagem_original": data,
                "mensagem_processada": mensagem_invertida,
                "timestamp_recebido": timestamp_recebido.isoformat(),
                "timestamp_enviado": timestamp_enviado.isoformat(),
                "latencia_ms": round(latencia_ms, 2),
                "caracteres": len(data)
            }
            
            # Envia resposta para o cliente específico
            await websocket.send_json(resposta)
            
            print(f"📤 Resposta enviada para cliente {client_id}")
            print(f"   • Latência: {latencia_ms:.2f}ms")
            print(f"   • Processamento: {mensagem_invertida}\n")
            
            # ==============================================================
            # BROADCAST (OPCIONAL)
            # ==============================================================
            """
            Se quiser enviar para TODOS os clientes conectados:
            
            for connection in active_connections:
                if connection != websocket:  # Não envia para si mesmo
                    await connection.send_json({
                        "tipo": "broadcast",
                        "de": client_id,
                        "mensagem": data
                    })
            """
    
    except WebSocketDisconnect:
        # ====================================================================
        # FASE 3: DESCONEXÃO
        # ====================================================================
        """
        Disparado quando:
        - Cliente fecha a aba/navegador
        - Perde conexão de internet
        - Chama websocket.close() no JavaScript
        """
        
        active_connections.remove(websocket)
        
        print("\n" + "="*70)
        print(f"🔌 CLIENTE DESCONECTADO")
        print("="*70)
        print(f"   • Cliente ID: {client_id}")
        print(f"   • Conexões restantes: {len(active_connections)}")
        print(f"   • Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ Erro no WebSocket do cliente {client_id}: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# ============================================================================
# INTERFACE HTML DE TESTE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """
    Serve a página HTML de teste com JavaScript integrado
    """
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# ============================================================================
# ENDPOINT DE HEALTHCHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Endpoint para verificar se o servidor está rodando
    Útil para monitoramento e load balancers
    """
    return {
        "status": "online",
        "websocket_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    """
    Para rodar este servidor:
    
    1. Instale as dependências:
       pip install fastapi uvicorn
    
    2. Execute o servidor:
       python main.py
       
       OU
       
       uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
    3. Acesse no navegador:
       http://localhost:8000
    
    Parâmetros do uvicorn:
    - --reload: Reinicia automaticamente ao salvar código (desenvolvimento)
    - --host: IP de escuta (0.0.0.0 = todas as interfaces)
    - --port: Porta do servidor
    - --workers: Número de processos workers (produção)
    """
    
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )