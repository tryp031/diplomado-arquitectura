@echo off
REM Diagnostico de esta maquina, para doble clic.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" -Doctor
