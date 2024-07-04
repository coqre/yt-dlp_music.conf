@echo off
:: Define la ruta de descarga
set "ruta_descarga=C:\users\usuario\Downloads\caciones\"

:: Subcarpeta de descarga de Playlist.
set "subF_playlist=default"

::La ruta a los archivos de configuración de yt-dlp.
set "ruta_config=C:\Program Files\yt-dlp\yt-dlp_music\"

:: Los siguientes argumentos se editan mejor en config.py para mayor versatilidad.
:: - 	Nombre de archivo temporal
:: - 	Nombre de carátula
:: - 	Tamaño máximo de carátula
:: - 	Calidad mínima de carátula
:: -------------------------------------------------------------------------------------------------------------------------------------------------------------

set "ruta_actual=%cd%"
cd /d %ruta_descarga%
setlocal enabledelayedexpansion

set "URL=%*"

echo !URL! | findstr /C:"playlist?list" > nul
if !errorlevel! equ 0 (
    echo ES una playlist
    if "!subF_playlist!" == "default" (for /f "delims=" %%i in ('yt-dlp --no-config --print ^%%(album^)s --playlist-items 1 !URL! 2^>nul') do set "subF_playlist=%%i")
    mkdir "%cd%\!subF_playlist!" && cd "%cd%\!subF_playlist!"
    echo Descargando primer video para extraer caratula...
    yt-dlp --config-location "%ruta_config%precesar.conf" ""!URL!""
	if errorlevel 1 (cd /d %ruta_actual% && exit /b 1)
	echo. && echo DESCARGANDO PLAYLIST. . . && echo.
    yt-dlp --config-location "%ruta_config%playlist.conf" ""!URL!""
    del "cover.webp"
    echo cover.webp eliminado.
) else (
    echo NO es una playlist
    yt-dlp --config-location "%ruta_config%single.conf" ""!URL!""
)

endlocal
cd /d %ruta_actual%
