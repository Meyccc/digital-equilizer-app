import streamlit as st
import numpy as np
import soundfile as sf
from scipy.signal import firwin, lfilter
import io
import librosa
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="Digital Music Equalizer", layout="centered")

# --- Session state to switch pages ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Styles ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0a0a, #1a001a);
        color: white;
        font-family: 'Orbitron', sans-serif;
    }

    h1, h2, h3 {
        color: white;
        text-shadow: 0 0 15px #ff69b4;
    }

    .center {
        text-align: center;
        margin-top: 8em;
    }

    .button-center {
        display: flex;
        justify-content: center;
        margin-top: 2em;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFileUploader > div,
    .main-button button {
        background: linear-gradient(90deg, #ff5f6d, #ff69b4);
        border: none;
        padding: 1.2em 3em;
        font-size: 1.2em;
        color: white;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0 0 25px #ff69b4;
        transition: 0.3s ease;
        text-align: center;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .main-button button:hover {
        background: linear-gradient(90deg, #ff85c1, #ff69b4);
        color: black;
    }

    .stSlider > div {
        background-color: #111;
        border-radius: 10px;
        padding: 0.5em;
    }

    .stSlider input[type=range]::-webkit-slider-thumb {
        background: #ff69b4;
        box-shadow: 0 0 12px #ff69b4;
    }

    .stSlider input[type=range]::-webkit-slider-runnable-track {
        background: #333;
    }

    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: 2em;
    }
    </style>
""", unsafe_allow_html=True)

# --- Functions ---
def load_audio(file):
    y, sr = librosa.load(file, sr=None, mono=True)
    return y, sr

def bandpass_filter(data, lowcut, highcut, fs, numtaps=101):
    taps = firwin(numtaps, [lowcut, highcut], pass_zero=False, fs=fs)
    return lfilter(taps, 1.0, data)

def apply_equalizer(data, fs, gains):
    bands = [(60, 250), (250, 4000), (4000, 10000)]  # Bass, Mid, Treble
    processed = np.zeros_like(data)
    for (low, high), gain in zip(bands, gains):
        filtered = bandpass_filter(data, low, high, fs)
        processed += filtered * gain
    return processed

# --- Home Page ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="center">
            <h1>🎧 Digital Music Equalizer</h1>
            <p style='font-size: 1.2em;'>Shape your sound with studio-level precision.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='button-center'>", unsafe_allow_html=True)
    if st.button("Start Now", key="start_home"):
        st.session_state.page = "about"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- About Page ---
elif st.session_state.page == "about":
    st.markdown("""
        <div class="center">
            <h1>ℹ️ About This App</h1>
            <p style='font-size: 1.1em;'>
            <strong>Welcome to the Digital Music Equalizer!</strong><br><br>
            🎶 <strong>What it does:</strong><br>
            This app allows you to fine-tune your audio files by adjusting frequency bands—<em>Bass</em>, <em>Midrange</em>, and <em>Treble</em>—using professional-grade filters.<br><br>
            🎚️ <strong>How it works:</strong><br>
            The audio signal is split into frequency bands with digital filters (FIR bandpass filters), and you can boost or reduce each band independently.<br><br>
            💾 <strong>Supported Files:</strong><br>
            • WAV or MP3 audio formats<br>
            • Maximum file size: 100 MB<br><br>
            📦 <strong>Features:</strong><br>
            • Studio-inspired design<br>
            • Real-time preview of your adjustments<br>
            • Download your customized track in WAV format<br>
            • Waveform visualization to monitor your sound<br><br>
            🎧 Whether you're enhancing podcasts, remixing songs, or refining recordings—<br>
            this equalizer gives you full control over your audio’s character.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Continue to Equalizer", key="to_equalizer"):
            st.session_state.page = "equalizer"
            st.rerun()

# --- Equalizer Page ---
elif st.session_state.page == "equalizer":
    st.title("🎛️ Digital Music Equalizer")

    if st.button("⬅️ Back to About"):
        st.session_state.page = "about"
        st.rerun()

    uploaded_file = st.file_uploader("🎵 Upload your audio track (WAV or MP3)", type=["wav", "mp3"])

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 100:
            st.error("⚠️ File size exceeds 100 MB limit. Please upload a smaller file.")
        else:
            data, fs = load_audio(uploaded_file)
            st.audio(uploaded_file)

            st.subheader("🎚️ Adjust the Frequencies")
            bass = st.slider("Bass Boost (60–250 Hz)", 0.0, 2.0, 1.0, 0.1)
            mid = st.slider("Midrange Boost (250 Hz – 4 kHz)", 0.0, 2.0, 1.0, 0.1)
            treble = st.slider("Treble Boost (4–10 kHz)", 0.0, 2.0, 1.0, 0.1)

            output = apply_equalizer(data, fs, [bass, mid, treble])

            # Save and play
            buf = io.BytesIO()
            sf.write(buf, output, fs, format='WAV')
            st.audio(buf, format='audio/wav')
            st.download_button("⬇️ Download Processed Audio", buf.getvalue(), file_name="equalized_output.wav")

            # Visualization
            st.subheader("🔊 Processed Track Waveform")
            fig, ax = plt.subplots(figsize=(10, 4))
            time = np.linspace(0, len(output) / fs, num=len(output))
            ax.plot(time, output, color="#ff69b4", linewidth=0.5)
            ax.set_title("Processed Audio", fontsize=12, color='#ff69b4')
            ax.set_xlabel("Time [s]", color='white')
            ax.set_ylabel("Amplitude", color='white')
            ax.set_facecolor("#0a0a0a")
            ax.tick_params(colors='white')
            fig.patch.set_facecolor("#0a0a0a")
            st.pyplot(fig)

























