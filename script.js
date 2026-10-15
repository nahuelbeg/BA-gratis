"use strict";

const SOURCES = [
  { id: "baires", name: "Baires Secreta", url: "https://bairessecreta.com/" },
  { id: "linda", name: "LINDA BA", url: "https://linda.buenosaires.gob.ar/" },
  { id: "alternativa", name: "Alternativa Teatral", url: "https://www.alternativateatral.com.ar/obras.asp?cat=9-infantiles" }
];

const FALLBACK_EVENTS = [
  { title: "Jazz Cartoons. Por Paris Jazz Club", category: "Teatro", genre: "Jazz", venue: "ND ATENEO", neighborhood: "Retiro", date: "2026-10-16", schedule: "VIE 21:00 · el 16/10", sourcePath: "obra68679-jazz-cartoons-por-paris-jazz-club" },
  { title: "Nicte", category: "Teatro", genre: "Teatro", venue: "MUY TEATRO", neighborhood: "Almagro", date: "2026-10-17", schedule: "SÁB 15:00 · hasta el 24/10", sourcePath: "obra91606-nicte" },
  { title: "ODISEA: Bajo el Mar", category: "Teatro", genre: "Teatro · Títeres", venue: "CENTRO CULTURAL 25 DE MAYO", neighborhood: "Villa Urquiza", date: "2026-10-17", schedule: "SÁB 15:00 · hasta el 28/11", sourcePath: "obra96700-odisea-bajo-el-mar" },
  { title: "3obras3", category: "Teatro", genre: "Títeres", venue: "MUSEO ARGENTINO DEL TITERE", neighborhood: "San Telmo", date: "2026-10-17", schedule: "SÁB 16:00 · el 17/10", sourcePath: "obra42355-3obras3" },
  { title: "Mi amiga la oscuridad", category: "Teatro", genre: "Teatro", venue: "TEATRO CIEGO", neighborhood: "Balvanera", date: "2026-10-17", schedule: "SÁB 16:00 · hasta el 26/12", sourcePath: "obra32241-mi-amiga-la-oscuridad" },
  { title: "Anna y Elsa: un musical entre hielos", category: "Teatro", genre: "Musical", venue: "TERRAZA TEATRO BAR", neighborhood: "San Nicolás", date: "2026-10-17", schedule: "SÁB 17:00 · el 17/10; SÁB 17:00 | DOM 17:00 · del 24/10 al 25/10", sourcePath: "obra80506-anna-y-elsa-un-musical-entre-hielos" },
  { title: "María Elena", category: "Teatro", genre: "Teatro", venue: "LA GALERA ENCANTADA", neighborhood: "Palermo", date: "2026-10-17", schedule: "SÁB 17:00 · el 17/10 y el 31/10; DOM 17:00 · el 29/11", sourcePath: "obra10643-maria-elena" },
  { title: "Mirá que te miro", category: "Teatro", genre: "Teatro · Comedia", venue: "GENTE DE ARTE", neighborhood: "Avellaneda", date: "2026-10-17", schedule: "SÁB 20:00 · hasta el 24/10", sourcePath: "obra73210-mira-que-te-miro" },
  { title: "Olga Poblete - Ciclo de Artes Circenses", category: "Teatro", genre: "Circo", venue: "EL SÁBATO ESPACIO CULTURAL ECONÓMICAS UBA", neighborhood: "Balvanera", date: "2026-10-17", schedule: "SÁB 20:00 · del 17/10 al 31/10", sourcePath: "obra103275-olga-poblete-ciclo-de-artes-circenses" },
  { title: "Y estoy vivo y Contando: Juan Moreira", category: "Teatro", genre: "Unipersonales · Títeres", venue: "MUSEO ARGENTINO DEL TITERE", neighborhood: "San Telmo", date: "2026-10-17", schedule: "SÁB 20:00 · el 17/10", sourcePath: "obra11479-y-estoy-vivo-y-contando-juan-moreira" },
  { title: "Chakana", category: "Teatro", genre: "Teatro · Circo", venue: "CLUB DE TRAPECISTAS ESTRELLA DEL CENTENARIO", neighborhood: "Villa Crespo", date: "2026-10-17", schedule: "SÁB 21:00 · hasta el 31/10", sourcePath: "obra97394-chakana" },
  { title: "Cinema Aventura", category: "Teatro", genre: "Teatro", venue: "NÜN TEATRO BAR", neighborhood: "Villa Crespo", date: "2026-10-18", schedule: "DOM 16:00 · hasta el 29/11", sourcePath: "obra103000-cinema-aventura" },
  { title: "El maravilloso Mago de Oz", category: "Teatro", genre: "Teatro", venue: "NUEVO TEATRO GARGANTÚA", neighborhood: "Palermo", date: "2026-10-18", schedule: "DOM 16:00 · del 18/10 al 25/10", sourcePath: "obra100365-el-maravilloso-mago-de-oz" },
  { title: "Alicia, un país de maravillas", category: "Teatro", genre: "Teatro", venue: "LA GALERA ENCANTADA", neighborhood: "Palermo", date: "2026-10-18", schedule: "DOM 17:00 · el 18/10 y el 15/11", sourcePath: "obra14347-alicia-un-pais-de-maravillas" },
  { title: "¡BASTA PARA MÍ, AQUÍ ME PLANTO!", category: "Teatro", genre: "Teatro", venue: "EL JUFRÉ TEATRO BAR", neighborhood: "Villa Crespo", date: "2026-10-18", schedule: "DOM 17:30 · del 18/10 al 25/10", sourcePath: "obra102689-basta-para-mi-aqui-me-planto" }
].map((event) => ({
  ...event,
  age: [],
  ageLabel: "Infantil · edad no especificada",
  description: `${event.genre}, en cartelera infantil de Alternativa Teatral.`,
  sources: [{
    id: "alternativa",
    name: "Alternativa Teatral",
    url: `https://www.alternativateatral.com/${event.sourcePath}`
  }]
}));
let EVENTS = [...FALLBACK_EVENTS];

