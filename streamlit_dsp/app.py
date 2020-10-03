#!/usr/bin/env python

import streamlit as st

import window_viewer
import filter_designer
import room_designer
import espnet2_loader

def main():
    ret = st.sidebar.radio("app", ["window viewer", "filter designer", "room designer", "espnet2_loader"])
    print(ret)

    if ret == "window viewer":
        window_viewer.main()
    elif ret == "filter designer":
        filter_designer.main()
    elif ret == "room designer":
        room_designer.main()
    elif ret == "espnet2_loader":
        espnet2_loader.main()


if __name__ == '__main__':
    main()
