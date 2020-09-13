# streamlit-dsp

This repository will contain streamlit sample app for digital signal processing.

## how to use

### preparation

```sh
$ pip install poetry invoke  # if you don't install poetry and invoke
$ git clone https://github.com/wrist/streamlit-dsp.git
$ cd streamlit-dsp
$ poetry install
```

The command `poetry install` usually tries to make new venv and install the dependencies unless you already activate some virtual-env.

### run apps

``` sh
$ inv run-window-viewer
$ inv run-filter-designer
$ inv run-room-designer
```
