---
title: Pre-Webapp Repository Audit — NormTrace-IHR (Mexico Pilot)
audit_date: 2026-05-05
auditor: NormTrace-IHR automated pipeline (Claude Sonnet 4.5)
base_path: /Users/adelasantos/Documents/NormTrace-IHR/
data_package_path: 04_outputs/exports/data_package_v0_1/
overall_verdict: PASS_WITH_DOCUMENTED_FINDINGS
review_required_before_deployment: true
---

> **Scope and limitations.** This audit is an automated structural and consistency check of the NormTrace-IHR Mexico pilot repository prior to webapp integration. It does not constitute a legal validation, a compliance determination, or an official institutional review. It does not verify the substantive legal accuracy of the mapping, the completeness of the domestic corpus survey, or the correctness of any anchoring assessment. Expert human review remains required before any output is used in official, legal, parliamentary, or policy contexts.

---

## 1. Path Audit

**Finding:** The filesystem mount exposes a 0-byte empty file named `NormTrace-IHR` (no trailing space) at the mount root, alongside the real repository directory `NormTrace-IHR ` (with a trailing space — a macOS filesystem artifact of the mount path). These are not duplicate repositories.

| Item | Value |
|---|---|
| Real repository (bash path) | `/sessions/.../mnt/NormTrace-IHR /` |
| User-facing path | `/Users/adelasantos/Documents/NormTrace-IHR/` |
| Artifact file | `NormTrace-IHR` (0 bytes, no space) — macOS artifact |
| Data duplication | None |

**Recommendation:** Delete the empty `NormTrace-IHR` file from the repository root. It is a macOS filesystem artifact and not part of the repository.

**Status:** INFO — no data integrity impact.

---

## 2. File Existence Audit

All 14 expected files were located. One filename inconsistency was identified.

| Key | Expected filename | Actual filename | Status |
|---|---|---|---|
| IHR 2005 obligations | `ihr_2005_obligations.csv` | `IHR-2005_obligations_domestic-anchoring.csv` | ⚠ RENAME RECOMMENDED |
| IHR 2024 changes | `ihr_2024_changes.csv` | `ihr_2024_changes.csv` | ✓ |
| Pandemic Agreement | `pandemic_agreement_obligations.csv` | `pandemic_agreement_obligations.csv` | ✓ |
| PABS draft | `pabs_draft_obligations.csv` | `pabs_draft_obligations.csv` | ✓ |
| Corpus index | `mexico_normative_corpus_index.csv` | `mexico_normative_corpus_index.csv` | ✓ |
| Actors | `mexico_health_governance_actors.csv` | `mexico_health_governance_actors.csv` | ✓ |
| Legal provisions | `mexico_legal_provisions.csv` | `mexico_legal_provisions.csv` | ✓ |
| Mapping | `mexico_ihr2005_mapping.csv` | `mexico_ihr2005_mapping.csv` | ✓ |
| Snapshot | `mexico_legal_internalisation_snapshot.md` | present | ✓ |
| Gap map | `mexico_implementation_gap_map.csv` | present | ✓ |
| Capacity brief | `mexico_capacity_building_entry_points.md` | present | ✓ |
| Mapping validation | `mexico_ihr2005_mapping_validation.md` | present | ✓ |
| Cross-validation | `mexico_ihr2005_outputs_cross_validation.md` | present | ✓ |
| Legal system profile | `mexico_legal_system_profile.md` | present | ✓ |

**Recommendation:** Rename `IHR-2005_obligations_domestic-anchoring.csv` → `ihr_2005_obligations.csv` to align with the naming convention used across all other data files. The cleaned data package uses the standardized name.

**Status:** ⚠ MINOR — naming inconsistency only; file is present and structurally sound.

---

## 3. CSV Schema Audit

Nine CSVs were audited for encoding (UTF-8 BOM-free), line endings (LF), structural integrity (no extra delimiter columns), duplicate IDs, and missing required fields.