const CATEGORY_COLORS = {
  Teatro: "#d98468",
  Música: "#8877ba",
  Cine: "#ce9c34",
  Recreación: "#4e9a8f",
  Museos: "#6689a6",
  Infantil: "#678c75"
};
const SOURCE_HOSTS = {
  baires: "bairessecreta.com",
  linda: "buenosaires.gob.ar",
  alternativa: "alternativateatral.com.ar"
};
const SOURCE_BY_NAME = Object.fromEntries(SOURCES.map((source) => [source.name, source]));
const CATEGORIES = new Set(Object.keys(CATEGORY_COLORS));
const AGE_RANGES = new Set(["0-3", "4-7", "8-12"]);

const state = {
  tab: "categories",
  category: "",
  search: "",
  age: "",
  neighborhood: ""
};

const categoryEvents = document.querySelector("#category-events");
const agendaEvents = document.querySelector("#agenda-events");
const resultsCount = document.querySelector("#results-count");
const searchInput = document.querySelector("#search-input");
const ageFilter = document.querySelector("#age-filter");
const neighborhoodFilter = document.querySelector("#neighborhood-filter");
const mapStatus = document.querySelector("#map-status");
const dataStatus = document.querySelector("#data-status");
let map;
let markers;

function populateNeighborhoodFilter() {
  const existing = new Set([...neighborhoodFilter.options].map((option) => option.value));
  [...new Set(EVENTS.map((event) => event.neighborhood).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, "es"))
    .forEach((neighborhood) => {
      if (existing.has(neighborhood)) return;
      neighborhoodFilter.add(new Option(neighborhood, neighborhood));
    });
}

