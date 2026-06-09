@echo off
REM TabBridge native-messaging host launcher (Windows).
REM Chrome registers THIS .bat as the host "path". It hands stdio to Python.
REM Relay address + token are read from the environment; set them for your user
REM (setx TABBRIDGE_RELAY "http://100.x.y.z:8765"  &  setx TABBRIDGE_TOKEN "...").
python "%~dp0tabbridge_host.py"
