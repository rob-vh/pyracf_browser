# browser front-end for pyracf

## installation steps

This web app is constructed with [streamlit](https://streamlit.io/), so make sure you have this installed:

`pip3 install streamlit`

Also, the most recent version of pyracf is needed (not the one from pypi), so install from [github](https://github.com/rob-vh/pyracf)

After installing this pyracf, edit file main.toml:

* specify the path to pyracf (unless you have pyracf installed from a fully fledged pypi, then leave this value empty or comment it out)

* specify a path to a RACF (IRRDBU00) unload file

## start the app

Start a terminal in the directory containing main.py and issue:

`streamlit run main.py`

