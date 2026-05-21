import streamlit as st

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning & Translation", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. INTERFACCIA UTENTE ---
st.title("Imprendo - Corsi in Multilingua")

# --- 3. LOGICA DI ASCOLTO CONTINUO CON BANNER MULTI-RIGA ---
st.write("")

import streamlit.components.v1 as components

# Blocco unico HTML/JS: garantisce lo spazio visivo fisso per 3 righe per lingua
js_speech_component = """
<div style="font-family: sans-serif; margin-bottom: 5px;">
    <div id="caption-banner" style="
        background-color: #111111;
        padding: 24px;
        border-radius: 12px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        line-height: 1.4;
        border: 2px solid #333333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        overflow: hidden;
        word-wrap: break-word;
    ">
        <div id="text-it" style="
            color: #00FF66; 
            font-size: 32px; 
            margin-bottom: 16px;
            min-height: 135px;
            max-height: 135px;
            overflow-y: auto;
        ">In attesa che il docente inizi a parlare... Il testo in italiano occuperà fino a tre righe prima di sostituirsi.</div>
        
        <div id="text-en" style="
            color: #FFCC00; 
            font-size: 24px; 
            font-style: italic; 
            border-top: 1px solid #222; 
            padding-top: 12px;
            min-height: 100px;
            max-height: 100px;
            overflow-y: auto;
        ">The English translation will appear here and will occupy up to three lines.</div>
    </div>

    <div style="color: #888888; font-size: 14px; padding: 12px; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e;">
        <div>
            <span id="status-dot" style="height: 10px; width: 10px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
            <span id="status-text" style="color: #aaaaaa; font-weight: 500;">Microfono spento. Clicca sul pulsante per attivare l'ascolto bilingue (max 3 righe).</span>
        </div>
        <button id="start-btn" style="padding: 10px 20px; background-color: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s;">🎯 AVVIA ASCOLTO CONTINUO</button>
    </div>
</div>

<script>
    const startBtn = document.getElementById('start-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const textItDiv = document.getElementById('text-it');
    const textEnDiv = document.getElementById('text-en');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        statusText.innerText = "Errore: Browser non supportato. Usa Google Chrome o Microsoft Edge.";
        startBtn.style.display = 'none';
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'it-IT';

        let isRecognizing = false;

        async function traduciInInglese(testo) {
            if (!testo.trim()) return '';
            try {
                const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=it&tl=en&dt=t&q=${encodeURIComponent(testo)}`);
                const data = await response.json();
                return data[0].map(item => item[0]).join('');
            } catch (error) {
                return 'Translation...';
            }
        }

        startBtn.addEventListener('click', () => {
            if (!isRecognizing) {
                recognition.start();
            } else {
                window.autoRestartEnabled = false;
                recognition.stop();
            }
        });

        recognition.onstart = () => {
            isRecognizing = true;
            window.autoRestartEnabled = true;
            statusDot.style.background = "#2ecc71";
            statusText.innerText = "Microfono ATTIVO. Il testo si sostituisce ad ogni nuova frase occupando fino a 3 righe.";
            startBtn.innerText = "⏹️ FERMA ASCOLTO";
            startBtn.style.backgroundColor = "#e74c3c";
        };

        recognition.onend = () => {
            isRecognizing = false;
            if (window.autoRestartEnabled) {
                recognition.start();
            } else {
                statusDot.style.background = "#e74c3c";
                statusText.innerText = "Microfono disattivato manualmente.";
                startBtn.innerText = "🎯 AVVIA ASCOLTO CONTINUO";
                startBtn.style.backgroundColor = "#2ecc71";
            }
        };

        let translationTimeout;

        recognition.onresult = (event) => {
            let fraseCorrenteIt = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                fraseCorrenteIt = event.results[i][0].transcript.trim();
            }
            
            if (fraseCorrenteIt.length > 0) {
                textItDiv.innerText = fraseCorrenteIt;
                textItDiv.scrollTop = textItDiv.scrollHeight;
            }

            clearTimeout(translationTimeout);
            translationTimeout = setTimeout(async () => {
                if (fraseCorrenteIt.length > 0) {
                    const traduzioneEn = await traduciInInglese(fraseCorrenteIt);
                    textEnDiv.innerText = traduzioneEn;
                    textEnDiv.scrollTop = textEnDiv.scrollHeight;
                }
            }, 300);
        };
    }
</script>
"""

# Portato l'height dell'iFrame a 480px per garantire che il banner da 3+3 righe 
# e la barra dei controlli verde siano totalmente visibili senza tagli di pixel
components.html(js_speech_component, height=480)
