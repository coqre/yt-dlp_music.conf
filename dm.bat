@echo off
:: Define la ruta de descarga
set "ruta_descarga=C:\users\usuario\Downloads\caciones\"

:: Subcarpeta de descarga de Playlist.
set "subF_playlist=playlist"

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
    mkdir "%ruta_descarga%%subF_playlist%\"
    cd /d "%ruta_descarga%%subF_playlist%\"
    echo Descargando primer video para extraer caratula...
    musica --config-location "%ruta_config%precesar.conf" "!URL!"
	if errorlevel 1 (cd /d %ruta_actual% && exit /b 1)
	echo. && echo DESCARGANDO PLAYLIST. . . && echo.
    musica --config-location "%ruta_config%playlist.conf" "!URL!"
    del "cover.webp"
    echo cover.webp eliminado."
) else (
    echo NO es una playlist
    musica --config-location "%ruta_config%single.conf" "!URL!"
)

endlocal
cd /d %ruta_actual%
