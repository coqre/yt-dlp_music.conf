# yt-dlp_musica.conf

Herramienta en CLI basado en scripts escritos en batch y en Python, con el fin de automatizar las descargas de cualquier tipo de audio de YouTube / Music (o de alguna otra plataforma compatible) en la mejor calidad posible, con metadatos corregidos y carátula personalizable. Capaz de distinguir entre álbumes, videos musicales, singles y playlists de singles.

Para descargar en la mejor calidad posible se recomienda el uso de YouTube Premium.

## Contiene:
- `dm.bat`
- `dmp.bat`
- `single.conf`
- `precesar.conf`
- `playlist.conf`
- `singlelist.conf`
- `procesar_webp.py`
- `porcesar_png.py`
- `metadatos.py`
- `musica.conf.py`

Se pensó el «súper script» de esta manera modular para que se pueda personalizar el código y acondicionarlo a las necesidades del usuario. (Para Linux se sustituyen los archivos ‘.bat’ por otros ‘.sh’. Leer más abajo para más información de compatibilidad).

## Dependencias
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: descargas
- **[ffmpeg](https://github.com/FFmpeg/FFmpeg)**: exportar carátula y manipulación multimedia
- **[cwebp](https://developers.google.com/speed/webp/download?hl=es-419) (opcional)**: maneja imágenes webp
- **[pngquant](https://pngquant.org/) (opcional)**: maneja imágenes png
- **Intérprete CLI de Windows (ej: [DOSBox](https://www.dosbox.com/download.php?main=1))**: Esto es solo para Linux
- **[python](https://www.python.org/downloads/)**: ejecución de scripts

## Librerías de Python
- `os`, `subprocess`, `sys`, `ctypes`, `argparse`, `base64`: Bibliotecas estándar
- `PIL (Pillow)`: procesamiento de imágenes
- `mutagen`: manipular metadatos de archivos de audio

## Instalación
1. Instalar [Python](https://www.python.org/downloads/).
   - Descarga e instala ejecutable. Asegúrate de marcar la opción de Agregar al PATH cuando vayas a instalarlo.

2. Instalar las bibliotecas Pillow y mutagen.
   - Una vez instalado Python, ejecutar los siguientes comandos:
     ```
     pip install Pillow
     pip install mutagen
     ```

3. Instalar [yt-dlp](https://github.com/yt-dlp/yt-dlp), [ffmpeg](https://github.com/FFmpeg/FFmpeg), y [cwebp](https://developers.google.com/speed/webp/download?hl=es-419) / [pngquant](https://pngquant.org/) (dependencias).
   - La forma fácil de instalar yt-dlp es con python ejecutando el comando `pip install yt-dlp`. Sino, descargar desde su repositorio de GitHub.
   - Tanto ffmpeg, cwebp y pngquant se descargan desde sus sitios webs oficiales y se los [añade al PATH](https://www.softzone.es/windows/como-se-hace/cambiar-path-variables-entorno/). Si no están en PATH, es necesario que estén en la misma carpeta que «yt-dlp_musica.conf».

   Nota: ‘cwebp’ manipula imágenes webp mientras ‘pngquant’ maneja png’s. Descargue según sus necesidades.

4. Instalar `yt-dlp_musica.conf`.
   - Descargue los archivos de este repositorio.
   - Agregue la carpeta al PATH o en la misma carpeta donde están las dependencias (desde ahora llamada «CARPETA PRINCIPAL»).

## Configuración
El archivo de configuración global es `musica.conf.py`. Este está pensado para configurar los distintos scripts y archivos ‘.conf’ de manera automática sin necesidad de ir uno por uno.

Se asume que la carpeta de `yt-dlp_music.conf` se llama `yt-dlp_musica` y está dentro la carpeta principal de `yt-dlp` en los archivos de programa de Windows, es por ello que este archivo .py pide derechos de administrador.

Nota: este archivo no tiene la necesidad de estar en la «carpeta principal» pero sí es necesario que esté bien configurado antes de ejecutarlo. Esto es así porque si la carpeta principal está en los Archivos de programa, necesita permisos de administrador cada que se edita; pero puede obviarse este archivo si quiere una configuración independiente para cada caso de descarga y editar los archivos para tener un mayor control.

`musica.conf.py` funciona como si fuese «un archivo .conf cutre» de `yt-dlp`, es por ello que se edita directamente si quiere realizar cambios globales en la forma de descargar las canciones y luego de guardar los cambios se ejecuta con derechos de administrador que pide automáticamente.

Los argumentos de la configuración global pueden editarse según las necesidades del usuario. A continuación se detallan los argumentos de la configuración global:

- `ruta_de_configuracion`: Es la ruta de la CARPETA PRINCIPAL donde se encuentran los archivos por lotes (.bat / .sh), los archivos de configuración de yt-dlp (.conf) y los scripts de metadatos (.py); y es donde este script va a buscar los archivos para editar sus configuraciones.
  - Por defecto: `C:\\Program Files\\yt-dlp\\yt-dlp_music\\`
  
- `ruta_de_descarga`: Es como el ‘-P’ de yt-dlp. Aquí se debe detallar la ruta completa de la carpeta destino de los audios a descargar.
  - Por defecto: `C:\\users\\usuario\\Downloads\\caciones\\`
  
- `subcarpeta_playlist`: Es el nombre de la subcarpeta de la carpeta destino de las canciones a descargar (no es la ruta completa solo el nombre. Para editar esto vaya directamente al archivo .conf).
  - Por defecto: `playlist`
  
- `archivo_temporal`: Nombre de cómo manejará yt-dlp a los archivos descargados. Para más versatilidad, editar los archivos .conf directamente.
  - Por defecto: `audio_temp`
  
- `nombre_de_cover`: Nombre de la carátula / cover temporal del single / álbum.
  - Por defecto: `cover`
  
- `formato_de_cover`: Formato de la carátula. Webp ofrece una buena calidad por un peso considerablemente bajo que la media, pero ya que algunos reproductores no admiten dicho formato está de auxiliar el png. De momento solo se admiten estos dos formatos y de no setear ninguno de ellos se aplicará por defecto ‘webp’. Para más formatos puede usar de referencia los .py ‘procesar_*’ y agregar dicho formato a Formato permitidos en el código.
  - Por defecto: `webp`
  
- `peso_máximo_de_cover`: Número que indica el peso (en KB) máximo que quiere que tenga la carátula.
  - Por defecto: `1300`
  
- `calidad_minima_de_cover`: Número que indica el porcentaje mínimo al cual debe someterse la imagen (carátula) en caso de pasarse del peso máximo permitido. Este cambio será gradual que irá del máximo (100) hasta el seteado y se controlará la mejor calidad dentro del rango. Por defecto la carátula tiene la misma calidad del video; puede cambiar este valor en los archivos ‘.conf’.
  - Por defecto: `80`

# Modo de uso y cómo funciona

En realidad el archivo por lotes principal solo discrimina entre posibles videos álbumes y singles. Una playlist de singles se ejecuta con su propio comando pero ya les explicaré bien más abajo.

En primer lugar he dividido el proceso entre descarga y postprocesado y este último a su vez se divide en la gestión de la portada y la gestión de los metadatos. Esto es así para que el cambio entre playlist y single sea más fácil.

Bien, ahora explicaré qué hace cada script. Cabe recordar que los cambios principales de calidad de los archivos descargados se hacen a través de los archivos `.conf`. También cabe recordar que si la carpeta principal no está en el PATH necesita el CMD iniciarse en la ruta de la carpeta principal.

## Archivos por lotes

### `dm.bat` y `dmp.bat` (y sus variantes `.sh` para Linux)

CMD llamará al archivo por lotes respectivo que pueden ser `dm` (descargar música) o `dmp` (descargar música playlist). Los nombres cortos son para más facilidad con el CMD, pero estos nombres pueden ser cambiados como gustes para que CMD pueda reconocerlos. Eso sí, si les cambias de nombre y quieres usar el archivo de configuración global también tienes que renombrar a dónde el archivo va a cambiar las líneas de código. (Y si usas Linux sin emulador DOS también tienes que comentar y descomentar algunas líneas del archivo de configuración global. Es intuitivo y está señalado en el propio código).

Estos pueden admitir únicamente el link del single / playlist. La única diferencia entre ambos es que uno discrimina entre playlist y el otro no. Es decir que `dm` reconoce cuando es un álbum y solo descarga la carátula del primer video y esa la aplica a todos los audios; mientras que si le pasas una playlist a `dmp` va a descargar todos los audios como si fuesen de distintos álbumes lo cual sirve para descargar... pues... eso, una playlist con distintos álbumes (de aquí en adelante ‘singlelist’).

A continuación se detalla el código.

### Al ejecutar `dm "link"` o `dmp "link"`:

1. Define variables de ruta:
    - `ruta_descarga` se establece en `C:\users\usuario\Downloads\canciones\`.
    - `subF_playlist` se establece en `playlist`.
    - `ruta_config` se establece en `C:\Program Files\yt-dlp\yt-dlp_music\`.
    
    Estos pueden ser modificados mediante el archivo de configuración global.

2. Cambia el directorio de trabajo:
    - `ruta_actual` almacena la ruta actual.
    - Cambia al directorio de descarga especificado en `ruta_descarga` (por eso dije que funcionaba como un `.conf` cutre).

3. Comprueba si la URL es una lista de reproducción:
    - Verifica si existe `playlist?list` en el enlace proporcionado. Dependiendo si es una lista de reproducción ejecuta `yt-dlp` con la configuración (archivos `.conf`) respectiva.

    - Si es una lista de reproducción:
        - Crea la subcarpeta en el directorio seteado.
        - Descarga el primer video para extraer la carátula utilizando la configuración en `precesar.conf`. Este puede editarse para ajustar la calidad deseada.
        - Si la primera parte devuelve un error termina la ejecución.
        - Descarga el resto de la lista de reproducción utilizando `playlist.conf`.
        - Elimina la carátula después de la descarga.

    - Si no es una lista de reproducción:
        - Descarga el audio utilizando `single.conf`.
        - En el caso de `dmp` siempre se ejecutará como si fuera un single con `singlelist.conf` descargando el video con el audio y extrayendo la carátula de cada uno de los videos. El objetivo de tener un archivo `.conf` solo para este caso es por personalización, pero realmente es idéntico a `single.conf`.

4. Finaliza:
    - Vuelve al directorio original de trabajo. Y por eso digo que es un `.conf` cutre. :v

## Archivos de configuración (.conf)

Por si se tiene una cuenta Premium todos activan la opción `--cookies-from` con el navegador Chrome, puede cambiarlo si desea o comentarlo para usar en un futuro… o borrarlo alv. :v

### Single y singlelist

Este se ejecuta como configuración no playlist:
- Establece el output `-o` definido por defecto por el archivo de configuración global (argumento `archivo_temporal`).
- Establece descargar el mejor audio con codec opus y el mejor video con extensión webm. Pueden cambiarse, pero creería que el único argumento que puede romper todo el script sería algún códec no compatible con el contenedor ogg. Léase más abajo para más información. Para la mejor calidad es necesario pasar las cookies de una cuenta premium de YouTube.
- Luego ejecuta el script de procesado de imagen (`procesar_*.py` según el formato seleccionado por `formato_de_cover`) pasando los argumentos del archivo descargado, el nombre de la imagen a exportar, el peso máximo y la calidad mínima; todos estos seteados por defecto por el archivo de configuración global (argumentos `nombre_de_cover` y `formato_de_cover` unidos `peso_máximo_de_cover` y `calidad_minima_de_cover`).
- Ejecuta el script del procesado de metadatos (`metadatos.py`) pasando los argumentos de `archivo_temporal`, el nombre y formato de la carátula, el ID del enlace, los metadatos de título, artista, álbum, artista del álbum seteado como vacío porque no suele haber, el número de índice y el año de publicación.
- Por último, elimina la imagen / carátula que para este momento ya debió haberse procesado con el audio.

### precesar

(pre-procesar) :v
Este se ejecuta como versión de la playlist para extraer la carátula del primer video y luego usar esa imagen como carátula de todo el álbum. Se hace de esta manera para evitar escribir datos innecesarios y porque algunos videos de la misma playlist tienen distintas calidades.
- Establece el output `-o` como el nombre de la carátula seteada por defecto en el archivo de configuración global.
- Setea la descarga como solo el mejor video de extensión webm. Puede cambiarse pero para la mejor calidad es necesario pasar las cookies de una cuenta premium de YouTube.
- Setea descargar solo el primer elemento de la lista de reproducción.
- Luego ejecuta el script de procesado de imagen (`procesar_*.py` según el formato seleccionado por `formato_de_cover`) pasando los argumentos del archivo descargado, el nombre de la imagen a exportar, el peso máximo y la calidad mínima; todos estos seteados por defecto por el archivo de configuración global (argumentos `nombre_de_cover` y `formato_de_cover` unidos `peso_máximo_de_cover` y `calidad_minima_de_cover`).
- Elimina el video descargado.

### playlist

Si el archivo `precesar.conf` se ejecutó sin errores pasa a este archivo. Este se ejecuta como la segunda parte de la descarga de lista de reproducción y tiene como objetivo descargar solo los audios, ya no los videos como en `single.conf` porque en teoría ya debería haber carátula.
- Establece el output `-o` definido por defecto por el archivo de configuración global (argumento `archivo_temporal`).
- Establece descargar el mejor audio con codec opus. Pueden cambiarse, pero creería que el único argumento que puede romper todo el script sería algún códec no compatible con el contenedor ogg. Léase más abajo para más información. Para la mejor calidad es necesario pasar las cookies de una cuenta premium de YouTube.
- Ejecuta el script del procesado de metadatos (`metadatos.py`) pasando los argumentos de `archivo_temporal`, el nombre y formato de la carátula, el ID del enlace, los metadatos de título, artista, álbum, artista del álbum seteado como vacío porque no suele haber, el número de índice y el año de publicación.

## Scripts de metadatos

Este se divide en el script de carátula y en el script de unificar los metadatos y el audio. Dependiendo del formato de imagen elegido en el archivo de configuración global se ejecutará el procesado de webp o de png. El procedimiento es el mismo, solo cambia el formato.

### procesar_imagen

1. En primer lugar extrae el primer fotograma del vídeo como una imagen y aquí depende el formato seteado. Por defecto se usa ffmpeg a la mejor calidad posible.
2. Este segundo paso puede ser controversial y en muchos casos errado, ya que aquí es donde se «««evalúa»»» si es un video musical o una canción porque el criterio es constatar que el video tenga una relación de aspecto cuadrada. :v En teoría las portadas usualmente son cuadradas, aún así si detecta que no lo es se te preguntará si desea conservar la imagen o eliminarla. Esta elección es crucial porque será importante a la hora de incrustar los metadatos. Si se elimina termina el script.

    Y si preguntas por qué elegí este criterio, la verdad es que probé con metadatos como el álbum, pero en algunos casos era muy errado. Este fue el que mejor funcionó. Aún así puedes modificar la función para adaptar el criterio al que creas mejor. Y si te funciona mejor avísame porfa. 😅

3. Si no se elimina, luego viene la verificación del tamaño máximo. Si la imagen extraída lo supera, intenta comprimir con pérdidas hasta obtener el tamaño querido; si llega hasta el porcentaje mínimo de calidad y aún no llega al tamaño deseado, se pregunta al usuario si desea continuar con el script o finalizar la descarga. Esta parte es un buen momento para saber qué hacer con la imagen o buscar una por internet. El punto no es finalizar la descarga, está pensado más bien como un “espérame a ver dónde consigo una imagen que se adapte a mis necesidades”. Si se elige continuar, usa la imagen presente y elimina el vídeo.

### metadatos

Este sin duda es el script más complejo de todos, ya que es el encargado de hacer toda la lógica y las correcciones de metadatos y elegir qué mismo hacer con todos los archivos actuales.

Si me permito la distensión, probé con contenedores matroska y mpeg, pero se me hacía complicado unificar los metadatos en mp3tag y Poweramp (el reproductor que uso). Algunas veces los leía, otras no, otras en el campo erróneo, otras veces unía dos campos en uno y donde en PowerAmp se mostraba bien en mp3tag no y a veces era al revés. De verdad, mucho lío. Opus fue el que mejor me resultó A MÍ, pero no lo quería dejar así suelto por lo que elegí el contenedor ogg. Siéntete libre de bifurcarlo y escoger otros contenedores. ^-^

En fin, ahora lo que hace este script:

1. Encapsula el archivo seteado en la configuración global en un ogg. Ya que de forma predeterminada el codec es un opus, es totalmente compatible.
2. Si la carátula no se encuentra, el script entiende que el audio proviene de un video y no de una canción como tal, por lo que simplemente pasa a renombrar el archivo. Más abajo se explica cómo se maneja.
3. Si la carátula es encontrada, hace un proceso bien raro para obtener los datos de la imagen y hacerla compatible con el contendor. No voy a explicar eso porque realmente no es necesario saberlo.

#### En cuanto a los metadatos. Bien, explicaré detalladamente qué hace:

- Hay veces donde no se encuentra el número de track, por lo que si no existe lo define como “01”.
- Hay veces donde no se encuentra el año, así que lo deja vacío si no existe.
- Verifica si en el propio nombre del track existe un “feat” (de múltiples versiones, aquí es donde tienes que poner una más si te encuentras con una rara). Si existe, entonces manda eso a concatenarse con los artistas y limpia el nombre para que no queden espacios ni paréntesis. Si el ft. ya se encuentra entre los artistas, no lo concatena.
- Si el título del track fue modificado (lo que significa que hay ft.), verifica si el título es igual al álbum. Si no es igual, significa que el track forma parte de un álbum y deja el nombre del álbum tal cual; si sí es igual, significa que es un single y que el ft. está inmiscuido en el nombre del álbum, por lo que setea el nombre del álbum como el nombre limpio del track.
- Los artistas suelen estar separados por comas, por lo que el metadato de artista elimina la coma espaciada y lo sustituye por el separador más conocido y más compatible: el punto y coma (;). Puedes cambiarlo.
- Si el álbum está vacío, setea el álbum como el nombre del track.
- Como no hay artista del álbum, setea el artista como artista del álbum y si hay más de uno, setea al artista del álbum como el primer artista ya que suele ser así.
- Si se te ocurre cómo mejorar esto o automatizar otros metadatos, eres bienvenido/a. :D

Luego intenta escribir los metadatos (con carátula incluida) en el archivo ogg y pone el ID del enlace de YouTube como metadato de comentario.

El renombrado de archivo se hace similar a cómo yt-dlp nombra a sus archivos para que sea compatible con los caracteres especiales que Windows no permite. Antes de renombrar el archivo ogg, setea el nombre del archivo como “título - artista(s)” donde “artista(s)” si hay más de uno, reemplaza el separador por “, ”. Luego verifica si hay caracteres no compatibles, si los hay los reemplaza por su versión ancha. En total, que los hace compatibles tal como lo hace yt-dlp así que el nombre permanece «original».

Para verificar cómo quedaron los metadatos o si hubo algún error en el procesado, imprime los metadatos del audio. Y si no se han puesto metadatos por no encontrar la imagen de carátula, imprime un aviso. Con esta opción se puede controlar si solo se quiere el audio en mejor calidad sin más o si también se quiere añadir las etiquetas manualmente.

## FIN

Al finalizar el script… finaliza. 🙃

El código es un asco pero funcional. :v

### ¿Y los .sh?
No hay.
.
.
.
.
.
Ok no, aquí esta el [dm](https://files.catbox.moe/t0lmuq.sh) y aquí está el [dmp](https://files.catbox.moe/ig6sco.sh)
Los subo en catbox.moe porque sólo quiero reservar esto para Windows. 🙃
