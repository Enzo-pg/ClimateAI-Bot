
@echo off
title ClimateAI - Inicializador
color 0A

echo =====================================
echo          CLIMATEAI BOT
echo =====================================
echo.

cd /d "%~dp0"

if not exist "bot.py" (
    echo ERRO: bot.py nao encontrado!
    pause
    exit /b
)

if not exist ".env" (
    echo ERRO: arquivo .env nao encontrado!
    echo Crie o arquivo com DISCORD_TOKEN e GUILD_ID.
    pause
    exit /b
)

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo Python nao encontrado!
    pause
    exit /b
)

echo.
echo [2/3] Instalando dependencias...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo Falha ao instalar dependencias!
    pause
    exit /b
)

echo.
echo [3/3] Iniciando ClimateAI...
echo.
python bot.py

echo.
echo ClimateAI foi encerrado.
pause