function isAllowedSourceUrl(source, url) {
    if (!source || typeof url !== "string") return false;
    try {
      const hostname = new URL(url).hostname;
      return hostname === SOURCE_HOSTS[source.id]
        || hostname.endsWith(`.${SOURCE_HOSTS[source.id]}`);
    } catch {
      return false;
    }
}

function eventFromScraperRecord(record) {
    if (
      !record
      || typeof record.title !== "string"
      || !record.source_details
      || !Array.isArray(record.sources)
    ) return null;
    const sources = record.sources.flatMap((sourceName) => {
      const source = SOURCE_BY_NAME[sourceName];
      const detail = record.source_details[sourceName];
      if (!source || !detail || !isAllowedSourceUrl(source, detail.url)) return [];
      return [{ id: source.id, name: source.name, url: detail.url }];
    });
    if (!sources.length) return null;

    const details = Object.values(record.source_details);
    const theater = record.source_details["Alternativa Teatral"];
    const primary = theater || details.find((detail) => detail.date || detail.venue) || details[0];
    const description = details
      .map((detail) => detail.description)
      .filter((text) => typeof text === "string" && text.trim())
      .join(" · ");
    return {
      title: primary?.title || record.title,
      category: theater ? "Teatro" : CATEGORIES.has(primary?.category) ? primary.category : "Infantil",
      genre: primary?.genres?.join(" · ") || "",
      venue: primary?.venue || "",
      neighborhood: primary?.neighborhood || "",
      address: primary?.address || "",
      latitude: primary?.latitude,
      longitude: primary?.longitude,
      date: primary?.date || "",
      time: primary?.time || "",
      schedule: primary?.schedule || "",
      age: [],
      ageLabel: "Infantil · edad no especificada",
      description: description || "Actividad infantil publicada en una fuente cultural.",
      sources,
      importedFromScraper: true
    };
}

function eventFromLegacyTheaterRecord(record) {
    if (
      !record
      || typeof record.title !== "string"
      || typeof record.url !== "string"
      || !isAllowedSourceUrl(SOURCE_BY_NAME["Alternativa Teatral"], record.url)
    ) return null;
    return {
      ...record,
      category: "Teatro",
      age: [],
      ageLabel: "Infantil · edad no especificada",
      description: `${(record.genres || []).join(" · ") || "Teatro"}, en cartelera infantil de Alternativa Teatral.`,
      sources: [{
        id: "alternativa",
        name: "Alternativa Teatral",
        url: record.url
      }],
      importedFromScraper: true
    };
}

async function loadScrapedEvents() {
    if (window.location.protocol === "file:") {
      dataStatus.textContent = "Usando agenda local. Serví el sitio por HTTP para cargar eventos_extraidos.json.";
      return;
    }
    try {
      const response = await fetch("./eventos_extraidos.json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} al leer eventos_extraidos.json`);
      }
      const report = await response.json();
      if (Array.isArray(report.events)) {
        EVENTS = report.events.map(eventFromScraperRecord).filter(Boolean);
        dataStatus.textContent = `Agenda actualizada desde ${EVENTS.length} eventos extraídos.`;
      } else if (Array.isArray(report.theater_events)) {
        EVENTS = report.theater_events.map(eventFromLegacyTheaterRecord).filter(Boolean);
        dataStatus.textContent = "El JSON es de una versión anterior: contiene teatro, pero no la unión de las tres fuentes. Volvé a ejecutar scraper.py.";
        console.warn("eventos_extraidos.json usa el formato anterior; faltan eventos de Baires Secreta y LINDA BA.");
      } else {
        throw new Error("El JSON no contiene el arreglo events.");
      }
      populateNeighborhoodFilter();
      render();
    } catch (error) {
      dataStatus.textContent = "No se pudo cargar el JSON del scraper; se muestra la agenda de respaldo.";
      console.warn("No se pudo cargar eventos_extraidos.json.", error);
    }
}

