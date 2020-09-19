#!/usr/bin/env python

import tempfile

import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fft as fft

import pandas as pd

import pyroomacoustics as pra
import soundfile as sf


def main():
    st.sidebar.markdown("""
    ## Room shape
    """)
    room_type = st.sidebar.selectbox("Choose room type", ["ShoeBox", "from corners"])
    room_dim = st.sidebar.selectbox("Room dimention", ["2D", "3D"])

    room_fs = st.sidebar.number_input("Room sampling frequency", min_value=1, max_value=192000, value=16000)

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
            room = pra.ShoeBox(room_size, fs=room_fs, absorption=absorption, max_order=max_order)
        else:
            room_size = [x, y]
            room = pra.ShoeBox(room_size, fs=room_fs, absorption=absorption, max_order=max_order)
    elif room_type == "from corners":
        st.write("Not implemented")

    st.sidebar.markdown("""## Source""")
    src_num = st.sidebar.number_input("#source", min_value=0, value=0)
    src_fs = None
    wav_ary = []
    wav_name_ary = []
    if src_num > 0:
        src_loc_ary = []
        for i in range(src_num):
            wav = st.sidebar.file_uploader(f"source {i}", type="wav", encoding=None)
            if wav:
                sig, src_fs = sf.read(wav)
                if room_fs != src_fs:
                    st.write("room fs is different from source fs")
                wav_ary.append(sig)
                wav_name_ary.append(wav)
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
        room.add_microphone_array(pra.MicrophoneArray(R, fs=room_fs))

    """# room designer"""
    st.write(f"room fs: {room.fs}, source fs: {src_fs}")
    fig, ax = room.plot()
    ax.set_xlim([0, room_size[0]])
    ax.set_ylim([0, room_size[1]])
    if room_dim=="3D":
        ax.set_zlim([0, room_size[2]])
    st.pyplot(fig)

    ret = st.button("Simulate")
    if ret:
        room.simulate()

        st.write("source")
        st.audio(wav_name_ary[0])

        for i in range(mic_num):
            st.write(f"impulse response to mic{i}")
            st.line_chart(room.rir[i][0])

            fp = tempfile.NamedTemporaryFile()
            sf.write(fp.name, room.mic_array.signals[i], src_fs, format="wav")
            st.audio(fp.name)

if __name__ == '__main__':
    main()
