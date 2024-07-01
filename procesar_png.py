import os
import subprocess
import sys
from PIL import Image

def is_pngquant_installed():
    """Verifica si pngquant está instalado y disponible en el PATH."""
    try:
        subprocess.run(['pngquant', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
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

def compress_png(input_file, max_size_kb):
    output_file = 'output.png'

    if not os.path.isfile(input_file):
        print(f"Error: El archivo de entrada \"{input_file}\" no existe.")
        return False

    try:
        command = f'pngquant --force --output {output_file} {input_file}'
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        size_kb = os.path.getsize(output_file) / 1024
        print(f"Tamaño: {size_kb:.2f} KB")

        if size_kb <= max_size_kb:
            print(f"El tamaño del archivo está dentro del límite: {size_kb:.2f} KB")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error al comprimir el archivo: {e}")

    print('No se pudo comprimir el archivo al tamaño deseado.')
    return False

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Uso: python compress_png.py <archivo> <archivo_de_entrada> <tamano_max_kb>')
        sys.exit(1)

    archivo = sys.argv[1]
    input_file = sys.argv[2]
    max_size_kb = int(sys.argv[3])

    # Verifica si el archivo existe
    if not os.path.isfile(archivo):
        print(f"Error: El archivo \"{archivo}\" no se encontró.")
        sys.exit(1)

    # Verifica si input_file termina en ".png"
    if not input_file.lower().endswith('.png'):
        print(f'El archivo "{input_file}" no termina en ".png". Renombrando a "cover.png".')
        input_file = 'cover.png'

    # Ejecuta ffmpeg para extraer la primera imagen del archivo
    print(f"Extrayendo 1er frame como carátula...")
    ffmpeg_command = f'ffmpeg -loglevel error -nostats -hide_banner -i "{archivo}" -vf "select=eq(n\\,0)" -frames:v 1 -update 1 "{input_file}"'
    try:
        subprocess.run(ffmpeg_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar ffmpeg: {e}")
        sys.exit(1)

    # Verifica si pngquant está instalado
    if not is_pngquant_installed():
        print('Error: pngquant no está instalado. Por favor, instala pngquant e intenta nuevamente.')
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

    if compress_png(input_file, max_size_kb):
        os.remove(input_file)  # Elimina el archivo original
        os.rename('output.png', input_file)  # Renombra el archivo comprimido con el nombre del archivo original
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
