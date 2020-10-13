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

import contextlib
from functools import wraps
from io import StringIO

from espnet_model_zoo.downloader import ModelDownloader
from espnet2.bin.asr_inference import Speech2Text


# https://github.com/streamlit/streamlit/issues/268
def capture_output(func):
    """Capture output from running a function and write using streamlit."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Redirect output to string buffers
        stdout, stderr = StringIO(), StringIO()
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                return func(*args, **kwargs)
        except Exception as err:
            st.write(f"Failure while executing: {err}")
        finally:
            _stdout = stdout.getvalue()
            if _stdout:
                st.write("Execution stdout:")
                st.code(_stdout)

            _stderr = stderr.getvalue()
            if _stderr:
                st.write("Execution stderr:")
                st.code(_stderr)

    return wrapper


def download_model(model_name):
    d = ModelDownloader()
    st.write("Model downloading...")

    downloader_wrapper = capture_output(d.download_and_unpack)
    model_dict = downloader_wrapper(model_name)

    speech2text = Speech2Text(**model_dict)
    return speech2text, model_dict


def main():
    model_name = st.sidebar.text_input("model name")
    st.sidebar.write('see [model names](https://github.com/espnet/espnet_model_zoo/blob/master/espnet_model_zoo/table.csv)')

    if model_name:
        speech2text, model_dict = download_model(model_name)

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
