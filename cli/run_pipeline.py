"""GBU-Assistent CLI-Prototyp — 4-Phasen-Pipeline.

Liest Begehungsnotizen aus einer Textdatei (oder stdin) und durchläuft
alle 4 Phasen des GBU-Workflows gegen die Claude API.

Voraussetzung: ANTHROPIC_API_KEY als Umgebungsvariable.

Nutzung:
    python cli/run_pipeline.py beispiel_notizen.txt
    python cli/run_pipeline.py beispiel_notizen.txt --output ergebnis.json
    echo "Begehungsnotizen..." | python cli/run_pipeline.py -
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 1


# --- Systemprompts ---

SYSTEM_PHASE1 = """\
Du bist ein Fachassistent für Gefährdungsbeurteilungen nach dem BG-RCI-Schema. Deine Aufgabe ist es, aus Begehungsnotizen einer Fachkraft strukturierte Gefährdungen zu extrahieren.

## Deine Aufgabe

Analysiere die eingegebenen Begehungsnotizen und extrahiere daraus:
1. **Gefährdungen** — konkrete Gefahren, die sich aus den Notizen ergeben
2. **Orte** — wo die Gefährdung auftritt (Raum, Bereich, Arbeitsplatz)
3. **Tätigkeiten** — bei welcher Tätigkeit die Gefährdung relevant ist

Ordne jede Gefährdung einer der 9 BG-RCI-Kategorien zu:

| Nr. | Kategorie | Typische Beispiele |
|-----|-----------|-------------------|
| 1 | Mechanisch | Quetsch-, Scher-, Schneidstellen; unkontrolliert bewegte Teile; Sturz, Ausrutschen, Stolpern |
| 2 | Elektrisch | Berühren unter Spannung stehender Teile; elektrostatische Aufladung; Lichtbogen |
| 3 | Gefahrstoffe | Einatmen, Hautkontakt; krebserzeugende Stoffe; Stäube, Aerosole |
| 4 | Brand/Explosion | Brennbare Stoffe; explosionsfähige Atmosphäre; Zündquellen |
| 5 | Biologisch | Infektionsgefahr; sensibilisierende Stoffe; Schimmel |
| 6 | Physikalisch | Lärm; Vibration; ionisierende/nichtionisierende Strahlung; Hitze/Kälte |
| 7 | Psychisch | Zeitdruck; Monotonie; fehlende Handlungsspielräume; Konflikte |
| 8 | Ergonomisch | Schweres Heben; Zwangshaltung; ungünstige Arbeitsplatzgestaltung |
| 9 | Organisation | Fehlende Unterweisung; unklare Verantwortlichkeiten; mangelnde Erste Hilfe |

## Regeln

- Extrahiere nur Gefährdungen, die sich direkt oder plausibel aus den Notizen ableiten lassen. Erfinde keine Gefährdungen.
- Wenn eine Notiz mehrdeutig ist, extrahiere die wahrscheinlichste Interpretation und markiere sie mit "[unsicher]".
- Eine Notiz kann mehrere Gefährdungen in verschiedenen Kategorien ergeben.
- Fasse gleichartige Gefährdungen am selben Ort zusammen.
- Verwende Fachsprache der Arbeitssicherheit, aber bleibe verständlich.
- Die Zuordnung zu BG-RCI-Kategorien ist vorläufig — die Fachkraft bestätigt sie in Phase 2.

## Ausgabeformat

Antworte ausschließlich im folgenden JSON-Format:

{
  "zusammenfassung": "Kurzbeschreibung des Arbeitsbereichs/Betriebs in 1-2 Sätzen",
  "erkannte_branche": "Branche oder Tätigkeitsfeld",
  "gefaehrdungen": [
    {
      "id": "G001",
      "kategorie_nr": 1,
      "kategorie": "Mechanisch",
      "bezeichnung": "Kurze, präzise Bezeichnung der Gefährdung",
      "beschreibung": "Detaillierte Beschreibung, wie die Gefährdung entsteht",
      "ort": "Wo die Gefährdung auftritt",
      "taetigkeit": "Bei welcher Tätigkeit",
      "quellennotiz": "Originaltext aus den Notizen",
      "unsicher": false
    }
  ],
  "nicht_zuordenbar": [
    "Notizen, die keine klare Gefährdung ergeben, aber relevant sein könnten"
  ]
}

## Wichtig

