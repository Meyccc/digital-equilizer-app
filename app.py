import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
import matplotlib.pyplot as plt
import base64

st.set_page_config(layout="wide")

# Load CSS styling with embedded background
def local_css_with_bg(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .start-button {{
        font-size: 1.3rem;
        border-radius: 40px;
        padding: 0.6em 1.8em;
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .start-button:hover {{
        transform: scale(1.05);
        background: linear-gradient(to right, #ec4899, #a855f7);
    }}
    .centered {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# Apply custom CSS
local_css_with_bg("background.jpg")

# Page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Homepage
def show_homepage():
    st.markdown(f"""
    <div class="centered">
        <h1 style="font-size: 3rem; font-weight: 600;">🎧 Digital Music Equalizer</h1>
        <p style="font-size: 1.2rem;">Shape your sound with studio-level precision.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎵 Start Now", key="start_button"):
        st.session_state.page = "equalizer"

# Equalizer UI
def show_equalizer():
    st.title("🎛️ Music Equalizer")

    audio_file = st.file_uploader("Upload Audio", type=["mp3", "wav"])
    bass_gain = st.slider("Bass Gain", -20, 20, 0)
    mid_gain = st.slider("Mid Gain", -20, 20, 0)
    treble_gain = st.slider("Treble Gain", -20, 20, 0)

    if audio_file:
        y, sr = librosa.load(audio_file, sr=None, mono=True)

        def apply_filter(y, sr, band, gain_db):
            if band == 'bass':
                b = firwin(numtaps=101, cutoff=200, fs=sr, pass_zero='lowpass')
            elif band == 'mid':
                b = firwin(numtaps=101, cutoff=[200, 2000], fs=sr, pass_zero='bandpass')
            else:
                b = firwin(numtaps=101, cutoff=2000, fs=sr, pass_zero='highpass')
            filtered = lfilter(b, [1.0], y)
            gain = 10 ** (gain_db / 20)
            return filtered * gain

        bass = apply_filter(y, sr, 'bass', bass_gain)
        mid = apply_filter(y, sr, 'mid', mid_gain)
        treble = apply_filter(y, sr, 'treble', treble_gain)

        y_eq = bass + mid + treble
        st.audio(y_eq, sample_rate=sr)

        sf.write("output.wav", y_eq, sr)
        with open("output.wav", "rb") as f:
            st.download_button("Download Modified Audio", f, "equalized_output.wav")

# Route app
if st.session_state.page == "home":
    show_homepage()
elif st.session_state.page == "equalizer":
    show_equalizer()


