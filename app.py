from flask import Flask, jsonify, request
from flask_cors import CORS
import script

app = Flask(__name__)
CORS(app)

# Rota GET - listar todas as tarefas
@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    tarefas = script.listar_tarefas()
    return jsonify(tarefas), 200

# Rota GET - buscar tarefa por ID
@app.route('/tarefas/<tarefa_id>', methods=['GET'])
def get_tarefa(tarefa_id):
    tarefa = script.buscar_tarefa(tarefa_id)
    if tarefa:
        return jsonify(tarefa), 200
    return jsonify({'erro': 'Tarefa não encontrada'}), 404

# Rota POST - criar nova tarefa
@app.route('/tarefas', methods=['POST'])
def criar_tarefa():
    dados = request.json
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')
    if not titulo or not descricao:
        return jsonify({'erro': 'Título e descrição são obrigatórios'}), 400
    nova_tarefa = script.adicionar_tarefa(titulo, descricao)
    return jsonify(nova_tarefa), 201

# Rota PUT - atualizar tarefa
@app.route('/tarefas/<tarefa_id>', methods=['PUT'])
def atualizar_tarefa(tarefa_id):
    dados = request.json
    titulo = dados.get('titulo')
    descricao = dados.get('descricao')
    status = dados.get('status')
    tarefa = script.atualizar_tarefa(tarefa_id, titulo, descricao, status)
    if tarefa:
        return jsonify(tarefa), 200
    return jsonify({'erro': 'Tarefa não encontrada'}), 404

# Rota DELETE - excluir tarefa
@app.route('/tarefas/<tarefa_id>', methods=['DELETE'])
def deletar_tarefa(tarefa_id):
    tarefa = script.deletar_tarefa(tarefa_id)
    if tarefa:
        return jsonify({'mensagem': 'Tarefa deletada'}), 200
    return jsonify({'erro': 'Tarefa não encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True)
