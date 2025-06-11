import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
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
    .hero {{
        height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        padding: 0 2rem;
    }}
    .hero h1 {{
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }}
    .hero p {{
        font-size: 1.25rem;
        font-weight: 400;
        margin-bottom: 2.5rem;
        letter-spacing: 1px;
    }}
    .start-now {{
        font-size: 1.2rem;
        padding: 0.75em 2em;
        border: none;
        border-radius: 50px;
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    .start-now:hover {{
        transform: scale(1.05);
        background: linear-gradient(to right, #ec4899, #a855f7);
    }}

    /* Equalizer styling */
    .custom-title {{
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-top: 1rem;
        font-family: 'Segoe UI', sans-serif;
    }}
    .stSlider > div {{
        padding: 10px 0px;
    }}
    .stSlider .css-14g5w8i, .stSlider .css-1r6slb0 {{
        background: linear-gradient(to right, #a855f7, #ec4899);
        border-radius: 12px;
        height: 10px;
    }}
    .stSlider .css-1c5h37h {{
        background-color: #1f2937;
        border-radius: 12px;
    }}
    .block-container {{
        background-color: rgba(0, 0, 0, 0.6);
        padding: 2rem;
        border-radius: 16px;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# Apply the background image styling
local_css_with_bg("background.jpg")

# Session page control
if "page" not in st.session_state:
    st.session_state.page = "home"

# Homepage UI
def show_homepage():
    st.markdown("""
    <div class="hero">
        <h1>🎧 Digital Music Equalizer</h1>
        <p>Shape your sound with studio-level precision</p>
        <form action="" method="post">
            <button class="start-now" type="submit" name="start">Start Now</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

    if "start" in st.experimental_get_query_params():
        st.session_state.page = "equalizer"

# Equalizer UI
def show_equalizer():
    st.markdown('<div class="custom-title">🎚️ Music Equalizer</div>', unsafe_allow_html=True)

    with st.container():
        audio_file = st.file_uploader("🎵 Upload Your Music File", type=["mp3", "wav"])
        bass_gain = st.slider("Bass Gain", -20, 20, 0, key="bass")
        mid_gain = st.slider("Mid Gain", -20, 20, 0, key="mid")
        treble_gain = st.slider("Treble Gain", -20, 20, 0, key="treble")

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
                st.download_button("⬇️ Download Modified Audio", f, "equalized_output.wav")

# Page routing
if st.session_state.page == "home":
    show_homepage()
elif st.session_state.page == "equalizer":
    show_equalizer()


