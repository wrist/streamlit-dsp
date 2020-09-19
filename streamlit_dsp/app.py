#!/usr/bin/env python

import streamlit as st

import window_viewer
import filter_designer
import room_designer

def main():
    ret = st.sidebar.radio("app", ["window viewer", "filter designer", "room designer"])
    print(ret)

    if ret == "window viewer":
        window_viewer.main()
    elif ret == "filter designer":
        filter_designer.main()
    elif ret == "room designer":
        room_designer.main()

if __name__ == '__main__':
    main()
