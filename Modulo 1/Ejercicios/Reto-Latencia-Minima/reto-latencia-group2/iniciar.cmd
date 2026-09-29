@echo off
REM Lanzador para doble clic. Delega en iniciar.ps1; nada de logica aqui.
REM -ExecutionPolicy Bypass vale solo para esta ejecucion; no cambia la maquina.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
if errorlevel 1 pause
