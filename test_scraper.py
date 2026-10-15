import json
import unittest
from datetime import date
from unittest.mock import patch

import scraper


class CulturalSourceTests(unittest.TestCase):
    def test_extracts_family_event_with_source_category_and_future_date(self):
        html = """
        <div class="event-card">
          <h3><a href="/agenda/titeres">Teatro de títeres para niñes</a></h3>
          <p>Una actividad para toda la familia. 22 de octubre de 2026 a las 16 h.</p>
        </div>
        <article>
          <h2><a href="/agenda/adultos">Una obra para adultos</a></h2>
          <p>Funciones el 24 de octubre de 2026 a las 20 h.</p>
        </article>
        """

        events = scraper.extraer_eventos_fuente(
            scraper.parsear_html(html),
            "Complejo Teatral de Buenos Aires",
            scraper.SOURCE_URLS["Complejo Teatral de Buenos Aires"],
            scraper.SOURCE_CATEGORIES["Complejo Teatral de Buenos Aires"],
            hoy=date(2026, 10, 15),
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["category"], "Teatro")
        self.assertEqual(events[0]["date"], "2026-10-22")
        self.assertEqual(events[0]["time"], "16:00")
        self.assertEqual(
            events[0]["url"],
            "https://complejoteatral.gob.ar/agenda/titeres",
        )

    def test_uses_upcoming_date_from_a_repeating_event_schedule(self):
        event_date, found_date = scraper.extraer_fecha_evento(
            "08, 15, 22 y 29 de octubre | 19 h",
            hoy=date(2026, 10, 15),
        )

        self.assertTrue(found_date)
        self.assertEqual(event_date, "2026-10-22")

    def test_rejects_cards_with_only_past_event_dates(self):
        html = """
        <div class="event-card">
          <h3>Teatro para niñas y niños</h3>
          <p>Para toda la familia. 8 de octubre de 2026 a las 16 h.</p>
        </div>
        """
        events = scraper.extraer_eventos_fuente(
            scraper.parsear_html(html),
            "Centro Cultural Recoleta",
            scraper.SOURCE_URLS["Centro Cultural Recoleta"],
            scraper.SOURCE_CATEGORIES["Centro Cultural Recoleta"],
            hoy=date(2026, 10, 15),
        )

        self.assertEqual(events, [])

    def test_skips_the_venue_presentation_as_an_event_card(self):
        html = """
        <div class="card-simple">
          <h1>Usina del Arte</h1>
          <p>Programación cultural y propuestas para toda la familia.</p>
        </div>
        """

        events = scraper.extraer_eventos_fuente(
            scraper.parsear_html(html),
            "Usina del Arte",
            scraper.SOURCE_URLS["Usina del Arte"],
            scraper.SOURCE_CATEGORIES["Usina del Arte"],
        )

        self.assertEqual(events, [])

    def test_extracts_only_movies_with_explicit_family_suitability(self):
        listing = """
        <a href="/cartelera-de-cine/pelicula/familiar">
          <article><h3>Una película</h3></article>
        </a>
        <a href="/cartelera-de-cine/pelicula/animada">
          <article><h3>Una película animada</h3></article>
        </a>
        <a href="/cartelera-de-cine/pelicula/adulta">
          <article><h3>Otra película</h3></article>
        </a>
        """
        movie_pages = {
            "https://www.lanacion.com.ar/cartelera-de-cine/pelicula/familiar": (
                '<script type="application/ld+json">'
                + json.dumps({
                    "@type": "Movie",
                    "name": "Una película",
                    "description": "Una aventura para toda la familia.",
                    "genre": "Animación",
                    "contentRating": "ATP",
                })
                + "</script>"
            ),
            "https://www.lanacion.com.ar/cartelera-de-cine/pelicula/animada": (
                '<script type="application/ld+json">'
                + json.dumps({
                    "@type": "Movie",
                    "name": "Una película animada",
                    "description": "Una aventura.",
                    "genre": "Animación",
                    "contentRating": "Sin calificación",
                })
                + "</script>"
            ),
            "https://www.lanacion.com.ar/cartelera-de-cine/pelicula/adulta": (
                '<script type="application/ld+json">'
                + json.dumps({
                    "@type": "Movie",
                    "name": "Otra película",
                    "description": "Un drama policial.",
                    "genre": "Drama",
                    "contentRating": "16",
                })
                + "</script>"
            ),
        }

        with patch.object(
            scraper,
            "descargar_html",
            side_effect=lambda *args: movie_pages[args[0]],
        ):
            events, errors = scraper.extraer_eventos_cine_lanacion(listing, 2)

        self.assertEqual(errors, [])
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["category"], "Cine")
        self.assertEqual(
            {event["title"] for event in events},
            {"Una película", "Una película animada"},
        )


if __name__ == "__main__":
    unittest.main()
