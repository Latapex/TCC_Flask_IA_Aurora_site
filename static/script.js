const messages = document.getElementById('messages');
const promptEl = document.getElementById('prompt');
const sendBtn = document.getElementById('send');
const clearBtn = document.getElementById('clear');

// 1. NOVO: Variável para armazenar o ID da sessão
let currentSessionId = null;


function addMessage(text, who) {
    const div = document.createElement('div');
    div.className = `msg ${who}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}


async function sendMessage() {
    const text = promptEl.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    promptEl.value = '';
    sendBtn.disabled = true;

    // 2. NOVO: Prepara os dados para incluir a mensagem e o ID da sessão
    const bodyData = {
        message: text,
        // Envia o ID atual (será null se for a primeira mensagem)
        session_id: currentSessionId 
    };

    const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        // 3. NOVO: Envia o objeto bodyData
        body: JSON.stringify(bodyData)
    });

    const data = await resp.json();

    // 4. NOVO: Armazena o ID retornado pelo servidor
    if (data.session_id) {
        currentSessionId = data.session_id; 
    }

    if (data.reply) addMessage(data.reply, 'bot');
    else addMessage('Erro ao obter resposta.', 'bot');

    sendBtn.disabled = false;
}


sendBtn.addEventListener('click', sendMessage);
promptEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});


clearBtn.addEventListener('click', () => {
    messages.innerHTML = '';
    addMessage('Conversa iniciada.', 'bot');
    // 5. NOVO: Limpa o ID da sessão ao iniciar uma nova conversa
    currentSessionId = null;
});