# BA gratis

Agenda cultural familiar de la Ciudad de Buenos Aires, hecha con HTML, CSS y JavaScript vanilla.

## Uso

Para ver los eventos del scraper, primero generá `eventos_extraidos.json` y serví la carpeta por HTTP desde la raíz del proyecto:

```powershell
py -m http.server 8000
```

Después abrí `http://localhost:8000` en el navegador. No abras `index.html` directamente: con `file://` el navegador bloquea la lectura del JSON y la página muestra la agenda estática de respaldo. El mapa usa Leaflet y teselas de OpenStreetMap, por lo que también necesita conexión a internet.

El `package.json` identifica el proyecto como un sitio estático y ofrece un comando `npm run build` sin dependencias. En el hosting, configurá como directorio de publicación la raíz del repositorio; `index.html`, `script.js`, `style.css` y `eventos_extraidos.json` deben quedar juntos. El JSON generado se versiona para que también llegue al hosting.

## Extracción y validación de cartelera

`scraper.py` requiere Python 3.10 o posterior y usa únicamente su biblioteca estándar. Alternativa carga la cartelera desde un endpoint JSONP público, Baires Secreta desde su búsqueda infantil y las páginas de Museos BA, Centro Cultural Recoleta, Usina del Arte, Complejo Teatral, Centro Cultural 25 de Mayo y LA NACION desde sus páginas públicas. Las tarjetas culturales se filtran por señales explícitas de público infantil/familiar; para cine, se usa la clasificación ATP, el género infantil, la animación sin una clasificación de edad restrictiva o una descripción infantil/familiar publicada en la ficha de la película. El scraper conserva fechas, horarios y enlaces cuando la fuente los publica, y une los eventos detectados en **cualquiera** de las fuentes; no exige que el mismo título aparezca en todas. Consultá las fuentes y guardá el informe como JSON:

```bash
python scraper.py
```

Por defecto escribe `eventos_extraidos.json`. Podés elegir otro archivo, aumentar el tiempo de espera o indicar una página específica de Baires Secreta:

```bash
python scraper.py --output cartelera.json --timeout 30 --days 7 \
  --baires-url "https://bairessecreta.com/"
```

El arreglo `events` del JSON contiene la unión deduplicada por título normalizado. Cada evento conserva `sources` y `source_details`, incluidos enlaces, fechas, horarios y datos de ubicación publicados por las fuentes. Los conteos de títulos presentes en varias fuentes o en todas se informan únicamente como validación; nunca excluyen eventos de la unión. Alternativa incluye funciones futuras sin límite predeterminado; podés limitarlas con `--days 7`. Los errores HTTP, de red y de lectura quedan en el informe y producen un código de salida distinto de cero. Versioná `eventos_extraidos.json` junto a `index.html` para publicarlo; si falta, la página muestra la agenda estática de respaldo.

## Curaduría y carga de actividades

Los eventos de teatro infantil se toman de la [cartelera infantil de Alternativa Teatral](https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles). El listado codificado en `script.js` es un respaldo estático de la consulta del 14/10/2026; al cargar `eventos_extraidos.json` por HTTP, la página usa en su lugar la unión más reciente del scraper. Sus fichas originales enlazan desde cada tarjeta. El catálogo puede devolver sala, barrio, funciones, dirección y coordenadas; la edad recomendada no se inventa cuando la fuente no la especifica.

El scraper consulta [Museos BA](https://buenosaires.gob.ar/gcaba_historico/cultura/museos) para actividades de museos; [Centro Cultural Recoleta](http://www.centroculturalrecoleta.org/), [Usina del Arte](https://buenosaires.gob.ar/gcaba_historico/cultura/usina-del-arte), [Complejo Teatral](https://complejoteatral.gob.ar/) y [Centro Cultural 25 de Mayo](https://buenosaires.gob.ar/gcaba_historico/cultura/centro-cultural-25-de-mayo) para programación de teatro y música; y la [cartelera de LA NACION](https://www.lanacion.com.ar/cartelera-de-cine) para cine. Cada evento conserva únicamente el enlace a la ficha o publicación desde la que se obtuvo. Las páginas sin una fecha explícita quedan sin fecha; el scraper no inventa horarios, sedes ni edades.

Para teatro, cada registro del arreglo `EVENTS` en `script.js` debe tener `category: "Teatro"`, el enlace a la ficha individual de Alternativa Teatral, título, sala, barrio, fecha de la próxima función mostrada y horario tal como aparecen en la cartelera. Cuando se actualice, revisá la página de origen y cambiá también `date` y `schedule`; no reutilices funciones ya pasadas.

El scraper incluye las actividades infantiles detectadas en una o más de las fuentes. Cada tarjeta mantiene enlaces solo a las publicaciones donde se encontró el evento; no agregues fuentes no verificadas ni presentes la unión como verificación de todas las fuentes. Las fuentes automáticas son:

- [Baires Secreta](https://bairessecreta.com/)
- [Alternativa Teatral](https://www.alternativateatral.com.ar/)
- [Museos BA](https://buenosaires.gob.ar/gcaba_historico/cultura/museos)
- [Centro Cultural Recoleta](http://www.centroculturalrecoleta.org/)
- [Usina del Arte](https://buenosaires.gob.ar/gcaba_historico/cultura/usina-del-arte)
- [Complejo Teatral](https://complejoteatral.gob.ar/)
- [Centro Cultural 25 de Mayo](https://buenosaires.gob.ar/gcaba_historico/cultura/centro-cultural-25-de-mayo)
- [LA NACION · Cartelera de cine](https://www.lanacion.com.ar/cartelera-de-cine)

En el JSON, cada evento puede incluir `title`, `category`, `venue`, `neighborhood`, `address`, `description`, `date` (formato `AAAA-MM-DD`), `time`, `latitude`, `longitude`, `sources` y `source_details`. Los datos que no estén publicados por la fuente se dejan vacíos; no se inventan edades, ubicaciones ni horarios.

Las vistas por categoría, agenda y mapa comparten el filtro por categoría. Los enlaces de referencia se muestran según la categoría elegida.
