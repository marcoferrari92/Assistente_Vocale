import streamlit as st

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning & Translation", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. INTERFACCIA UTENTE ---
st.title("🧏 Morpheus Live Subtitles & Translation")
st.subheader("Sottotitoli automatici e traduzione simultanea in inglese ad alta visibilità")
st.divider()

# --- 3. LOGICA DI ASCOLTO CONTINUO, TRADUZIONE ED ELABORAZIONE ---
st.write("### 🎙️ Stato Microfono Continuo")

import streamlit.components.v1 as components

# Blocco unico HTML/JS: gestisce microfono, traduzione e storico locale
js_speech_component = """
<div style="font-family: sans-serif; margin-bottom: 15px;">
    <!-- BANNER BILINGUE AD ALTO CONTRASTO -->
    <div id="caption-banner" style="
        background-color: #111111;
        padding: 24px;
        border-radius: 12px;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: bold;
        line-height: 1.6;
        min-height: 180px;
        max-height: 180px;
        margin-bottom: 20px;
        border: 2px solid #333333;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        overflow-y: auto;
        word-wrap: break-word;
    ">
        <div id="text-it" style="color: #00FF66; font-size: 32px; margin-bottom: 12px;">In attesa che il docente inizi a parlare... Il testo in italiano comparirà qui.</div>
        <div id="text-en" style="color: #FFCC00; font-size: 26px; font-style: italic; border-top: 1px solid #222; padding-top: 8px;">The English translation will appear here.</div>
    </div>

    <!-- CONTROLLI DI STATO E PULSANTE -->
    <div style="color: #888888; font-size: 14px; padding: 12px; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e; margin-bottom: 25px;">
        <div>
            <span id="status-dot" style="height: 10px; width: 10px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
            <span id="status-text" style="color: #aaaaaa; font-weight: 500;">Microfono spento. Clicca sul pulsante per attivare l'ascolto continuo bilingue.</span>
        </div>
        <button id="start-btn" style="padding: 10px 20px; background-color: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s;">🎯 AVVIA ASCOLTO CONTINUO</button>
    </div>

    <!-- STORICO DELLA LEZIONE (GESTITO LATO CLIENT PER EVITARE CRASH) -->
    <div style="margin-top: 20px;">
        <h4 style="color: #ffffff; margin-bottom: 10px;">📝 Storico Trascrizione Completa (Italiano & English)</h4>
        <div id="history-box" style="
            background-color: #1a1a1a;
            color: #dddddd;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #333;
            height: 250px;
            overflow-y: auto;
            font-size: 16px;
            line-height: 1.6;
        "><i style="color: #666;">Lo storico della lezione verrà generato automaticamente man mano che si consolideranno le frasi...</i></div>
        <button id="clear-btn" style="margin-top: 10px; padding: 6px 12px; background-color: #333; color: #ccc; border: 1px solid #444; border-radius: 4px; cursor: pointer;">🗑️ Cancella Storico Locale</button>
    </div>
</div>

<script>
    const startBtn = document.getElementById('start-btn');
    const clearBtn = document.getElementById('clear-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const captionBanner = document.getElementById('caption-banner');
    const textItDiv = document.getElementById('text-it');
    const textEnDiv = document.getElementById('text-en');
    const historyBox = document.getElementById('history-box');
    
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
        let finalTranscriptIt = '';
        let fullHistoryHTML = '';

        async function traduciInInglese(testo) {
            if (!testo.trim()) return '';
            try {
                const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=it&tl=en&dt=t&q=${encodeURIComponent(testo)}`);
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

        clearBtn.addEventListener('click', () => {
            fullHistoryHTML = '';
            historyBox.innerHTML = '<i style="color: #666;">Storico cancellato.</i>';
        });

        recognition.onstart = () => {
            isRecognizing = true;
            window.autoRestartEnabled = true;
            statusDot.style.background = "#2ecc71";
            statusText.innerText = "Microfono ATTIVO. Servizio di sottotitolazione e traduzione simultanea in corso.";
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
            let interimTranscriptIt = '';
            let currentFinalPhraseIt = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    const chunk = event.results[i][0].transcript.trim();
                    finalTranscriptIt += chunk + ' ';
                    currentFinalPhraseIt = chunk;
                } else {
                    interimTranscriptIt += event.results[i][0].transcript;
                }
            }
            
            // 1. Aggiorna l'Italiano sul Banner principale
            let completoIt = finalTranscriptIt + interimTranscriptIt;
            if (completoIt.trim().length > 0) {
                textItDiv.innerText = completoIt;
                captionBanner.scrollTop = captionBanner.scrollHeight;
            }

            // 2. Gestione Traduzione e Aggiornamento Storico
            clearTimeout(translationTimeout);
            translationTimeout = setTimeout(async () => {
                if (completoIt.trim().length > 0) {
                    const traduzioneEn = await traduciInInglese(completoIt);
                    textEnDiv.innerText = traduzioneEn;
                    captionBanner.scrollTop = captionBanner.scrollHeight;

                    // Se è stata consolidata una nuova frase finale, la scriviamo nel box dello storico bilingue
                    if (currentFinalPhraseIt.length > 0) {
                        const finalTranslationEn = await traduciInInglese(currentFinalPhraseIt);
                        
                        fullHistoryHTML += `<div><b style="color:#00FF66;">IT:</b> ${currentFinalPhraseIt}<br><i style="color:#FFCC00;"><b style="font-style:normal;">EN:</b> ${finalTranslationEn}</i></div><hr style="border-color:#2a2a2a; margin:8px 0;">`;
                        historyBox.innerHTML = fullHistoryHTML;
                        historyBox.scrollTop = historyBox.scrollHeight;
                    }
                }
            }, 400);
        };
    }
</script>
"""

# Renderizziamo l'interfaccia. Ho impostato l'altezza dell'Iframe a 600px 
# per includere sia il banner gigante che lo storico bilingue integrato in basso.
components.html(js_speech_component, height=600)
