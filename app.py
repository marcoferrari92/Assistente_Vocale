import streamlit as st
import streamlit.components.v1 as components

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="AI Live Captioning & Translation", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. DIZIONARIO LINGUE SUPPORTATE ---
DIZ_LINGUE = {
    "Italiano": {"speech": "it-IT", "trans": "it"},
    "English (Inglese)": {"speech": "en-US", "trans": "en"},
    "Español (Spagnolo)": {"speech": "es-ES", "trans": "es"},
    "Français (Francese)": {"speech": "fr-FR", "trans": "fr"},
    "Deutsch (Tedesco)": {"speech": "de-DE", "trans": "de"}
}

# --- 3. CONFIGURAZIONE BARRA LATERALE ---
st.sidebar.title("⚙️ Impostazioni")

lingua_parlata_nome = st.sidebar.selectbox(
    "🎙️ Lingua Parlata (Docente):", 
    options=list(DIZ_LINGUE.keys()), 
    index=0
)

lingua_traduzione_nome = st.sidebar.selectbox(
    "🔤 Lingua Traduzione:", 
    options=list(DIZ_LINGUE.keys()), 
    index=1
)

codice_ascolto = DIZ_LINGUE[lingua_parlata_nome]["speech"]
codice_da = DIZ_LINGUE[lingua_parlata_nome]["trans"]
codice_a = DIZ_LINGUE[lingua_traduzione_nome]["trans"]

st.sidebar.markdown("---")
st.sidebar.write("📺 **Visualizzazione Banner:**")

# SELETTORE PER LA MODALITÀ
modalita_visualizzazione = st.sidebar.radio(
    "Scegli dove mostrare i sottotitoli:",
    ["Incorporato nella pagina (Standard)", "Finestra Flottante (Overlay per presentazioni)"]
)

# --- 4. STRUTTURA DEL COMPONENTE JAVASCRIPT (BANNER REATTIVO) ---
# Il CSS e la logica cambiano leggermente in base alla modalità scelta per ottimizzare gli spazi
is_floating = modalita_visualizzazione == "Finestra Flottante (Overlay per presentazioni)"

altezza_banner = "75px" if is_floating else "135px"
altezza_traduzione = "65px" if is_floating else "100px"
altezza_iframe = 220 if is_floating else 450

js_speech_component = """
<div id="recognition-container" 
     data-speech="{speech}" 
     data-from="{from_lang}" 
     data-to="{to_lang}"
     style="font-family: sans-serif; margin-bottom: 5px;">
     
    <div id="caption-banner" style="
        background-color: #111111;
        padding: 20px;
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
            font-size: 30px; 
            margin-bottom: 12px;
            min-height: {h_banner};
            max-height: {h_banner};
            overflow-y: auto;
        ">In attesa che il docente inizi a parlare...</div>
        
        <div id="text-en" style="
            color: #FFCC00; 
            font-size: 24px; 
            font-style: italic; 
            border-top: 1px solid #222; 
            padding-top: 10px;
            min-height: {h_trans};
            max-height: {h_trans};
            overflow-y: auto;
        ">La traduzione simultanea comparirà qui.</div>
    </div>

    <div style="color: #888888; font-size: 13px; padding: 10px; border: 1px solid #333; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e; margin-top: 8px;">
        <div>
            <span id="status-dot" style="height: 9px; width: 9px; background-color: #e74c3c; border-radius: 50%; display: inline-block; margin-right: 8px;"></span>
            <span id="status-text" style="color: #aaaaaa; font-weight: 500;">Microfono spento. Clicca per attivare.</span>
        </div>
        <button id="start-btn" style="padding: 8px 16px; background-color: #2ecc71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: 0.3s; font-size: 12px;">🎯 AVVIA ASCOLTO CONTINUO</button>
    </div>
</div>

<script>
    const container = document.getElementById('recognition-container');
    const startBtn = document.getElementById('start-btn');
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    const textItDiv = document.getElementById('text-it');
    const textEnDiv = document.getElementById('text-en');
    
    const langSpeech = container.getAttribute('data-speech');
    const langFrom = container.getAttribute('data-from');
    const langTo = container.getAttribute('data-to');
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        statusText.innerText = "Errore: Browser non supportato. Usa Chrome o Edge.";
        startBtn.style.display = 'none';
    } else {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = langSpeech;

        let isRecognizing = false;

        async function traduciTesto(testo) {
            if (!testo.trim()) return '';
            if (langFrom === langTo) return testo;
            
            try {
                const response = await fetch(`https://translate.googleapis.com/translate_a/single?client=gtx&sl=${langFrom}&tl=${langTo}&dt=t&q=${encodeURIComponent(testo)}`);
                const data = await response.json();
                return data[0].map(item => item[0]).join('');
            } catch (error) {
                return 'Errore di traduzione...';
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
            statusText.innerText = "Microfono ATTIVO. Riconoscimento in corso...";
            startBtn.innerText = "⏹️ FERMA ASCOLTO";
            startBtn.style.backgroundColor = "#e74c3c";
        };

        recognition.onend = () => {
            isRecognizing = false;
            if (window.autoRestartEnabled) {
                recognition.start();
            } else {
                statusDot.style.background = "#e74c3c";
                statusText.innerText = "Microfono disattivato.";
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
""".replace("{speech}", codice_ascolto)\
   .replace("{from_lang}", codice_da)\
   .replace("{to_lang}", codice_a)\
   .replace("{h_banner}", altezza_banner)\
   .replace("{h_trans}", altezza_traduzione)

# --- 5. LOGICA DI RENDERING IN BASE ALLA SELEZIONE ---
if not is_floating:
    # MODALITÀ STANDARD: Mostra il titolo e il banner grande dentro Streamlit
    st.title("Imprendo - Corsi in Multilingua")
    st.write("Sottotitoli integrati nella pagina web corrente.")
    components.html(js_speech_component, height=altezza_iframe)
else:
    # MODALITÀ FLOTTANTE: Svuota la pagina principale e mette un bottone per lanciare il popup
    st.title("📺 Modalità Banner Flottante Attivata")
    st.write("Configura le lingue a sinistra e clicca il pulsante qui sotto per aprire il banner esterno.")
    
    # Questo pulsante genera lo script che forza il browser ad aprire una finestra popup pulita
    if st.button("🚀 APRI ORA IL BANNER ESTERNO", type="primary"):
        # Generiamo un URL pulito che contiene un parametro per dire a Streamlit di mostrare solo il banner
        js_popup = """
        <script>
            var popupUrl = window.parent.location.href;
            // Apre una finestra popup senza barre di navigazione, posizionata in basso
            window.open(popupUrl, 'SottotitoliOverlay', 'width=1100,height=260,top=750,left=150,toolbar=no,menubar=no,scrollbars=no,resizable=yes');
        </script>
        """
        components.html(js_popup, height=0)
    
    # Se la finestra corrente viene intercettata come l'effettivo popup, mostriamo solo il banner senza nient'altro attorno
    st.markdown("""
        <style>
            #MainMenu, header, footer {visibility: hidden;}
            .stDeployButton {display:none;}
            div[block-class="main"] {padding: 0px;}
        </style>
    """, unsafe_allow_index=True)
    
    # Mostriamo comunque il componente nel caso in cui siamo dentro il popup
    components.html(js_speech_component, height=altezza_iframe)