| File | Rows | Fields | Issues |
|---|---|---|---|
| `IHR-2005_obligations_domestic-anchoring.csv` | 45 | 14 | None |
| `ihr_2024_changes.csv` | 57 | 10 | **12 malformed rows** (see §3.1) |
| `pandemic_agreement_obligations.csv` | 83 | — | None |
| `pabs_draft_obligations.csv` | 38 | — | None |
| `mexico_normative_corpus_index.csv` | 18 | — | None |
| `mexico_health_governance_actors.csv` | 18 | — | None |
| `mexico_legal_provisions.csv` | 110 | — | None |
| `mexico_ihr2005_mapping.csv` | 80 | 18 | None |
| `mexico_implementation_gap_map.csv` | 19 | 11 | None |

### 3.1 IHR 2024 Changes — Malformed Rows

**Root cause:** 12 rows in `ihr_2024_changes.csv` contain unquoted semicolons within the `new_or_modified_concept` and/or `relevant_ihr2005_obligation_id` fields, causing the CSV parser to split those fields across extra columns.

**Affected rows:**

| change_id | Cause | Extra cols |
|---|---|---|
| IHR24-CHG-013 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-021 | Unquoted `;` in `relevant_ihr2005_obligation_id` (2 IDs) | 1 |
| IHR24-CHG-027 | Unquoted `;` in `relevant_ihr2005_obligation_id` (2 IDs) | 1 |
| IHR24-CHG-034 | Unquoted `;` in both fields (3 IDs) | 3 |
| IHR24-CHG-035 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-044 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-045 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-048 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-051 | Unquoted `;` in `relevant_ihr2005_obligation_id` (2 IDs) | 1 |
| IHR24-CHG-054 | Unquoted `;` in `relevant_ihr2005_obligation_id` (2 IDs) | 1 |
| IHR24-CHG-055 | Unquoted `;` in `new_or_modified_concept` | 1 |
| IHR24-CHG-056 | Unquoted `;` in `new_or_modified_concept` (2 splits) | 2 |

**Resolution in data package:** All 12 rows were reconstructed algorithmically. The reconstruction anchors on: (a) the first long quoted prose field as `change_summary`, (b) the last field as `notes`, (c) the fields between them as the Yes/No boolean fields plus IHR IDs. Reconstructed `relevant_ihr2005_obligation_id` values use `; ` as the multi-value separator.

**Recommendation:** Re-export `ihr_2024_changes.csv` from the source with all text fields properly quoted (use `csv.QUOTE_ALL` or equivalent). The data package version is the correct reference.

**Status:** ✓ FIXED in data package — ⚠ SOURCE FILE requires correction.

---

## 4. Referential Integrity Audit

| Check | References | Dangling | Status |
|---|---|---|---|
| `mapping.obligation_id` → `ihr_2005_obligations.obligation_id` | 80 | 0 | ✓ PASS |
| `mapping.domestic_provision_id` → `provisions.provision_id` | 80 | 0 | ✓ PASS |
| `provisions.norm_id` → `corpus_index.norm_id` | 110 | 0 | ✓ PASS |
| IHR 2005 full coverage (all 45 obligations in mapping) | 45 | 0 | ✓ PASS |
| Gap map actor mentions vs actors file (soft match) | — | see note | ⚠ WARN |

**Note on actor mentions:** The gap map references actors by abbreviation (ASF, CONAVE, CSG, DGE, DGE (NFP)) that do not match the `actor_name` field in the actors file via string substring search. This is expected: the gap map uses abbreviated names for readability, while the actors file uses full institutional names. Additionally, InDRE (referenced in the gap map with an explicit caveat) is not present in the actors file at all.

**Recommendation:** (a) Add `actor_abbreviation` or `actor_short_name` field to `mexico_health_governance_actors.csv` to support programmatic actor matching. (b) Consider adding InDRE to the actors file with a note on its COFEPRIS integration status.

**Status:** ⚠ MINOR — no broken foreign keys; actor matching limitation is design-level.

---

## 5. Value Normalization Audit

### 5.1 Mapping file — review_status

**Finding:** The mapping file uses `preliminary` (67 rows) alongside `requires_human_review` (13 rows). The gap map uses `preliminary_ai_assisted` (12 rows) and `requires_human_review` (7 rows). These two values represent the same semantic category but differ in spelling.

**Resolution in data package:** All `preliminary` values normalized to `preliminary_ai_assisted` in both files for consistency. Final valid set: `{preliminary_ai_assisted, requires_human_review, verified}`.

**Status:** ✓ FIXED in data package.

### 5.2 Corpus index — instrument_type

