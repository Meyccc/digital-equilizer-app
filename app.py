import streamlit as st
import numpy as np
import soundfile as sf
from scipy.signal import firwin, lfilter
import io
import librosa
import matplotlib.pyplot as plt

# --- Set Page Config ---
st.set_page_config(page_title="Digital Music Equalizer", layout="wide")

# --- Persistent State for Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Styling with Background and Neon Purple Theme ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');

    .stApp {
        background-image: url('https://raw.githubusercontent.com/your-username/your-repo-name/main/background.jpeg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        font-family: 'Orbitron', sans-serif;
    }

    h1, h2, h3 {
        color: white;
        text-shadow: 0 0 15px #a020f0;
    }

    .stSlider > div {
        background-color: #111;
        border-radius: 10px;
        padding: 0.5em;
    }

    .stSlider input[type=range]::-webkit-slider-thumb {
        background: #a020f0;
        box-shadow: 0 0 12px #a020f0;
    }

    .stSlider input[type=range]::-webkit-slider-runnable-track {
        background: #333;
    }

    .stDownloadButton button {
        background: #a020f0;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        box-shadow: 0 0 12px #a020f0;
    }

    .stDownloadButton button:hover {
        background: #c64ff7;
        color: #000;
    }

    .start-button {
        background: linear-gradient(45deg, #a020f0, #c64ff7);
        color: white;
        font-size: 1.5em;
        font-weight: bold;
        padding: 0.75em 2em;
        border-radius: 30px;
        border: none;
        box-shadow: 0 0 25px #c64ff7;
        margin-top: 2em;
    }

    .start-button:hover {
        background: #c64ff7;
        color: black;
    }

    audio {
        filter: drop-shadow(0 0 10px #a020f0aa);
    }
    </style>
""", unsafe_allow_html=True)

# --- Audio Processing Functions ---
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

# --- Homepage ---
def show_homepage():
    st.markdown("<h1 style='text-align: center;'>🎧 Digital Music Equalizer</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Shape your sound with studio-level precision.</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎵 Start Now", key="start_button", use_container_width=True):
            st.session_state.page = "equalizer"

# --- Equalizer Page ---
def show_equalizer():
    st.title("🎛️ Digital Music Equalizer")

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

            # --- Processed Visualization ---
            st.subheader("🔊 Processed Track Waveform")
            fig, ax = plt.subplots(figsize=(10, 4))
            time = np.linspace(0, len(output) / fs, num=len(output))
            ax.plot(time, output, color="#a020f0", linewidth=0.5)
            ax.set_title("Processed Audio", fontsize=12, color='#a020f0')
            ax.set_xlabel("Time [s]", color='white')
            ax.set_ylabel("Amplitude", color='white')
            ax.set_facecolor("#0a0a0a")
            ax.tick_params(colors='white')
            fig.patch.set_facecolor("#0a0a0a")
            st.pyplot(fig)

    # Optional back button
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "home"

# --- Render the Appropriate Page ---
if st.session_state.page == "home":
    show_homepage()
else:
    show_equalizer()
















