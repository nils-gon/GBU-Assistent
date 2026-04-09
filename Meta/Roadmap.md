# Roadmap — GBU-Assistent

## Stufe 0 — Konzept und Entscheidungen ✅

**Ziel:** Alle Grundsatzentscheidungen treffen, bevor Code geschrieben wird.

**Schritte:**
1. Konzeptdokument erstellen ✅
2. Meta-Struktur aufbauen (Aufgaben, Ideen, Roadmap) ✅
3. Tech-Stack-Entscheidungen treffen (SvelteKit, FastAPI, ChromaDB, python-docx) ✅
4. BG-RCI-Kategorienstruktur als Schema definieren ✅
5. Prototyp-Prompts für Phase 1–4 ausarbeiten ✅

**Ergebnis:** Klare Architektur, getestete Prompts, Technologie-Entscheidungen dokumentiert.

---

## Stufe 1 — Prompt-Prototyp (CLI) (aktuell)

**Ziel:** Den 5-Phasen-Workflow als reines Prompt-Engineering validieren — ohne UI, ohne RAG.

**Schritte:**
1. Phase 1 (Notizen → Gefährdungen) als Claude-API-Call implementieren ✅
2. Phase 2 (Ergänzung/Interview) als Claude-API-Call implementieren ✅
3. Phase 3 (Risikobewertung) als Claude-API-Call implementieren ✅
4. Phase 4 (Maßnahmen nach STOP) als Claude-API-Call implementieren ✅
5. Phase 5 (Berichterstellung) als Word-Export implementieren
6. End-to-End-Test mit realistischen Begehungsnotizen

**Ergebnis:** Funktionierender CLI-Prototyp, der den gesamten Workflow durchläuft.

---

## Stufe 2 — RAG-Wissensbasis

**Ziel:** Rechtsnormen und Gefährdungskataloge als durchsuchbare Wissensbasis bereitstellen.

**Schritte:**
1. Rechtsnormen-Korpus aufbauen (ArbSchG, BetrSichV, TRBS, TRGS, DGUV)
2. Chunking-Strategie implementieren (nach Paragraf, mit Metadaten)
3. Vektor-DB aufsetzen und befüllen
4. Hybrid-Retrieval (semantisch + Keyword) implementieren
5. Gefährdungskatalog als strukturierte Datenquelle aufbereiten
6. RAG in den Workflow integrieren (Phase 2 + Phase 4)

**Ergebnis:** Maßnahmenvorschläge mit konkreten Rechtsreferenzen.

---

## Stufe 3 — Web-App (MVP)

**Ziel:** Nutzbare Web-Oberfläche für den gesamten Workflow.

**Schritte:**
1. Frontend-Grundgerüst (Eingabe, Chat, Checklisten)
2. Backend-API (Session-Workflow, Claude-API-Anbindung)
3. Risikomatrix-Editor im Frontend
4. Berichtsvorschau und Download
5. End-to-End-Test über die Web-App

**Ergebnis:** Funktionierendes MVP, das eine Fachkraft nutzen kann.

---

## Stufe 4 — Qualitätssicherung und Feinschliff

**Ziel:** Produktionsreife.

**Schritte:**
1. Datenschutz-Review (AVV, Drittlandtransfer-Hinweis)
2. Prompt-Qualität optimieren (Halluzinationsschutz, Rechtsreferenz-Genauigkeit)
3. UX-Verbesserungen (Feedback von Testnutzern)
4. Deployment-Strategie (Hosting, Domain)
5. Dokumentation für Fachkräfte

**Ergebnis:** Einsatzbereite Anwendung.
