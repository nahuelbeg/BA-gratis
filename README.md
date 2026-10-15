# BA gratis

Agenda cultural familiar de la Ciudad de Buenos Aires, hecha con HTML, CSS y JavaScript vanilla.

## Uso

Abrí `index.html` en un navegador. El mapa usa Leaflet y teselas de OpenStreetMap; para cargarlos se necesita conexión a internet.

## Extracción y validación de cartelera

`scraper.py` requiere Python 3.10 o posterior y usa únicamente su biblioteca estándar. Alternativa carga la cartelera desde un endpoint JSONP público; el script consulta ese catálogo y filtra la clasificación infantil por funciones próximas, sin depender de ejecutar JavaScript ni de selectores visuales frágiles. Consultá las páginas configuradas y guardá el informe de extracción y coincidencias exactas como JSON:

```bash
python scraper.py
```

Por defecto escribe `eventos_extraidos.json`. Podés elegir otro archivo, aumentar el tiempo de espera o indicar páginas específicas de Baires Secreta y LINDA BA:

```bash
python scraper.py --output cartelera.json --timeout 30 --days 7 \
  --baires-url "https://bairessecreta.com/" \
  --linda-url "https://linda.buenosaires.gob.ar/agenda"
```

El JSON contiene la cartelera infantil de Alternativa Teatral (título, sala, barrio, dirección, coordenadas, próximas funciones, etiquetas y enlace a la ficha), el total infantil del catálogo, conteos de candidatos y coincidencias exactas de títulos normalizados entre las tres fuentes. El rango predeterminado cubre las funciones desde ahora hasta los próximos siete días; ajustalo con `--days`. Los errores HTTP, de red y de lectura quedan en el informe y producen un código de salida distinto de cero; una fuente sin candidatos también genera un aviso. Baires Secreta y LINDA BA se consultan como páginas HTML y pueden requerir URLs más específicas mediante sus opciones si la portada no publica tarjetas de eventos. Las coincidencias son una ayuda de curaduría, no una publicación automática: revisá los enlaces originales y no tomes cero coincidencias como prueba de que no hay actividades si una fuente usa carga dinámica o cambió su HTML. La agenda del sitio no se modifica al ejecutar el scraper.

## Curaduría y carga de actividades

Los eventos de teatro infantil se toman de la [cartelera infantil de Alternativa Teatral](https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles). El listado incluido es una consulta del 14/10/2026: contiene las 15 obras que mostraba entonces. Sus fichas originales enlazan desde cada tarjeta. La cartelera visual informa sala, barrio y funciones; el catálogo que consulta `scraper.py` también puede devolver dirección y coordenadas de las salas. La edad recomendada no se inventa cuando la fuente no la especifica.

Para teatro, cada registro del arreglo `EVENTS` en `script.js` debe tener `category: "Teatro"`, el enlace a la ficha individual de Alternativa Teatral, título, sala, barrio, fecha de la próxima función mostrada y horario tal como aparecen en la cartelera. Cuando se actualice, revisá la página de origen y cambiá también `date` y `schedule`; no reutilices funciones ya pasadas.

Para otras categorías, mantené la curaduría de triple fuente. Cada registro debe incluir los enlaces concretos de estas tres publicaciones:

- [Baires Secreta](https://bairessecreta.com/)
- [LINDA BA](https://linda.buenosaires.gob.ar/)
- [Alternativa Teatral](https://www.alternativateatral.com.ar/)

En las categorías no teatrales se necesitan `title`, `category`, `venue`, `neighborhood`, `address`, `description`, `date` (formato `AAAA-MM-DD`), `time`, `age` (por ejemplo `["4-7"]`), `latitude`, `longitude` y `sources`. `sources` debe incluir un objeto por cada fuente, con su identificador (`baires`, `linda` o `alternativa`) y la URL que confirma el evento. El renderizado conserva la regla de las tres fuentes para esos eventos.

Las vistas por categoría, agenda y mapa comparten la búsqueda y los filtros por edad y barrio.
