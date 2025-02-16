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

echo Playlist de singles... && echo.
mkdir "%ruta_descarga%%subF_playlist%\"
cd /d "%ruta_descarga%%subF_playlist%\"
yt-dlp --write-info-json --config-location "%ruta_config%singlelist.conf" ""!URL!""
endlocal
cd /d %ruta_actual%
