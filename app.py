import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pywt
from scipy.fftpack import fft
from scipy.stats import kurtosis, skew
import websocket
import json

# Page configuration
st.set_page_config(page_title="Fault Analysis with DWT and FFT", layout="wide")

# WebSocket server settings
WEBSOCKET_URL = "ws://0.0.0.0:9090"  # Use uppercase for constants


# Connect to WebSocket server
def fetch_vibration_data():
    """
    Fetch vibration data from the WebSocket server.
    Returns:
        pd.DataFrame: DataFrame containing vibration data.
    """
    try:
        ws = websocket.create_connection(WEBSOCKET_URL)
        st.success("Connected to WebSocket server.")
        vibration_records = []
        for _ in range(500):  # Limit to 500 samples for real-time analysis
            message = ws.recv()
            vibration = json.loads(message)
            vibration_records.append(vibration)
        ws.close()
        return pd.DataFrame(vibration_records)
    except Exception as e:
        st.error(f"Error connecting to WebSocket server: {e}")
        return pd.DataFrame()


# FFT analysis
def perform_fft(vibration_values, sampling_rate):
    """
    Perform FFT analysis on the vibration data.
    Args:
        vibration_values (list or np.array): Vibration data values.
        sampling_rate (int): Sampling rate of the data.
    Returns:
        tuple: Frequencies and their corresponding amplitudes.
    """
    n_samples = len(vibration_values)
    fft_values = fft(vibration_values)
    frequencies = np.fft.fftfreq(n_samples, d=1 / sampling_rate)
    return frequencies[:n_samples // 2], np.abs(fft_values[:n_samples // 2])


# DWT analysis
def perform_dwt(vibration_values, wavelet="db4"):
    """
    Perform DWT analysis on the vibration data.
    Args:
        vibration_values (list or np.array): Vibration data values.
        wavelet (str): Wavelet type for analysis.
    Returns:
        list: List of wavelet coefficients at each decomposition level.
    """
    return pywt.wavedec(vibration_values, wavelet, level=4)


# Statistical analysis
def perform_statistical_analysis(vibration_values):
    """
    Perform statistical analysis on vibration data.
    Args:
        vibration_values (list or np.array): Vibration data values.
    Returns:
        dict: Dictionary containing statistical metrics.
    """
    stats = {
        "Mean": np.mean(vibration_values),
        "Std Dev": np.std(vibration_values),
        "Skewness": skew(vibration_values),
        "Kurtosis": kurtosis(vibration_values),
        "Max": np.max(vibration_values),
        "Min": np.min(vibration_values),
    }
    return stats


# Main app
def main():
    st.title("Vibration Fault Identification and Analysis")
    st.sidebar.header("Settings")
    user_sampling_rate = st.sidebar.number_input("Sampling Rate (Hz)", value=1600, step=100)

    # Fetch data
    vibration_df = fetch_vibration_data()
    if not vibration_df.empty:
        st.subheader("Raw Vibration Data")
        st.line_chart(vibration_df)

        # Analyze X-axis vibration data
        x_vibration = vibration_df["x"]
        st.subheader("FFT Analysis")
        freqs, fft_values = perform_fft(x_vibration, user_sampling_rate)
        fig, ax = plt.subplots()
        ax.plot(freqs, fft_values)
        ax.set_title("Frequency Spectrum")
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        st.pyplot(fig)

        st.subheader("DWT Analysis")
        dwt_coeffs = perform_dwt(x_vibration)
        for i, coeff in enumerate(dwt_coeffs):
            st.line_chart(coeff, height=100)

        st.subheader("Statistical Analysis")
        stats = perform_statistical_analysis(x_vibration)
        st.json(stats)


if __name__ == "__main__":
    main()
