import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/tarefas'; // seu backend Flask

function App() {
  const [tarefas, setTarefas] = useState([]);
  const [titulo, setTitulo] = useState('');
  const [descricao, setDescricao] = useState('');
  const [editandoId, setEditandoId] = useState(null);

  useEffect(() => {
    listarTarefas();
  }, []);

  const listarTarefas = async () => {
    try {
      const res = await axios.get(API_URL);
      setTarefas(res.data);
    } catch (error) {
      console.error('Erro ao buscar tarefas', error);
    }
  };

  const criarTarefa = async () => {
    try {
      await axios.post(API_URL, { titulo, descricao });
      setTitulo('');
      setDescricao('');
      listarTarefas();
    } catch (error) {
      console.error('Erro ao criar tarefa', error);
    }
  };

  const iniciarEdicao = (tarefa) => {
    setEditandoId(tarefa.id);
    setTitulo(tarefa.titulo);
    setDescricao(tarefa.descricao);
  };

  const atualizarTarefa = async () => {
    try {
      await axios.put(`${API_URL}/${editandoId}`, { titulo, descricao, status: 'pendente' });
      setTitulo('');
      setDescricao('');
      setEditandoId(null);
      listarTarefas();
    } catch (error) {
      console.error('Erro ao atualizar tarefa', error);
    }
  };

  const deletarTarefa = async (id) => {
    try {
      await axios.delete(`${API_URL}/${id}`);
      listarTarefas();
    } catch (error) {
      console.error('Erro ao deletar tarefa', error);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 20 }}>
      <h1>Gerenciador de Tarefas</h1>

      <input
        placeholder="Título"
        value={titulo}
        onChange={(e) => setTitulo(e.target.value)}
      />
      <br />
      <textarea
        placeholder="Descrição"
        value={descricao}
        onChange={(e) => setDescricao(e.target.value)}
        rows={4}
      />
      <br />

      {editandoId ? (
        <button onClick={atualizarTarefa}>Atualizar Tarefa</button>
      ) : (
        <button onClick={criarTarefa}>Criar Tarefa</button>
      )}

      <hr />

      <ul>
        {tarefas.map((tarefa) => (
          <li key={tarefa.id}>
            <strong>{tarefa.titulo}</strong> - {tarefa.descricao}{' '}
            <button onClick={() => iniciarEdicao(tarefa)}>Editar</button>{' '}
            <button onClick={() => deletarTarefa(tarefa.id)}>Excluir</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