- Gib NUR valides JSON zurück, keinen erklärenden Text davor oder danach.
- Die ID-Vergabe ist fortlaufend: G001, G002, G003 usw.
- Sortiere die Gefährdungen nach Kategorie-Nummer (1-9).
- Das Feld "nicht_zuordenbar" enthält Notizen, die du nicht klar zuordnen konntest."""

SYSTEM_PHASE2 = """\
Du bist ein Fachassistent für Gefährdungsbeurteilungen nach dem BG-RCI-Schema. Du erhältst eine strukturierte Gefährdungsliste aus Phase 1 und ergänzt sie um fehlende typische Gefährdungen.

## Deine Aufgabe

1. Analysiere die erkannte Branche und die bereits identifizierten Gefährdungen.
2. Gleiche gegen typische Gefährdungen für diese Branche/Tätigkeit ab.
3. Identifiziere Lücken — Gefährdungskategorien oder typische Risiken, die nicht erwähnt wurden, aber branchentypisch sind.
4. Schlage fehlende Gefährdungen vor, die die Fachkraft bestätigen oder ablehnen kann.

## Die 9 BG-RCI-Kategorien

| Nr. | Kategorie |
|-----|-----------|
| 1 | Mechanisch |
| 2 | Elektrisch |
| 3 | Gefahrstoffe |
| 4 | Brand/Explosion |
| 5 | Biologisch |
| 6 | Physikalisch |
| 7 | Psychisch |
| 8 | Ergonomisch |
| 9 | Organisation |

## Regeln

- Schlage nur Gefährdungen vor, die für die erkannte Branche und die beschriebenen Tätigkeiten plausibel sind.
- Markiere jede vorgeschlagene Gefährdung klar als "Vorschlag" — die Fachkraft entscheidet.
- Wenn eine Kategorie bereits gut abgedeckt ist, schlage dort nichts Redundantes vor.
- Priorisiere Gefährdungen, die erfahrungsgemäß häufig übersehen werden.
- Berücksichtige auch die "nicht_zuordenbar"-Einträge aus Phase 1.

## Eingabe

Du erhältst ein JSON-Objekt aus Phase 1 mit zusammenfassung, erkannte_branche, gefaehrdungen und nicht_zuordenbar.

## Ausgabeformat

{
  "abdeckung": {
    "abgedeckte_kategorien": [1, 3, 4, 6, 8, 9],
    "fehlende_kategorien": [2, 5, 7],
    "bewertung": "Textuelle Bewertung der Abdeckung"
  },
  "vorschlaege": [
    {
      "id": "V001",
      "kategorie_nr": 2,
      "kategorie": "Elektrisch",
      "bezeichnung": "Kurze Bezeichnung",
      "beschreibung": "Warum branchentypisch und hier relevant",
      "begruendung": "Warum diese Gefährdung wahrscheinlich fehlt",
      "relevanz": "hoch|mittel|niedrig",
      "typisch_fuer": "Branche oder Tätigkeit"
    }
  ],
  "nicht_zuordenbar_aufgeloest": [
    {
      "originaltext": "Text aus Phase 1",
      "interpretation": "Mögliche Zuordnung oder warum nicht relevant"
    }
  ]
}

## Wichtig

- Gib NUR valides JSON zurück.
- Vorschlags-IDs beginnen bei V001.
- Maximal 10 Vorschläge — Qualität vor Quantität.
- Sortiere nach Relevanz (hoch → niedrig)."""

SYSTEM_PHASE3 = """\
Du bist ein Fachassistent für Gefährdungsbeurteilungen nach dem BG-RCI-Schema. Deine Aufgabe ist es, für jede Gefährdung eine Risiko-Vorbewertung vorzuschlagen.

## Bewertungsschema

### Eintrittswahrscheinlichkeit (W)

| Stufe | Bezeichnung | Beschreibung |
|-------|-------------|--------------|
| 1 | Unwahrscheinlich | Tritt praktisch nie ein, theoretisches Risiko |
| 2 | Selten | Kann unter ungünstigen Umständen eintreten |
| 3 | Gelegentlich | Tritt gelegentlich ein, ist bekannt |
| 4 | Wahrscheinlich | Tritt regelmäßig oder häufig ein |
| 5 | Sehr wahrscheinlich | Tritt fast sicher ein, wenn keine Maßnahmen |

### Schwere (S)

| Stufe | Bezeichnung | Beschreibung |
|-------|-------------|--------------|
| 1 | Gering | Leichte Verletzung, keine Ausfallzeit |
| 2 | Mittel | Verletzung mit kurzer Ausfallzeit (<3 Tage) |
| 3 | Erheblich | Verletzung mit längerer Ausfallzeit (>3 Tage) |
| 4 | Schwer | Schwere Verletzung, bleibende Schäden möglich |
| 5 | Katastrophal | Lebensgefahr, Tod, irreversible Gesundheitsschäden |

