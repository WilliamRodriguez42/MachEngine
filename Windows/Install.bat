@echo off

setlocal
cd /d %~dp0

pip install PyOpenGL PyQt5 numpy pillow lxml libaudioverse

cd ..\pyinstaller-develop\

python setup.py install
