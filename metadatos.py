import argparse
import os
import subprocess
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from PIL import Image
import base64

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

def metadatos(track, artista, album, artalb, numtrack, ayo):
    numtrack = f"{int(numtrack):02d}" if numtrack.isnumeric() else "01""
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
        
        print(f"Error al encapsular el archivo opus en ogg: {e}")
        return False
    return True

def agregar_caratula_opus(archivo_opus, archivo_imagen, title, artist, album, albumartist, date, tracknumber, comment):
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
    
    # Añadir los metadatos adicionales
    audio['TITLE'] = title
    audio['ARTIST'] = artist
    audio['ALBUM'] = album
    audio['ALBUMARTIST'] = albumartist
    audio['DATE'] = date
    audio['TRACKNUMBER'] = tracknumber
    audio['COMMENT'] = comment
    
    # Guardar los cambios
    audio.save()
    
    print(f"Carátula y metadatos agregados a {archivo_opus}")

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

    args = parser.parse_args()

    if not os.path.exists(args.filename):
        
        print(f"El archivo de audio '{args.filename}' no existe.")
        return

    # Encapsular el archivo .opus en un contenedor .ogg
    ogg_filename = args.filename.replace('.webm', '.ogg')
    if not encapsulate_opus_to_ogg(args.filename, ogg_filename):
        
        print("Error al encapsular el archivo .opus en .ogg. Abortando el proceso.")
        return
    else:
        os.remove(args.filename)

    if not os.path.exists(args.cover_image):
        
        print("NO SE ENCONTRÓ CARÁTULA. SE ASUME QUE ES UN VIDEO.")
        print("SE IGNORARÁN LOS METADATOS Y LA CARÁTULA.")
        
        # Renombrar el archivo final
        new_filename = f"{args.track} - {args.artista.replace(';', ', ')}.ogg"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(args.filename, new_filename)
        
        print(f'Archivo renombrado a {new_filename}')
        return

    track, artista, album, artalb, numtrack, ayo = metadatos(args.track, args.artista, args.album, args.artalb, args.numtrack, args.ayo)

    try:
        print(f"Intentando insertar metadatos...")
        agregar_caratula_opus(ogg_filename, args.cover_image, track, artista, album, artalb, ayo, numtrack, args.id)
        
        # Renombrar el archivo final
        new_filename = f"{track} - {artista.replace(';', ', ')}.ogg"
        new_filename = replace_invalid_chars(new_filename)
        os.rename(ogg_filename, new_filename)
        
        print(f'Archivo renombrado a {new_filename}')
        
        print(f'    Metadatos agregados al archivo {new_filename}:')
        print(f'    Track.......... :   {track}')
        print(f'    Artista........ :   {artista}')
        print(f'    Album.......... :   {album}')
        print(f'    Artista de álbum:   {artalb}')
        print(f'    Número de track :   {numtrack}')
        print(f'    Año............ :   {ayo}')
        print(f'    ID (Comentario) :   {args.id}')
        print(f'    Carátula....... :   {args.cover_image}')
        print(f"")
        

    except Exception as e:
        
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
