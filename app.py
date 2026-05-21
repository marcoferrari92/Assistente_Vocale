import streamlit as st
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder
import io

# --- 1. CONFIGURAZIONE PAGINA AD ALTO CONTRASTO ---
st.set_page_config(
    page_title="AI Live Captioning per Non Udenti", 
    page_icon="🧏", 
    layout="wide"
)

# --- 2. STILE CSS PERSONALIZZATO PER IL BANNER ---
# Crea un banner nero fisso in alto, con testo bianco molto grande e leggibile
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

# --- 3. INIZIALIZZAZIONE STATO E UTILI ---
if "cronologia_trascrizione" not in st.session_state:
    st.session_state.cronologia_trascrizione = []

if "openai_key" in st.secrets:
    client = OpenAI(api_key=st.secrets["openai_key"])
else:
    st.sidebar.error("⚠️ Inserisci la chiave API 'openai_key' nei Secrets per procedere.")
    client = None

# --- 4. INTERFACCIA UTENTE ---
st.title("🧏 Morpheus Live Subtitles")
st.subheader("Sottotitoli automatici ad alta visibilità per l'ascolto delle lezioni") # <--- Sostituito st.subtitle con st.subheader
st.divider()

