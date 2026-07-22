"""Genera `seeds/rsi_mx.seed.json` desde el CSV de obligaciones del RSI (2005)
de NormTrace.

Fuente (se lee, no se muta — dato de investigación):
  normtrace/03_tables/international_obligations/IHR-2005_obligations_domestic-anchoring.csv

Modelo de salida (segundo marco, para demostrar multi-marco en el escáner):
  - topic     = Título del RSI (parte)
  - subtopic  = artículo ("Art. N — título en español")
  - tag       = obligación (concepto), con una regex EN ESPAÑOL sembrada del
                concepto, pensada para detectar menciones en textos legislativos
                mexicanos (el CSV está en inglés; las regexes no).

Uso:
    python knowledgebase/gen_rsi_seed.py
"""

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
CSV_PATH = ROOT / "normtrace/03_tables/international_obligations/IHR-2005_obligations_domestic-anchoring.csv"
OUT_PATH = HERE / "seeds" / "rsi_mx.seed.json"

KB = "rsi_mx"


def _art_num(article):
    m = re.search(r"Art\.?\s*(\d+)", article)
    return int(m.group(1)) if m else None


def _titulo(article):
    """Devuelve (id_topic, nombre_topic) del Título del RSI para el artículo."""
    if article.startswith("Annex 1"):
        return ("rsi-anexo-1-capacidades-basicas", "RSI · Anexo 1 Capacidades básicas")
    n = _art_num(article)
    if n is None:
        return ("rsi-otros", "RSI · Otras disposiciones")
    if n <= 4:
        return ("rsi-titulo-1-autoridades", "RSI · Título I Autoridades responsables")
    if 5 <= n <= 14:
        return ("rsi-titulo-2-informacion-respuesta", "RSI · Título II Información y respuesta de salud pública")
    if 15 <= n <= 18:
        return ("rsi-titulo-3-recomendaciones", "RSI · Título III Recomendaciones")
    if 19 <= n <= 22:
        return ("rsi-titulo-4-puntos-de-entrada", "RSI · Título IV Puntos de entrada")
    if 23 <= n <= 34:
        return ("rsi-titulo-5-medidas-salud-publica", "RSI · Título V Medidas de salud pública")
    if 35 <= n <= 39:
        return ("rsi-titulo-6-documentos-sanitarios", "RSI · Título VI Documentos sanitarios")
    if 40 <= n <= 41:
        return ("rsi-titulo-7-cargos", "RSI · Título VII Cargos")
    return ("rsi-titulo-8-disposiciones-generales", "RSI · Título VIII Disposiciones generales")


