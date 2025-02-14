import argparse
import os
import subprocess
import json
import io
import base64
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from PIL import Image
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TDRC, TRCK, COMM, APIC, TXXX
from mutagen.mp3 import MP3

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

def convert_to_mp3(input_file, output_file):
    try:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostats', '-i', input_file, '-map', '0:a', '-c', 'libmp3lame', '-b:a', '320k', output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[31mERROR\033[0m al convertir el archivo opus a mp3: {e}")
        return False
    return True

def agregar_metadatos_mp3(archivo_mp3, archivo_imagen, title, artist, album, albumartist, date, tracknumber, comment, description):
    # Abrir el archivo mp3
    audio = MP3(archivo_mp3, ID3=ID3)
    
    # Crear un ID3 tag si no existe
    if audio.tags is None:
        audio.add_tags()
    
    # Agregar los metadatos
    audio.tags['TIT2'] = TIT2(encoding=3, text=title)  # Título de la canción
    audio.tags['TPE1'] = TPE1(encoding=3, text=artist)  # Artista
    audio.tags['TALB'] = TALB(encoding=3, text=album)  # Álbum
    audio.tags['TPE2'] = TPE2(encoding=3, text=albumartist)  # Artista del álbum
    audio.tags['TDRC'] = TDRC(encoding=3, text=date)  # Fecha de lanzamiento
    audio.tags['TRCK'] = TRCK(encoding=3, text=str(tracknumber))  # Número de pista
    audio.tags['COMM'] = COMM(encoding=3, lang='eng', desc='', text=f"ID={comment}")  # Comentario
    if description:
        audio.tags['TXXX:Description'] = TXXX(encoding=3, desc='Description', text=description) # Descripción adicional
    
    # Abrir la imagen y detectar su formato
    with open(archivo_imagen, "rb") as img_f:
        img = Image.open(img_f)
        img_format = img.format.lower()  # Detecta el formato de la imagen (JPEG, PNG, WEBP, etc.)

        # Crear el MIME tipo para la imagen
        if img_format == 'jpeg':
            mime_type = 'image/jpeg'
        elif img_format == 'png':
            mime_type = 'image/png'
        elif img_format == 'webp':
            mime_type = 'image/webp'
        else:
            raise ValueError("Formato de imagen no soportado. Solo JPEG, PNG y WEBP son válidos.")

        # Mover el puntero del archivo al inicio después de haber leído el formato
        img_f.seek(0)
        
        # Agregar la carátula con el tipo y formato adecuado
        audio.tags.add(APIC(encoding=3, mime=mime_type, type=3, desc="front cover", data=img_f.read()))

    # Guardar los cambios
    audio.save()
    
    # Eliminar metadatos innecesarios si existen
    for tag in ['TDEN', 'TENC', 'TLAN', 'TSSE']:
        if tag in audio.tags:
            del audio.tags[tag]
    
    # Guardar los cambios
    audio.save()
    
    print(f"Carátula y metadatos agregados a {archivo_mp3}")

def main():
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

    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"El archivo de audio '{args.filename}' no existe.")
        return

    # convertir el archivo a un .mp3
    input_filename = args.filename
    extension = input_filename.split('.')[-1].lower()  # Obtener la extensión del archivo

    # Determinar el nombre de archivo de salida
    mp3_filename = input_filename.replace(f'.{extension}', '.mp3')

    # Comprobar el tipo de archivo y proceder con la conversión
    if extension == 'opus' or extension == 'webm' or extension == 'm4a':
        if not convert_to_mp3(input_filename, mp3_filename):
            print("\033[31mERROR\033[0m al convertir el archivo a un .mp3. Abortando el proceso.")
        else:
            os.remove(input_filename)
    else:
        print("\033[31mERROR\033[0m El archivo no es un formato compatible (.opus, .webm, .m4a). Abortando el proceso.")


    if not os.path.exists(args.cover_image):
        print("NO SE ENCONTRÓ CARÁTULA. SE ASUME QUE ES UN VIDEO.")
        print("SE IGNORARÁN LOS METADATOS Y LA CARÁTULA.")
        
        # Renombrar el archivo final
        new_filename = f"{args.track} - {args.artista.replace(';', ', ')}.mp3"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(args.filename, new_filename)
        
        print(f'Archivo renombrado a {new_filename}')
        return

    track, artista, album, artalb, numtrack, ayo = metadatos(args.track, args.artista, args.album, args.artalb, args.numtrack, args.ayo)

    # Leer la descripción del archivo JSON
    description = leer_descripcion_json(args.description_json)

    try:
        print(f"Intentando insertar metadatos...")
        agregar_metadatos_mp3(mp3_filename, args.cover_image, track, artista, album, artalb, ayo, numtrack, args.id, description)
        
        # Renombrar el archivo final
        new_filename = f"{track} - {artista.replace(';', ', ')}.mp3"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(mp3_filename, new_filename)
        
        print(f'Archivo renombrado a {new_filename}')
        
        print(f'    Metadatos agregados al archivo {new_filename}:')
        print(f'    Track.......... :   {track}')
        print(f'    Artista........ :   {artista}')
        print(f'    Album.......... :   {album}')
        print(f'    Artista de álbum:   {artalb}')
        print(f'    Número de track :   {numtrack}')
        print(f'    Año............ :   {ayo}')
        print(f'    ID ............ :   {args.id}')
        print(f'    Carátula....... :   {args.cover_image}')
        if description:
            print(f'    Descripción.....:   {description.splitlines()[0]}') # Solo la primera línea
        print(f"")
        

    except Exception as e:
        print(f"\033[31mERROR:\033[0m {e}")

if __name__ == '__main__':
    main()
