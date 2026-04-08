# Aufgabenliste — GBU-Assistent

**Stand:** 2026-04-08

## Entscheidungspunkte

| # | Frage | Typ | Kontext | Betrifft |
|---|-------|-----|---------|----------|
| E1 | Welches Frontend-Framework? (React, Vue, Svelte, oder reines HTML+JS?) | Weichenstellung | Bestimmt gesamte Frontend-Architektur | #401 |
| E2 | Welches Backend-Framework? (FastAPI, Express, oder serverless?) | Weichenstellung | Bestimmt Deployment und API-Struktur | #501 |
| E3 | Welche Vektor-DB für RAG? (Chroma, Qdrant, Pinecone, oder dateisystem-basiert?) | Weichenstellung | Bestimmt RAG-Pipeline | #301 |
| E4 | Word-Export-Bibliothek? (python-docx, docxtpl, oder andere?) | Schnellentscheidung | Für Phase 5 Berichterstellung | #601 |

## Abrufbereite Aufgaben

### Kleine Aufgaben (K) — im Bündel startbar

_(Noch keine — Projekt in Konzeptphase)_

### Komplexe Aufgaben (X) — einzeln startbar

_(Noch keine abrufbereit — offene Entscheidungspunkte klären)_

## Aufgaben im Entwurf

| # | Aufgabe | Größe | Offene Fragen |
|---|---------|-------|---------------|
| #101 | BG-RCI-Kategorienstruktur als JSON-Schema aufsetzen | X | Format: JSON-Schema oder Python-Dataclass? |
| #201 | Prototyp-Prompt für Phase 1 (Notizen → Gefährdungen) ausarbeiten | X | — |
| #202 | Prototyp-Prompt für Phase 2 (Interview-Flow) ausarbeiten | X | Weg A und Weg B getrennt oder kombiniert? |
| #203 | Prototyp-Prompt für Phase 3 (Risikobewertung) ausarbeiten | X | — |
| #204 | Prototyp-Prompt für Phase 4 (Maßnahmen nach STOP) ausarbeiten | X | — |
| #301 | RAG-Pipeline und Chunking-Strategie für Rechtsnormen definieren | X | Vektor-DB? → E3 |
| #302 | Gefährdungskatalog als strukturierte Datenquelle aufbereiten | X | Quelle: BG-RCI-Merkblätter, DGUV? |
| #401 | Tech-Stack Frontend festlegen und Grundgerüst aufsetzen | X | Framework? → E1 |
| #501 | Tech-Stack Backend festlegen und Grundgerüst aufsetzen | X | Framework? → E2 |
| #502 | Claude-API-Integration (Systemprompts pro Phase) | X | Abhängig von #501 |
| #601 | Word-/PDF-Template nach BG-RCI-Vorlage erstellen | X | Export-Lib? → E4 |

## Archiv — Erledigte und obsolete Aufgaben

_(Noch leer)_