**Finding:** The source file uses English descriptive strings (`federal law`, `general law`, `constitution`, etc.) rather than snake_case machine-readable tokens.

**Resolution in data package:** Normalized to snake_case tokens: `federal_law`, `general_law`, `constitution`, `organic_law`, `regulation`, `nom_official_mexican_standard`, `administrative_agreement`, `decree`, `internal_regulation`.

**Status:** ✓ FIXED in data package.

### 5.3 Corpus index — normative_hierarchy

**Finding:** The source file uses numeric-prefixed codes (`1_constitution`, `3_general_law`, `4_federal_or_national_law`, `5_regulation`, `6_internal_regulation`, `7_NOM_or_technical_standard`, `8_administrative_agreement`).

**Resolution in data package:** Numeric prefixes stripped. Final values: `constitution`, `general_law`, `federal_or_national_law`, `regulation`, `internal_regulation`, `nom_or_technical_standard`, `administrative_agreement`.

**Recommendation:** The numeric ordering is useful for hierarchy display in the webapp. Consider adding a separate `normative_hierarchy_rank` integer field (1–8) to the corpus schema, preserving both machine-readable token and display ordering.

**Status:** ✓ FIXED in data package — ⚠ consider adding rank field.

### 5.4 Corpus index — source_status

**Finding:** The source file encodes provenance information in the `source_status` field rather than a dedicated field. Two values: `converted markdown from PDF` (16 rows, meaning "in force, sourced as converted PDF") and `superseded / archived / not active` (2 rows).

**Resolution in data package:** `source_status` normalized to `in_force` (16 rows) and `superseded` (2 rows). A new `source_provenance_note` field preserves the original value for human review.

**Recommendation:** In the corpus index source file, separate `source_status` (legal status: `in_force`, `superseded`, `draft`, etc.) from `source_provenance` (how the text was obtained: `converted_markdown_from_pdf`, `official_xml`, `manual_entry`, etc.).

**Status:** ✓ FIXED in data package — ⚠ source file schema refactor recommended.

### 5.5 Fit fields and other enumerations

All fit fields (`actor_fit`, `procedure_fit`, `coordination_fit`, `enforcement_fit`, `rights_safeguard_fit`, `federalism_fit`), `match_type`, `gap_type`, `anchoring_level`, and `confidence_level` passed value normalization with no invalid values found.

**Status:** ✓ PASS — no changes needed.

---

## 6. Output Consistency Audit

### 6.1 Average anchoring level

The snapshot states an average anchoring level of **1.76/5**. This audit computed 1.7556 per-obligation (taking the maximum anchoring level per IHR 2005 obligation across all mapping rows, then averaging over 45 obligations), which rounds to 1.76. The per-row average across all 80 mapping rows is 1.81.

The snapshot calculation is methodologically correct: per-obligation averaging avoids over-counting obligations with multiple domestic provisions.

**Status:** ✓ PASS.

### 6.2 No-match obligations

The mapping contains exactly 2 obligations with `match_type = no match identified`: IHR-OBL-011 and IHR-OBL-037. Both are referenced in the snapshot by ID.

**Status:** ✓ PASS.

### 6.3 Forbidden language scan

Automated scan for: `compliance`, `non-compliance`, `Mexico must`, `Mexico violates`, `legally required reform`, `binding PABS obligation` across four output files.

| File | Hits | Context |
|---|---|---|
| `mexico_legal_internalisation_snapshot.md` | 3 × "compliance" | All in explicit disclaimer sections ("does not assess compliance") |
| `mexico_capacity_building_entry_points.md` | "compliance", "non-compliance" | All in disclaimer and CNDH institutional mandate descriptions |
| `mexico_ihr2005_mapping_validation.md` | 1 × "compliance" | In disclaimer ("no assessments constitute...compliance certification") |
| `mexico_ihr2005_outputs_cross_validation.md` | Multiple | In a scan results table listing the forbidden phrases; all hits are meta-references |

**Verdict:** All hits are contextually exempt — appearing in explicit disclaimers, negation clauses ("nothing in this document constitutes an assessment of...compliance"), or as header text in a table that documents what was scanned for. Zero instances of forbidden language used to make substantive claims about Mexico's legal position.

**Status:** ✓ PASS (false-positive scan results; contextual review confirms clean).

### 6.4 PABS provisional framing