# Mapa por artículo exacto: (título del artículo en español, etiqueta, regex ES).
# Las regexes se compilan case-insensitive por el tagger; usamos acentos y \b en
# siglas siguiendo el estilo del corpus mexicano.
OBLIGATIONS = {
    "Art. 4": ("Autoridades responsables", "Centro Nacional de Enlace",
               r"Centro Nacional de Enlace|punto de contacto (nacional )?para el RSI|autoridad(es)? sanitaria(s)? responsable(s)?"),
    "Art. 5(1)": ("Vigilancia", "Vigilancia epidemiológica",
                  r"vigilancia (epidemiológica|en salud pública|sanitaria)|\bSINAVE\b|Sistema Nacional de Vigilancia Epidemiológica"),
    "Art. 5(2)": ("Vigilancia — prórroga", "Plan de implementación del RSI",
                  r"plan de (implementación|acción) (del|para el) RSI|prórroga.*capacidades básicas"),
    "Art. 6(1)": ("Notificación", "Notificación a la OMS",
                  r"notificaci(ón|ar).*(OMS|Organización Mundial de la Salud)|notificación de eventos( de salud pública)?"),
    "Art. 6(2)": ("Notificación — información continua", "Información continua a la OMS",
                  r"información (continua|oportuna).*(OMS|evento notificado)"),
    "Art. 7": ("Intercambio de información en eventos inusuales", "Eventos inusuales o inesperados",
               r"eventos? (inusuales?|inesperados?)|intercambio de información sanitaria"),
    "Art. 8": ("Consulta", "Consulta a la OMS",
               r"consulta (a|con) la (OMS|Organización Mundial de la Salud)"),
    "Art. 9(2)": ("Otros informes", "Otros informes a la OMS",
                  r"otros informes|fuentes distintas de la notificación"),
    "Art. 10(2)": ("Verificación", "Verificación de eventos",
                   r"verificaci(ón|ar)( de eventos)?|solicitud de verificación"),
    "Art. 13(1)": ("Respuesta de salud pública", "Capacidad de respuesta",
                   r"respuesta de salud pública|capacidad de respuesta( rápida)?"),
    "Annex 1A, par.2": ("Autoevaluación y plan de acción", "Autoevaluación de capacidades",
                        r"autoevaluación( de capacidades)?|plan de acción( nacional)?"),
    "Annex 1A, par.4": ("Capacidad — nivel comunitario y primer nivel", "Capacidades básicas: nivel local",
                        r"capacidades? básicas?.*(comunitario|local|primer nivel de atención)"),
    "Annex 1A, par.5": ("Capacidad — nivel intermedio", "Capacidades básicas: nivel intermedio",
                        r"capacidades? básicas?.*(intermedio|estatal|jurisdiccional)"),
    "Annex 1A, par.6 (assessment)": ("Capacidad — evaluación nivel nacional", "Capacidades básicas: nivel nacional",
                                     r"capacidades? básicas?.*nacional"),
    "Annex 1A, par.6 (response)": ("Capacidad — respuesta nivel nacional", "Respuesta nacional de salud pública",
                                   r"respuesta (nacional )?de salud pública.*(nivel nacional|coordinación)"),
    "Annex 1B, par.1": ("Capacidad básica en puntos de entrada", "Capacidades en puntos de entrada",
                        r"punto[s]? de entrada.*capacidad(es)?|capacidad(es)?.*punto[s]? de entrada"),
    "Annex 1B, par.2": ("Respuesta en puntos de entrada ante ESPII", "Respuesta ante emergencia en PoE",
                        r"punto[s]? de entrada.*(emergencia|\bESPII\b|importancia internacional)"),
    "Art. 19": ("Obligaciones generales en puntos de entrada", "Puntos de entrada",
                r"puntos? de entrada"),
    "Art. 20(1)": ("Aeropuertos y puertos — designación", "Aeropuertos y puertos designados",
                   r"aeropuertos? y puertos?|puertos? (designados?|autorizados?)"),
    "Art. 20(2)": ("Certificados de sanidad a bordo", "Certificado de sanidad a bordo",
                   r"certificado[s]? de (control de )?sanidad (a bordo|del buque)"),
    "Art. 20(3)": ("Notificación de puertos autorizados a la OMS", "Puertos autorizados",
                   r"puertos? autorizados?.*(OMS|lista)"),
    "Art. 21": ("Cruces terrestres — designación y acuerdos", "Cruces terrestres",
                r"cruces? terrestres?|pasos? fronterizos?"),
    "Art. 22(1)": ("Función de las autoridades competentes en PoE", "Autoridades competentes en PoE",
                   r"autoridad(es)? competente[s]? en (los )?puntos? de entrada"),
    "Art. 23(3)": ("Medidas a la llegada/salida — consentimiento informado", "Consentimiento informado",
                   r"consentimiento informado"),
    "Art. 23(4)": ("Información de riesgos de vacunación", "Información de riesgos de vacunación",
                   r"información sobre (los )?riesgos.*vacunación"),
    "Art. 24(1)": ("Operadores de medios de transporte", "Operadores de transporte",
                   r"operadores? de medios de transporte|medios de transporte"),
    "Art. 27(1)": ("Medios de transporte afectados", "Medios de transporte afectados",
                   r"medios de transporte afectados"),
    "Art. 30": ("Viajeros bajo observación de salud pública", "Viajeros bajo observación",
                r"viajeros? (bajo|en) (observación|vigilancia)( de salud pública)?"),
    "Art. 31(1)": ("Prohibición de condiciones invasivas de entrada", "Examen médico invasivo",
                   r"examen médico (invasivo|obligatorio)|condiciones? para (la )?entrada"),
    "Art. 31(2)": ("Medidas obligatorias en circunstancias excepcionales", "Medidas obligatorias",
                   r"medidas? (sanitarias )?obligatorias?|aislamiento|cuarentena"),
    "Art. 32": ("Trato a los viajeros", "Trato digno a viajeros",
                r"trato (digno )?(a|de) (los )?viajeros?|respeto (a la )?dignidad"),
    "Art. 35": ("Regla general — sin documentos sanitarios adicionales", "Documentos sanitarios",
                r"documentos? sanitarios?( adicionales?)?"),
    "Art. 36": ("Certificados de vacunación o profilaxis", "Certificado de vacunación",
                r"certificado[s]? (internacional(es)? )?de vacunación( o profilaxis)?"),
    "Art. 37": ("Declaración marítima de sanidad", "Declaración marítima de sanidad",
                r"declaración marítima de sanidad"),
    "Art. 38": ("Parte sanitaria de la declaración general de aeronave", "Declaración general de aeronave",
                r"declaración general de (la )?aeronave"),
    "Art. 39": ("Certificados de sanidad del buque", "Certificado de sanidad del buque",
                r"certificado[s]? de sanidad (del|de) buque"),
    "Art. 40": ("Cargos por medidas a viajeros", "Cargos a viajeros",
                r"gratuidad de (las )?medidas sanitarias|cobro[s]?.*viajeros?"),
    "Art. 41": ("Cargos por medidas a mercancías", "Cargos a mercancías",
                r"cobro[s]?.*(mercancías?|carga|contenedores?)"),
    "Art. 42": ("Aplicación — transparencia y no discriminación", "Transparencia y no discriminación",
                r"no discriminación|sin distinción.*medidas sanitarias|aplicación transparente"),
    "Art. 43(1)-(2)": ("Medidas adicionales — base científica y proporcionalidad", "Medidas adicionales: base científica",
                       r"medidas? sanitarias? adicionales?|base científica|proporcionalidad"),
    "Art. 43(3) and (5)": ("Medidas adicionales — notificación a la OMS", "Medidas adicionales: notificación",
                           r"medidas? adicionales?.*notificaci(ón|ar)"),
    "Art. 43(6)": ("Medidas adicionales — revisión periódica", "Medidas adicionales: revisión",
                   r"revisión periódica.*medidas"),
    "Art. 44(1)": ("Colaboración y asistencia entre Estados Partes", "Colaboración entre Estados",
                   r"colaboración( y asistencia)? entre (los )?Estados( Partes)?|asistencia (técnica|internacional)"),
    "Art. 45": ("Tratamiento de datos personales", "Datos personales",
                r"datos personales|protección de datos( personales)?|confidencialidad de la información"),
    "Art. 46": ("Transporte de sustancias biológicas y muestras", "Sustancias biológicas y muestras",
                r"sustancias biológicas|muestras? (biológicas?|para diagnóstico)|transporte de material biológico"),
}


