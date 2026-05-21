import streamlit as st

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning per Non Udenti", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .instruction-text {
        font-size: 18px;
        color: #888888;
    }
    /* Rende il box dell'expander più leggibile nel tema scuro/chiaro */
    .stAlert {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. INIZIALIZZAZIONE STATO ---
if "cronologia_trascrizione" not in st.session_state:
    st.session_state.cronologia_trascrizione = []

# --- 4. INTERFACCIA UTENTE ---
st.title("🧏 Morpheus Live Subtitles")
st.subheader("Sottotitoli automatici ad alta visibilità per l'ascolto delle lezioni")
st.divider()

# --- 5. LOGICA DI ASCOLTO CONTINUO ED ELABORAZIONE ---
st.write("### 🎙️ Stato Microfono Continuo")

import streamlit.components.v1 as components

# Unico blocco HTML/JS: gestisce il microfono, lo stato e il banner visivo direttamente nel browser
js_speech_component = """
<div style="font-family: sans-serif; margin-bottom: 15px;">
    <div id="caption-banner" style="
        background-color: #111111;
        color: #00FF66;
        padding: 24px;
        border-radius: 12px;
        font-size: 32px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        line-height: 1.5;
        min-height: 140px;
        max-height: 140px;
        margin-bottom: 20px;
        border: 2px solid #333333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        overflow-y: auto;
        word-wrap: break-word;
    ">In attesa che il docente inizi a parlare... Il testo comparirà qui in tempo reale.</div>

    <div style="color: #888888; font-size: 14px; padding: 12px; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e;">
        <div>
            <span id="status-dot" style="height: 10px; width: 10px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
            <span id="status-text" style="color: #aaaaaa; font-weight: 500;">Microfono spento. Clicca sul pulsante per attivare l'ascolto continuo.</span>
        </div>
        <button id="start-btn" style="padding: 10px 20px; background-color: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s;">🎯 AVVIA ASCOLTO CONTINUO</button>
    </div>
</div>

<script>
    const startBtn = document.getElementById('start-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const captionBanner = document.getElementById('caption-banner');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        statusText.innerText = "Errore: Browser non supportato. Usa Google Chrome o Microsoft Edge.";
        startBtn.style.display = 'none';
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true; // Mostra le parole in tempo reale mentre vengono pronunciate
        recognition.lang = 'it-IT';

        let isRecognizing = false;
        let finalTranscript = '';

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
            statusText.innerText = "Microfono ATTIVO. Il docente può parlare liberamente senza interruzioni.";
            startBtn.innerText = "⏹️ FERMA ASCOLTO";
            startBtn.style.backgroundColor = "#e74c3c";
        };

        recognition.onend = () => {
            isRecognizing = false;
            if (window.autoRestartEnabled) {
                // Auto-restart immediato se si disconnette per pause lunghe o timeout del browser
                recognition.start();
            } else {
                statusDot.style.background = "#e74c3c";
                statusText.innerText = "Microfono disattivato manualmente.";
                startBtn.innerText = "🎯 AVVIA ASCOLTO CONTINUO";
                startBtn.style.backgroundColor = "#2ecc71";
            }
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let currentFinalPhrase = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    const chunk = event.results[i][0].transcript.trim();
                    finalTranscript += chunk + ' ';
                    currentFinalPhrase = chunk;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            // Aggiorna visivamente il banner sul browser parola per parola
            let testoDaMostrare = finalTranscript + interimTranscript;
            if (testoDaMostrare.trim().length > 0) {
                captionBanner.innerText = testoDaMostrare;
                // Mantiene lo scroll automatico ancorato verso il basso
                captionBanner.scrollTop = captionBanner.scrollHeight;
            }

            // Invia la frase definitiva a Streamlit in background solo quando è consolidata
            if (currentFinalPhrase.length > 0) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: currentFinalPhrase
                }, '*');
            }
        };
    }
</script>
"""

# Renderizza il widget HTML/JS (Banner + Controlli). 
# Altezza impostata a 250px per contenere l'interfaccia senza scrollbar verticali esterne.
audio_data = components.html(js_speech_component, height=250)

# Cattura i dati inviati da JavaScript per aggiornare la cronologia di Streamlit
if audio_data:
    if not st.session_state.cronologia_trascrizione or st.session_state.cronologia_trascrizione[-1] != audio_data:
        st.session_state.cronologia_trascrizione.append(audio_data)

# --- 6. CRONOLOGIA COMPLETA DELLA LEZIONE ---
st.divider()
with st.expander("📝 Guarda l'intera trascrizione della lezione (Storico Frasi)"):
    if st.session_state.cronologia_trascrizione:
        testo_completo = " ... ".join(st.session_state.cronologia_trascrizione)
        st.write(testo_completo)
        
        st.write("")
        if st.button("🗑️ Cancella Storico Lezione", type="secondary"):
            st.session_state.cronologia_trascrizione = []
            st.rerun()
    else:
        st.info("Nessun testo registrato nello storico per ora.")
