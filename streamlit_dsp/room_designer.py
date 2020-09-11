#!/usr/bin/env python

import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fft as fft

import pandas as pd

import pyroomacoustics as pra
import soundfile as sf


if __name__ == '__main__':
    st.sidebar.markdown("""
    ## Room shape
    """)
    room_type = st.sidebar.selectbox("Choose room type", ["ShoeBox", "from corners"])
    room_dim = st.sidebar.selectbox("Room dimention", ["2D", "3D"])

    max_order = st.sidebar.number_input("max order", min_value=0, value=1)
    absorption = st.sidebar.number_input("absorption", min_value=0.0, max_value=1.0)

    room = None
    room_size = None
    if room_type == "ShoeBox":
        x = st.sidebar.slider("x", min_value=0.0, max_value=100.0)
        y = st.sidebar.slider("y", min_value=0.0, max_value=100.0)
        if room_dim == "3D":
            z = st.sidebar.slider("z", min_value=0.0, max_value=100.0)
            room_size = [x, y, z]
            room = pra.ShoeBox(room_size, absorption=absorption, max_order=max_order)
        else:
            room_size = [x, y]
            room = pra.ShoeBox(room_size, absorption=absorption, max_order=max_order)
    elif room_type == "from corners":
        pass

    st.sidebar.markdown("""## Source""")
    src_num = st.sidebar.number_input("#source", min_value=0, value=0)
    if src_num > 0:
        src_loc_ary = []
        wav_ary = []
        for i in range(src_num):
            wav = st.sidebar.file_uploader(f"source {i}", type="wav", encoding=None)
            if wav:
                sig, fs = sf.read(wav)
                wav_ary.append(sig)
            x = st.sidebar.slider("x", min_value=0.0, max_value=room_size[0], key=f"src{i}_x")
            y = st.sidebar.slider("y", min_value=0.0, max_value=room_size[1], key=f"src{i}_y")
            if room_dim == "3D":
                z = st.sidebar.slider("z", min_value=0.0, max_value=room_size[2], key=f"src{i}_z")
                src_loc_ary.append([x, y, z])
            else:
                src_loc_ary.append([x, y])

        if len(wav_ary) > 0:
            R = np.array(src_loc_ary).T
            room.add_source(R, signal=wav_ary[0])

    st.sidebar.markdown("""## Microphone""")
    mic_num = st.sidebar.number_input("#mic", min_value=0, value=0)
    if mic_num > 0:
        mic_loc_ary = []
        for i in range(mic_num):
            st.sidebar.write(f"mic {i}")
            x = st.sidebar.slider("x", min_value=0.0, max_value=room_size[0], key=f"mic{i}_x")
            y = st.sidebar.slider("y", min_value=0.0, max_value=room_size[1], key=f"mic{i}_y")
            if room_dim == "3D":
                z = st.sidebar.slider("z", min_value=0.0, max_value=room_size[2], key=f"mic{i}_z")
                mic_loc_ary.append([x, y, z])
            else:
                mic_loc_ary.append([x, y])

        R = np.array(mic_loc_ary).T
        room.add_microphone_array(pra.MicrophoneArray(R, fs=room.fs))

    """# room designer"""
    fig, ax = room.plot()
    st.pyplot(fig)

    ret = st.button("Simulate")
    if ret:
        room.simulate()
        st.line_chart(room.rir[0][0])
