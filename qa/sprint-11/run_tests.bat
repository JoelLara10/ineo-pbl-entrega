@echo off
setlocal
set "PYTHON_EXE=C:\Users\al222\AppData\Local\Programs\Python\Python311\python.exe"

if not exist ".venv-sprint11\Scripts\python.exe" (
  "%PYTHON_EXE%" -m venv .venv-sprint11 || exit /b 1
)

.venv-sprint11\Scripts\python.exe -m pip install -r qa\sprint-11\requirements.txt || exit /b 1
.venv-sprint11\Scripts\python.exe -m pytest qa\sprint-11 -v -c qa\sprint-11\pytest.ini --junitxml=qa\sprint-11\reports\resultados-locales.xml
exit /b %errorlevel%