def main():
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8"), delimiter=";"))
    topics = {}  # id -> topic dict
    missing = []

    for r in rows:
        article = r["article"].strip().strip('"')
        if article not in OBLIGATIONS:
            missing.append(article)
            continue
        title_es, tag_name, regex_es = OBLIGATIONS[article]
        topic_id, topic_name = _titulo(article)
        topic = topics.setdefault(
            topic_id,
            {
                "_id": topic_id,
                "name": topic_name,
                "shortname": topic_name.split("·")[-1].strip()[:24],
                "description": "Obligaciones del Reglamento Sanitario Internacional (2005) con "
                "anclaje jurídico interno. Fuente: piloto RSI de NormTrace.",
                "knowledgebase": KB,
                "public": True,
                "tags": [],
            },
        )
        topic["tags"].append(
            {
                "regex": regex_es,
                "tag": tag_name,
                "subtopic": f"{article} — {title_es}",
                "shuffle": False,
            }
        )

    if missing:
        raise SystemExit(f"Artículos del CSV sin mapear en OBLIGATIONS: {missing}")

    # Orden estable de topics por id para diffs reproducibles.
    out = [topics[k] for k in sorted(topics)]
    OUT_PATH.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    n_tags = sum(len(t["tags"]) for t in out)
    print(f"Escrito {OUT_PATH} :: {len(out)} topics (Títulos RSI), {n_tags} obligaciones.")


if __name__ == "__main__":
    main()
