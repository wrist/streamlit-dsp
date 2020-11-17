# streamlit-dsp

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/wrist/streamlit-dsp/sharing/streamlit_dsp/app.py)

This repository will contain streamlit sample app for digital signal processing.

## how to run

### preparation

```sh
$ pip install poetry invoke  # if you don't install poetry and invoke
$ git clone https://github.com/wrist/streamlit-dsp.git
$ cd streamlit-dsp
$ poetry install
```

*notice*

The command `poetry install` usually tries to make a new venv then install the dependencies into the inside,
but if you already activate some virtualenv(including conda env), poetry tries to use the virtualenv.

### run apps

``` sh
$ inv run
```

You can run each apps separately like below.

``` sh
$ inv run-window-viewer
$ inv run-filter-designer
$ inv run-room-designer
```
