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
st.subtitle("Sottotitoli automatici ad alta visibilità per l'ascolto delle lezioni")
st.divider()

# Area del Banner di Sottotitolazione
placeholder_banner = st.empty()

# Renderizziamo il banner iniziale o l'ultimo testo rilevato
if st.session_state.cronologia_trascrizione:
    testo_visualizzato = st.session_state.cronologia_trascrizione[-1]
else:
    testo_visualizzato = "In attesa che il docente inizi a parlare... Il testo comparirà qui."

placeholder_banner.markdown(
    f'<div class="caption-banner">{testo_visualizzato}</div>', 
    unsafe_allow_html=True
)

# --- 5. LOGICA DI ASCOLTO E TRASCRIZIONE ---
st.write("### 🎙️ Controllo Microfono")
st.markdown('<p class="instruction-text">Clicca sul microfono per avviare l\'ascolto. Il sistema rileverà automaticamente le pause del parlato per aggiornare il banner.</p>', unsafe_allow_html=True)

if client:
    # Il componente audio_recorder gestisce autonomamente il buffer di registrazione
    # energy_threshold=(-1.0, 1.0) aiuta a regolare la sensibilità al silenzio
    audio_bytes = audio_recorder(
        text="Ascolto attivo... Parla ora",
        recording_color="#e74c3c",
        neutral_color="#2ecc71",
        icon_size="3x",
        pause_threshold=2.0 # Invia l'audio all'AI dopo 2 secondi di silenzio
    )

    if audio_bytes:
        try:
            # Trasformiamo i byte audio in un file virtuale per l'API di OpenAI
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "chunk_lezione.wav"
            
            # Chiamata rapida a Whisper per la trascrizione in italiano
            with st.spinner("Traduzione del parlato in corso..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file, 
                    language="it"
                )
            
            testo_rilevato = transcript.text.strip()
            
            if testo_rilevato:
                # Salviamo nella cronologia e aggiorna il banner istantaneamente
                st.session_state.cronologia_trascrizione.append(testo_rilevato)
                
                # Aggiorna il banner dinamico con l'ultima frase
                placeholder_banner.markdown(
                    f'<div class="caption-banner">{testo_rilevato}</div>', 
                    unsafe_allow_html=True
                )
                
        except Exception as e:
            st.error(f"Errore di trascrizione AI: {e}")

# --- 6. CRONOLOGIA COMPLETA DELLA LEZIONE ---
st.divider()
with st.expander("📝 Guarda l'intera trascrizione della lezione (Storico Frasi)"):
    if st.session_state.cronologia_trascrizione:
        # Mostra i testi uno dopo l'altro per permettere il riassunto o lo studio successivo
        testo_completo = " ".join(st.session_state.cronologia_trascrizione)
        st.write(testo_completo)
        
        # Pulsante per cancellare lo storico se necessario
        if st.button("🗑️ Cancella Storico Lezione"):
            st.session_state.cronologia_trascrizione = []
            st.rerun()
    else:
        st.info("Nessun testo registrato nello storico per ora.")
