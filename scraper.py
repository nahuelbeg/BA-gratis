#!/usr/bin/env python3
import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen
from time import time as timestamp


URL_BAIRES_SECRETA = "https://bairessecreta.com/?s=infantil"
URL_ALTERNATIVA_INFANTILES = (
    "https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles"
)
URL_ALTERNATIVA_CATALOG = "https://www.alternativateatral.com.ar/get-json.php"

MAX_RESPONSE_BYTES = 8 * 1024 * 1024
USER_AGENT = "PlanazoAgenda/1.0 (+https://www.alternativateatral.com.ar/)"
BUENOS_AIRES_TZ = timezone(timedelta(hours=-3))
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    parent: Node | None = None
    children: list[Node | str] = field(default_factory=list)

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())


class DocumentParser(HTMLParser):
    """Construye un árbol HTML pequeño para poder leer tarjetas y sus campos."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {})
        self.stack = [self.root]

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        node = Node(
            tag.lower(),
            {key.lower(): value or "" for key, value in attrs},
            self.stack[-1],
        )
        self.stack[-1].children.append(node)
        if node.tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        node = Node(
            tag.lower(),
            {key.lower(): value or "" for key, value in attrs},
            self.stack[-1],
        )
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.stack[-1].children.append(data)


def descendants(node: Node) -> Iterable[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from descendants(child)


def text_content(node: Node) -> str:
    pieces: list[str] = []
    for child in node.children:
        pieces.append(text_content(child) if isinstance(child, Node) else child)
    return re.sub(r"\s+", " ", " ".join(pieces)).strip()


def first_node(
    node: Node, *, tag: str | None = None, class_name: str | None = None
) -> Node | None:
    return next(
        (
            child
            for child in descendants(node)
            if (tag is None or child.tag == tag)
            and (class_name is None or class_name in child.classes)
        ),
        None,
    )


def normalizar_texto(texto: str) -> str:
    """Normaliza acentos, signos y espacios antes de comparar títulos."""
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def es_evento_infantil(titulo: str, descripcion: str = "") -> bool:
    titulo_norm = normalizar_texto(titulo)
    descripcion_norm = normalizar_texto(descripcion)
    audiencia_explicita = (
        r"\b(ninos|ninas|infantil\w*|chicos|chicas|bebes|infancias|"
        r"adolescentes)\b"
    )
    familia_explicita = (
        r"\b(en familia|para familias|para la familia|para toda la familia|"
        r"familiar)\b"
    )
    if re.search(audiencia_explicita, titulo_norm):
        return True
    if re.search(familia_explicita, titulo_norm):
        return True
    return bool(
        re.search(audiencia_explicita, descripcion_norm)
        or re.search(familia_explicita, descripcion_norm)
    )


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())


def html_a_texto(value: object) -> str:
    if not isinstance(value, str):
        return ""
    parser = HTMLTextExtractor()
    parser.feed(value)
    parser.close()
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def menciona_dia_del_nino_pasado(titulo: str, descripcion: str) -> bool:
    if "dia del nino" not in normalizar_texto(titulo):
        return False
    meses = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }
    texto = normalizar_texto(descripcion)
    match = re.search(
        r"\b(\d{1,2})\s+de\s+("
        + "|".join(meses)
        + r")\s+de\s+(\d{4})\b",
        texto,
    )
    if not match:
        return False
    try:
        event_date = date(
            int(match.group(3)), meses[match.group(2)], int(match.group(1))
        )
    except ValueError:
        return False
    return event_date < datetime.now(BUENOS_AIRES_TZ).date()


def descargar_html(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        if response.status < 200 or response.status >= 300:
            raise OSError(f"Respuesta HTTP inesperada: {response.status}")
        content_type = response.headers.get_content_charset() or "utf-8"
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError(
                f"La respuesta supera el límite de {MAX_RESPONSE_BYTES} bytes."
            )
    return body.decode(content_type, errors="replace")


def parsear_html(html: str) -> Node:
    parser = DocumentParser()
    parser.feed(html)
    parser.close()
    return parser.root


def extraer_tarjetas_genericas(
    root: Node, nombre_fuente: str, url_fuente: str
) -> list[dict[str, str]]:
    """Lee tarjetas editoriales de la fuente y filtra las infantiles."""
    containers = [
        node
        for node in descendants(root)
        if node.tag == "article"
        or node.classes.intersection({"post-item", "event-card", "agenda-item"})
    ]
    if not containers:
        containers = [
            node
            for node in descendants(root)
            if node.tag in {"h2", "h3", "h4"}
        ]

    results: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for container in containers:
        heading = first_node(container, tag="h1") or first_node(
            container, tag="h2"
        ) or first_node(container, tag="h3") or first_node(container, tag="h4")
        title_node = heading or first_node(container, tag="a")
        if title_node is None:
            continue
        title = text_content(title_node)
        description_node = first_node(container, tag="p")
        description = text_content(description_node) if description_node else ""
        if not title or not es_evento_infantil(title):
            continue
        if nombre_fuente == "Baires Secreta" and menciona_dia_del_nino_pasado(
            title, description
        ):
            continue

        link_node = first_node(heading, tag="a") if heading else None
        if title_node.tag == "a":
            link_node = title_node
        href = link_node.attrs.get("href", "") if link_node else ""
        item_url = urljoin(url_fuente, href) if href else url_fuente
        key = (normalizar_texto(title), item_url)
        if key in seen:
            continue
        seen.add(key)
        results.append(
            {
                "title": title,
                "normalized_title": key[0],
                "description": description,
                "url": item_url,
                "source": nombre_fuente,
            }
        )
    return results


def es_categoria_infantil(classifications: object) -> bool:
    if not isinstance(classifications, dict):
        return False
    category = classifications.get("9")
    return isinstance(category, dict) and category.get("descripcion") == "Infantiles"


def extraer_cartelera_alternativa(
    payload: object, dias: int | None, hoy: date | None = None
) -> tuple[list[dict[str, object]], int]:
    """Extrae obras infantiles con funciones próximas del catálogo."""
    if not isinstance(payload, dict) or not isinstance(payload.get("espectaculos"), dict):
        raise ValueError("El catálogo JSON de Alternativa no tiene la estructura esperada.")

    catalog = payload["espectaculos"]
    infantil_count = 0
    today = hoy or date.today()
    now = (
        datetime.now(BUENOS_AIRES_TZ).replace(tzinfo=None)
        if hoy is None
        else datetime.combine(today, datetime.min.time())
    )
    last_day = today + timedelta(days=dias) if dias is not None else None
    events: list[dict[str, object]] = []

    for show in catalog.values():
        if not isinstance(show, dict) or not es_categoria_infantil(
            show.get("clasificaciones")
        ):
            continue
        infantil_count += 1

        title = show.get("titulo")
        path = show.get("url")
        venues = show.get("lugares")
        if not isinstance(title, str) or not isinstance(path, str):
            continue
        if not isinstance(venues, dict):
            continue

        upcoming: list[
            tuple[datetime, dict[str, object], dict[str, object]]
        ] = []
        for venue in venues.values():
            if not isinstance(venue, dict):
                continue
            functions = venue.get("funciones")
            if not isinstance(functions, dict):
                continue
            for function in functions.values():
                if not isinstance(function, dict):
                    continue
                function_date = function.get("proxima_fecha")
                if not isinstance(function_date, str):
                    continue
                try:
                    starts_at = datetime.strptime(function_date, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if starts_at < now:
                    continue
                if last_day is not None and starts_at.date() > last_day:
                    continue
                upcoming.append((starts_at, venue, function))

        if not upcoming:
            continue
        upcoming.sort(key=lambda function: function[0])
        next_start, venue, next_details = upcoming[0]
        classifications = show.get("clasificaciones")
        genres = []
        if isinstance(classifications, dict):
            genres = list(dict.fromkeys(
                item["descripcion"]
                for item in classifications.values()
                if isinstance(item, dict)
                and item.get("padre") == 26
                and isinstance(item.get("descripcion"), str)
            ))
        source_url = urljoin(
            "https://www.alternativateatral.com.ar/", path.lstrip("/")
        )
        events.append(
            {
                "title": title,
                "normalized_title": normalizar_texto(title),
                "category": "Teatro",
                "venue": str(venue.get("nombre", "")),
                "neighborhood": str(venue.get("zona", "")),
                "province": str(venue.get("provincia", "")),
                "address": str(venue.get("direccion", "")),
                "latitude": venue.get("lat"),
                "longitude": venue.get("lng"),
                "date": next_start.date().isoformat(),
                "time": next_start.strftime("%H:%M"),
                "schedule": (
                    f"{str(next_details.get('dia', '')).upper()} "
                    f"{next_start.strftime('%H:%M')} · {next_start.date().isoformat()}"
                ),
                "functions": [
                    {
                        "date": starts_at.date().isoformat(),
                        "time": starts_at.strftime("%H:%M"),
                        "weekday": str(details.get("dia", "")),
                        "venue": str(function_venue.get("nombre", "")),
                        "neighborhood": str(function_venue.get("zona", "")),
                    }
                    for starts_at, function_venue, details in upcoming
                ],
                "genres": genres,
                "url": source_url,
                "source": "Alternativa Teatral",
            }
        )

    events.sort(
        key=lambda event: (
            str(event["date"]),
            str(event["time"]),
            str(event["title"]),
        )
    )
    return events, infantil_count


def descargar_cartelera_alternativa(
    timeout: float, dias: int | None
) -> tuple[list[dict[str, object]], int]:
    params = urlencode(
        {
            "t": "novedades",
            "r": "cartelera",
            "callback": "jsoncallback",
            "_": int(timestamp() * 1000),
        }
    )
    url = f"{URL_ALTERNATIVA_CATALOG}?{params}"
    response_text = descargar_html(url, timeout).lstrip("\ufeff").strip()
    match = re.fullmatch(r"jsoncallback\((.*)\);?", response_text, re.DOTALL)
    if not match:
        raise ValueError("Alternativa devolvió una respuesta JSONP inesperada.")
    payload = json.loads(match.group(1).lstrip("\ufeff"))
    return extraer_cartelera_alternativa(payload, dias)


def consolidar_eventos(
    eventos_por_fuente: dict[str, list[dict[str, object]]]
) -> tuple[list[dict[str, object]], dict[str, int]]:
    """Une los eventos de todas las fuentes y anota dónde apareció cada uno."""
    eventos_unicos: dict[str, dict[str, object]] = {}
    for fuente, eventos in eventos_por_fuente.items():
        for evento in eventos:
            titulo = evento.get("title")
            if not isinstance(titulo, str) or not titulo.strip():
                continue
            titulo_normalizado = normalizar_texto(titulo)
            if not titulo_normalizado:
                continue

            evento_unificado = eventos_unicos.setdefault(
                titulo_normalizado,
                {
                    "title": titulo,
                    "normalized_title": titulo_normalizado,
                    "sources": [],
                    "source_details": {},
                },
            )
            if fuente not in evento_unificado["sources"]:
                evento_unificado["sources"].append(fuente)
                evento_unificado["source_details"][fuente] = evento

    eventos = sorted(
        eventos_unicos.values(),
        key=lambda evento: (str(evento["normalized_title"]), str(evento["title"])),
    )
    return eventos, {
        "events_in_one_source": sum(len(evento["sources"]) == 1 for evento in eventos),
        "events_in_multiple_sources": sum(
            len(evento["sources"]) > 1 for evento in eventos
        ),
        "events_in_all_sources": sum(
            len(evento["sources"]) == len(eventos_por_fuente) for evento in eventos
        ),
    }


def obtener_fuente(
    nombre: str, url: str, timeout: float
) -> tuple[list[dict[str, str]], dict[str, str] | None]:
    try:
        html = descargar_html(url, timeout)
    except HTTPError as error:
        return [], {
            "source": nombre,
            "url": url,
            "error": f"HTTP {error.code}: {error.reason}",
        }
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return [], {
            "source": nombre,
            "url": url,
            "error": f"{type(error).__name__}: {error}",
        }
    return extraer_tarjetas_genericas(parsear_html(html), nombre, url), None


def ejecutar(
    timeout: float, dias: int | None, baires_url: str
) -> dict[str, object]:
    print("Consultando fuentes culturales...", file=sys.stderr)
    baires, baires_error = obtener_fuente(
        "Baires Secreta", baires_url, timeout
    )
    try:
        alternativa, catalog_count = descargar_cartelera_alternativa(timeout, dias)
        alternativa_error = None
    except HTTPError as error:
        alternativa = []
        catalog_count = 0
        alternativa_error = {
            "source": "Alternativa Teatral",
            "url": URL_ALTERNATIVA_INFANTILES,
            "error": f"HTTP {error.code}: {error.reason}",
        }
    except (URLError, TimeoutError, OSError, ValueError) as error:
        alternativa = []
        catalog_count = 0
        alternativa_error = {
            "source": "Alternativa Teatral",
            "url": URL_ALTERNATIVA_INFANTILES,
            "error": f"{type(error).__name__}: {error}",
        }

    source_events = {
        "Baires Secreta": [dict(event) for event in baires],
        "Alternativa Teatral": [dict(event) for event in alternativa],
    }
    all_events, distribution = consolidar_eventos(source_events)
    source_title_sets = {
        source: {event["normalized_title"] for event in events}
        for source, events in source_events.items()
    }
    all_source_matches = set.intersection(*source_title_sets.values())
    cross_source_matches = (
        set.union(*source_title_sets.values()) - all_source_matches
    )
    errors = [
        error
        for error in (baires_error, alternativa_error)
        if error is not None
    ]

    return {
        "generated_at": datetime.now(BUENOS_AIRES_TZ).isoformat(timespec="seconds"),
        "theater_source": URL_ALTERNATIVA_INFANTILES,
        "upcoming_days": dias,
        "catalog_infantile_count": catalog_count,
        "theater_events": alternativa,
        "cross_validation": {
            "method": "coincidencia exacta de títulos normalizados",
            "publishing_rule": (
                "unión de eventos infantiles; la coincidencia entre fuentes "
                "no es requisito para incluirlos"
            ),
            "source_counts": {
                "baires_secreta_infantil_candidates": len(baires),
                "alternativa_infantiles_in_range": len(alternativa),
            },
            "title_distribution": distribution,
            "titles_in_multiple_sources_but_not_all": len(cross_source_matches),
            "titles_found_in_all_sources": len(all_source_matches),
        },
        "events": all_events,
        "errors": errors,
    }


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extrae la cartelera infantil de Alternativa Teatral y compara "
            "títulos infantiles detectados en las fuentes."
        )
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("eventos_extraidos.json"),
        help="Archivo JSON de salida (por defecto: eventos_extraidos.json).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="Tiempo máximo de espera por sitio, en segundos (por defecto: 20).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Limita las funciones a los próximos N días (por defecto: sin límite).",
    )
    parser.add_argument(
        "--baires-url",
        default=URL_BAIRES_SECRETA,
        help="URL de la página de Baires Secreta que se va a revisar.",
    )
    return parser.parse_args()


def main() -> int:
    args = parsear_argumentos()
    if args.timeout <= 0 or (args.days is not None and args.days < 0):
        print("El timeout debe ser positivo y los días no negativos.", file=sys.stderr)
        return 2

    for option_name, url in (("--baires-url", args.baires_url),):
        if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
            print(f"{option_name} debe ser una URL HTTP o HTTPS válida.", file=sys.stderr)
            return 2

    report = ejecutar(args.timeout, args.days, args.baires_url)
    try:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"No se pudo guardar {args.output}: {error}", file=sys.stderr)
        return 1

    counts = report["cross_validation"]["source_counts"]
    days_summary = (
        "sin límite de días"
        if report["upcoming_days"] is None
        else f"en los próximos {report['upcoming_days']} días"
    )
    print(
        "Cartelera infantil de Alternativa: "
        f"{counts['alternativa_infantiles_in_range']} obras con función "
        f"{days_summary} "
        f"({report['catalog_infantile_count']} infantiles en el catálogo).",
        file=sys.stderr,
    )
    print(
        f"Eventos infantiles incluidos en la unión: {len(report['events'])} "
        "(cada evento conserva las fuentes donde fue encontrado).",
        file=sys.stderr,
    )
    print(
        "Coincidencias en todas las fuentes (solo estadística): "
        f"{report['cross_validation']['titles_found_in_all_sources']}.",
        file=sys.stderr,
    )
    print(f"Informe guardado en: {args.output}", file=sys.stderr)
    for error in report["errors"]:
        print(
            f"Error al consultar {error['source']} ({error['url']}): "
            f"{error['error']}",
            file=sys.stderr,
        )
    if (
        any(count == 0 for count in counts.values())
        and not report["errors"]
    ):
        print(
            "Aviso: una fuente devolvió cero candidatos infantiles; "
            "revisá el HTML y los selectores antes de interpretar "
            "la ausencia de coincidencias como definitiva.",
            file=sys.stderr,
        )
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
