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

import ast_util


def st_create_room(room_type, room_dim, room_fs, absorption, max_order):
    room = None
    room_size = None

    if room_type == "ShoeBox":
        rx = st.sidebar.slider("x", min_value=0.0, max_value=100.0)
        ry = st.sidebar.slider("y", min_value=0.0, max_value=100.0)
        if room_dim == "3D":
            rz = st.sidebar.slider("z", min_value=0.0, max_value=100.0)
            room_size = [rx, ry, rz]
            room = pra.ShoeBox(room_size, fs=room_fs, absorption=absorption, max_order=max_order)
        else:
            room_size = [rx, ry]
            room = pra.ShoeBox(room_size, fs=room_fs, absorption=absorption, max_order=max_order)
    elif room_type == "from corners":
        st.write("Not implemented")

    return (room, room_size)


def st_source_setting(room_dim, room_size):
    wav_ary = []
    src_loc_ary = []

    src_num = st.sidebar.number_input("#source", min_value=0, value=0)

    if src_num > 0:
        for i in range(src_num):
            # wave file upload
            wav_filelike = st.sidebar.file_uploader(f"source {i}", type="wav", encoding=None)
            if wav_filelike:
                sig, src_fs = sf.read(wav_filelike)
                wav_ary.append((wav_filelike, sig, src_fs))
            else:
                wav_ary.append(None)

            # source position
            sx = st.sidebar.slider("x", min_value=0.0, max_value=room_size[0], key=f"src{i}_x")
            sy = st.sidebar.slider("y", min_value=0.0, max_value=room_size[1], key=f"src{i}_y")

            if room_dim == "3D":
                sz = st.sidebar.slider("z", min_value=0.0, max_value=room_size[2], key=f"src{i}_z")
                src_loc_ary.append([sx, sy, sz])
            else:
                src_loc_ary.append([sx, sy])

    return (wav_ary, src_loc_ary)


def st_mic_setting(room_dim, room_size):
    mic_loc_ary = []

    mic_num = st.sidebar.number_input("#mic", min_value=0, value=0)
    if mic_num > 0:
        for i in range(mic_num):
            st.sidebar.write(f"mic {i}")
            mx = st.sidebar.slider("x", min_value=0.0, max_value=room_size[0], key=f"mic{i}_x")
            my = st.sidebar.slider("y", min_value=0.0, max_value=room_size[1], key=f"mic{i}_y")
            if room_dim == "3D":
                mz = st.sidebar.slider("z", min_value=0.0, max_value=room_size[2], key=f"mic{i}_z")
                mic_loc_ary.append([mx, my, mz])
            else:
                mic_loc_ary.append([mx, my])

    return mic_loc_ary


def main():
    # ==================================================
    # room setting
    # ==================================================
    st.sidebar.write("## Room shape")

    room_type = st.sidebar.selectbox("Choose room type", ["ShoeBox", "from corners"])
    room_dim = st.sidebar.selectbox("Room dimention", ["2D", "3D"])

    room_fs = st.sidebar.number_input("Room sampling frequency", min_value=1, max_value=192000, value=16000)

    max_order = st.sidebar.number_input("max order", min_value=0, value=1)
    absorption = st.sidebar.number_input("absorption", min_value=0.0, max_value=1.0)

    room, room_size = st_create_room(room_type, room_dim, room_fs, absorption, max_order)

    # ==================================================
    # source setting
    # ==================================================
    st.sidebar.write("## Source")

    wav_loc_tup = st_source_setting(room_dim, room_size)

    wav_ary = wav_loc_tup[0]  # list of (filelike, ndarray, fs)
    src_loc_ary = wav_loc_tup[1]

    # add sources to room
    src_fs = None
    for src_loc, wav_tup in zip(src_loc_ary, wav_ary):
        R = np.array(src_loc).T
        if wav_tup is not None:
            src_fs = wav_tup[2]
            if room_fs != src_fs:
                st.write("room fs is different from source fs")

            room.add_source(R, signal=wav_tup[1])
        else:
            room.add_source(R)

    # ==================================================
    # microphone setting
    # ==================================================
    st.sidebar.write("## Microphone")
    mic_loc_ary = st_mic_setting(room_dim, room_size)
    mic_num = len(mic_loc_ary)

    if len(mic_loc_ary) > 0:
        R = np.array(mic_loc_ary).T
        room.add_microphone_array(pra.MicrophoneArray(R, fs=room_fs))

    # ==================================================
    # body
    # ==================================================
    st.write("# room designer")
    st.write(f"room fs: {room.fs}, source fs: {src_fs}")

    fig, ax = room.plot()
    ax.set_xlim([0, room_size[0]])
    ax.set_ylim([0, room_size[1]])
    if room_dim=="3D":
        ax.set_zlim([0, room_size[2]])
    st.pyplot(fig)

    # ==================================================
    # simulation
    # ==================================================
    ret = st.button("Simulate")
    if ret:
        exist_all_src = all([wav_tup is not None for wav_tup in wav_ary])

        if exist_all_src:
            room.simulate()
            for si, wav_tup in enumerate(wav_ary):
                if wav_tup is not None:
                    st.write(f"source {si}")
                    st.audio(wav_tup[0])
        else:
            room.compute_rir()

        for mi in range(mic_num):
            for si, wav_tup in enumerate(wav_ary):
                st.write(f"impulse response from source{si} to mic{mi}")
                st.line_chart(room.rir[mi][si])

            if room.mic_array.signals is not None:
                st.write(f"microphone{mi} observed signal")
                fp = tempfile.NamedTemporaryFile()
                sf.write(fp.name, room.mic_array.signals[mi], src_fs, format="wav")
                st.audio(fp.name)

    # ==================================================
    # code generation
    # ==================================================
    ret = st.button("generate code")
    if ret:
        fname = __file__
        src = ast_util.transform_file(
                fname,
                {
                    "room_type": room_type,
                    "room_dim": room_dim,
                    "room_fs": room_fs,
                    "max_order": max_order,
                    "absorption": absorption,
                    "wav_loc_tup" : None,
                    "wav_ary": wav_loc_tup[0],
                    "src_loc_ary": wav_loc_tup[1],
                    "mic_loc_ary" : mic_loc_ary,
                 })

        st.write("""```python
{0}
```""".format(src))

if __name__ == '__main__':
    main()
