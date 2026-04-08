# GBU-Assistent — Projekt-Arbeitsanweisungen

## Projektbeschreibung

KI-gestützter Assistent für Gefährdungsbeurteilungen (GBU) nach BG-RCI-Schema. Stateless Web-App: Fachkraft gibt Begehungsnotizen ein, durchläuft 5-Phasen-Workflow, lädt fertigen Bericht herunter. Keine Persistenz, keine Nutzerdaten.

## Projektstruktur

```
GBU-Assistent/
├── CLAUDE.md              ← Diese Datei
├── Meta/
│   ├── Aufgaben.md        ← Aufgabenliste (K/X-Modell)
│   ├── Ideen.md           ← Ideensammlung
│   └── Roadmap.md         ← Stufenplan
└── docs/
    └── konzept-gbu-assistent.md  ← Konzeptdokument (Architektur, Workflow, Datenschutz)
```

## Konzeptdokumente

| Dokument | Zuständigkeit |
|----------|---------------|
| `docs/konzept-gbu-assistent.md` | Gesamtkonzept (Workflow, Architektur, Datenschutz) |

## Aufgabenmanagement

- **Aufgaben:** `Meta/Aufgaben.md`
- **Ideen-Inbox:** `Meta/Ideen.md`
- **Roadmap:** `Meta/Roadmap.md`
- **Nummernschema:** 1xx Infrastruktur/Setup, 2xx Prototyping, 3xx RAG/Wissensbasis, 4xx Frontend, 5xx Backend/API, 6xx Berichterstellung, 9xx Niedrige Prio

## Technische Konventionen

- **Formeln:** LaTeX ($...$ inline, $$...$$ Display)
- **Rechtsreferenzen:** Immer mit Norm-ID (z.B. ArbSchG §5, TRGS 400)
- **BG-RCI-Kategorien:** 9 Gefährdungskategorien als feste Struktur (Mechanisch, Elektrisch, Gefahrstoffe, Brand/Explosion, Biologisch, Physikalisch, Psychisch, Ergonomisch, Organisation)

## Aktuelle Phase

Konzeptphase — noch kein Code. Nächster Schritt: Prototyp-Prompts und Tech-Stack-Entscheidung.
