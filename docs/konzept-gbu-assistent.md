# KI-gestützter GBU-Assistent – Konzept (stateless)

## Grundprinzip

Kein Login, keine Nutzerdaten, keine Persistenz. Die Fachkraft startet eine Session, gibt Notizen ein, durchläuft den Workflow, lädt am Ende den fertigen Bericht herunter. Danach ist die Session weg. Das System speichert nichts über den Kunden.

---

## Workflow in 5 Phasen

### Phase 1 – Eingabe

Die Fachkraft gibt ihre unstrukturierten Begehungsnotizen als Freitext ein. Die KI extrahiert daraus Gefährdungen, Orte und Tätigkeiten und ordnet sie vorläufig den BG-RCI-Kategorien zu.

### Phase 2 – Ergänzung (zwei Wege)

**Weg A – Automatisch:**
KI erkennt Branche/Tätigkeit aus den Notizen, gleicht gegen den Gefährdungskatalog ab, schlägt fehlende typische Gefährdungen vor. Fachkraft bestätigt per Checkbox.

**Weg B – KI-Interview:**
Die KI führt die Fachkraft systematisch durch alle BG-RCI-Gefährdungskategorien:

1. Mechanisch
2. Elektrisch
3. Gefahrstoffe
4. Brand/Explosion
5. Biologisch
6. Physikalisch
7. Psychisch
8. Ergonomisch
9. Organisation

Pro Kategorie 2–4 gezielte Fragen zum konkreten Arbeitsbereich. Die Fachkraft antwortet aus dem Gedächtnis.

Beide Wege münden in dieselbe Gefährdungsliste.

### Phase 3 – Risikobewertung

Für jede Gefährdung bewertet die Fachkraft Eintrittswahrscheinlichkeit und Schwere. Die KI schlägt eine Vorbewertung vor, die Fachkraft überschreibt verbindlich.

**Ergebnis:** Priorisierte Risikomatrix.

### Phase 4 – Maßnahmenableitung (STOP-Prinzip)

Die KI generiert pro Gefährdung Vorschläge in der Hierarchie:

| Priorität | Stufe | Beschreibung |
|-----------|-------|--------------|
| 1 | **S** – Substitution | Gefährdung beseitigen oder ersetzen |
| 2 | **T** – Technisch | Technische Schutzmaßnahmen |
| 3 | **O** – Organisatorisch | Organisatorische Maßnahmen |
| 4 | **P** – Personenbezogen | Persönliche Schutzausrüstung, Unterweisung |

Jeder Vorschlag wird über das RAG-System mit der konkreten Rechtsgrundlage referenziert:

- ArbSchG, BetrSichV, GefStoffV, ArbStättV
- TRBS, TRGS
- DGUV-Vorschriften, DGUV-Regeln, DGUV-Informationen
- BG-RCI-Merkblätter

Die Fachkraft wählt, modifiziert und verantwortet.

### Phase 5 – Berichterstellung

Strukturierter Export als Word/PDF nach BG-RCI-Schema:

1. Deckblatt
2. Betriebsbeschreibung
3. Gefährdungstabelle (kategorisiert)
4. Risikobewertung
5. Maßnahmenplan mit Verantwortlichen und Fristen
6. Rechtsquellenverzeichnis
7. Wirksamkeitskontrolle (Wiedervorlagetermin)

Die Fachkraft lädt den Bericht herunter. Session beendet.

---

## Architektur

### Sprachmodell (Claude API)

Zentrales Gehirn für alle Phasen. Pro Phase ein spezialisierter Systemprompt. Kein Fine-Tuning nötig – die Steuerung läuft über Prompt-Engineering und RAG-Kontext.

### RAG-Wissensbasis (serverseitig, statisch)

Zwei Schichten, beide ohne Kundendaten:

**1. Rechtsnormen-Korpus**

- ArbSchG, BetrSichV, GefStoffV, ArbStättV
- TRBS, TRGS
- DGUV Vorschriften / Regeln / Informationen
- BG-RCI-Merkblätter
- Chunking nach Paragraf, Metadaten (Norm-ID, Fassung)
- Hybrid-Retrieval (semantisch + Keyword)

**2. Gefährdungskataloge**

