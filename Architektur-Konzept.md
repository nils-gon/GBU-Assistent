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
