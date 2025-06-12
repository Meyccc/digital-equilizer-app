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

# --- Custom Styles ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #1e1e2f, #2e003e);
        color: white;
        font-family: 'Orbitron', sans-serif;
        text-align: center;
    }

    h1, h2, h3, p {
        text-align: center;
        color: white;
        font-size: 1.5em;
    }

    .main-button button,
    .stButton>button,
    .stDownloadButton button {
        background: linear-gradient(90deg, #ff9ebc, #d47bc0);
        border: none;
        padding: 1.0em 2.8em;
        font-size: 1.2em;
        color: white;
        font-weight: bold;
        border-radius: 999px;
        box-shadow: 0 0 15px rgba(255, 158, 188, 0.3);
        transition: all 0.3s ease;
        text-align: center;
        margin: 1em auto;
        display: block;
    }

    .main-button button:hover,
    .stButton>button:hover,
    .stDownloadButton button:hover {
        background: linear-gradient(90deg, #d47bc0, #ff9ebc);
        color: black;
        transform: scale(1.03);
    }

    .stSlider > div {
        background-color: #1a1a2a;
        border-radius: 10px;
        padding: 0.5em;
    }

    .stSlider label {
        font-size: 1.1em;
        color: #f5f5f5;
    }

    .stSlider input[type=range]::-webkit-slider-thumb {
        background: #ff9ebc;
        box-shadow: 0 0 8px #ff9ebc;
    }

    .stSlider input[type=range]::-webkit-slider-runnable-track {
        background: #444;
    }

    .center {
        text-align: center;
        margin-top: 6em;
    }

    .block-container {
        padding-top: 2rem;
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
    st.markdown("""<div class="center">""", unsafe_allow_html=True)
    st.markdown("<h1>🎧 Digital Music Equalizer</h1>", unsafe_allow_html=True)
    st.markdown("<p>Shape your sound with studio-level precision.</p>", unsafe_allow_html=True)
    if st.button("Start Now", key="start_home"):
        st.session_state.page = "about"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- About Page ---
elif st.session_state.page == "about":
    st.markdown("""<div class="center">""", unsafe_allow_html=True)
    st.markdown("<h1>ℹ️ About This App</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p>
        🎶 <strong>What it does:</strong><br>
        Fine-tune your audio by adjusting Bass, Midrange, and Treble.<br><br>
        💾 <strong>Supported:</strong> WAV or MP3 files under 100 MB<br>
        📈 <strong>Features:</strong> Real-time preview, waveform display, studio feel<br><br>
        Whether enhancing a podcast or remixing a song — you’re in control.
        </p>
    """, unsafe_allow_html=True)

    if st.button("Continue to Equalizer", key="to_equalizer"):
        st.session_state.page = "equalizer"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Equalizer Page ---
elif st.session_state.page == "equalizer":
    st.markdown("<h1>🎛️ Digital Music Equalizer</h1>", unsafe_allow_html=True)

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
            ax.plot(time, output, color="#ff9ebc", linewidth=0.5)
            ax.set_title("Processed Audio", fontsize=14, color='#ff9ebc')
            ax.set_xlabel("Time [s]", color='white')
            ax.set_ylabel("Amplitude", color='white')
            ax.set_facecolor("#1e1e2f")
            ax.tick_params(colors='white')
            fig.patch.set_facecolor("#1e1e2f")
            st.pyplot(fig)






