- Typische Gefährdungen pro Tätigkeit/Branche
- Dienen als Grundlage für Phase 2 (Ergänzung und Interview-Fragen)

Diese Wissensbasis ist für alle Nutzer identisch und enthält keine betriebsspezifischen Daten.

### Backend (leichtgewichtig)

Koordiniert den Session-Workflow, hält den Zustand nur im Arbeitsspeicher (oder im Browser-State). Ruft Claude API + RAG auf, baut am Ende den Bericht zusammen. Kein Login, keine Datenbank, kein Speichern nach Session-Ende.

### Frontend (Web-App)

- Eingabefeld für Notizen
- Chat-Interface fürs Interview
- Checklisten
- Risikomatrix-Editor
- Berichtsvorschau
- Download-Button (Word/PDF)

### Berichterstellung

Serverseitig generiertes Word-Dokument nach BG-RCI-Vorlage. Alternativ PDF.

---

## Architekturübersicht

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│  (Notizen · Chat · Checklisten · Risikomatrix)  │
└──────────────────────┬──────────────────────────┘
                       │ Session-State (Browser)
                       ▼
┌─────────────────────────────────────────────────┐
│              Backend (stateless)                  │
│         Workflow-Koordination pro Phase           │
│                                                   │
│  Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4    │
│                                         │        │
│                                         ▼        │
│                                    Phase 5       │
│                                  (Bericht)       │
└────────┬────────────────────┬───────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────────────┐
│   Claude API    │  │   RAG-Wissensbasis       │
│  (Systemprompt  │  │  ┌───────────────────┐   │
│   pro Phase)    │  │  │ Rechtsnormen      │   │
│                 │  │  │ Gefährdungskatalog│   │
└─────────────────┘  │  └───────────────────┘   │
                     └─────────────────────────┘
```

---

## Verantwortungsmodell

| Rolle | KI | Fachkraft |
|---|---|---|
| Notizen strukturieren | vorschlagen | bestätigen |
| Typische Gefährdungen | vorschlagen | entscheiden |
| Risikobewertung | vorschlagen | verbindlich bewerten |
| Maßnahmen (STOP) | vorschlagen | verantworten |
| Rechtsreferenzen | zuordnen | prüfen |
| Bericht | generieren | freigeben + unterschreiben |

> **Prinzip:** Die KI ist Zuarbeiterin, die Fachkraft trägt die Verantwortung. Jede KI-Ausgabe ist ein Vorschlag, keine verbindliche Bewertung.

---

## Datenschutz

### Was entfällt

- Keine Nutzerdatenbank
- Keine Persistenz
- Keine Accounts
- Session-Daten existieren nur während der Nutzung

Damit entfällt:
- DSGVO-Auskunftsrecht (keine gespeicherten Daten)
- Löschprozesse (nichts zu löschen)
- Rollenkonzept (kein Login)
- Datenschutzerklärung für Nutzerkonten

### Was verbleibt

- **AVV mit Anthropic** – abgedeckt über Commercial Terms
- **Hinweis an Nutzer** zum Drittlandtransfer (USA, abgesichert über SCCs)
- **Nutzungshinweis:** Fachkraft wird angewiesen, keine Personennamen einzugeben

---

## Tech-Stack (entschieden 2026-04-08)

| Komponente | Technologie |
|------------|-------------|
| Frontend | **SvelteKit** |
| Backend | **FastAPI (Python)** |
| Vektor-DB (RAG) | **ChromaDB** |
| Word-Export | **python-docx** |
| LLM | Claude API (Anthropic) |

## Offene Nächste Schritte

- [x] Prototyp-Prompt für Phase 1 (Notizen → Gefährdungen) ausarbeiten
- [x] Prototyp-Prompts für Phase 2–4 ausarbeiten
- [x] BG-RCI-Kategorienstruktur als Schema aufsetzen
- [ ] Interview-Flow (Weg B) durchskizzieren
- [ ] RAG-Pipeline und Chunking-Strategie für Rechtsnormen definieren
- [ ] Word-/PDF-Template nach BG-RCI-Vorlage erstellen
- [x] Tech-Stack festlegen (Frontend-Framework, Backend, Vektor-DB)
