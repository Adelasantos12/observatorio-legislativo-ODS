# Country Legal Brains

This folder contains curated country-specific legal reasoning profiles for NormTrace-IHR.

These files are not raw legal sources and are not final policy outputs. They are an **intermediate knowledge layer** that translates each country's legal system into a structured analytical profile, enabling NormTrace to reason in a country-specific way about how international health obligations are — or are not — anchored in domestic law.

---

## What each country legal brain should describe

- **Constitutional architecture:** form of state, constitutional supremacy, fundamental rights framework.
- **Treaty incorporation and domestic legal effect:** how international treaties enter domestic law; self-executing vs. non-self-executing treaties; rank in the legal hierarchy.
- **Legal hierarchy:** the normative pyramid — Constitution, statutes, regulations, administrative rules, and their mutual relationships.
- **Federalism or territorial distribution of competences:** exclusive, shared, and concurrent competences; the role of subnational entities in health governance.
- **Public administration:** structure of the executive branch; ministry organisation; inter-institutional coordination mechanisms.
- **Sector-specific governance architecture:** the health sector legal and institutional framework; key agencies, their mandates, and their legal bases.
- **Types of legal instruments:** the full typology of normative instruments used in the country (laws, regulations, decrees, normas oficiales, circulars, etc.) and their binding force.
- **Oversight and accountability mechanisms:** legislative oversight, judicial review, ombudsman, audit bodies, and other accountability structures relevant to health governance.
- **Document structure and drafting patterns:** how laws are structured; numbering conventions; amendment and derogation practices; transitional provisions.
- **Legal anchoring assessment rules:** country-specific rules for interpreting what constitutes strong or weak anchoring of an international obligation in domestic law.

---

## Folder logic across the repository

### 1. `01_sources/`
Raw and converted source documents.

Examples:
- Constitution PDFs
- Laws in Markdown
- Regulations in Markdown
- Treaty texts
- Metadata files

### 2. `02_country_legal_brains/`
Curated country-specific legal reasoning.

Examples:
- `mexico_legal_system_profile.md`
- `mexico_legal_document_structure_patterns.md`
- `mexico_legal_reasoning_rules.md`

### 3. `03_tables/`
Structured analytical tables.

Examples:
- `ihr_2005_obligations.csv`
- `ihr_2024_changes.csv`
- `pandemic_agreement_obligations.csv`
- `pabs_draft_obligations.csv`
- `mexico_normative_corpus_index.csv`
- `mexico_legal_actors.csv`
- `mexico_ihr_mapping.csv`

### 4. `04_outputs/`
Human-readable products.

Examples:
- Country briefs
- Policy notes
- Exported reports
- Validation logs

---

## Status of country profiles

| Country | Profile | Document patterns | Reasoning rules |
|---|---|---|---|
| Mexico | `mexico_legal_system_profile.md` | `mexico_legal_document_structure_patterns.md` | `mexico_legal_reasoning_rules.md` |
| Switzerland | placeholder | — | — |
| Germany | placeholder | — | — |

*Files marked as placeholder require substantive development.*