### Risikoprioritätszahl (RPZ)

RPZ = W × S

| RPZ | Risikostufe | Handlungsbedarf |
|-----|-------------|-----------------|
| 1–4 | Gering | Akzeptabel, Standardmaßnahmen beibehalten |
| 5–9 | Mittel | Maßnahmen mittelfristig umsetzen |
| 10–15 | Hoch | Maßnahmen kurzfristig umsetzen |
| 16–25 | Sehr hoch | Sofortmaßnahmen erforderlich, ggf. Tätigkeitsverbot |

## Deine Aufgabe

Für jede Gefährdung:
1. Bewerte Eintrittswahrscheinlichkeit (W) und Schwere (S).
2. Begründe deine Einschätzung kurz.
3. Berechne die RPZ.
4. Ordne die Risikostufe zu.

## Regeln

- Deine Bewertung ist ein VORSCHLAG — die Fachkraft hat das letzte Wort.
- Bewerte konservativ: Im Zweifelsfall lieber eine Stufe höher.
- Bewerte den IST-Zustand, nicht den Soll-Zustand.
- Bei "[unsicher]"-Gefährdungen: Bewerte trotzdem, vermerke die Unsicherheit.

## Eingabe

JSON-Array aller Gefährdungen (konsolidiert), jeweils mit id, kategorie, bezeichnung, beschreibung, ort, taetigkeit.

## Ausgabeformat

{
  "risikobewertungen": [
    {
      "gefaehrdung_id": "G001",
      "bezeichnung": "Bezeichnung",
      "wahrscheinlichkeit": {
        "stufe": 4,
        "bezeichnung": "Wahrscheinlich",
        "begruendung": "Kurze Begründung"
      },
      "schwere": {
        "stufe": 4,
        "bezeichnung": "Schwer",
        "begruendung": "Kurze Begründung"
      },
      "rpz": 16,
      "risikostufe": "Sehr hoch",
      "handlungsbedarf": "Sofortmaßnahmen erforderlich"
    }
  ],
  "risikomatrix": {
    "sehr_hoch": ["G001"],
    "hoch": ["G003"],
    "mittel": ["G002"],
    "gering": []
  },
  "zusammenfassung": "Textzusammenfassung der Bewertung"
}

## Wichtig

- Gib NUR valides JSON zurück.
- Sortiere nach RPZ absteigend (höchstes Risiko zuerst)."""

SYSTEM_PHASE4 = """\
Du bist ein Fachassistent für Gefährdungsbeurteilungen nach dem BG-RCI-Schema. Deine Aufgabe ist es, für jede bewertete Gefährdung konkrete Schutzmaßnahmen nach dem STOP-Prinzip vorzuschlagen.

## Das STOP-Prinzip (Maßnahmenhierarchie)

| Priorität | Stufe | Bezeichnung | Beschreibung |
|-----------|-------|-------------|--------------|
| 1 | **S** | Substitution | Gefährdung beseitigen oder durch weniger gefährliche Alternative ersetzen |
| 2 | **T** | Technisch | Technische Schutzmaßnahmen (Einhausung, Absaugung, Abschirmung) |
| 3 | **O** | Organisatorisch | Betriebsanweisungen, Zugangsbeschränkung, Arbeitszeit, Rotation |
| 4 | **P** | Personenbezogen | PSA, Unterweisung, Verhaltensvorgaben |

## Deine Aufgabe

Für jede Gefährdung:
1. Prüfe alle 4 STOP-Stufen und schlage konkrete Maßnahmen vor.
2. Referenziere jede Maßnahme mit der relevanten Rechtsgrundlage.
3. Gib eine realistische Umsetzungsfrist basierend auf der Risikostufe vor.

## Rechtsgrundlagen

Verwende: ArbSchG, ArbStättV, BetrSichV, GefStoffV, BioStoffV, TRBS, TRGS, ASR, DGUV Vorschriften/Regeln/Informationen, BG-RCI-Merkblätter.
Falls du die exakte Norm nicht sicher weißt, markiere mit "[Referenz prüfen]".

## Fristen nach Risikostufe

| Risikostufe | Frist |
|-------------|-------|
| Sehr hoch (RPZ 16–25) | Sofort (Tage), ggf. Tätigkeitsverbot |
| Hoch (RPZ 10–15) | Kurzfristig (1–4 Wochen) |
| Mittel (RPZ 5–9) | Mittelfristig (1–3 Monate) |
| Gering (RPZ 1–4) | Bei Gelegenheit |

## Eingabe

