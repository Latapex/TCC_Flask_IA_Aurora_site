# TCC_Flask_IA_Aurora_site
# 🤖 Assistente Virtual com Memória e Base de Conhecimento (Gemini Flash)

Este projeto implementa um chatbot baseado em Python com Flask, utilizando a API do Google Gemini (modelo Flash) para processamento de linguagem natural. O diferencial é a **persistência de conversas** (memória por sessão) e a capacidade de responder perguntas baseadas em uma **base de conhecimento customizável** carregada a partir de diversos tipos de arquivos.

## 🚀 Funcionalidades Principais

*   **Memória de Sessão:** Mantém o histórico de conversas salvo em arquivos JSON, permitindo que o assistente se lembre do contexto anterior dentro da mesma sessão.
*   **Base de Conhecimento Customizável:** Carrega e concatena informações de arquivos `.txt`, `.json`, `.pdf` e `.docx` localizados na pasta `training_data`.
*   **Contextualização com Gemini Flash:** A base de conhecimento e a instrução do sistema são injetadas como contexto inicial na primeira pergunta de cada sessão, garantindo respostas informadas.
*   **Interface Web Simples:** Uma interface básica via Flask e HTML/CSS/JS para interação direta.
*   **Segurança:** Utiliza variáveis de ambiente (`.env`) para armazenar a chave da API do Gemini.

## 📂 Estrutura do Projeto
.
├── app.py # Aplicação Flask principal e lógica do backend.
├── requirements.txt # Dependências necessárias para rodar o projeto.
├── .env # (Local, não versionado) Armazena a GEMINI_API_KEY.
├── memory/ # Diretório para salvar os arquivos de histórico (.json).
├── training_data/ # Diretório onde os arquivos de conhecimento são lidos.
│ ├── treinamento.txt
│ ├── produtos.txt
│ ├── info.txt
│ ├── treinamento_hornets_aurora.txt
│ ├── info-mercado.txt
│ ├── perguntar-freq.txt
│ └── atendimento.txt
├── static/
│ ├── script.js # Lógica JavaScript do frontend (gerenciamento de sessão).
│ ├── style.css # Estilização da interface do chat.
│ └── img/
│ └── perfil.jpg # Imagem de perfil do bot (Aurora AI).
├── templates/
│ └── index.html # Template HTML da interface do chat.
└── README.md # Este arquivo.

## 🛠️ Pré-requisitos

Você precisa ter o Python instalado (versão 3.7+ recomendada).

## ⚙️ Configuração e Execução

### 1. Instalar Dependências

Crie um ambiente virtual e instale as bibliotecas listadas no `requirements.txt`:

```bash
# 1. Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate   # No Windows

# 2. Instale as dependências
pip install -r requirements.txt

2. Configurar a Chave da API
Crie um arquivo chamado .env na raiz do projeto e adicione sua chave da API do Gemini:
GEMINI_API_KEY="SUA_CHAVE_AQUI"

3. Iniciar a Aplicação
Execute o arquivo app.py:
python app.py

O servidor estará acessível em http://0.0.0.0:10000 (ou na porta definida pela variável de ambiente PORT).

4. Interação com a Interface
Acesse a URL no seu navegador.
Nova Conversa: Clique em Limpar para iniciar uma nova sessão e gerar um novo session_id.
Continuar Conversa: Se o session_id for mantido, o histórico será carregado do disco.
📚 Base de Conhecimento
O sistema lê todos os arquivos com extensões suportadas (.txt, .json, .pdf, .docx) dentro da pasta training_data/ e os concatena em um grande bloco de texto que serve como contexto para o Gemini.
Arquivos de Treinamento Utilizados:
treinamento.txt
produtos.txt
info.txt
treinamento_hornets_aurora.txt
info-mercado.txt
perguntar-freq.txt
atendimento.txt
⚠️ Observações Importantes
Gemini API Key: A aplicação falhará ao iniciar se a variável de ambiente GEMINI_API_KEY não estiver definida, garantindo que o custo de API não seja acidentalmente incorrido.
Modelagem de Histórico: O call_gemini trata o histórico de conversas como mensagens sequenciais enviadas ao modelo. A instrução do sistema e a base de conhecimento são injetadas apenas na primeira mensagem do usuário da sessão para otimizar o uso do contexto e seguir a arquitetura de RAG (Retrieval-Augmented Generation) simples.
Bibliotecas de Documentos: Para ler arquivos .pdf e .docx, as bibliotecas PyPDF2 e python-docx são necessárias, conforme listado em requirements.txt.
