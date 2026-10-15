# BA gratis

Agenda cultural familiar de la Ciudad de Buenos Aires, hecha con HTML, CSS y JavaScript vanilla.

## Uso

Para ver los eventos del scraper, primero generá `eventos_extraidos.json` y serví la carpeta por HTTP desde la raíz del proyecto:

```powershell
py -m http.server 8000
```

Después abrí `http://localhost:8000` en el navegador. No abras `index.html` directamente: con `file://` el navegador bloquea la lectura del JSON y la página muestra la agenda estática de respaldo. El mapa usa Leaflet y teselas de OpenStreetMap, por lo que también necesita conexión a internet.

## Extracción y validación de cartelera

`scraper.py` requiere Python 3.10 o posterior y usa únicamente su biblioteca estándar. Alternativa carga la cartelera desde un endpoint JSONP público; LINDA BA se consulta desde su API pública paginada y Baires Secreta desde su búsqueda de contenido infantil. El scraper extrae títulos con señales explícitas de público infantil/familiar, conserva solo funciones futuras de LINDA y Alternativa, y une los eventos detectados en **cualquiera** de las fuentes; no exige que el mismo título aparezca en todas. Consultá las fuentes y guardá el informe como JSON:

```bash
python scraper.py
```

Por defecto escribe `eventos_extraidos.json`. Podés elegir otro archivo, aumentar el tiempo de espera o indicar páginas específicas de Baires Secreta y LINDA BA:

```bash
python scraper.py --output cartelera.json --timeout 30 --days 7 \
  --baires-url "https://bairessecreta.com/" \
  --linda-url "https://linda.buenosaires.gob.ar/agenda"
```

El arreglo `events` del JSON contiene la unión deduplicada por título normalizado. Cada evento conserva `sources` y `source_details`, incluidos enlaces, fechas, horarios y datos de ubicación publicados por las fuentes. Los conteos de títulos presentes en varias fuentes o en las tres se informan únicamente como validación; nunca excluyen eventos de la unión. Alternativa y LINDA BA incluyen funciones futuras sin límite predeterminado; podés limitar ambas con `--days 7`. Los errores HTTP, de red y de lectura quedan en el informe y producen un código de salida distinto de cero. El archivo está ignorado por Git: para publicar el sitio en hosting estático, asegurate de incluir `eventos_extraidos.json` junto a `index.html`; si falta, la página muestra la agenda estática de respaldo.

## Curaduría y carga de actividades

Los eventos de teatro infantil se toman de la [cartelera infantil de Alternativa Teatral](https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles). El listado codificado en `script.js` es un respaldo estático de la consulta del 14/10/2026; al cargar `eventos_extraidos.json` por HTTP, la página usa en su lugar la unión más reciente del scraper. Sus fichas originales enlazan desde cada tarjeta. El catálogo puede devolver sala, barrio, funciones, dirección y coordenadas; la edad recomendada no se inventa cuando la fuente no la especifica.

Para teatro, cada registro del arreglo `EVENTS` en `script.js` debe tener `category: "Teatro"`, el enlace a la ficha individual de Alternativa Teatral, título, sala, barrio, fecha de la próxima función mostrada y horario tal como aparecen en la cartelera. Cuando se actualice, revisá la página de origen y cambiá también `date` y `schedule`; no reutilices funciones ya pasadas.

El scraper incluye las actividades infantiles detectadas en una o más de las fuentes. Cada tarjeta mantiene enlaces solo a las publicaciones donde se encontró el evento; no agregues fuentes no verificadas ni presentes la unión como verificación triple. Las fuentes son:

- [Baires Secreta](https://bairessecreta.com/)
- [LINDA BA](https://linda.buenosaires.gob.ar/)
- [Alternativa Teatral](https://www.alternativateatral.com.ar/)

En el JSON, cada evento puede incluir `title`, `category`, `venue`, `neighborhood`, `address`, `description`, `date` (formato `AAAA-MM-DD`), `time`, `latitude`, `longitude`, `sources` y `source_details`. Los datos que no estén publicados por la fuente se dejan vacíos; no se inventan edades, ubicaciones ni horarios.

Las vistas por categoría, agenda y mapa comparten la búsqueda y los filtros por edad y barrio.
