@echo off
cd /d "%~dp0"
echo Installing dependencies (only needed once)...
py -3.13 -m pip install -r requirements.txt 2>nul || py -3.12 -m pip install -r requirements.txt || python -m pip install -r requirements.txt
echo Starting Isekai Odyssey...
py -3.13 main.py 2>nul || py -3.12 main.py || python main.py
pause
