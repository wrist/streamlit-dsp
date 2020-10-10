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

@task
def run(c):
    c.run("poetry run streamlit run streamlit_dsp/app.py")

@task
def push_to_heroku(c):
    c.run("git push heroku heroku:main")

@task
def generate_requirements(c):
    c.run("poetry export -f requirements.txt --output requirements.txt")

@task
def set_heroku_buildpack(c):
    c.run("heroku buildpacks:clear")
    c.run("heroku buildpacks:add heroku-community/apt")
    c.run("heroku buildpacks:add heroku/python")
