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
    st.write("# window viewer")

    windows = ["boxcar", "triang", "blackman", "hamming", "hann", "bartlett", "flattop", "parzen", "bohman", "blackmanharris",
            "nuttall", "barthann", "kaiser", "gaussian", "general_gaussian", "slepian", "dpss", "chebwin", "exponential", "tukey"]

    #win_name = st.sidebar.selectbox("select window", windows, 4)
    win_names = st.sidebar.multiselect("select window", windows, [windows[4]])
    Nx = st.sidebar.selectbox("Window Length", [2**i for i in range(16)], 8)
    nfft = st.sidebar.selectbox("FFT Length", [2**i for i in range(16)], 10)
    fs = st.sidebar.number_input("Sampling Frequency", min_value=1.0, step=1.0, value=16000.0)

    eps = 1.e-16
    f = (fs / nfft) * np.arange(-nfft/2, nfft/2)

    # TODO: need to add UI for other windows require extra parameters
    win_ary = []
    W_power_ary = []

    for win_name in win_names:
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
        W_power = fft.fftshift(W_power)

        win_ary.append(win)
        W_power_ary.append(W_power)

    # ==================================================
    # using matplotlib
    # ==================================================
    # fig, axes = plt.subplots(2, 1)

    # for win in win_ary:
    #     axes[0].plot(win)
    # for W_power in W_power_ary:
    #     axes[1].plot(f, W_power)

    # axes[0].grid(b=True)
    # axes[1].grid(b=True)
    # axes[1].set_ylim([-140.0, 10.0])

    # st.pyplot(fig)

    # ==================================================
    # using st.line_chart
    # ==================================================
    df_win = pd.DataFrame(np.array(win_ary).T,
                          index=np.arange(Nx),
                          columns=win_names)

    df_freq = pd.DataFrame(data=np.array(W_power_ary).T,
                           index=f,
                           columns=win_names)

    #st.line_chart(df_win)
    #st.line_chart(df_freq)

    # ==================================================
    # using st.altair_chart
    # see: https://github.com/streamlit/streamlit/issues/1129
    #      https://github.com/altair-viz/altair/issues/271
    # ==================================================
    df_win_melt = df_win.reset_index().melt("index", var_name="windows", value_name="y")
    c = alt.Chart(df_win_melt).mark_line().encode(
            alt.X("index", title="coeff index"),
            alt.Y("y", title="amplitude"),
            tooltip=["index", "y"],
            color='windows:N'
            ).interactive()
    st.altair_chart(c, use_container_width=True)

    df_freq_melt = df_freq.reset_index().melt("index", var_name="windows_power", value_name="y")
    c = alt.Chart(df_freq_melt).mark_line().encode(
            alt.X("index", title="frequency [Hz]"),
            alt.Y("y", title="power [dB]", scale=alt.Scale(domain=[-140, 10])),
            tooltip=["index", "y"],
            color='windows_power:N'
            ).interactive()
    st.altair_chart(c, use_container_width=True)


    # ==================================================
    # show information
    # ==================================================
    st.write("## windows information")
    st.write("{0}, win.shape: {1}, W.shape: {2}".format(win_names, win.shape, W.shape))
    st.write("df_win")
    st.write(df_win)
    st.write("df_win_melt")
    st.write(df_win_melt)
    st.write("df_freq")
    st.write(df_freq)
    st.write("df_freq_melt")
    st.write(df_freq_melt)


if __name__ == '__main__':
    main()
