@echo off
rem Lo lanza una tarea programada de Windows (sin Claude, sin tokens): sube el siguiente Short de la cola en el hueco indicado.
rem Uso: subir_programado.bat 09:15 [N]   (hora(s) UTC del hueco, separadas por comas; N = cuántos, def. 1)
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set N=%2
if "%N%"=="" set N=1
echo ==== %date% %time% hueco %~1 >> "..\output\subida_programada.log"
python subir_shorts.py subir %N% --huecos %~1 --sep 60 >> "..\output\subida_programada.log" 2>&1
