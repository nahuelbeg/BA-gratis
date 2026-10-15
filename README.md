# BA gratis

Agenda cultural familiar de la Ciudad de Buenos Aires, hecha con HTML, CSS y JavaScript vanilla.

## Uso

Abrí `index.html` en un navegador. El mapa usa Leaflet y teselas de OpenStreetMap; para cargarlos se necesita conexión a internet.

## Extracción y validación de cartelera

`scraper.py` requiere Python 3.10 o posterior y usa únicamente su biblioteca estándar. Alternativa carga la cartelera desde un endpoint JSONP público; el script consulta ese catálogo y extrae sus obras infantiles con funciones futuras, sin depender de ejecutar JavaScript ni de selectores visuales frágiles. Une los eventos infantiles detectados en **cualquiera** de las tres fuentes: no exige que el mismo título aparezca en todas. Consultá las páginas configuradas y guardá el informe de extracción y validación como JSON:

```bash
python scraper.py
```

Por defecto escribe `eventos_extraidos.json`. Podés elegir otro archivo, aumentar el tiempo de espera o indicar páginas específicas de Baires Secreta y LINDA BA:

```bash
python scraper.py --output cartelera.json --timeout 30 --days 7 \
  --baires-url "https://bairessecreta.com/" \
  --linda-url "https://linda.buenosaires.gob.ar/agenda"
```

El arreglo `events` del JSON contiene la unión de eventos infantiles, deduplicada por título normalizado. Cada evento conserva `sources` y `source_details` para saber en qué fuente aparece y qué datos publica cada una. Los conteos de títulos presentes en varias fuentes o en las tres se informan únicamente como validación; nunca excluyen eventos de la unión. La cartelera de Alternativa incluye todas las funciones futuras del catálogo, sin límite predeterminado; podés limitarla con `--days 7`. Los errores HTTP, de red y de lectura quedan en el informe y producen un código de salida distinto de cero; una fuente sin candidatos también genera un aviso. Baires Secreta y LINDA BA se consultan como páginas HTML y pueden requerir URLs más específicas mediante sus opciones si la portada no publica tarjetas de eventos. Para mostrar la unión en el sitio, serví el proyecto por HTTP y dejá `eventos_extraidos.json` en la misma carpeta que `index.html`; la página lo carga y usa la agenda estática de respaldo si el archivo falta o no es válido. Abrir el HTML directamente con `file://` no permite esa carga.

## Curaduría y carga de actividades

Los eventos de teatro infantil se toman de la [cartelera infantil de Alternativa Teatral](https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles). El listado codificado en `script.js` es un respaldo estático de la consulta del 14/10/2026; al cargar `eventos_extraidos.json` por HTTP, la página usa en su lugar la unión más reciente del scraper. Sus fichas originales enlazan desde cada tarjeta. El catálogo puede devolver sala, barrio, funciones, dirección y coordenadas; la edad recomendada no se inventa cuando la fuente no la especifica.

Para teatro, cada registro del arreglo `EVENTS` en `script.js` debe tener `category: "Teatro"`, el enlace a la ficha individual de Alternativa Teatral, título, sala, barrio, fecha de la próxima función mostrada y horario tal como aparecen en la cartelera. Cuando se actualice, revisá la página de origen y cambiá también `date` y `schedule`; no reutilices funciones ya pasadas.

Para añadir contenido manual a las otras categorías, mantené la curaduría de triple fuente. Cada registro debe incluir los enlaces concretos de estas tres publicaciones:

- [Baires Secreta](https://bairessecreta.com/)
- [LINDA BA](https://linda.buenosaires.gob.ar/)
- [Alternativa Teatral](https://www.alternativateatral.com.ar/)

En las categorías no teatrales se necesitan `title`, `category`, `venue`, `neighborhood`, `address`, `description`, `date` (formato `AAAA-MM-DD`), `time`, `age` (por ejemplo `["4-7"]`), `latitude`, `longitude` y `sources`. `sources` debe incluir un objeto por cada fuente, con su identificador (`baires`, `linda` o `alternativa`) y la URL que confirma el evento. La unión automática del scraper muestra las actividades infantiles publicadas en una fuente, sin exigir coincidencia con las otras dos; sus fuentes se presentan juntas cuando el título coincide.

Las vistas por categoría, agenda y mapa comparten la búsqueda y los filtros por edad y barrio.
