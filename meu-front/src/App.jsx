import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useKeycloak } from '@react-keycloak/web';

const API_URL = 'http://127.0.0.1:5000/tarefas';

function App() {
  const { keycloak, initialized } = useKeycloak();
  const [tarefas, setTarefas] = useState([]);
  const [titulo, setTitulo] = useState('');
  const [descricao, setDescricao] = useState('');
  const [editandoId, setEditandoId] = useState(null);

  // Configura o interceptor do axios para incluir o token
  useEffect(() => {
    if (initialized) {
      axios.interceptors.request.use((config) => {
        if (keycloak.authenticated) {
          config.headers.Authorization = `Bearer ${keycloak.token}`;
        }
        return config;
      });
    }
  }, [initialized, keycloak]);

  useEffect(() => {
    if (initialized && keycloak.authenticated) {
      listarTarefas();
    }
  }, [initialized, keycloak.authenticated]);

  const listarTarefas = async () => {
    try {
      const res = await axios.get(API_URL);
      setTarefas(res.data);
    } catch (error) {
      console.error('Erro ao buscar tarefas', error);
      if (error.response?.status === 401) {
        keycloak.login(); // Redireciona para login se não autenticado
      }
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

  if (!initialized) {
    return <div>Carregando...</div>;
  }

  if (!keycloak.authenticated) {
    return (
      <div style={{ maxWidth: 600, margin: 'auto', padding: 20, textAlign: 'center' }}>
        <h1>Gerenciador de Tarefas</h1>
        <p>Você precisa estar logado para acessar esta aplicação</p>
        <button 
          onClick={() => keycloak.login()}
          style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}
        >
          Login
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Gerenciador de Tarefas</h1>
        <div>
          <span style={{ marginRight: '10px' }}>Olá, {keycloak.tokenParsed?.preferred_username || 'Usuário'}</span>
          <button 
            onClick={() => keycloak.logout()}
            style={{ padding: '5px 10px', cursor: 'pointer' }}
          >
            Logout
          </button>
        </div>
      </div>

      <div style={{ margin: '20px 0' }}>
        <input
          placeholder="Título"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
        />
        <textarea
          placeholder="Descrição"
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          rows={4}
          style={{ width: '100%', padding: '8px', marginBottom: '10px' }}
        />
        {editandoId ? (
          <button 
            onClick={atualizarTarefa}
            style={{ padding: '8px 16px', marginRight: '10px', cursor: 'pointer' }}
          >
            Atualizar Tarefa
          </button>
        ) : (
          <button 
            onClick={criarTarefa}
            style={{ padding: '8px 16px', marginRight: '10px', cursor: 'pointer' }}
          >
            Criar Tarefa
          </button>
        )}
        {editandoId && (
          <button 
            onClick={() => {
              setEditandoId(null);
              setTitulo('');
              setDescricao('');
            }}
            style={{ padding: '8px 16px', cursor: 'pointer' }}
          >
            Cancelar
          </button>
        )}
      </div>

      <hr />

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {tarefas.map((tarefa) => (
          <li 
            key={tarefa.id} 
            style={{ 
              padding: '15px', 
              margin: '10px 0', 
              border: '1px solid #ddd', 
              borderRadius: '4px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <strong style={{ fontSize: '18px' }}>{tarefa.titulo}</strong>
              <p style={{ margin: '5px 0 0 0' }}>{tarefa.descricao}</p>
            </div>
            <div>
              <button 
                onClick={() => iniciarEdicao(tarefa)}
                style={{ 
                  padding: '5px 10px', 
                  marginRight: '5px', 
                  cursor: 'pointer',
                  backgroundColor: '#f0f0f0',
                  border: '1px solid #ccc'
                }}
              >
                Editar
              </button>
              <button 
                onClick={() => deletarTarefa(tarefa.id)}
                style={{ 
                  padding: '5px 10px', 
                  cursor: 'pointer',
                  backgroundColor: '#ffebee',
                  border: '1px solid #ffcdd2'
                }}
              >
                Excluir
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;