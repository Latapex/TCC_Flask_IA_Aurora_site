from flask import Flask, render_template, request, jsonify
import os
import datetime
import json
import uuid  
from google import genai
# NOVO: Importa a função load_dotenv para carregar o arquivo .env
from dotenv import load_dotenv 
import PyPDF2
import docx

# NOVO: Carrega as variáveis de ambiente do arquivo .env
load_dotenv() 

# NOVO: Obtém a chave da variável de ambiente GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# =========================================================================
# Verificação de Segurança
if not GEMINI_API_KEY:
    # Lança um erro se a chave não estiver configurada, garantindo que o servidor não inicie sem credenciais.
    raise ValueError("A chave de API GEMINI_API_KEY não foi encontrada nas variáveis de ambiente. Verifique seu arquivo .env ou a configuração do Render.")
# =========================================================================

app = Flask(__name__)

# =========================
#   CONFIG GERAL
# =========================
MEMORY_DIR = "memory"
TRAINING_DIR = "training_data"

os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(TRAINING_DIR, exist_ok=True)


# =========================
#   CARREGAR MEMÓRIA POR ID
# =========================
def load_memory(session_id):
    """Carrega o histórico de conversa de um arquivo JSON específico."""
    file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"ERRO ao carregar memória de {file_path}: {e}")
            return []
    return []


# =========================
#   SALVAR MEMÓRIA POR ID
# =========================
def save_memory(session_id, conversation_history):
    """Salva (ou sobrescreve) o histórico de conversa completo em um único arquivo JSON."""
    file_path = os.path.join(MEMORY_DIR, f"{session_id}.json")
    
    if not isinstance(conversation_history, list):
        print(f"ERRO: Tentativa de salvar memória sem histórico válido para ID {session_id}")
        return

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=4)
        print(f"Memória salva/atualizada com sucesso em: {file_path}")
    except Exception as e:
        print(f"ERRO ao salvar memória em JSON para ID {session_id}: {e}")


# =========================
#   CARREGAR TREINAMENTO
# =========================
def load_training_material():
    """Lê todos os arquivos dentro de training_data e retorna um texto concatenado."""
    combined_text = ""
    for file_name in os.listdir(TRAINING_DIR):
        path = os.path.join(TRAINING_DIR, file_name)

        if file_name.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                combined_text += f"\n---[TXT] {file_name}---\n" + f.read()

        elif file_name.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                combined_text += f"\n---[JSON] {file_name}---\n" + f.read()

        elif file_name.endswith(".pdf"):
            try:
                # É necessário ter PyPDF2 instalado
                pdf = PyPDF2.PdfReader(path)
                text = "\n".join([page.extract_text() for page in pdf.pages])
                combined_text += f"\n---[PDF] {file_name}---\n" + text
            except Exception as e:
                combined_text += f"\n---[PDF] {file_name} NÃO PÔDE SER LIDO---\n"

        elif file_name.endswith(".docx"):
            try:
                # É necessário ter python-docx instalado
                doc = docx.Document(path)
                text = "\n".join([p.text for p in doc.paragraphs])
                combined_text += f"\n---[DOCX] {file_name}---\n" + text
            except Exception as e:
                combined_text += f"\n---[DOCX] {file_name} NÃO PÔDE SER LIDO---\n"

        else:
            combined_text += f"\n---[ARQUIVO NÃO SUPORTADO] {file_name}---\n"

    return combined_text


# =========================
#   GEMINI FLASH (USA O HISTÓRICO COMPLETO)
# =========================
def call_gemini(full_history):
    """Envia mensagens ao Gemini Flash, incluindo o histórico completo e base de conhecimento."""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY) 
        training_data = load_training_material()
        
        system_instruction_text = (
            "Você é um atendente virtual educado, direto e eficiente. "
            "Use a Base de Conhecimento fornecida para responder à pergunta. "
            "Se o histórico de conversa for longo, concentre-se nas informações mais recentes."
        )

        contents = []
        
        # 1. Converter o histórico simples para o formato de API do Gemini
        for turn in full_history:
             contents.append(
                {"role": turn["role"], "parts": [{"text": turn["content"]}]}
            )
            
        # 2. Injetar o contexto de treinamento e a instrução no PRIMEIRO turno de USER
        if contents and contents[0]['role'] == 'user':
            first_user_content = contents[0]['parts'][0]['text']
            
            full_context_prompt = (
                system_instruction_text + 
                f"\n\n--- Base de Conhecimento ---\n{training_data}\n--------------------------\n\n" + 
                first_user_content
            )
            
            contents[0]['parts'][0]['text'] = full_context_prompt
        
        # 3. Chamar o modelo com o histórico completo
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )

        return response.text

    except Exception as e:
        print(f"ERRO ao chamar Gemini: {e}")
        return "Desculpe, ocorreu um erro ao comunicar com o assistente virtual."


# =========================
#   ROTAS
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    # 1. LER DADOS E ID DE SESSÃO
    data = request.get_json() 
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", None) 

    if not user_msg:
        return jsonify({"reply": "Por favor, envie uma mensagem válida."}), 400

    # 2. GERENCIAR SESSÃO/HISTÓRICO
    if session_id:
        conversation_history = load_memory(session_id)
    else:
        session_id = str(uuid.uuid4())
        conversation_history = []
        
    # 3. ADICIONAR NOVA MENSAGEM DO USUÁRIO AO HISTÓRICO
    conversation_history.append({"role": "user", "content": user_msg})

    # 4. CHAMAR GEMINI COM O HISTÓRICO COMPLETO
    reply = call_gemini(conversation_history)

    # 5. ADICIONAR RESPOSTA DO BOT AO HISTÓRICO
    conversation_history.append({"role": "model", "content": reply})

    # 6. SALVAR MEMÓRIA
    save_memory(session_id, conversation_history)

    # 7. RETORNAR RESPOSTA E O ID DA SESSÃO
    return jsonify({"reply": reply, "session_id": session_id})


# =========================
#   INICIAR SERVIDOR
# =========================
if __name__ == "__main__":
    # Configuração dinâmica da porta e host para deploy (Render/outros) e fallback local
    port = int(os.environ.get("PORT", 10000))
    # '0.0.0.0' garante que o servidor escute em todas as interfaces, necessário para deploy
    app.run(host='0.0.0.0', port=port, debug=False)
