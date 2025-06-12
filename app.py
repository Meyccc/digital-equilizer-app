import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
import base64

st.set_page_config(layout="wide")

# Load and inject CSS for background and theme
def load_css_with_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Segoe UI', sans-serif;
    }}
    .centered {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
        color: white;
    }}
    .start-btn {{
        font-size: 2rem;
        padding: 1rem 3rem;
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
        border: none;
        border-radius: 2rem;
        cursor: pointer;
        transition: transform 0.2s ease;
    }}
    .start-btn:hover {{
        transform: scale(1.05);
        background: linear-gradient(to right, #ec4899, #a855f7);
    }}
    .slider-label {{
        font-size: 1.3rem;
        color: #e879f9;
        font-weight: 600;
        margin-top: 1rem;
    }}
    input[type=range] {{
        accent-color: #e879f9;
        height: 10px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load the background
load_css_with_background("e818d5f8-b1d0-45aa-a633-e9c61552732d.png")  # Adjust filename if needed

# Session state setup
if "page" not in st.session_state:
    st.session_state.page = "home"

# Homepage
def show_homepage():
    st.markdown(f"""
    <div class="centered">
        <h1 style="font-size: 4rem; font-weight: 800;">🎧 Digital Music Equalizer</h1>
        <p style="font-size: 1.5rem;">Shape your sound with studio-level precision.</p>
        <form action="" method="post">
            <button class="start-btn" name="start" type="submit">🎵 Start Now</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

    # Detect the button click via query param
    if st.query_params.get("start") is not None or st.session_state.get("start_pressed"):
        st.session_state.page = "equalizer"

    # Fallback: Button (for environments with no JS/form support)
    if st.button("Start Now (Fallback)", key="start_fallback"):
        st.session_state.page = "equalizer"

# Equalizer
def show_equalizer():
    st.markdown("<h1 style='text-align:center; color:white; font-size:3rem;'>🎛️ Music Equalizer</h1>", unsafe_allow_html=True)

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        return

    audio_file = st.file_uploader("Upload Audio", type=["mp3", "wav"])

    st.markdown('<div class="slider-label">Bass Gain</div>', unsafe_allow_html=True)
    bass_gain = st.slider("", -20, 20, 0, key="bass", label_visibility="collapsed")

    st.markdown('<div class="slider-label">Mid Gain</div>', unsafe_allow_html=True)
    mid_gain = st.slider("", -20, 20, 0, key="mid", label_visibility="collapsed")

    st.markdown('<div class="slider-label">Treble Gain</div>', unsafe_allow_html=True)
    treble_gain = st.slider("", -20, 20, 0, key="treble", label_visibility="collapsed")

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

# Routing
if st.session_state.page == "home":
    show_homepage()
else:
    show_equalizer()















