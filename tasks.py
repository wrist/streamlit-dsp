from invoke import task

@task
def run_window_viewer(c):
    c.run("poetry run streamlit run streamlit_dsp/window_viewer.py")

@task
def run_filter_designer(c):
    c.run("poetry run streamlit run streamlit_dsp/filter_designer.py")

@task
def run_room_designer(c):
    c.run("poetry run streamlit run streamlit_dsp/room_designer.py")
