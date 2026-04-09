# Aufgabenliste — GBU-Assistent

**Stand:** 2026-04-08

## Entscheidungspunkte

| # | Frage | Typ | Ergebnis | Datum |
|---|-------|-----|----------|-------|
| E1 | Frontend-Framework | Weichenstellung | **SvelteKit** | 2026-04-08 |
| E2 | Backend-Framework | Weichenstellung | **FastAPI (Python)** | 2026-04-08 |
| E3 | Vektor-DB für RAG | Weichenstellung | **ChromaDB** | 2026-04-08 |
| E4 | Word-Export-Bibliothek | Schnellentscheidung | **python-docx** | 2026-04-08 |

## Abrufbereite Aufgaben

### Kleine Aufgaben (K) — im Bündel startbar

_(Noch keine — Projekt in Konzeptphase)_

### Komplexe Aufgaben (X) — einzeln startbar

| # | Aufgabe | Abhängigkeiten |
|---|---------|----------------|
| #301 | RAG-Pipeline und Chunking-Strategie für Rechtsnormen definieren (ChromaDB) | — |
| #302 | Gefährdungskatalog als strukturierte Datenquelle aufbereiten | — |
| #401 | SvelteKit-Grundgerüst aufsetzen | — |
| #501 | FastAPI-Grundgerüst aufsetzen | — |
| #502 | Claude-API-Integration (Systemprompts pro Phase) | #501 |
| #601 | Word-Template nach BG-RCI-Vorlage erstellen (python-docx) | — |

## Aufgaben im Entwurf

_(Keine — alle Aufgaben sind abrufbereit)_

## Archiv — Erledigte Aufgaben

| # | Aufgabe | Erledigt |
|---|---------|----------|
| #101 | BG-RCI-Kategorienstruktur als JSON-Schema + Python-Dataclass | 2026-04-08 |
| #201 | Prototyp-Prompt Phase 1 (Notizen → Gefährdungen) | 2026-04-08 |
| #202 | Prototyp-Prompt Phase 2 (Ergänzung — Weg A + B) | 2026-04-08 |
| #203 | Prototyp-Prompt Phase 3 (Risikobewertung) | 2026-04-08 |
| #204 | Prototyp-Prompt Phase 4 (Maßnahmen nach STOP) | 2026-04-08 |
| #205 | CLI-Prototyp: 4-Phasen-Pipeline gegen Claude API | 2026-04-08 |
