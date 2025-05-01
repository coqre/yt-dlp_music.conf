import ctypes
import os
import sys

# ----------------------------------------------------------------------------------


# CONFIGURACIÓN GLOBAL DE YT-DLP_MUSICA

ruta_de_configuracion = "C:\\Program Files\\yt-dlp\\yt-dlp_music\\"
ruta_de_descarga = "C:\\users\\usuario\\Downloads\\caciones\\"
subcarpeta_playlist = "default"
archivo_temporal = "audio_temp"
nombre_de_cover = "cover"
formato_de_cover = "webp"   # Solo adminte webp (con cwebp), jpg (con jpegoptim), y png (con pngquant). Tome como referencia los .py "procesar_" para usar otros formatos. Agréguelo a Formatos permitidos.
peso_maximo_de_cover = "1300"
calidad_minina_de_cover = "80"
liricas = "s"       # "s" = Sí, "n" = No.


# ----------------------------------------------------------------------------------

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

# Formatos de cover permitidos.
if formato_de_cover not in ["webp", "png", "jpg"]:
    print(f'Formato de cover no válido: {formato_de_cover}. Cambiando a "webp".')
    formato_de_cover = "webp"

# --------------- INICIO DE LOS CAMBIOS dm.bat -------------------

if liricas == "s":
    liricas = " --lyrics"
elif liricas =="n":
    liricas = ""
else:
    print(f'{liricas} no es un valor permitido. Cambiando a "s".')
    liricas = " --lyrics"

nueva_linea_3 = f'set "ruta_descarga={ruta_de_descarga}"\n'
nueva_linea_6 = f'set "subF_playlist={subcarpeta_playlist}"\n'
nueva_linea_9 = f'set "ruta_config={ruta_de_configuracion}"\n'
nueva_linea_34 = f'    del "{nombre_de_cover}.{formato_de_cover}" "{archivo_temporal}.info.json"\n'
nueva_linea_35 = f'    echo {nombre_de_cover}.{formato_de_cover} y {archivo_temporal}.info.json eliminados.\n'

nombre_bat = f'{ruta_de_configuracion}dm.bat'

with open(nombre_bat, 'r') as archivo:
    lineas = archivo.readlines()

if len(lineas) >= 3:
    lineas[2] = nueva_linea_3
if len(lineas) >= 6:
    lineas[5] = nueva_linea_6
if len(lineas) >= 9:
    lineas[8] = nueva_linea_9
if len(lineas) >= 34:
    lineas[33] = nueva_linea_34
if len(lineas) >= 35:
    lineas[34] = nueva_linea_35

with open(nombre_bat, 'w') as archivo:
    archivo.writelines(lineas)

print(f'El archivo {nombre_bat} ha sido actualizado.')

nueva_linea_3 = f'set "ruta_descarga={ruta_de_descarga}"\n'
nueva_linea_6 = f'set "subF_playlist={subcarpeta_playlist}"\n'
nueva_linea_9 = f'set "ruta_config={ruta_de_configuracion}"\n'

nombre_pbat = f'{ruta_de_configuracion}dmp.bat'

# ---------------FIN DE LOS CAMBIOS ------------------

with open(nombre_pbat, 'r') as archivo:
    lineas = archivo.readlines()

if len(lineas) >= 3:
    lineas[2] = nueva_linea_3
if len(lineas) >= 6:
    lineas[5] = nueva_linea_6
if len(lineas) >= 9:
    lineas[8] = nueva_linea_9

with open(nombre_pbat, 'w') as archivo:
    archivo.writelines(lineas)

print(f'El archivo {nombre_pbat} ha sido actualizado.')

temp = archivo_temporal
n_cover = nombre_de_cover
f_cover = formato_de_cover
s_cover = peso_maximo_de_cover
q_cover = calidad_minina_de_cover

contenido_conf_single = f'''# Single
--cookies-from Opera
-o "{temp}.%(ext)s"
--write-info-json
--format "(bestvideo[ext=webm]/bestvideo)+(bestaudio[acodec^=opus]/bestaudio)/best"
--exec 'procesar_{f_cover}.py {{}} "{n_cover}.{f_cover}" "{s_cover}" "{q_cover}"'
--exec 'metadatos.py "{temp}.%(ext)s" "{n_cover}.{f_cover}" """%(id)s""" %(title)q %(artist)q %(album)q "" "%(playlist_index)s" "%(release_year)s" "{temp}.info.json"{liricas}'
--exec 'del {n_cover}.{f_cover} {temp}.info.json && echo'
'''

nombre_single = f'{ruta_de_configuracion}single.conf'

with open(nombre_single, 'w') as archivo:
    archivo.write(contenido_conf_single)

print(f'El archivo {nombre_single} ha sido actualizado.')

contenido_conf_precesar = f'''# List-cover
--cookies-from Opera
-o "{n_cover}.%(ext)s"
--format "(bestvideo[ext=webm]/bestvideo)"
--playlist-items "1"
--exec 'procesar_{f_cover}.py {{}} "{n_cover}.{f_cover}" "{s_cover}" "{q_cover}"'
--exec 'del {n_cover}.%(ext)s'
'''

nombre_precesar = f'{ruta_de_configuracion}precesar.conf'

with open(nombre_precesar, 'w') as archivo:
    archivo.write(contenido_conf_precesar)

print(f'El archivo {nombre_precesar} ha sido actualizado.')

contenido_conf_playlist = f'''# List-música
--cookies-from Opera
-o "{temp}.%(ext)s"
--write-info-json
--format "(bestaudio[acodec^=opus]/bestaudio)"
--exec 'metadatos.py "{temp}.%(ext)s" "{n_cover}.{f_cover}" """%(id)s""" %(title)q %(artist)q %(album)q "" "%(playlist_index)s" "%(release_year)s" "{temp}.info.json"{liricas}'
--exec 'del {temp}.info.json && echo'
'''

nombre_playlist = f'{ruta_de_configuracion}playlist.conf'

with open(nombre_playlist, 'w') as archivo:
    archivo.write(contenido_conf_playlist)

print(f'El archivo {nombre_playlist} ha sido actualizado.')

contenido_conf_singlelist = f'''# Playlist de Singles
--cookies-from Opera
-o "{temp}.%(ext)s"
--format "(bestvideo[ext=webm]/bestvideo)+(bestaudio[acodec^=opus]/bestaudio)/best"
--exec 'procesar_{f_cover}.py {{}} "{n_cover}.{f_cover}" "{s_cover}" "{q_cover}"'
--exec 'metadatos.py "{temp}.%(ext)s" "{n_cover}.{f_cover}" """%(id)s""" %(title)q %(artist)q %(album)q "" "%(playlist_index)s" "%(release_year)s" "{temp}.info.json"{liricas}'
--exec 'del {n_cover}.{f_cover} {temp}.info.json && echo'
'''

nombre_singlelist = f'{ruta_de_configuracion}singlelist.conf'

with open(nombre_singlelist, 'w') as archivo:
    archivo.write(contenido_conf_singlelist)

print(f'El archivo {nombre_singlelist} ha sido actualizado.')

print(f"")
print(f"Presione Enter para finalizar...")
input()

