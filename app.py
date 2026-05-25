import streamlit as st
import streamlit.components.v1 as components
import urllib.parse

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="AI Live Captioning & Translation", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. SISTEMA DI LOGIN CON BANCA DATI DA STREAMLIT SECRETS ---
def check_password():
    """Restituisce True se l'utente ha inserito le credenziali corrette."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Se l'utente è già autenticato, procedi subito
    if st.session_state.authenticated:
        return True

    # Mostra il form di login
    st.title("🔒 Accesso a Imprendo Multilingua")
    st.write("Inserisci le tue credenziali per accedere allo strumento di trascrizione.")
    
    with st.form("login_form"):
        user_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Accedi")
        
        if submit_button:
            # Recupera i dati dal file secrets.toml
            try:
                secret_user = st.secrets["credentials"]["username"]
                secret_pass = st.secrets["credentials"]["password"]
                
                if user_input == secret_user and password_input == secret_pass:
                    st.session_state.authenticated = True
                    st.success("Accesso effettuato! Caricamento dell'app...")
                    st.rerun()
                else:
                    st.error("❌ Username o Password errati.")
            except KeyError:
                st.error("⚠️ Configurazione interrotta: File secrets.toml non trovato o malformato.")
                
    return False

# Blocca l'applicazione se il login fallisce
if not check_password():
    st.stop()

# =====================================================================
# DA QUI IN POI L'UTENTE È AUTENTICATO (LOGGATO)
# =====================================================================

# --- 3. DIZIONARIO LINGUE SUPPORTATE ---
DIZ_LINGUE = {
    "Italiano": {"speech": "it-IT", "trans": "it"},
    "English (Inglese)": {"speech": "en-US", "trans": "en"},
    "Español (Spagnolo)": {"speech": "es-ES", "trans": "es"},
    "Français (Francese)": {"speech": "fr-FR", "trans": "fr"},
    "Deutsch (Tedesco)": {"speech": "de-DE", "trans": "de"}
}

# --- 4. GESTIONE PARAMETRI URL ---
query_params = st.query_params
default_parlata = query_params.get("lang_from", "Italiano")
default_traduzione = query_params.get("lang_to", "English (Inglese)")
is_popup_window = query_params.get("mode", "standard") == "popup"

if default_parlata not in DIZ_LINGUE: default_parlata = "Italiano"
if default_traduzione not in DIZ_LINGUE: default_traduzione = "English (Inglese)"

index_parlata = list(DIZ_LINGUE.keys()).index(default_parlata)
index_traduzione = list(DIZ_LINGUE.keys()).index(default_traduzione)

# --- 5. INTERFACCIA (BARRA LATERALE E BANNER) ---
if is_popup_window:
    lingua_parlata_nome = default_parlata
    lingua_traduzione_nome = default_traduzione
    is_floating = True
else:
    st.sidebar.title("⚙️ Impostazioni")
    
    # Bottone di Logout rapido
    if st.sidebar.button("🚪 Esci (Logout)"):
        st.session_state.authenticated = False
        st.rerun()
        
    st.sidebar.markdown("---")
    
    lingua_parlata_nome = st.sidebar.selectbox(
        "🎙️ Lingua Parlata (Docente):", 
        options=list(DIZ_LINGUE.keys()), 
        index=index_parlata
    )
    lingua_traduzione_nome = st.sidebar.selectbox(
        "🔤 Lingua Traduzione:", 
        options=list(DIZ_LINGUE.keys()), 
        index=index_traduzione
    )
    st.sidebar.markdown("---")
    st.sidebar.write("📺 **Visualizzazione Banner:**")
    modalita_visualizzazione = st.sidebar.radio(
        "Scegli dove mostrare i sottotitoli:",
        ["Incorporato nella pagina (Standard)", "Finestra Flottante (Overlay per presentazioni)"]
    )
    is_floating = modalita_visualizzazione == "Finestra Flottante (Overlay per presentazioni)"

codice_ascolto = DIZ_LINGUE[lingua_parlata_nome]["speech"]
codice_da = DIZ_LINGUE[lingua_parlata_nome]["trans"]
codice_a = DIZ_LINGUE[lingua_traduzione_nome]["trans"]

altezza_banner = "75px" if is_floating else "135px"
altezza_traduzione = "65px" if is_floating else "100px"
altezza_iframe = 220 if is_floating else 450

# --- 6. COMPONENTE JAVASCRIPT ---
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
        statusText.innerText = "Errore: Browser non supportato.";
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
            } catch (error) { return 'Errore...'; }
        }

        startBtn.addEventListener('click', () => {
            if (!isRecognizing) { recognition.start(); } 
            else { window.autoRestartEnabled = false; recognition.stop(); }
        });

        recognition.onstart = () => {
            isRecognizing = true; window.autoRestartEnabled = true;
            statusDot.style.background = "#2ecc71"; statusText.innerText = "Ascolto...";
            startBtn.innerText = "⏹️ FERMA ASCOLTO"; startBtn.style.backgroundColor = "#e74c3c";
        };

        recognition.onend = () => {
            isRecognizing = false;
            if (window.autoRestartEnabled) { recognition.start(); } 
            else {
                statusDot.style.background = "#e74c3c"; statusText.innerText = "Spento.";
                startBtn.innerText = "🎯 AVVIA ASCOLTO CONTINUO"; startBtn.style.backgroundColor = "#2ecc71";
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

# --- 7. RENDERING DELLE MODALITÀ ---
if is_popup_window:
    # Se è la finestra popup, pulisci tutto il layout grafico residuo
    st.markdown("""
        <style>
            #MainMenu, header, footer {visibility: hidden;}
            .stDeployButton {display:none;}
            div[block-class="main"] {padding: 0px !important;}
            iframe {border: none;}
        </style>
    """, unsafe_allow_index=True)
    components.html(js_speech_component, height=altezza_iframe)

else:
    # Interfaccia standard post-login
    if not is_floating:
        st.title("Imprendo - Corsi in Multilingua")
        st.write("Sottotitoli integrati nella pagina web corrente.")
        components.html(js_speech_component, height=altezza_iframe)
    else:
        st.title("📺 Modalità Banner Flottante Pronta")
        st.write(f"Hai configurato: **{lingua_parlata_nome}** ➡️ **{lingua_traduzione_nome}**")
        st.write("Clicca il pulsante qui sotto per generare l'overlay.")
        
        p_from = urllib.parse.quote(lingua_parlata_nome)
        p_to = urllib.parse.quote(lingua_traduzione_nome)
        
        js_popup = f"""
        <script>
            var currentUrl = window.parent.location.href.split('?')[0];
            var targetUrl = currentUrl + "?mode=popup&lang_from={p_from}&lang_to={p_to}";
            window.open(targetUrl, 'SottotitoliOverlay', 'width=1100,height=250,top=750,left=150,toolbar=no,menubar=no,scrollbars=no,resizable=yes');
        </script>
        """
        if st.button("🚀 APRI ORA IL BANNER ESTERNO", type="primary"):
            components.html(js_popup, height=0)
