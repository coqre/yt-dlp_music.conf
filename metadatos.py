import argparse
import os
import subprocess
import json
from pymediainfo import MediaInfo
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3
from PIL import Image
import base64
import sys
import requests


# --- lrclib functionality integrated ---
def segundos_a_minutos(segundos):
    segundos = int(round(segundos))
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return f"{minutos}:{segundos_restantes:02d}"


def fetch_synced_lyrics(track_name, target_duration=None):
    query = track_name.replace(' ', '+')
    url = f"https://lrclib.net/api/search?q={query}"
    try:
        resp = requests.get(url, headers={'User-Agent': 'yt-dlp_music.conf v0.4 (https://github.com/coqre/yt-dlp_music.conf/releases)'})
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error buscando letras: {e}")
        return ""
    results = resp.json()
    if not results:
        print("No se encontraron letras sincronizadas.")
        return ""
    if target_duration:
        print(f"\nResultados de letras sincronizadas para: {track_name} [{target_duration}]")
    else:
        print(f"\nResultados de letras sincronizadas para: {track_name} [duración no encontrada]")
    # input
    for i, s in enumerate(results, start=1):
        t = s.get('trackName','Desconocido')
        a = s.get('artistName','Desconocido')
        d = segundos_a_minutos(s.get('duration',0))
        print(f"{i}. {t} - {a} [{d}]")
    # Selección interactiva
    while True:
        try:
            sel = int(input("Elige número de la canción para letra: "))
            if 1 <= sel <= len(results): break
        except ValueError:
            pass
        print("Selección inválida.")
    chosen = results[sel-1]
    lyrics = chosen.get('syncedLyrics','')
    if not lyrics.strip():
        print("La selección no tiene letras sincronizadas.")
        return ""
    return lyrics


# Mapa de caracteres no permitidos y sus reemplazos de ancho completo
replacement_map = {
    '\\': '⧹',
    '/': '⧸',
    ':': '：',
    '*': '＊',
    '?': '？',
    '"': '＂',
    '<': '＜',
    '>': '＞',
    '|': '｜'
}

def replace_invalid_chars(filename):
    for invalid_char, replacement_char in replacement_map.items():
        filename = filename.replace(invalid_char, replacement_char)
    return filename

def leer_descripcion_json(ruta_json):
    """Lee el archivo JSON y extrae el campo 'description'."""
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if "description" in datos:
                return datos["description"]
            else:
                print(f"\033[31mERROR:\033[0m El archivo '{ruta_json}' no contiene la clave 'description'.")
                return False
    except FileNotFoundError:
        print(f"\033[31mERROR:\033[0m No se encontró el archivo '{ruta_json}'.")        
        return False
    except json.JSONDecodeError as e:
        print(f"\033[31mERROR\033[0m al leer el archivo '{ruta_json}': {e}")
        return False
    except Exception as e:
        print(f"\033[31mERROR\033[0m inesperado al leer el archivo '{ruta_json}': {e}")
        return False
        
def leer_duration_string(ruta_json):
    """Lee el archivo JSON y extrae el campo 'duration_string'."""
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if "duration_string" in datos:
                return datos["duration_string"]
            else:
                print(f"\033[31mERROR:\033[0m El archivo '{ruta_json}' no contiene la clave 'duration_string'.")
                return False
    except FileNotFoundError:
        print(f"\033[31mERROR:\033[0m No se encontró el archivo '{ruta_json}'.")        
        return False
    except json.JSONDecodeError as e:
        print(f"\033[31mERROR\033[0m al leer el archivo '{ruta_json}': {e}")
        return False
    except Exception as e:
        print(f"\033[31mERROR\033[0m inesperado al leer el archivo '{ruta_json}': {e}")
        return False

def metadatos(track, artista, album, artalb, numtrack, ayo):
    numtrack = f"{int(numtrack):02d}" if numtrack.isnumeric() else "01"
    ayo = ayo if ayo.isnumeric() else ""
    altrack = False
    
    trackverif = track.find(" (con ")
    if trackverif > -1:
        if track == album:
            altrack = True
        tracksobra = track[trackverif + 6: -1]
        if tracksobra not in artista:
            artista = f"{artista}, {tracksobra}"
        track = track[:trackverif]

    trackverif = track.find(" (feat. ")
    if trackverif > -1:
        if track == album:
            altrack = True
        tracksobra = track[trackverif + 8: -1]
        if tracksobra not in artista:
            artista = f"{artista}, {tracksobra}"
        track = track[:trackverif]
    
    trackverif = track.find(" (Feat. ")
    if trackverif > -1:
        if track == album:
            altrack = True
        tracksobra = track[trackverif + 8: -1]
        if tracksobra not in artista:
            artista = f"{artista}, {tracksobra}"
        track = track[:trackverif]
    
    if altrack:
        album = track
    if not album:
        album = track
    artista = artista.replace(", ", ";")
    artalbverif = artista.find(";")
    if artalbverif > -1:
        artalb = artista[:artalbverif]
    else:
        artalb = artista

    return track, artista, album, artalb, numtrack, ayo

