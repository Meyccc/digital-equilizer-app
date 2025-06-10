import streamlit as st
import numpy as np
import soundfile as sf
from scipy.signal import firwin, lfilter
import io
import librosa
import matplotlib.pyplot as plt

# --- Custom CSS for styling and background ---
st.markdown(
    """
    <style>
    body {
        background-image: url('studio.jpeg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    .stApp {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 2rem;
        border-radius: 15px;
    }
    h1, h2, h3, label {
        color: #FFD700;
    }
    .stButton>button {
        background-color: #FFD700;
        color: black;
        font-size: 18px;
        font-weight: bold;
        padding: 0.5em 1.5em;
        border-radius: 10px;
    }
    .stSlider>div {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Session state to handle home page logic ---
if "page" not in st.session_state:
    st.session_state.page = "home"

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
    st.markdown("<h1 style='text-align: center;'>🎛️ Welcome to Digital Music Equalizer</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Enhance your sound. Adjust bass, mids, and treble effortlessly.</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🎧 Start Now"):
        st.session_state.page = "equalizer"
        st.experimental_rerun()

# --- Equalizer Page ---
elif st.session_state.page == "equalizer":
    st.title("🎚️ Digital Music Equalizer")

    uploaded_file = st.file_uploader("Upload audio file (WAV or MP3)", type=["wav", "mp3"])

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 100:
            st.error("⚠️ File size exceeds 100 MB limit. Please upload a smaller file.")
        else:
            data, fs = load_audio(uploaded_file)
            st.audio(uploaded_file)

            st.subheader("Adjust Frequency Bands 🎚️")
            bass = st.slider("🎵 Bass (60–250 Hz)", 0.0, 2.0, 1.0, 0.1)
            mid = st.slider("🎶 Midrange (250 Hz – 4 kHz)", 0.0, 2.0, 1.0, 0.1)
            treble = st.slider("🎼 Treble (4–10 kHz)", 0.0, 2.0, 1.0, 0.1)

            output = apply_equalizer(data, fs, [bass, mid, treble])

            buf = io.BytesIO()
            sf.write(buf, output, fs, format='WAV')
            st.audio(buf, format='audio/wav')
            st.download_button("⬇️ Download Processed Audio", buf.getvalue(), file_name="equalized_output.wav")

            st.subheader("Waveform Visualization 📊")
            fig, ax = plt.subplots(figsize=(10, 3))
            time = np.linspace(0, len(output) / fs, num=len(output))
            ax.plot(time, output, color="gold", linewidth=0.5)
            ax.set_facecolor("black")
            fig.patch.set_facecolor("black")
            ax.set_xlabel("Time [s]", color='white')
            ax.set_ylabel("Amplitude", color='white')
            ax.set_title("Processed Audio Waveform", color='gold')
            ax.tick_params(colors='white')
            st.pyplot(fig)