All three output levels correctly apply provisional framing to PABS references: (a) explicit disclaimer box in the snapshot and brief; (b) `pabs_dependency` field in the gap map with values `Yes - provisional only` or `TBD after final PABS Annex`; (c) inline IGWG attribution in the brief. No PABS obligation is presented as legally binding.

**Status:** ✓ PASS.

---

## 7. Data Package — `04_outputs/exports/data_package_v0_1/`

The following files constitute the cleaned, normalized data package for webapp integration:

| File | Delimiter | Rows | Changes from source |
|---|---|---|---|
| `ihr_2005_obligations.csv` | `;` | 45 | Whitespace trimmed |
| `ihr_2024_changes.csv` | `;` | 57 | **12 malformed rows reconstructed** |
| `pandemic_agreement_obligations.csv` | `;` | 83 | Whitespace trimmed |
| `pabs_draft_obligations.csv` | `;` | 38 | Whitespace trimmed |
| `mexico_normative_corpus_index.csv` | `,` | 18 | instrument_type, normative_hierarchy, source_status normalized; `source_provenance_note` field added |
| `mexico_health_governance_actors.csv` | `,` | 18 | Whitespace trimmed |
| `mexico_legal_provisions.csv` | `,` | 110 | Whitespace trimmed |
| `mexico_ihr2005_mapping.csv` | `,` | 80 | `preliminary` → `preliminary_ai_assisted` in review_status |
| `mexico_implementation_gap_map.csv` | `,` | 19 | Whitespace trimmed |

All files: UTF-8 (no BOM), LF line endings, `QUOTE_ALL` quoting, no None-key columns, zero duplicate IDs, zero empty ID fields.

**Schema directory:** `04_outputs/exports/data_package_v0_1/schemas/` — contains 9 JSON Schema (draft-07) files, one per CSV, defining field names, types, and enum constraints where applicable.

**Validation result:** 9/9 CSVs PASS all structural checks.

---

## 8. Known Limitations and Recommendations Before Webapp Deployment

The following items are documented from prior validation passes (see `mexico_ihr2005_mapping_validation.md` and `mexico_ihr2005_outputs_cross_validation.md`) and remain open:

| ID | Issue | Severity | Action Required |
|---|---|---|---|
| L-01 | RISS 1985 (NOM-017-SSA2) currency unverified — may have been superseded or substantially amended | HIGH | Human legal review before publication |
| L-02 | InDRE not in actors file; referenced in gap map with caveat | MEDIUM | Add InDRE record to actors file |
| L-03 | `source_status` field in corpus index conflates legal status with provenance; two-field solution needed | MEDIUM | Schema refactor in source file |
| L-04 | `normative_hierarchy_rank` integer field absent — webapp sort/display will require workaround | LOW | Add rank field to schema and corpus |
| L-05 | Actor abbreviation matching not supported by current actors file schema | LOW | Add `actor_abbreviation` field |
| L-06 | `ihr_2024_changes.csv` source file retains unquoted semicolons; re-export required | MEDIUM | Re-export with QUOTE_ALL from source |
| L-07 | 80 mapping rows carry `preliminary_ai_assisted` review status — no human legal review completed | HIGH | Expert review before any public-facing use |
| L-08 | PABS references are based on IGWG Bureau draft of 9 March 2026 (not adopted) — webapp must display provisional disclaimer prominently | HIGH | UI/UX design requirement |

---

## 9. Overall Verdict

**PASS_WITH_DOCUMENTED_FINDINGS**

The repository is structurally sound and the data package is ready for webapp integration from a data engineering perspective. All critical structural defects identified in the audit have been resolved in `data_package_v0_1/`. Source files retain the original issues documented above (L-01, L-03, L-06) and should be corrected in a subsequent data refresh.

No findings in this audit invalidate the analytical conclusions documented in the country outputs. The high-severity items (L-01, L-07, L-08) are substantive review requirements that must be addressed before the webapp outputs are used in any official, legal, or policy context — they are not data engineering blockers.

**Recommended next step:** Human expert review pass covering L-01 (RISS currency), L-07 (mapping review status upgrade for verified rows), and UI design for L-08 (PABS provisional disclaimer).

---

*Generated by NormTrace-IHR automated pipeline — 2026-05-05. This report is part of the analytical record and does not constitute legal advice or an official government position.*
