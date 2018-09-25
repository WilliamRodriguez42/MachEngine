@echo off

setlocal
cd /d %~dp0
cd ..\Project

rmdir /S /Q __pycache__ build dist
del /F /Q main.spec

python ../pyinstaller-develop/PyInstaller.py main.py

IF EXIST dist\main (
  robocopy resources dist\main\resources /e
)