function isVerifiedEvent(event) {
    if (!Array.isArray(event.sources) || !Array.isArray(event.age)) return false;
    if (event.importedFromScraper) {
      return typeof event.title === "string"
        && CATEGORIES.has(event.category)
        && event.sources.length > 0
        && event.sources.every((source) =>
          isAllowedSourceUrl(SOURCE_BY_NAME[source.name], source.url)
        );
    }
  const validDate = typeof event.date === "string"
    && /^\d{4}-\d{2}-\d{2}$/.test(event.date)
    && !Number.isNaN(new Date(`${event.date}T00:00:00Z`).getTime())
    && new Date(`${event.date}T00:00:00Z`).toISOString().slice(0, 10) === event.date;
  const validRecord = validDate
    && typeof event.title === "string"
    && typeof event.description === "string"
    && CATEGORIES.has(event.category)
    && typeof event.venue === "string"
    && typeof event.neighborhood === "string";
  if (!validRecord) return false;

  if (event.category === "Teatro") {
    const source = event.sources[0];
    if (event.sources.length !== 1 || !source || source.id !== "alternativa") return false;
    try {
      const sourceUrl = new URL(source.url);
      return (sourceUrl.hostname === "www.alternativateatral.com"
        || sourceUrl.hostname === "www.alternativateatral.com.ar")
        && /^\/obra\d+-/.test(sourceUrl.pathname)
        && typeof event.schedule === "string";
    } catch {
      return false;
    }
  }

  const linkedSources = new Set(event.sources.map((source) => source.id));
  const hasThreeSourceLinks = SOURCES.every((source) => {
    const link = event.sources.find((item) => item.id === source.id);
    if (!link || typeof link.url !== "string") return false;
    try {
      const hostname = new URL(link.url).hostname;
      return hostname === SOURCE_HOSTS[source.id] || hostname.endsWith(`.${SOURCE_HOSTS[source.id]}`);
    } catch {
      return false;
    }
  });
  return linkedSources.size === SOURCES.length
    && hasThreeSourceLinks
    && Number.isFinite(event.latitude)
    && Number.isFinite(event.longitude)
    && event.latitude >= -90
    && event.latitude <= 90
    && event.longitude >= -180
    && event.longitude <= 180
    && event.age.length > 0
    && event.age.every((range) => AGE_RANGES.has(range));
}

function getVisibleEvents() {
  const query = state.search.trim().toLocaleLowerCase("es");
  return EVENTS.filter(isVerifiedEvent).filter((event) => {
    const searchable = [
      event.title,
      event.category,
      event.venue,
      event.neighborhood,
      event.description,
      event.address,
      event.schedule
    ].join(" ").toLocaleLowerCase("es");
    return (!state.category || event.category === state.category)
      && (!state.age || event.age.includes(state.age))
      && (!state.neighborhood || event.neighborhood === state.neighborhood)
      && (!query || searchable.includes(query));
  }).sort((a, b) => {
    if (!a.date) return b.date ? 1 : 0;
    if (!b.date) return -1;
    return new Date(a.date) - new Date(b.date);
  });
}

function formatDate(date, options = { weekday: "long", day: "numeric", month: "long" }) {
  if (!date || Number.isNaN(new Date(`${date}T12:00:00`).getTime())) {
    return "Fecha a confirmar";
  }
  return new Intl.DateTimeFormat("es-AR", options).format(new Date(`${date}T12:00:00`));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  })[character]);
}

