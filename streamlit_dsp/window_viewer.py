import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fftpack as fft

import pandas as pd
#import soundifle as sf

import altair as alt

def main():
    """
    # window viewer
    """

    windows = ["boxcar", "triang", "blackman", "hamming", "hann", "bartlett", "flattop", "parzen", "bohman", "blackmanharris",
            "nuttall", "barthann", "kaiser", "gaussian", "general_gaussian", "slepian", "dpss", "chebwin", "exponential", "tukey"]

    win_name = st.sidebar.selectbox("select window", windows, 4)
    Nx = st.sidebar.selectbox("Window Length", [2**i for i in range(16)], 8)
    nfft = st.sidebar.selectbox("FFT Length", [2**i for i in range(16)], 10)
    fs = st.sidebar.number_input("Sampling Frequency", min_value=1.0, step=1.0, value=16000.0)

    eps = 1.e-16

    # TODO: need to add UI for other windows require extra parameters
    win_arg = None
    if win_name in ["kaiser"]:
        beta = st.sidebar.number_input("beta")
        win_arg = (win_name, beta)
    else:
        win_arg = win_name

    win = sg.get_window(win_arg, Nx)

    W = fft.fft(win, nfft)
    W_power = 20.0 * np.log10(np.abs(W) + eps)
    W_power -= W_power[0]

    f = (fs / nfft) * np.arange(-nfft/2, nfft/2)

    # ==================================================
    # using matplotlib
    # ==================================================
    #fig, axes = plt.subplots(2, 1)

    #axes[0].plot(win)
    #axes[0].grid(b=True)

    #axes[1].plot(f, fft.fftshift(W_power))
    #axes[1].grid(b=True)
    #axes[1].set_ylim([-120.0, 10.0])

    #st.pyplot(fig)

    # ==================================================
    # using st.line_chart
    # ==================================================
    #st.line_chart(win)

    #df = pd.DataFrame(data=fft.fftshift(W_power), index=f)
    #st.line_chart(df)

    # ==================================================
    # using st.altair_chart
    # ==================================================
    df = pd.DataFrame({"x": np.arange(Nx), "y": win})
    c = alt.Chart(df).mark_line().encode(
            alt.X("x", title="coeff index"),
            alt.Y("y", title="amplitude"),
            tooltip=["x", "y"]
            ).interactive()
    st.altair_chart(c, use_container_width=True)

    df = pd.DataFrame({"x": f, "y": fft.fftshift(W_power)})

    c = alt.Chart(df).mark_line().encode(
            alt.X("x", title="frequency [Hz]"),
            alt.Y("y", title="power [dB]", scale=alt.Scale(domain=[-140, 10])),
            tooltip=["x", "y"]
            ).interactive()
    st.altair_chart(c, use_container_width=True)


    st.write("{0}, win.shape: {1}, W.shape: {2}".format(win_name, win.shape, W.shape))

if __name__ == '__main__':
    main()
