from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Middleware para logar todas as requisições
@app.before_request
def log_request():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*80}")
    print(f"[{timestamp}] Nova requisição recebida:")
    print(f"  Método: {request.method}")
    print(f"  URL: {request.url}")
    print(f"  IP do cliente: {request.remote_addr}")
    print(f"  Headers:")
    for header, value in request.headers:
        print(f"    {header}: {value}")
    
    if request.data:
        print(f"  Body:")
        try:
            print(f"    {json.dumps(request.get_json(), indent=4)}")
        except:
            print(f"    {request.data.decode('utf-8', errors='ignore')}")
    
    if request.args:
        print(f"  Query Parameters:")
        for key, value in request.args.items():
            print(f"    {key}: {value}")
    
    print(f"{'='*80}\n")

# Endpoint principal
@app.route('/')
def home():
    return jsonify({
        "message": "Servidor API funcionando!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "GET /": "Esta página",
            "GET /api/status": "Status do servidor",
            "POST /api/data": "Enviar dados",
            "GET /api/echo": "Echo com query params",
            "Any method /*": "Aceita qualquer requisição"
        }
    })

# Endpoint de status
@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat()
    })

# Endpoint para receber dados via POST
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    return jsonify({
        "message": "Dados recebidos com sucesso",
        "received": data,
        "timestamp": datetime.now().isoformat()
    }), 201

# Endpoint de echo
@app.route('/api/echo')
def echo():
    return jsonify({
        "query_params": dict(request.args),
        "timestamp": datetime.now().isoformat()
    })

# Endpoint de inspeção completa da requisição (raio-x)
@app.route('/api/inspect', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def inspect():
    """Retorna todos os dados da requisição para análise detalhada"""
    
    # Capturar o body de forma segura
    body_data = None
    body_raw = None
    if request.data:
        try:
            body_data = request.get_json()
        except:
            body_raw = request.data.decode('utf-8', errors='ignore')
    
    # Capturar form data
    form_data = dict(request.form) if request.form else None
    files_data = {key: value.filename for key, value in request.files.items()} if request.files else None
    
    inspection_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": {
            "full": request.url,
            "base": request.base_url,
            "path": request.path,
            "scheme": request.scheme,
            "host": request.host,
            "root_url": request.root_url
        },
        "client": {
            "ip": request.remote_addr,
            "user_agent": request.headers.get('User-Agent'),
            "referrer": request.referrer
        },
        "headers": dict(request.headers),
        "query_params": dict(request.args),
        "body": {
            "json": body_data,
            "raw": body_raw,
            "form": form_data,
            "files": files_data
        },
        "cookies": dict(request.cookies),
        "environment": {
            "is_secure": request.is_secure,
            "is_json": request.is_json,
            "content_type": request.content_type,
            "content_length": request.content_length,
            "mimetype": request.mimetype,
            "mimetype_params": request.mimetype_params
        }
    }
    
    return jsonify(inspection_data)

# Endpoint para capturar e salvar requisição bruta
@app.route('/api/capture', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def capture():
    """Captura a requisição completa e salva em arquivo para análise posterior"""
    
    # Criar diretório para capturas se não existir
    captures_dir = 'captured_requests'
    os.makedirs(captures_dir, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filename = f"{captures_dir}/request_{timestamp}.txt"
    
    # Montar requisição HTTP bruta
    raw_request = []
    
    # Linha de requisição
    raw_request.append(f"{request.method} {request.full_path if request.query_string else request.path} HTTP/1.1")
    
    # Headers
    for header, value in request.headers:
        raw_request.append(f"{header}: {value}")
    
    raw_request.append("")  # Linha em branco entre headers e body
    
    # Body
    if request.data:
        try:
            # Tentar decodificar como texto
            body_str = request.data.decode('utf-8', errors='replace')
            raw_request.append(body_str)
        except:
            raw_request.append(f"[Binary data: {len(request.data)} bytes]")
    
    # Salvar em arquivo
    raw_content = "\n".join(raw_request)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(raw_content)
    
    # Também salvar versão JSON estruturada
    json_filename = filename.replace('.txt', '.json')
    
    # Capturar dados estruturados
    body_data = None
    body_raw = None
    if request.data:
        try:
            body_data = request.get_json()
        except:
            body_raw = request.data.decode('utf-8', errors='replace')
    
    form_data = dict(request.form) if request.form else None
    files_data = {key: value.filename for key, value in request.files.items()} if request.files else None
    
    structured_data = {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": request.url,
        "path": request.path,
        "query_string": request.query_string.decode('utf-8'),
        "headers": dict(request.headers),
        "client_ip": request.remote_addr,
        "body": {
            "json": body_data,
            "raw": body_raw,
            "form": form_data,
            "files": files_data
        }
    }
    
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        "message": "Requisição capturada com sucesso",
        "files": {
            "raw": filename,
            "json": json_filename
        },
        "timestamp": datetime.now().isoformat()
    }), 200

# Catch-all para qualquer outra rota
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    return jsonify({
        "message": f"Você acessou: /{path}",
        "method": request.method,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Servidor API Iniciado!")
    print("="*80)
    print("Disponível em:")
    print("  - http://localhost:5000")
    print("  - http://0.0.0.0:5000")
    print("  - http://[seu-ip-local]:5000")
    print("\nTodas as requisições serão exibidas no console.")
    print("Pressione Ctrl+C para parar o servidor.")
    print("="*80 + "\n")
    
    # Escutar em 0.0.0.0 para ficar acessível na rede interna
    app.run(host='0.0.0.0', port=5000, debug=True)
