from flask import Flask, jsonify, request
from flask_cors import CORS
import script
from keycloak import KeycloakOpenID
import uuid

app = Flask(__name__)
CORS(app)

# Configuração do Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/",  # Ou "http://keycloak:8080/" se estiver no Docker
    client_id="backend-service",          # Client ID no Keycloak (confidential)
    realm_name="tarefas-app",
    client_secret_key="SUA_CHAVE_SECRETA",  # Gerada no Keycloak
    verify=False
)

def verificar_token(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'erro': 'Token de acesso não fornecido'}), 401
            
        token = auth_header.split(" ")[1]
        
        try:
            # Verifica e decodifica o token
            token_info = keycloak_openid.introspect(token)
            
            if not token_info['active']:
                return jsonify({'erro': 'Token inválido ou expirado'}), 401
                
            # Adiciona informações do usuário ao request
            request.user_info = {
                'user_id': token_info.get('sub'),
                'username': token_info.get('preferred_username'),
                'email': token_info.get('email'),
                'roles': token_info.get('realm_access', {}).get('roles', [])
            }
            
        except Exception as e:
            return jsonify({'erro': 'Falha na verificação do token', 'detalhes': str(e)}), 401
            
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/tarefas', methods=['GET'])
@verificar_token
def get_tarefas():
    try:
        # Filtro opcional por status
        status = request.args.get('status')
        tarefas = script.listar_tarefas()
        
        if status:
            tarefas = [t for t in tarefas if t['status'] == status]
            
        return jsonify(tarefas), 200
    except Exception as e:
        return jsonify({'erro': 'Erro ao buscar tarefas', 'detalhes': str(e)}), 500

@app.route('/tarefas', methods=['POST'])
@verificar_token
def criar_tarefa():
    try:
        data = request.get_json()
        
        if not data or 'titulo' not in data:
            return jsonify({'erro': 'Título é obrigatório'}), 400
            
        nova_tarefa = script.adicionar_tarefa(
            titulo=data['titulo'],
            descricao=data.get('descricao', ''),
            criado_por=request.user_info['username']  # Registra quem criou
        )
        
        return jsonify(nova_tarefa), 201
    except Exception as e:
        return jsonify({'erro': 'Erro ao criar tarefa', 'detalhes': str(e)}), 500

@app.route('/tarefas/<tarefa_id>', methods=['GET'])
@verificar_token
def get_tarefa(tarefa_id):
    try:
        tarefa = script.buscar_tarefa(tarefa_id)
        if tarefa:
            return jsonify(tarefa), 200
        return jsonify({'erro': 'Tarefa não encontrada'}), 404
    except Exception as e:
        return jsonify({'erro': 'Erro ao buscar tarefa', 'detalhes': str(e)}), 500

@app.route('/tarefas/<tarefa_id>', methods=['PUT'])
@verificar_token
def atualizar_tarefa(tarefa_id):
    try:
        tarefa = script.buscar_tarefa(tarefa_id)
        if not tarefa:
            return jsonify({'erro': 'Tarefa não encontrada'}), 404
            
        # Verifica permissão (criador ou admin)
        if tarefa.get('criado_por') != request.user_info['username'] and 'admin' not in request.user_info['roles']:
            return jsonify({'erro': 'Acesso não autorizado'}), 403
            
        data = request.get_json()
        tarefa_atualizada = script.atualizar_tarefa(
            tarefa_id=tarefa_id,
            titulo=data.get('titulo'),
            descricao=data.get('descricao'),
            status=data.get('status')
        )
        
        return jsonify(tarefa_atualizada), 200
    except Exception as e:
        return jsonify({'erro': 'Erro ao atualizar tarefa', 'detalhes': str(e)}), 500

@app.route('/tarefas/<tarefa_id>', methods=['DELETE'])
@verificar_token
def deletar_tarefa(tarefa_id):
    try:
        tarefa = script.buscar_tarefa(tarefa_id)
        if not tarefa:
            return jsonify({'erro': 'Tarefa não encontrada'}), 404
            
        # Verifica permissão (criador ou admin)
        if tarefa.get('criado_por') != request.user_info['username'] and 'admin' not in request.user_info['roles']:
            return jsonify({'erro': 'Acesso não autorizado'}), 403
            
        script.deletar_tarefa(tarefa_id)
        return jsonify({'mensagem': 'Tarefa deletada com sucesso'}), 200
    except Exception as e:
        return jsonify({'erro': 'Erro ao deletar tarefa', 'detalhes': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)