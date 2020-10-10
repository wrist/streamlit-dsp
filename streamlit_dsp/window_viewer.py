import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fftpack as fft

import pandas as pd
#import soundifle as sf

import altair as alt


def kaiser_beta(sl_dB):
    try:
        return sg.kaiser_beta(sl_dB)
    except:
        if sl_dB > 50.0:
            return 0.1102 * (sl_dB - 8.7)
        elif sl_dB > 21.0:
            return 0.5842 * ((sl_dB - 21.0) ** 0.4) + 0.07886 * (sl_dB - 21.0)
        else:
            return 0.0


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

    win_ary = []
    W_power_ary = []

    for win_name in win_names:
        win_arg = None
        if win_name == "kaiser":
            st.sidebar.write("## kaiser window option")
            sl_dB = st.sidebar.number_input("sidelobe attenuation [dB]", value=30.0, min_value=0.0)
            beta = kaiser_beta(sl_dB)
            st.sidebar.write("beta = {0}".format(beta))
            win_arg = (win_name, beta)
        elif win_name == "gaussian":
            st.sidebar.write("## gaussian window option")
            std_dev = st.sidebar.number_input("standard deviation", value=1.0, min_value=0.0)
            win_arg = (win_name, std_dev)
        elif win_name == "general_gaussian":
            st.sidebar.write("## general gaussian window option")
            power = st.sidebar.number_input("power", value=1.0)
            std_dev = st.sidebar.number_input("standard deviation", value=1.0, min_value=0.0)
            win_arg = (win_name, power, std_dev)
        elif win_name == "slepian":
            st.sidebar.write("## slepian window option")
            band_width = st.sidebar.number_input("band width", value=0.5)
            win_arg = (win_name, band_width)
        elif win_name == "dpss":
            st.sidebar.write("## dpss window option")
            raise NotImplementedError
        elif win_name == "chebwin":
            st.sidebar.write("## chebwin window option")
            attenuation = st.sidebar.number_input("attenuation [dB]", value=60.0, min_value=0.0)
            win_arg = (win_name, attenuation)
        elif win_name == "exponential":
            st.sidebar.write("## exponential window option")
            use_center = st.sidebar.checkbox("Use center", False)
            center = st.sidebar.number_input("center", value=Nx/2, min_value=0.0) if use_center else None
            tau = st.sidebar.number_input("tau", value=1.0, min_value=0.0)
            win_arg = (win_name, center, tau)
        elif win_name == "tukey":
            st.sidebar.write("## tukey window option")
            alpha = st.sidebar.number_input("alpha", value=0.5, min_value=0.0)
            win_arg = (win_name, alpha)
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
