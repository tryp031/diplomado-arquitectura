@echo off
REM Lanzador para doble clic. Delega en iniciar.ps1; nada de logica aqui.
REM -ExecutionPolicy Bypass evita que la politica por defecto de Windows bloquee
REM el script sin explicar por que: es solo para esta ejecucion, no cambia nada
REM en la maquina.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
if errorlevel 1 pause
