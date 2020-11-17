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

import yaml

import time
import contextlib

from concurrent.futures import ThreadPoolExecutor
from io import StringIO

from espnet_model_zoo.downloader import ModelDownloader
from espnet2.bin.asr_inference import Speech2Text


def thread_func(model_name: str, sio: StringIO):
    d = ModelDownloader()
    #with contextlib.redirect_stdout(sio):
    with contextlib.redirect_stderr(sio):
        model_dict = d.download_and_unpack(model_name)

    speech2text = Speech2Text(**model_dict)
    return speech2text, model_dict


def main():
    model_name = st.sidebar.text_input("model name")
    st.sidebar.write('see [model names](https://github.com/espnet/espnet_model_zoo/blob/master/espnet_model_zoo/table.csv)')

    if model_name:
        shared_sio = StringIO()

        with ThreadPoolExecutor() as executor:
            st.write("Model downloading...")
            future = executor.submit(thread_func, model_name, shared_sio)

            # observe shared_sio
            placeholder = st.empty()
            while future.running():
                placeholder.empty()
                sio_str = shared_sio.getvalue()
                last_line = sio_str.split('\r')[-1]
                placeholder.write(last_line)
                time.sleep(1)

            placeholder.empty()
            sio_str = shared_sio.getvalue()
            last_line = sio_str.split('\r')[-1]
            placeholder.write(last_line)

            speech2text, model_dict = future.result()

        st.write("## Upload and decode")
        wav = st.file_uploader("wav", type=["wav", "flac"], encoding=None)

        if wav is not None:
            speech, rate = sf.read(wav)

            fp = tempfile.NamedTemporaryFile()
            sf.write(fp.name, speech, rate, format="wav")

            st.write(f"sampling rate: {rate}")
            st.audio(fp.name)
            st.line_chart(speech)

            ret = st.button("decode")
            if ret:
                nbests = speech2text(speech)
                st.write("### result")
                nbests_len = min([len(nbests), 3])
                for i, nbest in enumerate(nbests[:nbests_len]):
                    text, *_ = nbest
                    st.write(f"* [{i}]: {text}")

        # show model information
        st.write("## Model information")
        st.write(model_dict)

        st.write("## ASR Train Config:")
        with open(model_dict["asr_train_config"]) as fp:
            config = yaml.load(fp)
            st.write(config)

        st.write("## LM Train Config:")
        with open(model_dict["lm_train_config"]) as fp:
            config = yaml.load(fp)
            st.write(config)


if __name__ == '__main__':
    main()