function renderEmptyState(container, heading, message) {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon" aria-hidden="true">✳</div>
      <h3>${heading}</h3>
      <p>${message}</p>
      <div class="source-links">
        ${SOURCES.map((source) => `<a href="${source.url}" target="_blank" rel="noopener noreferrer">${source.name} ↗</a>`).join("")}
      </div>
    </div>`;
}

function sourceLinks(event) {
  return event.sources.map((source) =>
    `<a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.name)}</a>`
  ).join("");
}

function renderEventCard(event) {
  const hasCoordinates = Number.isFinite(event.latitude) && Number.isFinite(event.longitude);
  const hasVenue = Boolean(event.address || event.venue || event.neighborhood);
  const directions = hasCoordinates
    ? `https://www.google.com/maps/dir/?api=1&destination=${event.latitude},${event.longitude}`
    : hasVenue
      ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${event.address || ""} ${event.venue || ""} ${event.neighborhood || ""} Buenos Aires`)}`
      : event.sources[0].url;
  const ageLabel = event.ageLabel || `${event.age.join(" · ")} años`;
  return `
    <article class="event-card">
      <div class="event-card-body">
        <div class="event-meta">
          <span class="event-category"><span aria-hidden="true">✳</span> ${escapeHtml(event.category)}${event.genre ? ` · ${escapeHtml(event.genre)}` : ""}</span>
          <span class="event-age">${escapeHtml(ageLabel)}</span>
        </div>
        <h3>${escapeHtml(event.title)}</h3>
        <p class="event-description">${escapeHtml(event.description)}</p>
        <dl class="event-details">
          <div><dt aria-label="Fecha">◷</dt><dd>${escapeHtml(event.schedule || `${formatDate(event.date)}${event.time ? ` · ${event.time}` : ""}`)}</dd></div>
          <div><dt aria-label="Lugar">⌖</dt><dd>${escapeHtml(event.venue || "Lugar a confirmar")}${event.neighborhood ? ` · ${escapeHtml(event.neighborhood)}` : ""}</dd></div>
        </dl>
      </div>
      <div class="event-card-footer">
        <div class="card-sources">${sourceLinks(event)}</div>
        <a class="directions-link" href="${escapeHtml(directions)}" target="_blank" rel="noopener noreferrer">${hasVenue ? "Cómo llegar ↗" : "Ver fuente ↗"}</a>
      </div>
    </article>`;
}

function renderCategories(events) {
  if (!events.length) {
    renderEmptyState(
      categoryEvents,
      state.search || state.age || state.neighborhood || state.category
        ? "No encontramos planes con esos filtros"
        : state.category === "Teatro" ? "No hay funciones infantiles listadas" : "Estamos armando la agenda",
      state.search || state.age || state.neighborhood || state.category
        ? "Probá cambiar la búsqueda o combinar otros filtros. Las funciones de teatro se toman de la cartelera infantil de Alternativa Teatral."
        : "No hay actividades disponibles en esta categoría con el criterio de fuentes que usamos."
    );
    return;
  }
  categoryEvents.innerHTML = events.map(renderEventCard).join("");
}

function renderAgenda(events) {
  if (!events.length) {
    renderEmptyState(
      agendaEvents,
      "Todavía no hay fechas confirmadas",
      "Cuando haya funciones vigentes en la cartelera infantil, aparecerán aquí ordenadas por día y horario."
    );
    return;
  }

  const days = new Map();
  events.forEach((event) => {
    const date = event.date || "";
    if (!days.has(date)) days.set(date, []);
    days.get(date).push(event);
  });
  agendaEvents.innerHTML = [...days.entries()].map(([date, dayEvents]) => `
    <section class="agenda-day">
      <div class="agenda-day-label">${escapeHtml(formatDate(date))}</div>
      <div class="agenda-day-events">
        ${dayEvents.map((event) => `
          <article class="agenda-entry">
            <h3><a href="${escapeHtml(event.sources[0].url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(event.title)}</a></h3>
            <p>${escapeHtml(event.schedule || `${event.time || "Horario a confirmar"} · ${event.venue || "Lugar a confirmar"}${event.neighborhood ? ` · ${event.neighborhood}` : ""} · ${event.category}`)}</p>
          </article>`).join("")}
      </div>
    </section>`).join("");
}

function initializeMap() {
  if (map || !window.L) return;
  map = L.map("map", { scrollWheelZoom: false }).setView([-34.6037, -58.3816], 11);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  markers = L.featureGroup().addTo(map);
}

