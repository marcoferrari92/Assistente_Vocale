import streamlit as st

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning per Non Udenti", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. STILE CSS PERSONALIZZATO PER IL BANNER ---
st.markdown("""
    <style>
    .caption-banner {
        background-color: #111111;
        color: #00FF66; /* Verde fluo ad altissima visibilità */
        padding: 24px;
        border-radius: 12px;
        font-size: 32px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        line-height: 1.5;
        min-height: 180px;
        margin-bottom: 20px;
        border: 2px solid #333333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .instruction-text {
        font-size: 18px;
        color: #888888;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. INIZIALIZZAZIONE STATO ---
if "cronologia_trascrizione" not in st.session_state:
    st.session_state.cronologia_trascrizione = []

# --- 4. INTERFACCIA UTENTE ---
st.title("🧏 Morpheus Live Subtitles")
st.write("Sottotitoli automatici ad alta visibilità per l'ascolto delle lezioni")
st.divider()

# Area del Banner di Sottotitolazione
placeholder_banner = st.empty()

# Gestione testo da visualizzare sul Banner principale
if st.session_state.cronologia_trascrizione:
    testo_visualizzato = st.session_state.cronologia_trascrizione[-1]
else:
    testo_visualizzato = "In attesa che il docente inizi a parlare... Il testo comparirà qui."

placeholder_banner.markdown(
    f'<div class="caption-banner">{testo_visualizzato}</div>', 
    unsafe_allow_html=True
)

# --- 5. LOGICA DI ASCOLTO CONTINUO (JAVASCRIPT EMBED) ---
st.write("### 🎙️ Stato Microfono Continuo")

# Riceve i dati inviati dal componente JavaScript personalizzato
# Nota: La Web Speech API usa i modelli vocali locali del browser (es. Google Speech su Chrome)
import streamlit.components.v1 as components

# Script HTML/JS per gestire il microfono sempre attivo
js_speech_component = """
<div style="font-family: sans-serif; color: #888888; font-size: 14px; padding: 10px; border: 1px dashed #333; border-radius: 8px;">
    <span id="status-dot" style="height: 10px; width: 10px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
    <span id="status-text">Microfono spento. Clicca sul pulsante per attivare l'ascolto continuo.</span>
    <br><br>
    <button id="start-btn" style="padding: 10px 20px; background-color: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">🎯 AVVIA ASCOLTO CONTINUO</button>
</div>

<script>
    const startBtn = document.getElementById('start-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    
    // Verifica supporto browser
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        statusText.innerText = "Errore: Il tuo browser non supporta il riconoscimento vocale continuo. Usa Google Chrome o Microsoft Edge.";
        startBtn.style.display = 'none';
    } else {
        const recognition = new SpeechRecognition();
        
        // Impostazioni per ascolto continuo senza interruzioni
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'it-IT';

        let isRecognizing = false;

        startBtn.addEventListener('click', () => {
            if (!isRecognizing) {
                recognition.start();
            } else {
                recognition.stop();
            }
        });

        recognition.onstart = () => {
            isRecognizing = true;
            statusDot.style.background = "#2ecc71";
            statusText.innerText = "Microfono ATTIVO in modalità continua. Il docente può parlare liberamente.";
            startBtn.innerText = "⏹️ FERMA ASCOLTO";
            startBtn.style.backgroundColor = "#e74c3c";
        };

        recognition.onend = () => {
            isRecognizing = false;
            statusDot.style.background = "#e74c3c";
            statusText.innerText = "Microfono disattivato.";
            startBtn.innerText = "🎯 AVVIA ASCOLTO CONTINUO";
            startBtn.style.backgroundColor = "#2ecc71";
            
            // Auto-restart di sicurezza se si disconnette durante la lezione
            if(window.autoRestartEnabled) {
                recognition.start();
            }
        };

        recognition.onresult = (event) => {
            // Prende l'ultimo blocco di testo elaborato dopo una pausa naturale
            const lastResultIndex = event.results.length - 1;
            const textOutput = event.results[lastResultIndex][0].transcript.trim();
            
            if (textOutput.length > 0) {
                // Invia la stringa di testo direttamente a Streamlit simulando un cambio di stato
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: textOutput
                }, '*');
            }
        };
        
        // Mantieni attivo il microfono anche se il docente fa pause lunghe
        window.autoRestartEnabled = true;
    }
</script>
"""

# Renderizziamo il microfono JS invisibile/indipendente dal ciclo di Streamlit
# Altezza minima di sicurezza per mostrare i controlli di avvio
audio_data = components.html(js_speech_component, height=110)

# Se JavaScript rileva una nuova frase, la inserisce nello stato senza perdere il focus del mic
if audio_data:
    # Evitiamo duplicati se la pagina si refresha rapidamente
    if not st.session_state.cronologia_trascrizione or st.session_state.cronologia_trascrizione[-1] != audio_data:
        st.session_state.cronologia_trascrizione.append(audio_data)
        st.rerun()

# --- 6. CRONOLOGIA COMPLETA DELLA LEZIONE ---
st.divider()
with st.expander("📝 Guarda l'intera trascrizione della lezione (Storico Frasi)"):
    if st.session_state.cronologia_trascrizione:
        testo_completo = " ".join(st.session_state.cronologia_trascrizione)
        st.write(testo_completo)
        
        if st.button("🗑️ Cancella Storico Lezione"):
            st.session_state.cronologia_trascrizione = []
            st.rerun()
    else:
        st.info("Nessun testo registrato nello storico per ora.")
