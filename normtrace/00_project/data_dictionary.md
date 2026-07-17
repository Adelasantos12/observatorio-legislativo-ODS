# Data Dictionary — NormTrace-IHR

**Version:** 0.1.0-pilot  
**Date:** 2026-05-05  
**Status:** Draft — fields subject to revision as datasets are built

---

## Overview

This data dictionary describes the structure and field definitions for the core datasets used in NormTrace-IHR. All datasets are stored as CSV files in `02_data/` (raw and processed) and summarised in analytical tables in `03_tables/`.

---

## Dataset: `ihr_2005_obligations.csv`

*Location:* `02_data/processed/ihr_2005_obligations.csv`  
*Status:* **Placeholder — not yet created**  
*Description:* Structured list of all obligations derived from the International Health Regulations (2005).

| Field | Type | Description |
|---|---|---|
| `obligation_id` | string | Unique identifier (e.g., `IHR_A6_1`) |
| `ihr_article` | string | Article and paragraph reference (e.g., `Art. 6(1)`) |
| `ihr_part` | string | Part of the IHR in which the article appears |
| `obligation_text` | string | Verbatim or closely paraphrased text of the obligation |
| `obligation_type` | string | Category: `notification` / `assessment` / `response` / `coordination` / `legal` / `rights` / `other` |
| `state_obligation` | boolean | Whether the obligation is directed at State Parties |
| `who_obligation` | boolean | Whether the obligation is directed at WHO |
| `notes` | string | Analyst notes or flags |

---

## Dataset: `ihr_2024_changes.csv`

*Location:* `02_data/processed/ihr_2024_changes.csv`  
*Status:* **Placeholder — not yet created**  
*Description:* Structured list of changes introduced by the 2024 IHR amendments (WHA77.17), mapped against the 2005 baseline.

| Field | Type | Description |
|---|---|---|
| `change_id` | string | Unique identifier for the change (e.g., `CHG_2024_A5_1`) |
| `ihr_article_ref` | string | Article and paragraph affected |
| `change_type` | string | `new_article` / `amendment` / `deletion` / `addition` / `clarification` |
| `original_text_2005` | string | Original 2005 text (if amended or deleted) |
| `amended_text_2024` | string | New or amended text as adopted by WHA77.17 |
| `substantive_change` | boolean | Whether the change introduces a new or modified obligation |
| `notes` | string | Analyst notes |

---

## Dataset: `mexico_legal_actors.csv`

*Location:* `02_data/processed/mexico_legal_actors.csv`  
*Status:* **Placeholder — not yet created**  
*Description:* Registry of Mexican governmental institutions identified as potentially relevant to IHR implementation.

| Field | Type | Description |
|---|---|---|
| `actor_id` | string | Unique identifier (e.g., `MX_SSA`) |
| `actor_name_es` | string | Official name in Spanish |
| `actor_name_en` | string | Name in English |
| `actor_type` | string | `federal_ministry` / `federal_agency` / `state_authority` / `inter-institutional` / `other` |
| `legal_basis` | string | Legal instrument establishing the actor |
| `ihr_relevance` | string | Brief note on IHR-relevant functions |
| `notes` | string | Analyst notes |

---

## Dataset: `mexico_ihr_mapping.csv`

*Location:* `02_data/processed/mexico_ihr_mapping.csv`  
*Status:* **Placeholder — not yet created**  
*Description:* Core mapping table linking each IHR obligation to its domestic legal anchoring in Mexico.

| Field | Type | Description |
|---|---|---|
| `mapping_id` | string | Unique identifier for each mapping row |
| `obligation_id` | string | FK → `ihr_2005_obligations.obligation_id` |
| `ihr_2024_change_id` | string | FK → `ihr_2024_changes.change_id` (if applicable) |
| `domestic_instrument` | string | Name of the domestic legal instrument |
| `domestic_article` | string | Article and paragraph of the domestic provision |
| `domestic_text_es` | string | Verbatim or paraphrased domestic provision in Spanish |
| `actor_id` | string | FK → `mexico_legal_actors.actor_id` |
| `competence_type` | string | `exclusive` / `shared` / `concurrent` / `delegated` / `undefined` |
| `procedure_described` | boolean | Whether a procedure is described in the domestic provision |
| `coordination_mechanism` | string | Description of coordination mechanism (if any) |
| `oversight_mechanism` | string | Description of oversight/accountability mechanism (if any) |
| `anchoring_score` | integer | Score 0–5 (see methodology_note.md) |
| `gap_types` | string | Comma-separated list of gap types (see methodology_note.md) |
| `source_notes` | string | Source references and traceability notes |
| `review_status` | string | `preliminary` / `under_review` / `validated` |
| `analyst` | string | Initials or ID of analyst |
| `date_analysed` | date | Date of analysis (YYYY-MM-DD) |

---

## Controlled vocabulary

Controlled vocabulary lists for fields marked with fixed categories are maintained in `02_data/lookup_tables/`. Files to be created:

- `lookup_obligation_types.csv`
- `lookup_competence_types.csv`
- `lookup_gap_types.csv`
- `lookup_review_status.csv`
