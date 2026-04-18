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
