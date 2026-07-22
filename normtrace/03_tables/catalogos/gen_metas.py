"""Genera `metas.json`: catálogo de las 169 metas de la Agenda 2030.

- `codigo`, `ods`: estructura canónica del marco (enumerada abajo, 169 metas).
- `nombre_corto_es`: denominación abreviada; para las 45 metas ya usadas se toma
  del objeto METAS de la referencia (docs/referencia/dashboard_huella2030.html).
- `nombre_oficial_es`: texto oficial (A/RES/70/1). Se deja `null` cuando no se
  dispone de la redacción oficial verificada; la vista muestra el nombre corto
  con la marca "denominación abreviada". NO se inventan redacciones oficiales.

Uso: python normtrace/03_tables/catalogos/gen_metas.py
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "metas.json"

# Sufijos de meta por ODS (estructura oficial del marco; total = 169).
TARGETS = {
    1: ["1", "2", "3", "4", "5", "a", "b"],
    2: ["1", "2", "3", "4", "5", "a", "b", "c"],
    3: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d"],
    4: ["1", "2", "3", "4", "5", "6", "7", "a", "b", "c"],
    5: ["1", "2", "3", "4", "5", "6", "a", "b", "c"],
    6: ["1", "2", "3", "4", "5", "6", "a", "b"],
    7: ["1", "2", "3", "a", "b"],
    8: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "a", "b"],
    9: ["1", "2", "3", "4", "5", "a", "b", "c"],
    10: ["1", "2", "3", "4", "5", "6", "7", "a", "b", "c"],
    11: ["1", "2", "3", "4", "5", "6", "7", "a", "b", "c"],
    12: ["1", "2", "3", "4", "5", "6", "7", "8", "a", "b", "c"],
    13: ["1", "2", "3", "a", "b"],
    14: ["1", "2", "3", "4", "5", "6", "7", "a", "b", "c"],
    15: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c"],
    16: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "a", "b"],
    17: [str(i) for i in range(1, 20)],  # 17.1 .. 17.19
}

# Nombres cortos (denominaciones abreviadas) de la referencia — objeto METAS.
NOMBRE_CORTO = {
    "1.3": "Sistemas de protección social",
    "1.4": "Acceso a servicios básicos y vivienda",
    "2.5": "Diversidad genética de semillas y cultivos",
    "3.4": "Enfermedades no transmisibles",
    "3.a": "Control del tabaco (CMCT)",
    "5.1": "Fin de la discriminación contra las mujeres",
    "5.2": "Eliminación de la violencia de género",
    "5.4": "Cuidados y trabajo doméstico no remunerado",
    "5.5": "Participación plena y paridad",
    "5.c": "Políticas y leyes para la igualdad",
    "6.1": "Agua potable segura y asequible",
    "6.2": "Saneamiento e higiene",
    "6.4": "Uso eficiente del agua",
    "6.5": "Gestión integrada de recursos hídricos",
    "6.b": "Participación local en la gestión del agua",
    "7.1": "Acceso a energía asequible",
    "7.2": "Energías renovables",
    "7.b": "Infraestructura energética",
    "8.2": "Productividad y diversificación",
    "8.3": "Políticas para empleo y emprendimiento",
    "8.5": "Empleo pleno y trabajo decente",
    "8.7": "Erradicación del trabajo forzoso",
    "8.8": "Derechos laborales y trabajo seguro",
    "9.1": "Infraestructura de calidad",
    "9.2": "Industrialización inclusiva",
    "9.5": "Investigación e innovación",
    "9.b": "Desarrollo tecnológico nacional",
    "9.c": "Acceso a las TIC",
    "10.2": "Inclusión social, económica y política",
    "10.4": "Políticas fiscales y de protección social",
    "11.1": "Vivienda adecuada y asequible",
    "11.2": "Transporte seguro y sostenible",
    "12.7": "Adquisiciones públicas sostenibles",
    "15.1": "Conservación de ecosistemas terrestres",
    "15.2": "Gestión sostenible de bosques",
    "16.1": "Reducción de la violencia",
    "16.10": "Acceso a la información",
    "16.3": "Estado de derecho y acceso a la justicia",
    "16.4": "Combate a la delincuencia organizada",
    "16.5": "Reducción de la corrupción",
    "16.6": "Instituciones eficaces y transparentes",
    "16.7": "Decisiones inclusivas y participativas",
    "16.a": "Fortalecimiento de capacidades institucionales",
    "17.1": "Movilización de recursos internos",
    "17.3": "Recursos financieros adicionales",
}


def main():
    metas = []
    for ods, suffixes in TARGETS.items():
        for suf in suffixes:
            codigo = f"{ods}.{suf}"
            metas.append({
                "codigo": codigo,
                "ods": ods,
                "nombre_corto_es": NOMBRE_CORTO.get(codigo),
                "nombre_oficial_es": None,
            })
    assert len(metas) == 169, f"esperaba 169 metas, generé {len(metas)}"
    # Verifica que todos los cortos de la referencia existan como código válido.
    faltan = [c for c in NOMBRE_CORTO if c not in {m["codigo"] for m in metas}]
    assert not faltan, f"códigos de METAS no válidos: {faltan}"
    OUT.write_text(json.dumps(metas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    con_corto = sum(1 for m in metas if m["nombre_corto_es"])
    print(f"Escrito {OUT}: {len(metas)} metas, {con_corto} con nombre corto.")


if __name__ == "__main__":
    main()