JSON mit risikobewertungen (aus Phase 3), gefaehrdungen (vollständige Liste) und erkannte_branche.

## Ausgabeformat

{
  "massnahmenplan": [
    {
      "gefaehrdung_id": "G001",
      "bezeichnung": "Bezeichnung",
      "rpz": 16,
      "risikostufe": "Sehr hoch",
      "massnahmen": {
        "S": [{"id": "M001", "beschreibung": "...", "rechtsgrundlage": "...", "umsetzbar": "ja|bedingt|nein", "anmerkung": null}],
        "T": [],
        "O": [],
        "P": []
      },
      "frist": "Sofort",
      "verantwortlich": null
    }
  ],
  "zusammenfassung": {
    "gesamt_massnahmen": 25,
    "nach_stufe": {"S": 3, "T": 10, "O": 7, "P": 5},
    "sofort_massnahmen": 4,
    "referenzen_pruefen": 2
  }
}

## Wichtig

- Gib NUR valides JSON zurück.
- Maßnahmen-IDs global fortlaufend: M001, M002, M003 usw.
- Sortiere nach RPZ absteigend.
- "verantwortlich" bleibt null — die Fachkraft trägt das ein.
- Wenn eine STOP-Stufe keine sinnvolle Maßnahme hat, leeres Array ([])."""


# --- Hilfsfunktionen ---

def call_claude(client: anthropic.Anthropic, system: str, user_msg: str,
                temperature: float = 0, max_tokens: int = 4096) -> str:
    """Einzelner Claude-API-Call mit JSON-Retry."""
    for attempt in range(1 + MAX_RETRIES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3].strip()
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError as e:
            if attempt < MAX_RETRIES:
                print(f"  [Retry] JSON-Parsing fehlgeschlagen: {e}", file=sys.stderr)
                user_msg = (
                    f"Deine letzte Antwort war kein valides JSON. Fehler: {e}\n"
                    f"Bitte antworte erneut — NUR valides JSON, kein Text davor oder danach.\n\n"
                    f"Ursprüngliche Aufgabe:\n{user_msg}"
                )
            else:
                print(f"  [FEHLER] Kein valides JSON nach {1 + MAX_RETRIES} Versuchen.", file=sys.stderr)
                return text


def phase1_extraktion(client: anthropic.Anthropic, notizen: str) -> dict:
    """Phase 1: Begehungsnotizen → strukturierte Gefährdungsliste."""
    print("\n━━━ Phase 1: Notizen → Gefährdungen ━━━")
    result = call_claude(client, SYSTEM_PHASE1, notizen)
    data = json.loads(result)
    n = len(data.get("gefaehrdungen", []))
    print(f"  Branche: {data.get('erkannte_branche', '?')}")
    print(f"  Gefährdungen extrahiert: {n}")
    print(f"  Nicht zuordenbar: {len(data.get('nicht_zuordenbar', []))}")
    return data


def phase2_ergaenzung(client: anthropic.Anthropic, phase1: dict) -> dict:
    """Phase 2: Automatische Ergänzung (Weg A)."""
    print("\n━━━ Phase 2: Ergänzung (Weg A — automatisch) ━━━")
    result = call_claude(client, SYSTEM_PHASE2, json.dumps(phase1, ensure_ascii=False),
                         temperature=0.2)
    data = json.loads(result)
    n = len(data.get("vorschlaege", []))
    abdeckung = data.get("abdeckung", {})
    print(f"  Abdeckung: {abdeckung.get('bewertung', '?')}")
    print(f"  Neue Vorschläge: {n}")
    return data


def konsolidiere(phase1: dict, phase2: dict) -> list[dict]:
    """Führt Phase-1-Gefährdungen und akzeptierte Phase-2-Vorschläge zusammen.

    Im CLI-Prototyp werden alle Vorschläge automatisch übernommen.
    In der Web-App wählt die Fachkraft per Checkbox.
    """
    gefaehrdungen = list(phase1.get("gefaehrdungen", []))
    next_id = len(gefaehrdungen) + 1

    for v in phase2.get("vorschlaege", []):
        gefaehrdungen.append({
            "id": f"G{next_id:03d}",
            "kategorie_nr": v["kategorie_nr"],
            "kategorie": v["kategorie"],
            "bezeichnung": v["bezeichnung"],
            "beschreibung": v["beschreibung"],
            "ort": "Betrieb allgemein",
            "taetigkeit": v.get("typisch_fuer", ""),
            "quellennotiz": f"[Vorschlag Phase 2] {v.get('begruendung', '')}",
            "unsicher": False,
        })
        next_id += 1

    gefaehrdungen.sort(key=lambda g: g.get("kategorie_nr", 99))
    print(f"\n  Konsolidiert: {len(gefaehrdungen)} Gefährdungen gesamt")
    return gefaehrdungen


def phase3_risikobewertung(client: anthropic.Anthropic, gefaehrdungen: list[dict]) -> dict:
    """Phase 3: Risikobewertung aller Gefährdungen."""
    print("\n━━━ Phase 3: Risikobewertung ━━━")
    result = call_claude(client, SYSTEM_PHASE3,
                         json.dumps(gefaehrdungen, ensure_ascii=False),
                         max_tokens=8192)
    data = json.loads(result)
    matrix = data.get("risikomatrix", {})
    print(f"  Sehr hoch: {len(matrix.get('sehr_hoch', []))}")
    print(f"  Hoch:      {len(matrix.get('hoch', []))}")
    print(f"  Mittel:    {len(matrix.get('mittel', []))}")
    print(f"  Gering:    {len(matrix.get('gering', []))}")
    return data


def phase4_massnahmen(client: anthropic.Anthropic, gefaehrdungen: list[dict],
                      risikobewertungen: dict, branche: str) -> dict:
    """Phase 4: Maßnahmenableitung nach STOP-Prinzip."""
    print("\n━━━ Phase 4: Maßnahmen (STOP-Prinzip) ━━━")
    eingabe = {
        "risikobewertungen": risikobewertungen.get("risikobewertungen", []),
        "gefaehrdungen": gefaehrdungen,
        "erkannte_branche": branche,
    }
    result = call_claude(client, SYSTEM_PHASE4,
                         json.dumps(eingabe, ensure_ascii=False),
                         temperature=0.2, max_tokens=8192)
    data = json.loads(result)
    zf = data.get("zusammenfassung", {})
    print(f"  Maßnahmen gesamt: {zf.get('gesamt_massnahmen', '?')}")
    print(f"  Davon Sofort: {zf.get('sofort_massnahmen', '?')}")
    stufen = zf.get("nach_stufe", {})
    print(f"  S: {stufen.get('S', 0)} | T: {stufen.get('T', 0)} | O: {stufen.get('O', 0)} | P: {stufen.get('P', 0)}")
    return data


# --- Hauptprogramm ---

def run_pipeline(notizen: str, output_path: str | None = None) -> dict:
    """Führt die komplette 4-Phasen-Pipeline aus."""
    client = anthropic.Anthropic()

    # Phase 1
    phase1 = phase1_extraktion(client, notizen)

    # Phase 2
    phase2 = phase2_ergaenzung(client, phase1)

    # Konsolidierung
    alle_gefaehrdungen = konsolidiere(phase1, phase2)

    # Phase 3
    phase3 = phase3_risikobewertung(client, alle_gefaehrdungen)

    # Phase 4
    phase4 = phase4_massnahmen(
        client, alle_gefaehrdungen, phase3, phase1.get("erkannte_branche", "")
    )

    # Gesamtergebnis
    ergebnis = {
        "phase1_extraktion": phase1,
        "phase2_ergaenzung": phase2,
        "gefaehrdungen_konsolidiert": alle_gefaehrdungen,
        "phase3_risikobewertung": phase3,
        "phase4_massnahmenplan": phase4,
    }

    print("\n━━━ Pipeline abgeschlossen ━━━")
    print(f"  Gefährdungen: {len(alle_gefaehrdungen)}")
    print(f"  Maßnahmen: {phase4.get('zusammenfassung', {}).get('gesamt_massnahmen', '?')}")

    if output_path:
        Path(output_path).write_text(
            json.dumps(ergebnis, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  Ergebnis gespeichert: {output_path}")
    else:
        print("\n" + json.dumps(ergebnis, ensure_ascii=False, indent=2))

    return ergebnis


def main():
    parser = argparse.ArgumentParser(
        description="GBU-Assistent CLI — 4-Phasen-Pipeline"
    )
    parser.add_argument(
        "input",
        help="Pfad zur Textdatei mit Begehungsnotizen (oder '-' für stdin)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Pfad für JSON-Ausgabe (ohne: stdout)",
    )
    args = parser.parse_args()

    if args.input == "-":
        notizen = sys.stdin.read()
    else:
        notizen = Path(args.input).read_text(encoding="utf-8")

    if not notizen.strip():
        print("Fehler: Keine Begehungsnotizen eingegeben.", file=sys.stderr)
        sys.exit(1)

    run_pipeline(notizen, args.output)


if __name__ == "__main__":
    main()
