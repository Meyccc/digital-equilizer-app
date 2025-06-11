import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
import matplotlib.pyplot as plt
import base64

st.set_page_config(layout="wide")

# ---- Load CSS with background and style ----
def local_css_with_bg(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
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
        font-size: 1.3rem;
        border-radius: 40px;
        padding: 0.6em 2em;
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 1.5rem;
    }}
    .start-button:hover {{
        transform: scale(1.05);
        background: linear-gradient(to right, #ec4899, #a855f7);
    }}
    .navbar {{
        background-color: rgba(0,0,0,0.7);
        padding: 0.75rem 2rem;
        border-bottom: 1px solid #444;
        color: white;
        font-size: 1.1rem;
    }}
    .stSlider > div {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    .stSlider label {{
        font-size: 1.2rem !important;
        color: white !important;
    }}
    .stSlider .css-1n76uvr {{
        font-size: 1.1rem !important;
        color: #f0a3f6 !important;
    }}
    .stSlider .st-cf {{
        height: 10px;
    }}
    .stSlider .st-cg {{
        width: 24px;
        height: 24px;
        background: linear-gradient(to right, #a855f7, #ec4899);
        border: none;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

local_css_with_bg("home background.jpg")

# ---- Routing state ----
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---- Homepage ----
def show_homepage():
    st.markdown("""
    <div class="centered">
        <h1 style="font-size: 3rem; font-weight: 600;">🎧 Digital Music Equalizer</h1>
        <p style="font-size: 1.2rem;">Shape your sound with studio-level precision.</p>
        <form action="" method="post">
            <button class="start-button" name="start" type="submit">🎵 Start Now</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

# ---- Equalizer Page ----
def show_equalizer():
    st.markdown('<div class="navbar">🎛️ Music Equalizer</div>', unsafe_allow_html=True)
    st.markdown("## Upload Your Audio and Adjust Equalizer")

    audio_file = st.file_uploader("🎵 Upload Audio", type=["mp3", "wav"])

    with st.container():
        bass_gain = st.slider("🔊 Bass Gain", -20, 20, 0)
        mid_gain = st.slider("🎶 Mid Gain", -20, 20, 0)
        treble_gain = st.slider("🎵 Treble Gain", -20, 20, 0)

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

        st.markdown("### 🎧 Original Audio")
        st.audio(audio_file)

        st.markdown("### 🎚️ Equalized Audio")
        st.audio(y_eq, sample_rate=sr)

        # Waveform Visualization
        st.markdown("### 🔍 Audio Waveforms")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(y, alpha=0.5, label="Original", color='gray')
        ax.plot(y_eq, alpha=0.7, label="Equalized", color='#a855f7')
        ax.set_title("Waveform Comparison", color='white')
        ax.set_facecolor("#111")
        ax.tick_params(colors='white')
        ax.legend()
        st.pyplot(fig)

        sf.write("output.wav", y_eq, sr)
        with open("output.wav", "rb") as f:
            st.download_button("⬇️ Download Modified Audio", f, "equalized_output.wav")

# ---- Routing logic ----
if st.session_state.page == "home":
    if st.form_submit_button("start"):
        st.session_state.page = "equalizer"
    show_homepage()
elif st.session_state.page == "equalizer":
    show_equalizer()


