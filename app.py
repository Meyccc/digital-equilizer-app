import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
import base64
import os

st.set_page_config(layout="wide")

# Load background CSS with embedded image
def local_css_with_bg(image_path):
    if not os.path.exists(image_path):
        st.error(f"Background image not found: {image_path}")
        return
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
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
    .start-button {{
        font-size: 1.4rem;
        border-radius: 40px;
        padding: 0.75em 2.5em;
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
    h1, p {{
        text-shadow: 2px 2px 6px rgba(0,0,0,0.6);
    }}
    .stSlider > div {{
        height: 45px;
    }}
    .stSlider label {{
        font-size: 1.2rem !important;
        color: #ffffff !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# Load custom style
local_css_with_bg("background.jpg")

# Set page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Home Page
def show_homepage():
    st.markdown("""
    <div class="centered">
        <h1 style="font-size: 3rem; font-weight: 600;">🎧 Digital Music Equalizer</h1>
        <p style="font-size: 1.2rem;">Shape your sound with studio-level precision.</p>
        <form action="?equalizer">
            <button class="start-button" type="submit">🎵 Start Now</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

# Equalizer Page
def show_equalizer():
    st.title("🎛️ Digital Music Equalizer")

    audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
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
            st.download_button("Download Equalized Audio", f, "equalized_output.wav")

# Navigation based on URL
if "equalizer" in st.query_params:
    st.session_state.page = "equalizer"

# Show page
if st.session_state.page == "home":
    show_homepage()
elif st.session_state.page == "equalizer":
    show_equalizer()




