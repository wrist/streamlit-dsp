import streamlit as st

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.signal as sg
import scipy.fftpack as fft

import pandas as pd
#import soundifle as sf

if __name__ == '__main__':
    """
    # filter designer
    """

    ft = st.sidebar.selectbox("Filter type", ["FIR", "IIR"])
    coeff_type = st.sidebar.selectbox("Coefficient type", ["ba", "zpk", "sos"])

    wav = st.sidebar.file_uploader("input wave file", type="wav", encoding=None)

    if wav:
        st.audio(wav)

