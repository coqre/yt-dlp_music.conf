import os
import subprocess
import sys
from PIL import Image

def is_cwebp_installed():
    """Verifica si cwebp está instalado y disponible en el PATH."""
    try:
        subprocess.run(['cwebp', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_square_image(file_path):
    """Verifica si la imagen es cuadrada."""
    try:
        with Image.open(file_path) as img:
            return img.width == img.height
    except Exception as e:
        print(f"Error al abrir la imagen: {e}")
        return False

def compress_webp(input_file, max_size_kb, min_quality):
    max_quality = 100
    output_file = 'output.webp'

    if not os.path.isfile(input_file):
        print(f"Error: El archivo de entrada \"{input_file}\" no existe.")
        return False

    for quality in range(max_quality, min_quality - 1, -1):
        try:
            # Ejecuta cwebp con el nivel de calidad actual
            command = f'cwebp -quiet -exact -q {quality} {input_file} -o {output_file}'
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Verifica el tamaño del archivo de salida
            size_kb = os.path.getsize(output_file) / 1024
            print(f"Calidad: {quality}, Tamaño: {size_kb:.2f} KB")

            if size_kb <= max_size_kb:
                print(f"El tamaño del archivo está dentro del límite: {size_kb:.2f} KB")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Reintentando comprimir carátula, espere...")

    print('No se pudo comprimir el archivo al tamaño deseado.')
    return False

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Uso: python compress_webp.py <archivo> <archivo_de_entrada> <tamano_max_kb> <min_quality>')
        sys.exit(1)

    archivo = sys.argv[1]
    input_file = sys.argv[2]
    max_size_kb = int(sys.argv[3])
    min_quality = int(sys.argv[4])

    # Verifica si el archivo existe
    if not os.path.isfile(archivo):
        print(f"Error: El archivo \"{archivo}\" no se encontró.")
        sys.exit(1)

    # Verifica si input_file termina en ".webp"
    if not input_file.lower().endswith('.webp'):
        print(f'El archivo "{input_file}" no termina en ".webp". Renombrando a "cover.webp".')
        input_file = 'cover.webp'

    # Ejecuta ffmpeg para extraer la primera imagen del archivo
    print(f"Extrayendo 1er frame como carátula...")
    ffmpeg_command = f'ffmpeg -loglevel error -nostats -hide_banner -i "{archivo}" -vf "select=eq(n\\,0),format=rgba" -frames:v 1 -lossless 1 "{input_file}"'
    try:
        subprocess.run(ffmpeg_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar ffmpeg: {e}")
        sys.exit(1)

    # Verifica si cwebp está instalado
    if not is_cwebp_installed():
        print('Error: cwebp no está instalado. Por favor, instala cwebp e intenta nuevamente.')
        sys.exit(1)

    if not is_square_image(input_file):
        print(f'El archivo "{input_file}" no es una imagen cuadrada. Si elimina la imagen no se insertarán los metadatos.')
        while True:
            user_choice = input('¿Desea eliminar el archivo no cuadrado? (s/n): ').lower()
            if user_choice == 's':
                os.remove(input_file)
                print(f'"{input_file}" ha sido eliminado.')
                sys.exit(1)
            elif user_choice == 'n':
                print(f'El archivo "{input_file}" no ha sido eliminado.')
                sys.exit(0)
            else:
                print('Opción no válida. Por favor, elija "s" para sí o "n" para no.')

    size_kb = os.path.getsize(input_file) / 1024
    if size_kb <= max_size_kb:
        print(f'El archivo "{input_file}" ya está dentro del tamaño máximo permitido ({size_kb:.2f} KB). No se necesita compresión.')
        sys.exit(0)

    if compress_webp(input_file, max_size_kb, min_quality):
        os.remove(input_file)  # Elimina el archivo original
        os.rename('output.webp', input_file)  # Renombra el archivo comprimido con el nombre del archivo original
        print(f'El archivo original "{input_file}" ha sido reemplazado por la versión comprimida.')
    else:
        while True:
            user_choice = input('No se pudo comprimir el archivo al tamaño deseado. ¿Desea continuar de todos modos? (s/n): ').lower()
            if user_choice == 's':
                print('Continuando con el archivo sin comprimir...')
                sys.exit(0)
            elif user_choice == 'n':
                print(f'No se pudo comprimir el archivo "{input_file}" al tamaño deseado.')
                sys.exit(1)
            else:
                print('Opción no válida. Por favor, elija "s" para sí o "n" para no.')
