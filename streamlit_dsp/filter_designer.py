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

import ast_util

def main():
    """
    # filter designer
    """

    # ==================================================
    # sidebar
    # ==================================================
    ft = st.sidebar.selectbox("Filter type", ["FIR", "IIR"])
    fs = st.sidebar.number_input("Sampling Frequency", min_value=1, max_value=192000, value=16000)

    eps = 1.e-12
    nyq_hz = fs / 2

    design_method = None
    num_taps = None
    if ft == "FIR":
        design_method = st.sidebar.selectbox("filter design method", ["firwin", "firwin2", "firls"])
        num_taps = st.sidebar.number_input("#tap", min_value=1, max_value=192000, value=128)
        filter_shape = st.sidebar.selectbox("filter shape", ["lowpass", "highpass", "bandpass", "bandstop"])

        cutoff_hz = None
        cutoff_hz_begin = None
        cutoff_hz_end = None
        if filter_shape == "bandpass":
            cutoff_hz_begin = st.sidebar.number_input("cutoff begin [Hz]", min_value=0.0, max_value=fs/2.0, value=100.0)
            cutoff_hz_end   = st.sidebar.number_input("cutoff end   [Hz]", min_value=0.0, max_value=fs/2.0, value=200.0)
            cutoff_hz = [cutoff_hz_begin, cutoff_hz_end]
        elif filter_shape == "bandstop":
            cutoff_hz_begin = st.sidebar.number_input("cutoff begin [Hz]", min_value=0.0, max_value=fs/2.0, value=100.0)
            cutoff_hz_end   = st.sidebar.number_input("cutoff end   [Hz]", min_value=0.0, max_value=fs/2.0, value=200.0)
            cutoff_hz = [cutoff_hz_begin, cutoff_hz_end, nyq_hz - 2.0 * eps, nyq_hz - eps]
        elif filter_shape == "highpass":
            cutoff_hz_begin = st.sidebar.number_input("cutoff [Hz]", min_value=0.0, max_value=fs/2.0, value=100.0)
            cutoff_hz_end = nyq_hz - 1.e-12
            cutoff_hz = [cutoff_hz_begin, cutoff_hz_end]
        else:
            cutoff_hz = st.sidebar.number_input("cutoff [Hz]", min_value=0.0, max_value=fs/2.0, value=100.0)
    elif ft == "IIR":
        design_method = st.sidebar.selectbox("filter design method", ["butter"])

    coeff_type = st.sidebar.selectbox("Coefficient type", ["ba", "zpk", "sos"])

    wav = st.sidebar.file_uploader("input wave file", type="wav", encoding=None)


    # ==================================================
    # body
    # ==================================================

    show_time_coeff = st.checkbox("time coefficient", value=True)
    show_freq_resp = st.checkbox("frequency response", value=True)
    show_phase_resp = st.checkbox("phase response", value=False)
    show_group_delay = st.checkbox("group delay", value=False)

    b = None
    a = None

    nfft = 1024
    worN = nfft // 2

    if design_method == "firwin":
        if filter_shape == "highpass":
            b = sg.firwin(num_taps, cutoff_hz, fs=fs, pass_zero=False)
        elif filter_shape == "bandpass":
            b = sg.firwin(num_taps, cutoff_hz, fs=fs, pass_zero=False)
        else:
            b = sg.firwin(num_taps, cutoff_hz, fs=fs)
    else:
        raise NotImplementedError

    if b is not None and ft == "FIR":

        w, h = sg.freqz(b, worN=worN)
        h_power = 20.0 * np.log10(np.abs(h))
        _, gd = sg.group_delay((b, [1.0]), w=w)
        phase = np.angle(h)

        f = (w / np.pi) * (fs / 2.0)


        if show_time_coeff:
            st.line_chart(b)

        if show_freq_resp:
            df_h = pd.DataFrame(h_power, index=f)
            st.line_chart(df_h)

        if show_phase_resp:
            df_phase = pd.DataFrame(phase, index=f)
            st.line_chart(df_phase)

        if show_group_delay:
            df_gd = pd.DataFrame(gd, index=f)
            st.line_chart(df_gd)

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
            raise NotImplementedError

    if wav:
        st.write("input wave file")
        st.audio(wav)
        if ft == "FIR":
            sig, wav_fs = sf.read(wav)
            #st.line_chart(sig)

            ys = sg.lfilter(b, [1.0], sig)

            st.write("filtered wave file")
            fp = tempfile.NamedTemporaryFile()
            sf.write(fp.name, ys, wav_fs, format="wav")
            st.audio(fp.name)
            #st.line_chart(ys)

    ret = st.button("generate code")
    if ret:
        fname = __file__
        src = ast_util.transform_file(
                fname,
                {"ft": ft,
                 "fs": fs,
                 "design_method": design_method,
                 "num_taps": num_taps,
                 "filter_shape": filter_shape,
                 "cutoff_hz_begin": cutoff_hz_begin,
                 "cutoff_hz_end": cutoff_hz_end,
                 "cutoff_hz": cutoff_hz,
                 "coeff_type": coeff_type,
                 "show_time_coeff": True,
                 "show_freq_resp": True,
                 "show_phase_resp": True,
                 "show_group_delay": True,
                 })

        st.write("""```python
{0}
```""".format(src))


if __name__ == '__main__':
    main()