def encapsulate_opus_to_ogg(input_file, output_file):
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostats', '-i', input_file, '-map', '0:a', '-c', 'copy', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[31mERROR\033[0m al encapsular el archivo opus en ogg: {e}")
        return False
    return True

def extract_to_m4a(input_file, output_file):
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostats', '-i', input_file, '-map', '0:a', '-c', 'copy', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[31mERROR\033[0m al extraer el archivo mkv en m4a: {e}")
        return False
    return True
    
def extract_to_contenedor(input_file, output_file):
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostats', '-i', input_file, '-map', '0:a', '-c', 'copy', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[31mERROR\033[0m al extraer y encapsular el archivo {input_file} en {output_file}: {e}")
        return False
    return True

def agregar_metadatos_ogg(archivo_opus, archivo_imagen, title, artist, album, albumartist, date, tracknumber, comment, description, lyrics=""):
    # Abrir el archivo OPUS
    audio = OggOpus(archivo_opus)
    
    # Crear el objeto Picture
    caratula = Picture()
    
    # Leer la imagen y establecer los parámetros de la carátula
    with open(archivo_imagen, "rb") as img_f:
        caratula.data = img_f.read()
        
    # Obtener el formato de la imagen
    img = Image.open(archivo_imagen)
    caratula.mime = Image.MIME[img.format]
    caratula.type = 3  # 3 es el tipo estándar para carátulas de álbum
    caratula.width, caratula.height = img.size
    
    # Calcular la profundidad de bits de la imagen
    depth_mapping = {
        '1': 1,
        'L': 8,
        'P': 8,
        'RGB': 24,
        'RGBA': 32,
        'CMYK': 32,
        'YCbCr': 24,
        'LAB': 24,
        'HSV': 24,
        'I': 32,
        'F': 32
    }
    
    caratula.depth = depth_mapping.get(img.mode, 0)
    
    if img.mode == 'P':
        caratula.colors = len(img.getpalette()) // 3
    else:
        caratula.colors = 0  # Sin paleta de colores
    
    # Codificar la carátula en base64 para OggOpus
    caratula_data = base64.b64encode(caratula.write()).decode('ascii')
    
    # Añadir la carátula al archivo OPUS
    audio["METADATA_BLOCK_PICTURE"] = caratula_data
    
    # Añadir los metadatos
    audio['TITLE'] = title
    audio['ARTIST'] = artist
    audio['ALBUM'] = album
    audio['ALBUMARTIST'] = albumartist
    audio['DATE'] = date
    audio['TRACKNUMBER'] = tracknumber
    audio['ID'] = comment
    if description:
        audio['DESCRIPTION'] = description # Agrega DESCRIPTION solo si no está vacío
    if lyrics:
        audio['LYRICS'] = lyrics

    # Elimina metadatos no deseados
    for unwanted_tag in ['duration', 'encoder', 'language']:
        if unwanted_tag in audio:
            del audio[unwanted_tag]
    
    # Guardar los cambios
    audio.save()
    
    print(f"Carátula y metadatos agregados a {archivo_opus}")

def agregar_metadatos_m4a(archivo_m4a, archivo_imagen, title, artist, album, albumartist, date, tracknumber, comment, description, lyrics=""):
    # Cargar el archivo de audio
    audio = MP4(archivo_m4a)
    
    # Leer la imagen y detectar formato
    with open(archivo_imagen, "rb") as img_f:
        image_data = img_f.read()
    
    img = Image.open(archivo_imagen)
    formato = img.format.upper()
    
    # Definir el formato compatible con MP4Cover
    if formato == "JPEG":
        image_format = MP4Cover.FORMAT_JPEG
    elif formato == "PNG":
        image_format = MP4Cover.FORMAT_PNG
    elif formato == "WEBP": #Puede fallar
        image_format = MP4Cover.FORMAT_PNG
        print(f"\033[94mLa carátula se insertará como un PNG (puede fallar).\033[0m")
    else:
        raise ValueError("Formato de imagen no soportado. Usa jpg, webp, o png.")
    
    # Agregar la carátula
    audio["covr"] = [MP4Cover(image_data, imageformat=image_format)]
    
    
    # Agregar metadatos básicos
    audio["\xa9nam"] = title            # TITLE
    audio["\xa9ART"] = artist           # ARTIST
    audio["\xa9alb"] = album            # ALBUM
    audio["aART"] = albumartist          # ALBUMARTIST
    audio["trkn"] = [(int(tracknumber), 0)]   # TRACKNUMBER
    audio["\xa9day"] = date              # YEAR
    audio["desc"] = description          # DESCRIPTION
    if comment:
        audio["\xa9cmt"] = comment       # COMMENT. Lo agrega solo si existe
    
    if lyrics:
        audio['©lyr'] = lyrics

    # Guardar los cambios
    audio.save()
    print(f"Carátula y metadatos agregados a {archivo_m4a}")

def get_audio_codec(video_path):
    media_info = MediaInfo.parse(video_path)
    for track in media_info.tracks:
        if track.track_type == "Audio":
            return track.format
    return None

