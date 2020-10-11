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
import st_util

st.set_option('deprecation.showfileUploaderEncoding', False)


def main():
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

    #wav = st.sidebar.file_uploader("input wave file", type="wav", encoding=None)
    wav_ary = st.sidebar.file_uploader("input wave file", type="wav", encoding=None, accept_multiple_files=True)


    # ==================================================
    # body
    # ==================================================
    st.write("# filter designer")

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
            st_util.st_my_line_chart(np.arange(len(b)), b, ["b"], "coeff index [pt]", "amplitude")

        if show_freq_resp:
            st_util.st_my_line_chart(f, h_power, ["h_power"], "frequency [Hz]", "power [dB]")

        if show_phase_resp:
            st_util.st_my_line_chart(f, phase, ["phase"], "frequency [Hz]", "phase angle [rad]")

        if show_group_delay:
            st_util.st_my_line_chart(f, gd, ["group delay"], "frequency [Hz]", "group delay [pt]")

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

    # ==================================================
    # processing for uploaded files
    # ==================================================

    st.write("# Processing for uploaded files")

    show_wave_amp = st.checkbox("show waveform", value=False)
    show_wave_freq = st.checkbox("show spectrogram", value=False)

    if wav_ary is not None:
        for i, wav in enumerate(wav_ary):
            st.write(f"input wave file{i}")
            st.audio(wav)
            if ft == "FIR":
                sig, wav_fs = sf.read(wav)

                ys = sg.lfilter(b, [1.0], sig)

                st.write(f"filtered wave file{i}")

                # FIXME: pass original filename as prefix but we can't get the name still
                # see: https://github.com/streamlit/streamlit/issues/896
                fp = tempfile.NamedTemporaryFile()
                sf.write(fp.name, ys, wav_fs, format="wav")
                st.audio(fp.name)

                href = st_util.get_binary_file_downloader_html(fp.name, "filtered wave file", ".wav")
                st.markdown(href, unsafe_allow_html=True)

                if show_wave_amp:
                    st.line_chart(sig)
                    st.line_chart(ys)

                if show_wave_freq:
                    f, t, Sxx = sg.spectrogram(sig, fs)
                    f2, t2, Sxx2 = sg.spectrogram(ys, fs)

                    fig, axes = plt.subplots(2,1)
                    axes[0].pcolormesh(t, f, Sxx)
                    axes[0].set_yscale("log")
                    axes[0].set_ylim([100.0, fs/2])
                    axes[0].set_ylabel("frequency [Hz]")
                    axes[0].set_xlabel("time [s]")

                    axes[1].pcolormesh(t2, f2, Sxx2)
                    axes[1].set_yscale("log")
                    axes[1].set_ylim([100.0, fs/2])
                    axes[1].set_ylabel("frequency [Hz]")
                    axes[1].set_xlabel("time [s]")

                    st.pyplot(fig)


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