function renderMap(events) {
  if (!window.L) {
    mapStatus.textContent = "No se pudo cargar el mapa. Revisá tu conexión e intentá nuevamente.";
    return;
  }
  initializeMap();
  markers.clearLayers();
  const mappableEvents = events.filter((event) =>
    Number.isFinite(event.latitude) && Number.isFinite(event.longitude)
  );
  mappableEvents.forEach((event) => {
    const color = CATEGORY_COLORS[event.category] || "#285d49";
    const icon = L.divIcon({
      className: "map-pin-wrap",
      html: `<span class="map-pin" style="--pin-color:${color}"></span>`,
      iconSize: [32, 38],
      iconAnchor: [16, 34],
      popupAnchor: [0, -32]
    });
    const directions = `https://www.google.com/maps/dir/?api=1&destination=${event.latitude},${event.longitude}`;
    const popup = `
      <div class="map-popup">
        <h3>${escapeHtml(event.title)}</h3>
        <p>${escapeHtml(event.category)} · ${escapeHtml(event.ageLabel || `${event.age.join(" · ")} años`)}</p>
        <p>${escapeHtml(event.venue)}<br>${escapeHtml(event.address || event.neighborhood)}</p>
        <p>${escapeHtml(formatDate(event.date))}${event.time ? ` · ${escapeHtml(event.time)}` : ""}</p>
        <a href="${directions}" target="_blank" rel="noopener noreferrer">Cómo llegar ↗</a>
      </div>`;
    L.marker([event.latitude, event.longitude], { icon }).bindPopup(popup).addTo(markers);
  });
  mapStatus.textContent = mappableEvents.length
    ? `${mappableEvents.length} ${mappableEvents.length === 1 ? "actividad" : "actividades"} con ubicación precisa en el mapa.${mappableEvents.length < events.length ? " El resto de las fuentes no aporta coordenadas; no se muestran pines aproximados." : ""}`
    : events.length
      ? "Las fuentes no aportan coordenadas precisas para estas actividades; no mostramos pines aproximados."
      : "El mapa mostrará ubicaciones cuando haya actividades con coordenadas precisas.";
  if (mappableEvents.length) {
    const bounds = markers.getBounds();
    map.fitBounds(bounds.pad(0.18), { maxZoom: 14 });
  } else {
    map.setView([-34.6037, -58.3816], 11);
  }
  window.requestAnimationFrame(() => map.invalidateSize());
}

function render() {
  const events = getVisibleEvents();
  resultsCount.textContent = `${events.length} ${events.length === 1 ? "actividad" : "actividades"}`;
  renderCategories(events);
  renderAgenda(events);
  if (state.tab === "map") renderMap(events);
}

function selectTab(tabName) {
  state.tab = tabName;
  document.querySelectorAll(".tab-button").forEach((button) => {
    const selected = button.dataset.tab === tabName;
    button.classList.toggle("is-active", selected);
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
    document.querySelector(`#panel-${button.dataset.tab}`).hidden = !selected;
  });
  if (tabName === "map") renderMap(getVisibleEvents());
}

document.querySelectorAll(".tab-button").forEach((button, index, buttons) => {
  button.addEventListener("click", () => selectTab(button.dataset.tab));
  button.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const offset = event.key === "ArrowRight" ? 1 : -1;
    const next = buttons[(index + offset + buttons.length) % buttons.length];
    next.focus();
    selectTab(next.dataset.tab);
  });
});

document.querySelectorAll(".category-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    state.category = chip.dataset.category;
    document.querySelectorAll(".category-chip").forEach((item) => {
      item.classList.toggle("is-selected", item === chip);
    });
    render();
  });
});

searchInput.addEventListener("input", () => {
  state.search = searchInput.value;
  render();
});
ageFilter.addEventListener("change", () => {
  state.age = ageFilter.value;
  render();
});
neighborhoodFilter.addEventListener("change", () => {
  state.neighborhood = neighborhoodFilter.value;
  render();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

populateNeighborhoodFilter();
render();
loadScrapedEvents();
