# GBU-Assistent — Architektur-Konzept

**Gesamtarchitektur & Entwicklungsregeln** | Stand: April 2026 (erstellt: 18.04.2026)

---

## Inhaltsverzeichnis

1. [Projektidee](#1-projektidee)
2. [Architektur: Die vier Bereiche](#2-architektur-die-vier-bereiche)
3. [Wissensbasis (RAG)](#3-wissensbasis-rag)
4. [Workflow-Pipeline (5 Phasen)](#4-workflow-pipeline-5-phasen)
5. [Anwendung (Frontend + Backend)](#5-anwendung-frontend--backend)
6. [Meta / Projektsteuerung](#6-meta--projektsteuerung)
7. [Stateless-Prinzip & Datenschutz](#7-stateless-prinzip--datenschutz)
8. [Ordnerstruktur](#8-ordnerstruktur)
9. [Dokumentenhierarchie](#9-dokumentenhierarchie)
10. [Tech-Stack](#10-tech-stack)
11. [Änderungshistorie](#11-änderungshistorie)

---

> **Verbindlicher Arbeitshinweis — Konzeptdokument-Pflege**
>
> Dieses Dokument ist die **übergeordnete Wahrheitsquelle** für die Gesamtarchitektur des Projekts „GBU-Assistent". Es definiert die Bereiche, ihre Beziehungen und die Regeln für bereichsübergreifende Tätigkeiten.
>
> Für die **Workflow-interne** Architektur (Phasen-Details, Systemprompts, Ein-/Ausgabe-Schemas, Verantwortungsmodell) gilt weiterhin `docs/konzept-gbu-assistent.md` als zuständiges Dokument.
>
> *Kurzregel: Wer die Projektstruktur ändert, schreibt dieses Konzept mit — ausnahmslos.*

---

## 1 Projektidee

Der GBU-Assistent ist ein KI-gestützter Assistent für Gefährdungsbeurteilungen (GBU) nach dem BG-RCI-Schema. Eine Fachkraft für Arbeitssicherheit gibt unstrukturierte Begehungsnotizen ein, durchläuft einen 5-Phasen-Workflow und lädt am Ende einen fertigen Bericht (Word/PDF) herunter.

Das System besteht aus mehreren Bereichen mit unterschiedlichen Aufgaben und Änderungszyklen:

- Die **Wissensbasis** hält langlebige, kundenneutrale Quelldaten (Rechtsnormen, Gefährdungskataloge, BG-RCI-Schema, Berichtsvorlagen).
- Die **Workflow-Pipeline** implementiert den 5-Phasen-Prozess als verkettete Claude-API-Aufrufe mit Phase-spezifischen Systemprompts.
- Die **Anwendung** (Frontend + Backend) stellt den Prozess als nutzbare stateless Web-App bereit.
- Der **Meta-Bereich** steuert Planung, Aufgaben und Architekturentscheidungen.

**Statelessness ist kein Feature, sondern ein Architekturprinzip.** Es prägt jeden Bereich: keine Nutzerdatenbank, keine Persistenz, keine Accounts, keine Session-Logs. Session-Daten existieren nur im Browser oder im Arbeitsspeicher des Backends während einer aktiven Sitzung. Dieses Prinzip ist Grundlage des Datenschutzmodells (→ Abschnitt 7) und bindend für alle Architekturentscheidungen.

Die Wissensbasis konsumiert die Pipeline, um Maßnahmenvorschläge mit Rechtsreferenzen zu erzeugen — sie existiert aber unabhängig von der Pipeline und wird durch eigene Prozesse (Norm-Updates, Katalogpflege) gepflegt.

---

## 2 Architektur: Die vier Bereiche

| Bereich | Ordner (Zielzustand) | Zweck | Änderungszyklen |
|---------|---------------------|-------|-----------------|
| **Wissensbasis** | `Referenz/` | Kundenneutrale Quelldaten: Rechtsnormen, Gefährdungskataloge, BG-RCI-Schema, Berichtsvorlagen | Selten — wächst durch Norm-Updates und Katalogpflege |
| **Workflow-Pipeline** | `prompts/`, `schemas/`, `cli/` (später `backend/pipeline/`) | Werkzeuge des 5-Phasen-Prozesses: Systemprompts, Schemas, Orchestrator | Mittel — wächst mit Prompt-Iterationen und neuen Phasen-Varianten |
| **Anwendung** | `frontend/`, `backend/` (noch zu bauen) | Nutzbare stateless Web-App: UI, API, Session-Orchestrierung, Export | Hoch — aktive Produktentwicklung |
| **Meta** | `Meta/`, `docs/` | Projektsteuerung: Aufgaben, Ideen, Roadmap, Architektur- und Konzeptdokumente | Häufig — laufende Projektarbeit |

**Session-Artefakte** (der generierte Bericht pro Sitzung) haben bewusst **keinen Ordner im Repo**: sie sind flüchtig, werden nach Session-Ende verworfen und nur über den Download zur Fachkraft ausgeliefert. Das ist die bauliche Konsequenz aus dem Stateless-Prinzip.

### Beziehungen

```
Meta (Projektsteuerung)
  │
  ├── steuert ──→ Wissensbasis         (Norm-Pflege, Katalogaufbau, Qualitätssicherung)
  ├── steuert ──→ Workflow-Pipeline    (Prompt-Entwicklung, Schema-Design, Test)
  ├── steuert ──→ Anwendung            (Frontend, Backend, Integration, Deployment)
  │
  └── Anwendung
        ├── ruft auf ──→ Workflow-Pipeline   (je Phase einen Claude-API-Call)
        │                    │
        │                    └── liest ──→ Wissensbasis   (RAG-Retrieval pro Phase)
        │
        └── liefert aus ──→ Session-Artefakt (Bericht-Download, nicht gespeichert)
```

Der Meta-Bereich ist die **übergeordnete Ebene**. Er umfasst alle Steuerungsdateien, die das System weiterentwickeln — sowohl die Wissensbasis, die Pipeline als auch die Anwendung. Die Anwendung ist zur Laufzeit der einzige Einstiegspunkt; sie kapselt die Pipeline und liest die Wissensbasis. Die Pipeline ist das Herzstück — die Anwendung ist ihre Trägerin.

### Abgrenzung der Bereiche

| Frage | Zuständiger Bereich |
|-------|--------------------|
| Welche Systemprompts laufen in welcher Phase? | Workflow-Pipeline (`prompts/`, Details in `docs/konzept-gbu-assistent.md`) |
| Welche Rechtsnormen stehen für RAG zur Verfügung? | Wissensbasis (`Referenz/`) |
| Wie sieht die UI der Phase 3 aus? | Anwendung (`frontend/`) |
| Wie ist die Ordnerstruktur auf Dach-Ebene? | Dieses Dokument |
| Welche Aufgaben sind abrufbereit? | Meta (`Meta/Aufgaben.md`) |
| Wie wird der Bericht gerendert? | Anwendung (`backend/`), unter Nutzung der Vorlage aus Wissensbasis |

---

## 3 Wissensbasis (RAG)

Die Wissensbasis ist die fachliche Grundlage des gesamten Systems. Sie wird von der Pipeline über RAG-Retrieval gelesen, aber **nicht** von der Pipeline verwaltet. Die Pflege der Wissensbasis ist eine eigenständige, kundenneutrale Projektaufgabe — sie enthält **keinerlei** betriebsspezifische Daten.

### Struktur (Zielzustand)

| Unterordner | Inhalt | Rolle im Workflow |
|-------------|--------|-------------------|
| `Referenz/Rechtsnormen/` | Gesetzestexte, Verordnungen, Regeln: ArbSchG, BetrSichV, GefStoffV, ArbStättV, TRBS, TRGS, DGUV-Vorschriften/Regeln/Informationen, BG-RCI-Merkblätter | RAG-Quelle für Phase 4 (Rechtsreferenz zu Maßnahmen) |
| `Referenz/Gefaehrdungskataloge/` | Typische Gefährdungen pro Branche/Tätigkeit, strukturiert nach BG-RCI-Kategorien | RAG-Quelle für Phase 2 (Ergänzungsvorschläge + Interviewfragen) |
| `Referenz/Schema/` | BG-RCI-Kategorienstruktur und Ein-/Ausgabe-Schemas (JSON/Dataclass) | Validierung für Phasen 1–4 (aktuell unter `schemas/`) |
| `Referenz/Berichtsvorlagen/` | Word-/PDF-Vorlagen nach BG-RCI-Schema | Rendering-Basis für Phase 5 |

Aktuell liegt die Schema-Komponente noch unter `schemas/bgr_ci_kategorien.py`. Die Verschiebung nach `Referenz/Schema/` gehört zum Zielzustand und wird beim Aufbau der RAG-Pipeline (Roadmap Stufe 2) vollzogen.

### RAG-Architektur

**Zwei Schichten — beide ohne Kundendaten:**

1. **Rechtsnormen-Korpus** — durchsuchbare Paragrafenchunks mit Metadaten (Norm-ID, Fassung, Paragraf). Wird in Phase 4 abgefragt, um Maßnahmenvorschläge mit konkreter Rechtsgrundlage zu belegen.
2. **Gefährdungskataloge** — strukturierte Liste typischer Gefährdungen je Branche/Tätigkeit. Wird in Phase 2 abgefragt, um automatisch Ergänzungsvorschläge zu generieren (Weg A) bzw. Interview-Fragen zu formulieren (Weg B).

**Chunking-Strategie:**

- Rechtsnormen: ein Chunk pro Paragraf/Absatz, Metadaten (Norm, Fassung, Paragraf, Thema).
- Gefährdungskataloge: ein Chunk pro Gefährdungseintrag, Metadaten (Branche, Tätigkeit, BG-RCI-Kategorie).

**Retrieval:** Hybrid — semantisch (Embeddings) + Keyword (BM25). Vektor-DB: ChromaDB (Entscheidung E3).

Die Wissensbasis ist für **alle Nutzer identisch**. Sie wird versioniert (Norm-Fassungen), damit ein Bericht nachvollziehbar auf einen definierten Stand verweisen kann.

### Regeln für Wissensbasis-Dateien

- **Quellenangabe ist Pflicht.** Jeder Rechtsnorm-Chunk trägt Norm-ID, Fassung und Paragraf. Jeder Gefährdungskatalog-Eintrag nennt die Quelle (z.B. BG-RCI-Merkblatt M-001).
- **Keine Kundendaten.** Kein Betriebsname, keine Personennamen, kein Standort, keine branchenspezifischen Interna einer realen Firma — auch nicht in Beispielen. Test-Beispiele werden aus `cli/beispiel_*.txt` gelesen, nicht in die Wissensbasis aufgenommen.
- **Keine Redundanz.** Ein Paragraf wird genau einmal gechunkt. Querverweise über Norm-ID statt Duplikate.
- **LaTeX für Formeln.** Inline `$...$`, Display `$$...$$` — ausnahmslos (analog Schulmaterial-Regel).
- **Rechtsreferenz mit Norm-ID.** Im Fließtext immer mit Norm-ID (z.B. ArbSchG §5, TRGS 400) — nie verkürzt.
- **Versionierung.** Bei Norm-Änderung wird eine neue Fassung eingespielt, die alte bleibt erhalten (nachvollziehbare Rechtsgrundlage für archivierte Berichte — falls ein Nutzer sie später wieder hochlädt).

### Abgrenzung: Wissensbasis vs. Session-Daten

| Ebene | Persistenz | Inhalt |
|-------|-----------|--------|
| **Wissensbasis** | Dauerhaft im Repo + Vektor-DB | Kundenneutrale Referenzen (Normen, Kataloge, Schemas, Vorlagen) |
| **Session-Daten** | Nur zur Laufzeit (Browser/RAM) | Konkrete Begehungsnotizen, Gefährdungsliste, Bewertungen, generierter Bericht |

Die Pipeline darf aus der Wissensbasis **lesen**, aber **nie** Session-Daten zurück in die Wissensbasis schreiben. Das ist der bauliche Garant für das Stateless-Prinzip.
