import uuid

tarefas = []

def listar_tarefas():
    return tarefas

def buscar_tarefa(tarefa_id):
    for tarefa in tarefas:
        if tarefa['id'] == tarefa_id:
            return tarefa
    return None

def adicionar_tarefa(titulo, descricao):
    nova_tarefa = {
        'id': str(uuid.uuid4()),
        'titulo': titulo,
        'descricao': descricao,
        'status': 'pendente'
    }
    tarefas.append(nova_tarefa)
    return nova_tarefa

def atualizar_tarefa(tarefa_id, titulo, descricao, status):
    for tarefa in tarefas:
        if tarefa['id'] == tarefa_id:
            tarefa['titulo'] = titulo or tarefa['titulo']
            tarefa['descricao'] = descricao or tarefa['descricao']
            tarefa['status'] = status or tarefa['status']
            return tarefa
    return None

def deletar_tarefa(tarefa_id):
    for tarefa in tarefas:
        if tarefa['id'] == tarefa_id:
            tarefas.remove(tarefa)
            return tarefa
    return None
