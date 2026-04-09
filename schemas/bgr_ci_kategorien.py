"""BG-RCI Gefährdungskategorien — Schema-Definition.

Definiert die 9 Gefährdungskategorien nach BG-RCI-Schema als Python-Dataclasses
und stellt sie als JSON-Schema bereit. Dient als zentrale Datengrundlage für
alle Phasen des GBU-Assistenten.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from typing import Optional


class KategorieNr(IntEnum):
    """Die 9 BG-RCI-Gefährdungskategorien."""
    MECHANISCH = 1
    ELEKTRISCH = 2
    GEFAHRSTOFFE = 3
    BRAND_EXPLOSION = 4
    BIOLOGISCH = 5
    PHYSIKALISCH = 6
    PSYCHISCH = 7
    ERGONOMISCH = 8
    ORGANISATION = 9


@dataclass
class Unterkategorie:
    """Unterkategorie einer Gefährdungskategorie."""
    id: str
    bezeichnung: str
    beispiele: list[str]


@dataclass
class Kategorie:
    """Eine der 9 BG-RCI-Gefährdungskategorien mit Unterkategorien."""
    nr: int
    bezeichnung: str
    beschreibung: str
    unterkategorien: list[Unterkategorie]
    typische_rechtsgrundlagen: list[str]


@dataclass
class Gefaehrdung:
    """Eine einzelne identifizierte Gefährdung."""
    id: str
    kategorie_nr: int
    kategorie: str
    bezeichnung: str
    beschreibung: str
    ort: str
    taetigkeit: str
    quellennotiz: str
    unsicher: bool = False


@dataclass
class Risikobewertung:
    """Risikobewertung einer Gefährdung (Phase 3)."""
    gefaehrdung_id: str
    wahrscheinlichkeit: int  # 1-5
    schwere: int  # 1-5
    rpz: int  # W × S
    risikostufe: str  # Gering / Mittel / Hoch / Sehr hoch
    begruendung_w: str
    begruendung_s: str

    def __post_init__(self):
        self.rpz = self.wahrscheinlichkeit * self.schwere
        if self.rpz <= 4:
            self.risikostufe = "Gering"
        elif self.rpz <= 9:
            self.risikostufe = "Mittel"
        elif self.rpz <= 15:
            self.risikostufe = "Hoch"
        else:
            self.risikostufe = "Sehr hoch"


@dataclass
class Massnahme:
    """Eine Schutzmaßnahme nach STOP-Prinzip (Phase 4)."""
    id: str
    gefaehrdung_id: str
    stop_stufe: str  # S, T, O, P
    beschreibung: str
    rechtsgrundlage: Optional[str] = None
    umsetzbar: str = "ja"  # ja, bedingt, nein
    anmerkung: Optional[str] = None
    verantwortlich: Optional[str] = None
    frist: Optional[str] = None


# --- Kategorienkatalog ---

KATEGORIEN: list[Kategorie] = [
    Kategorie(
        nr=1,
        bezeichnung="Mechanisch",
        beschreibung="Gefährdungen durch bewegte oder unbewegliche Maschinenteile, Werkzeuge, Werkstücke, Oberflächen und Transportmittel.",
        unterkategorien=[
            Unterkategorie("1.1", "Ungeschützt bewegte Maschinenteile", [
                "Quetschstellen", "Scherstellen", "Schneidstellen", "Stichstellen",
                "Fangstellen", "Einzugstellen"
            ]),
            Unterkategorie("1.2", "Teile mit gefährlichen Oberflächen", [
                "Ecken", "Kanten", "Spitzen", "raue Oberflächen"
            ]),
            Unterkategorie("1.3", "Bewegte Transportmittel und -güter", [
                "Anfahren", "Überfahren", "Umkippen", "herabfallende Gegenstände"
            ]),
            Unterkategorie("1.4", "Unkontrolliert bewegte Teile", [
                "Wegfliegende Werkstücke", "Späne", "Bruchstücke", "Splitter"
            ]),
            Unterkategorie("1.5", "Sturz, Ausrutschen, Stolpern, Umknicken", [
                "Glätte", "Unebenheiten", "Stolperstellen", "Absturzgefahr"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "BetrSichV §5–§6",
            "DGUV Vorschrift 1",
            "DGUV Regel 100-500 (Betreiben von Arbeitsmitteln)",
            "Maschinenrichtlinie 2006/42/EG",
        ],
    ),
    Kategorie(
        nr=2,
        bezeichnung="Elektrisch",
        beschreibung="Gefährdungen durch elektrischen Strom, elektrostatische Aufladung und elektromagnetische Felder.",
        unterkategorien=[
            Unterkategorie("2.1", "Berühren unter Spannung stehender Teile", [
                "Direktes Berühren", "indirektes Berühren", "defekte Isolation"
            ]),
            Unterkategorie("2.2", "Elektrostatische Aufladung", [
                "Funkenentladung", "Zündgefahr", "Schreckreaktionen"
            ]),
            Unterkategorie("2.3", "Lichtbogen", [
                "Kurzschluss", "Schaltfehler", "thermische Wirkung"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "BetrSichV §5–§6",
            "DGUV Vorschrift 3 (Elektrische Anlagen und Betriebsmittel)",
            "TRBS 2131 (Elektrische Gefährdungen)",
        ],
    ),
    Kategorie(
        nr=3,
        bezeichnung="Gefahrstoffe",
        beschreibung="Gefährdungen durch chemische Stoffe und Gemische — Einatmen, Hautkontakt, Verschlucken.",
        unterkategorien=[
            Unterkategorie("3.1", "Einatmen von Gefahrstoffen", [
                "Dämpfe", "Aerosole", "Stäube", "Fasern", "Gase"
            ]),
            Unterkategorie("3.2", "Hautkontakt mit Gefahrstoffen", [
                "Verätzung", "Sensibilisierung", "Resorption"
            ]),
            Unterkategorie("3.3", "Verschlucken von Gefahrstoffen", [
                "Kontamination von Nahrung", "Hand-Mund-Kontakt"
            ]),
            Unterkategorie("3.4", "Krebserzeugende/mutagene Stoffe (CMR)", [
                "CMR-Stoffe Kat. 1A/1B", "Asbest", "Hartholzstäube"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "GefStoffV §6–§11",
            "TRGS 400 (Gefährdungsbeurteilung Gefahrstoffe)",
            "TRGS 500 (Schutzmaßnahmen)",
            "TRGS 900 (AGW)", "TRGS 905 (CMR-Verzeichnis)",
            "DGUV Regel 113-001",
        ],
    ),
    Kategorie(
        nr=4,
        bezeichnung="Brand/Explosion",
        beschreibung="Gefährdungen durch brennbare Stoffe, explosionsfähige Atmosphären und Zündquellen.",
        unterkategorien=[
            Unterkategorie("4.1", "Brennbare Feststoffe, Flüssigkeiten, Gase", [
                "Brandlasten", "Lagerung brennbarer Stoffe", "Selbstentzündung"
            ]),
            Unterkategorie("4.2", "Explosionsfähige Atmosphäre", [
                "Ex-Zonen", "Staubexplosion", "Gas-/Dampf-Luft-Gemische"
            ]),
            Unterkategorie("4.3", "Zündquellen", [
                "Heißarbeiten", "mechanische Funken", "elektrostatische Entladung"
            ]),
            Unterkategorie("4.4", "Unzureichende Brandbekämpfung", [
                "Fehlende/verstellte Feuerlöscher", "Fluchtweg-Mängel", "keine Brandmeldeanlage"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "GefStoffV §6",
            "BetrSichV Anhang 3",
            "TRGS 720–727 (Ex-Schutz)",
            "TRBS 2152 (Explosionsfähige Atmosphären)",
            "ASR A2.2 (Maßnahmen gegen Brände)",
        ],
    ),
    Kategorie(
        nr=5,
        bezeichnung="Biologisch",
        beschreibung="Gefährdungen durch biologische Arbeitsstoffe — Infektionen, Sensibilisierungen, toxische Wirkungen.",
        unterkategorien=[
            Unterkategorie("5.1", "Infektionsgefahr", [
                "Bakterien", "Viren", "Parasiten", "Nadelstichverletzung"
            ]),
            Unterkategorie("5.2", "Sensibilisierende biologische Stoffe", [
                "Schimmelpilze", "Enzyme", "Tierhaare/-schuppen"
            ]),
            Unterkategorie("5.3", "Toxische Wirkung biologischer Stoffe", [
                "Endotoxine", "Mykotoxine"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "BioStoffV",
            "TRBA 400 (Handlungsanleitung Gefährdungsbeurteilung)",
            "TRBA 500 (Allgemeine Hygienemaßnahmen)",
        ],
    ),
    Kategorie(
        nr=6,
        bezeichnung="Physikalisch",
        beschreibung="Gefährdungen durch physikalische Einwirkungen — Lärm, Vibration, Strahlung, Klima.",
        unterkategorien=[
            Unterkategorie("6.1", "Lärm", [
                "Gehörschäden", "Kommunikationsstörung", "Tages-Lärmexposition >80 dB(A)"
            ]),
            Unterkategorie("6.2", "Vibration", [
                "Hand-Arm-Vibration", "Ganzkörper-Vibration"
            ]),
            Unterkategorie("6.3", "Ionisierende Strahlung", [
                "Röntgenstrahlung", "radioaktive Stoffe"
            ]),
            Unterkategorie("6.4", "Nichtionisierende Strahlung", [
                "UV-Strahlung", "Laserstrahlung", "elektromagnetische Felder"
            ]),
            Unterkategorie("6.5", "Klima (Hitze, Kälte)", [
                "Hitzearbeit", "Kältearbeit", "Zugluft", "unzureichende Belüftung"
            ]),
            Unterkategorie("6.6", "Beleuchtung", [
                "Zu geringe Beleuchtung", "Blendung", "Flimmern"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "LärmVibrationsArbSchV",
            "OStrV (Optische Strahlung)",
            "TROS (Technische Regeln Optische Strahlung)",
            "ASR A3.4 (Beleuchtung)", "ASR A3.5 (Raumtemperatur)",
        ],
    ),
    Kategorie(
        nr=7,
        bezeichnung="Psychisch",
        beschreibung="Psychische Belastungen aus Arbeitsinhalten, -organisation, sozialen Beziehungen und Arbeitsumgebung.",
        unterkategorien=[
            Unterkategorie("7.1", "Arbeitsinhalt/-aufgabe", [
                "Über-/Unterforderung", "Monotonie", "fehlende Handlungsspielräume"
            ]),
            Unterkategorie("7.2", "Arbeitsorganisation", [
                "Zeitdruck", "Schichtarbeit", "unklare Zuständigkeiten", "häufige Störungen"
            ]),
            Unterkategorie("7.3", "Soziale Beziehungen", [
                "Konflikte", "Mobbing", "fehlende soziale Unterstützung", "Alleinarbeit"
            ]),
            Unterkategorie("7.4", "Arbeitsumgebung", [
                "Lärm (psychische Wirkung)", "räumliche Enge", "fehlende Rückzugsmöglichkeit"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "ArbSchG §5 Abs. 3 Nr. 6",
            "GDA-Leitlinie Psychische Belastung",
            "DGUV Information 206-001 (Stress am Arbeitsplatz)",
        ],
    ),
    Kategorie(
        nr=8,
        bezeichnung="Ergonomisch",
        beschreibung="Gefährdungen durch ergonomisch ungünstige Arbeitsbedingungen — Heben, Tragen, Haltung, Arbeitsplatzgestaltung.",
        unterkategorien=[
            Unterkategorie("8.1", "Schweres Heben und Tragen", [
                "Überschreitung der Lastgewichte", "fehlende Hebehilfen", "ungünstige Griffhöhen"
            ]),
            Unterkategorie("8.2", "Zwangshaltungen", [
                "Überkopfarbeit", "Knien", "gebückte Haltung", "statische Haltearbeit"
            ]),
            Unterkategorie("8.3", "Bildschirmarbeit", [
                "Monitor-Aufstellung", "Tastatur-/Maushaltung", "fehlende Pausen"
            ]),
            Unterkategorie("8.4", "Arbeitsplatzmaße und -gestaltung", [
                "Arbeitshöhe", "Greifräume", "Beinfreiheit", "Steh-/Sitzarbeit"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "LasthandhabV",
            "ArbStättV Anhang (Bildschirmarbeitsplätze)",
            "AMR 13.2 (Tätigkeiten mit wesentlich erhöhten körperlichen Belastungen)",
            "DGUV Information 208-033 (Belastung Muskel-Skelett)",
        ],
    ),
    Kategorie(
        nr=9,
        bezeichnung="Organisation",
        beschreibung="Gefährdungen durch organisatorische Mängel — Unterweisung, Erste Hilfe, Prüffristen, Fremdfirmen.",
        unterkategorien=[
            Unterkategorie("9.1", "Unterweisung und Qualifikation", [
                "Fehlende/veraltete Unterweisung", "unzureichende Einarbeitung",
                "fehlende Sachkunde"
            ]),
            Unterkategorie("9.2", "Erste Hilfe und Notfallorganisation", [
                "Zu wenig Ersthelfer", "fehlender Erste-Hilfe-Raum",
                "kein Alarmplan", "fehlende Notfallübungen"
            ]),
            Unterkategorie("9.3", "Betriebsanweisungen und Dokumentation", [
                "Fehlende Betriebsanweisungen", "Gefahrstoffverzeichnis unvollständig",
                "Prüffristen nicht dokumentiert"
            ]),
            Unterkategorie("9.4", "Fremdfirmen und Zusammenarbeit", [
                "Fehlende Abstimmung", "keine gemeinsame Gefährdungsbeurteilung",
                "Sprachbarrieren"
            ]),
            Unterkategorie("9.5", "Prüfungen und Wartung", [
                "Überfällige Prüfungen (DGUV V3, BetrSichV)",
                "fehlende Wartung", "keine Prüfdokumentation"
            ]),
        ],
        typische_rechtsgrundlagen=[
            "ArbSchG §12 (Unterweisung)",
            "DGUV Vorschrift 1 §4 (Unterweisung)",
            "ASR A4.3 (Erste-Hilfe-Räume)",
            "BetrSichV §14–§16 (Prüfung von Arbeitsmitteln)",
        ],
    ),
]


def get_kategorie(nr: int) -> Kategorie:
    """Gibt eine Kategorie nach Nummer zurück."""
    for k in KATEGORIEN:
        if k.nr == nr:
            return k
    raise ValueError(f"Kategorie {nr} existiert nicht (gültig: 1–9)")


def to_json_schema() -> dict:
    """Exportiert den Kategorienkatalog als JSON-Schema."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "BG-RCI Gefährdungskategorien",
        "description": "Die 9 Gefährdungskategorien nach BG-RCI-Schema mit Unterkategorien und Rechtsgrundlagen.",
        "type": "object",
        "properties": {
            "kategorien": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nr": {"type": "integer", "minimum": 1, "maximum": 9},
                        "bezeichnung": {"type": "string"},
                        "beschreibung": {"type": "string"},
                        "unterkategorien": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string", "pattern": r"^\d+\.\d+$"},
                                    "bezeichnung": {"type": "string"},
                                    "beispiele": {"type": "array", "items": {"type": "string"}},
                                },
                                "required": ["id", "bezeichnung", "beispiele"],
                            },
                        },
                        "typische_rechtsgrundlagen": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["nr", "bezeichnung", "beschreibung", "unterkategorien", "typische_rechtsgrundlagen"],
                },
                "minItems": 9,
                "maxItems": 9,
            }
        },
        "required": ["kategorien"],
    }


def to_json() -> str:
    """Exportiert den Kategorienkatalog als JSON-Daten."""
    return json.dumps(
        {"kategorien": [asdict(k) for k in KATEGORIEN]},
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    import sys

    if "--schema" in sys.argv:
        print(json.dumps(to_json_schema(), ensure_ascii=False, indent=2))
    else:
        print(to_json())
