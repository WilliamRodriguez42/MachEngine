@echo off

setlocal
cd /d %~dp0

python -m pip install --upgrade pip
pip install PyOpenGL PyQt5 numpy pillow lxml

cd ..\pyinstaller-develop\

python setup.py install