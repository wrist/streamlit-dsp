#!/usr/bin/env python

import tempfile

import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fft as fft

import pandas as pd
import soundfile as sf

if __name__ == '__main__':
    """
    # filter designer
    """

    ft = st.sidebar.selectbox("Filter type", ["FIR", "IIR"])
    fs = st.sidebar.number_input("Sampling Frequency", min_value=1, max_value=192000, value=16000)

    design_method = None
    num_taps = None
    if ft == "FIR":
        design_method = st.sidebar.selectbox("filter design method", ["firwin", "firwin2", "firls"])
        num_taps = st.sidebar.number_input("#tap", min_value=1, max_value=192000, value=1)
        filter_shape = st.sidebar.selectbox("filter shape", ["lowpass", "highpass", "bandpass", "bandstop"])
        cutoff_hz = st.sidebar.number_input("cutoff [Hz]", min_value=0.0, max_value=fs/2.0, value=0.0)
    elif ft == "IIR":
        design_method = st.sidebar.selectbox("filter design method", ["butter"])

    b = None
    a = None

    nfft = 1024
    worN = nfft // 2

    if design_method == "firwin":
        b = sg.firwin(num_taps, cutoff_hz, fs=fs)

    if b is not None:
        coeff_type = st.sidebar.selectbox("Coefficient type", ["ba", "zpk", "sos"])

        w, h = sg.freqz(b, worN=worN)
        h_power = 20.0 * np.log10(np.abs(h))

        f = (w / np.pi) * (fs / 2.0)
        df_h = pd.DataFrame(data = h_power, index= f)

        st.line_chart(b)
        st.line_chart(df_h)

        st.write(f"{ft} coefficient as {coeff_type}")

        if coeff_type == "ba":
            df = pd.DataFrame(data = b, columns=["b"])
            st.dataframe(df)
        elif coeff_type == "zpk":
            z, p, k = sg.tf2zpk(b, [1.0])
            zs = [str(zi) for zi in z]

            df = pd.DataFrame(zs, columns=["z"])
            st.write("z")
            st.dataframe(df)

            df = pd.DataFrame(p, columns=["p"])
            st.write("p")
            st.dataframe(df)

            df = pd.DataFrame([k], columns=["k"])
            st.write("k")
            st.dataframe(df)
        elif coeff_type == "sos":
            st.write("not implemented")

    wav = st.sidebar.file_uploader("input wave file", type="wav", encoding=None)

    if wav:
        st.write("input wave file")
        st.audio(wav)
        if ft == "FIR":
            sig, wav_fs = sf.read(wav)
            ys = sg.lfilter(b, [1.0], sig)

            st.write("filtered wave file")
            fp = tempfile.NamedTemporaryFile()
            sf.write(fp.name, ys, wav_fs, format="wav")
            st.audio(fp.name)
