import streamlit as st
import numpy as np
import soundfile as sf
from scipy.signal import firwin, lfilter
import io
import librosa
import matplotlib.pyplot as plt

st.set_page_config(page_title="Digital Music Equalizer", layout="centered")

# Session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- CSS for centering and styling ---
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
        text-align: center;
    }

    .home-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 85vh;
    }

    .home-button {
        background: linear-gradient(90deg, #ff5f6d, #ff69b4);
        border: none;
        padding: 1em 3em;
        font-size: 1.2em;
        color: white;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0 0 25px #ff69b4;
        transition: 0.3s ease;
    }

    .home-button:hover {
        background: linear-gradient(90deg, #ff85c1, #ff69b4);
        color: black;
    }

    .stButton > button {
        all: unset;
    }

    .centered {
        display: flex;
        justify-content: center;
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
    bands = [(60, 250), (250, 4000), (4000, 10000)]
    processed = np.zeros_like(data)
    for (low, high), gain in zip(bands, gains):
        filtered = bandpass_filter(data, low, high, fs)
        processed += filtered * gain
    return processed

# --- Pages ---
if st.session_state.page == "home":
    st.markdown("""
        <div class="home-container">
            <h1>🎧 Digital Music Equalizer</h1>
            <p style='font-size: 1.2em; text-align: center;'>Shape your sound with studio-level precision.</p>
            <div class="centered">
                <form action="#" method="post">
                    <button class="home-button" type="submit">Start Now</button>
                </form>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.form_submit_button("Start Now"):
        st.session_state.page = "about"
        st.rerun()

elif st.session_state.page == "about":
    st.markdown("""
        <h1>ℹ️ About This App</h1>
        <p style='font-size: 1.1em; text-align: center;'>
        🎶 <strong>What it does:</strong> Fine-tune audio files by adjusting <em>Bass</em>, <em>Mid</em>, and <em>Treble</em>.<br><br>
        🎚️ <strong>How it works:</strong> Uses digital bandpass filters and gain adjustments.<br><br>
        💾 <strong>Supported:</strong> WAV/MP3 up to 100MB.<br><br>
        🎧 Customize podcasts, remixes, or recordings with studio precision.
        </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Continue to Equalizer"):
            st.session_state.page = "equalizer"
            st.rerun()

elif st.session_state.page == "equalizer":
    st.title("🎛️ Digital Music Equalizer")

    if st.button("⬅️ Back to About"):
        st.session_state.page = "about"
        st.rerun()

    uploaded_file = st.file_uploader("🎵 Upload your audio (WAV or MP3)", type=["wav", "mp3"])
    if uploaded_file:
        file_size = uploaded_file.size / (1024 * 1024)
        if file_size > 100:
            st.error("⚠️ File size exceeds 100 MB.")
        else:
            data, fs = load_audio(uploaded_file)
            st.audio(uploaded_file)

            st.subheader("🎚️ Adjust Frequencies")
            bass = st.slider("Bass (60–250 Hz)", 0.0, 2.0, 1.0, 0.1)
            mid = st.slider("Mid (250 Hz – 4 kHz)", 0.0, 2.0, 1.0, 0.1)
            treble = st.slider("Treble (4–10 kHz)", 0.0, 2.0, 1.0, 0.1)

            output = apply_equalizer(data, fs, [bass, mid, treble])
            buf = io.BytesIO()
            sf.write(buf, output, fs, format='WAV')
            st.audio(buf, format='audio/wav')
            st.download_button("⬇️ Download Output", buf.getvalue(), file_name="equalized_output.wav")

            st.subheader("🔊 Waveform")
            fig, ax = plt.subplots()
            t = np.linspace(0, len(output) / fs, len(output))
            ax.plot(t, output, color="#ff69b4")
            ax.set_facecolor("#0a0a0a")
            ax.set_title("Processed Audio", color='white')
            ax.set_xlabel("Time [s]", color='white')
            ax.set_ylabel("Amplitude", color='white')
            ax.tick_params(colors='white')
            fig.patch.set_facecolor("#0a0a0a")
            st.pyplot(fig)

























