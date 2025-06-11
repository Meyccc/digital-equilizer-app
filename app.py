import streamlit as st
import numpy as np
import librosa
import soundfile as sf
from scipy.signal import firwin, lfilter
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

# Load CSS styling
def local_css():
    st.markdown("""
    <style>
    body {
        background-color: #0d0d0d;
    }
    .main {
        background: url('background.jpg') no-repeat center center fixed;
        background-size: cover;
    }
    .start-button {
        font-size: 1.3rem;
        border-radius: 40px;
        padding: 0.6em 1.8em;
        background: linear-gradient(to right, #a855f7, #ec4899);
        color: white;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .start-button:hover {
        transform: scale(1.05);
        background: linear-gradient(to right, #ec4899, #a855f7);
    }
    .centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Homepage
def show_homepage():
    st.markdown(f"""
    <div class="centered">
        <h1 style="font-size: 3rem; font-weight: 600;">🎧 Digital Music Equalizer</h1>
        <p style="font-size: 1.2rem;">Shape your sound with studio-level precision.</p>
        <button class="start-button" onclick="window.location.reload();">
            Start Now
        </button>
    </div>
    """, unsafe_allow_html=True)

    # JS to switch session state
    st.markdown("""
    <script>
    const btn = window.parent.document.querySelector(".start-button");
    btn.onclick = () => {
        fetch("/_stcore/streamlit/message?streamlit_client=true", {
            method: "POST",
            body: JSON.stringify({ "type": "customEvent", "data": "go-to-equalizer" })
        });
    };
    </script>
    """, unsafe_allow_html=True)

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

# Listen for navigation trigger
if st.session_state.page == "home":
    show_homepage()

st.experimental_data_editor({"_type": "customEvent"}, key="start-trigger", on_change=lambda: st.session_state.update(page="equalizer"))

if st.session_state.page == "equalizer":
    show_equalizer()


