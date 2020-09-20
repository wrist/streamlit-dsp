# streamlit-dsp

This repository will contain streamlit sample app for digital signal processing.

## how to run

You can run streamlit apps on your local machine from github repository directly.

```sh
$ pip install streamlit
$ pip install ...  # install dependencies, see pyproject.toml
$ streamlit run https://raw.githubusercontent.com/wrist/streamlit-dsp/master/streamlit_dsp/window_viewer.py
$ streamlit run https://raw.githubusercontent.com/wrist/streamlit-dsp/master/streamlit_dsp/filter_designer.py
$ streamlit run https://raw.githubusercontent.com/wrist/streamlit-dsp/master/streamlit_dsp/room_designer.py
```

## how to develop

### preparation

```sh
$ pip install poetry invoke  # if you don't install poetry and invoke
$ git clone https://github.com/wrist/streamlit-dsp.git
$ cd streamlit-dsp
$ poetry install
```

*notice*

The command `poetry install` usually tries to make a new venv then install the dependencies into the inside,
but if you already activate some virtualenv(including conda env), poetry try to use the virtualenv.

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
