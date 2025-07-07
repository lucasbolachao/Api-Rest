from flask import Flask, request, jsonify
from functools import wraps
import uuid
import jwt
import requests
from jwt.algorithms import RSAAlgorithm

app = Flask(__name__)

# Configurações do Keycloak
KEYCLOAK_URL = 'http://localhost:8080'
REALM = 'meu_realm'
CLIENT_ID = 'meu-backend'

# Armazenamento em memória (substitua por um banco de dados em produção)
tarefas = []

# Cache para a chave pública
public_key = None

def get_public_key():
    global public_key
    if not public_key:
        jwks_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
        response = requests.get(jwks_url)
        jwks = response.json()
        public_key = RSAAlgorithm.from_jwk(jwks['keys'][0])
    return public_key

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token foi enviado no header Authorization
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
        
        if not token:
            return jsonify({'message': 'Token de acesso não fornecido!'}), 401
            
        try:
            # Decodifica e valida o token
            decoded_token = jwt.decode(
                token,
                get_public_key(),
                algorithms=['RS256'],
                audience=CLIENT_ID,
                options={'verify_exp': True}
            )
            # Adiciona as informações do usuário ao contexto da requisição
            request.user_info = {
                'user_id': decoded_token.get('sub'),
                'username': decoded_token.get('preferred_username'),
                'email': decoded_token.get('email'),
                'roles': decoded_token.get('realm_access', {}).get('roles', [])
            }
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated

@app.route('/tarefas', methods=['GET'])
@token_required
def listar_tarefas():
    # Filtro opcional por status
    status = request.args.get('status')
    if status:
        tarefas_filtradas = [t for t in tarefas if t['status'] == status]
        return jsonify(tarefas_filtradas)
    return jsonify(tarefas)

@app.route('/tarefas/<tarefa_id>', methods=['GET'])
@token_required
def buscar_tarefa(tarefa_id):
    tarefa = next((t for t in tarefas if t['id'] == tarefa_id), None)
    if tarefa:
        return jsonify(tarefa)
    return jsonify({'message': 'Tarefa não encontrada'}), 404

@app.route('/tarefas', methods=['POST'])
@token_required
def adicionar_tarefa():
    data = request.get_json()
    if not data or 'titulo' not in data:
        return jsonify({'message': 'Título é obrigatório'}), 400
        
    nova_tarefa = {
        'id': str(uuid.uuid4()),
        'titulo': data['titulo'],
        'descricao': data.get('descricao', ''),
        'status': 'pendente',
        'criado_por': request.user_info['username']  # Registra quem criou a tarefa
    }
    tarefas.append(nova_tarefa)
    return jsonify(nova_tarefa), 201

@app.route('/tarefas/<tarefa_id>', methods=['PUT'])
@token_required
def atualizar_tarefa(tarefa_id):
    data = request.get_json()
    tarefa = next((t for t in tarefas if t['id'] == tarefa_id), None)
    
    if not tarefa:
        return jsonify({'message': 'Tarefa não encontrada'}), 404
        
    # Verifica se o usuário pode editar (criador ou admin)
    if tarefa.get('criado_por') != request.user_info['username'] and 'admin' not in request.user_info['roles']:
        return jsonify({'message': 'Você não tem permissão para editar esta tarefa'}), 403
    
    tarefa['titulo'] = data.get('titulo', tarefa['titulo'])
    tarefa['descricao'] = data.get('descricao', tarefa['descricao'])
    tarefa['status'] = data.get('status', tarefa['status'])
    
    return jsonify(tarefa)

@app.route('/tarefas/<tarefa_id>', methods=['DELETE'])
@token_required
def deletar_tarefa(tarefa_id):
    tarefa = next((t for t in tarefas if t['id'] == tarefa_id), None)
    
    if not tarefa:
        return jsonify({'message': 'Tarefa não encontrada'}), 404
        
    # Verifica se o usuário pode deletar (criador ou admin)
    if tarefa.get('criado_por') != request.user_info['username'] and 'admin' not in request.user_info['roles']:
        return jsonify({'message': 'Você não tem permissão para deletar esta tarefa'}), 403
    
    tarefas.remove(tarefa)
    return jsonify({'message': 'Tarefa deletada com sucesso'})

if __name__ == '__main__':
    app.run(debug=True)