def main():
    activar_m4a = False
    parser = argparse.ArgumentParser(description='Procesar metadatos de una canción.')
    parser.add_argument('filename', type=str, help='Nombre del archivo de audio')
    parser.add_argument('cover_image', type=str, help='Ruta a la imagen de la carátula')
    parser.add_argument('id', type=str, help='ID para el campo COMMENT')
    parser.add_argument('track', type=str, help='Nombre de la canción')
    parser.add_argument('artista', type=str, help='Nombre del artista')
    parser.add_argument('album', type=str, help='Nombre del álbum')
    parser.add_argument('artalb', type=str, help='Artista del álbum')
    parser.add_argument('numtrack', type=str, help='Número de pista')
    parser.add_argument('ayo', type=str, help='Año')
    parser.add_argument('description_json', type=str, help='archivo JSON para descripción')
    parser.add_argument('--lyrics', action='store_true', help='Buscar e incluir letras sincronizadas')
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"El archivo '{args.filename}' no existe.")
        return

    #verificar la extensión del archivo
    input_filename = args.filename
    extension = input_filename.split('.')[-1].lower()  # Obtener la extensión del archivo
    
    codec = get_audio_codec(args.filename)
    print(f"\033[94mcódec: {codec}\033[0m")
    codec = codec.lower()
    if codec == "opus":
        contenedor_codec = ".ogg"
    elif codec == "aac":
        contenedor_codec = ".m4a"
        activar_m4a = True
    else:
        print(f"Códec de audio {codec.lower()} no compatible. Finalizando script.")
        return
    
    # Extraer y encapsular el archivo de audio en el contenedor respectivo.
    cancion_filename = args.filename.replace(f".{extension}", contenedor_codec)
    
    if not args.filename == cancion_filename:
        if not extract_to_contenedor(args.filename, cancion_filename):
            print(f"\033[31mERROR\033[0m al extraer y encapsular el archivo .{extension} en {contenedor_codec}.")
            print("--ABORTANDO EL PROCESO--")
            return
        else:
            os.remove(args.filename)
    else:
        print(f"El archivo {cancion_filename} ya existe. Extracción y encapsulado ignorado.")

    if not os.path.exists(args.cover_image):
        print("NO SE ENCONTRÓ CARÁTULA. SE ASUME QUE ES UN VIDEO.")
        print("SE IGNORARÁN LOS METADATOS Y LA CARÁTULA.")
        
        # Renombrar el archivo final
        new_filename = f"{args.track} - {args.artista.replace(';', ', ')}{contenedor_codec}"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(cancion_filename, new_filename)
        print(f"")
        print(f'Archivo renombrado a {new_filename}')
        print("     ·················································")
        print("\033[31m     ATENCIÓN.....:¡CANCIÓN SIN CARÁTULA NI METADATOS!\033[0m")
        print("     .................................................")
        print(f"")
        return

    track, artista, album, artalb, numtrack, ayo = metadatos(args.track, args.artista, args.album, args.artalb, args.numtrack, args.ayo)

    # Leer la descripción del archivo JSON
    
    duration_string = leer_duration_string(args.description_json)
    lyrics = ''
    if args.lyrics:
        un_artista = artista.split(";", 1)[0]
        buscar_por = f"{track} {un_artista}"
        lyrics = fetch_synced_lyrics(buscar_por, duration_string)
    description = leer_descripcion_json(args.description_json)

    try:
        print(f"Intentando insertar metadatos...")
        
        if activar_m4a == True:
            agregar_metadatos_m4a(cancion_filename, args.cover_image, track, artista, album, artalb, ayo, numtrack, args.id, description, lyrics)
        else:
            agregar_metadatos_ogg(cancion_filename, args.cover_image, track, artista, album, artalb, ayo, numtrack, args.id, description, lyrics)

        # Renombrar el archivo final
        new_filename = f"{track} - {artista.replace(';', ', ')}{contenedor_codec}"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(cancion_filename, new_filename)
        
        print(f'Archivo renombrado a {new_filename}')
        
        print(f'    Metadatos agregados al archivo {new_filename}:')
        print(f'    Track.......... :   {track}')
        print(f'    Artista........ :   {artista}')
        print(f'    Album.......... :   {album}')
        print(f'    Artista de álbum:   {artalb}')
        if activar_m4a == False:
            print(f'    Número de track :   {numtrack}')
        else:
            print(f'    Número de track :   {int(numtrack)}')
        print(f'    Año............ :   {ayo}')
        print(f'    ID ............ :   {args.id}')
        print(f'    Carátula....... :   {args.cover_image}')
        if description:
            print(f'    Descripción.....:   {description.splitlines()[0]}') # Solo la primera línea
        if lyrics:
            print(f'    Líricas.........:   {lyrics.splitlines()[0]}') # Solo la primera línea
        print(f"")
        

    except Exception as e:
        print(f"\033[31mERROR:\033[0m {e}")

if __name__ == '__main__':
    main()
