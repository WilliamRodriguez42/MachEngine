@echo off

where python

IF %ERRORLEVEL% NEQ 0 (
  echo ERRORLEVEL
  echo Please install python version 3.7.0 from https://www.python.org/downloads/release/python-370/
  echo Make sure "Add Python 3.7.0 to PATH" is enabled on the first page of the installer
  echo Click "Disable path length limit" when the installation is done
  GOTO:eof
)

for /f "tokens=*" %%a in (
'PyVersion.bat'
) do (
set PYTHON_CORRECT=%%a
)

IF NOT "%PYTHON_CORRECT%" == "Python 3.7.0" (
  echo INCORRECT VERSION
  python -V
  echo Please install python version 3.7.0 from https://www.python.org/downloads/release/python-370/
  echo Make sure "Add Python 3.7.0 to PATH" is enabled on the first page of the installer
  echo Click "Disable path length limit" when the installation is done
  GOTO:eof
)
