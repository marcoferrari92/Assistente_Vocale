import streamlit as st

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning & Translation", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. DIZIONARIO LINGUE SUPPORTATE ---
# Mappa il nome visualizzato con il codice di riconoscimento (BCP 47) e il codice di traduzione (ISO 639-1)
DIZ_LINGUE = {
    "Italiano": {"speech": "it-IT", "trans": "it"},
    "English (Inglese)": {"speech": "en-US", "trans": "en"},
    "Español (Spagnolo)": {"speech": "es-ES", "trans": "es"},
    "Français (Francese)": {"speech": "fr-FR", "trans": "fr"},
    "Deutsch (Tedesco)": {"speech": "de-DE", "trans": "de"}
}

# --- 3. CONFIGURAZIONE LINGUE IN BARRA LATERALE ---
st.sidebar.title("⚙️ Impostazioni Lingua")
st.sidebar.write("Configura le lingue per il corso in tempo reale:")

lingua_parlata_nome = st.sidebar.selectbox(
    "🎙️ Lingua Parlata (Docente):", 
    options=list(DIZ_LINGUE.keys()), 
    index=0  # Default: Italiano
)

lingua_traduzione_nome = st.sidebar.selectbox(
    "🔤 Lingua Traduzione (Sottotitoli inferiori):", 
    options=list(DIZ_LINGUE.keys()), 
    index=1  # Default: Inglese
)

# Estrazione dei codici tecnici da passare a JavaScript
codice_ascolto = DIZ_LINGUE[lingua_parlata_nome]["speech"]
codice_da = DIZ_LINGUE[lingua_parlata_nome]["trans"]
codice_a = DIZ_LINGUE[lingua_traduzione_nome]["trans"]

# --- 4. INTERFACCIA UTENTE PRINCIPALE ---
st.title("Imprendo - Corsi in Multilingua")

# --- 5. LOGICA DI ASCOLTO CONTINUO CON BANNER REATTIVO ---
st.write("")

import streamlit.components.v1 as components

# Iniezione dinamica dei codici lingua scelti nei parametri JS (lang_speech, lang_from, lang_to)
js_speech_component = f"""
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
        ">In attesa che il docente inizi a parlare... [{lingua_parlata_nome}]</div>
        
        <div id="text-en" style="
            color: #FFCC00; 
            font-size: 24px; 
            font-style: italic; 
            border-top: 1px solid #222; 
            padding-top: 12px;
            min-height: 100px;
            max-height: 100px;
            overflow-y: auto;
        ">La traduzione simultanea comparirà qui. [{lingua_traduzione_nome}]</div>
    </div>

    <div style="color: #888888; font-size: 14px; padding: 12px; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e;">
        <div>
            <span id="status-dot" style="height: 10px; width: 10px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
            <span id="status-text" style="color: #aaaaaa; font-weight: 500;">Microfono spento. Clicca per attivare l'ascolto continuo ({lingua_parlata_nome} ➔ {lingua_traduzione_nome}).</span>
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
    
    // Configurazione variabili passate dinamiche da Streamlit
    const langSpeech = "{codice_ascolto}";
    const langFrom = "{codice_da}";
    const langTo = "{codice_a}";
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        statusText.innerText = "Errore: Browser non supportato. Usa Google Chrome o Microsoft Edge.";
        startBtn.style.display = 'none';
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = langSpeech;

        let isRecognizing = false;

        async function traduciTesto(testo) {
            if (!testo.trim()) return '';
            // Se la lingua parlata e quella di destinazione sono identiche, evita la chiamata API
            if (langFrom === langTo) return testo;
            
            try {
                const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=${{langFrom}}&tl=${{langTo}}&dt=t&q=${{encodeURIComponent(testo)}}`);
                const data = await response.json();
                return data[0].map(item => item[0]).join('');
            } catch (error) {
                return 'Translation error...';
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
            statusText.innerText = "Microfono ATTIVO. Riconoscimento e traduzione fluidi impostati su 3 righe max.";
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
            let fraseCorrente = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                fraseCorrente = event.results[i][0].transcript.trim();
            }
            
            if (fraseCorrente.length > 0) {
                textItDiv.innerText = fraseCorrente;
                textItDiv.scrollTop = textItDiv.scrollHeight;
            }

            clearTimeout(translationTimeout);
            translationTimeout = setTimeout(async () => {
                if (fraseCorrente.length > 0) {
                    const traduzione = await traduciTesto(fraseCorrente);
                    textEnDiv.innerText = traduzione;
                    textEnDiv.scrollTop = textEnDiv.scrollHeight;
                }
            }, 300);
        };
    }
</script>
"""

# Rendering dell'interfaccia a 480px per mantenere l'assenza totale di tagli grafici
components.html(js_speech_component, height=480)
