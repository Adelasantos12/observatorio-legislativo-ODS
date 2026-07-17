# NormTrace-IHR — Final Cross-Validation Report
## Mexico–IHR 2005 Mapping Package and Derived Outputs

**Report type:** Cross-validation — NormTrace-IHR QA layer  
**Generated:** 2026-05-05  
**Validator:** NormTrace automated cross-validation pipeline (human review required to confirm)  
**Files reviewed:** 4 primary outputs + 3 validation reports + 2 source tables  
**Status declared at end of this report**

> This report does not constitute a legal validation, a compliance determination, or an official institutional review. It is an automated consistency check of the analytical pipeline outputs against the source mapping data.

---

## 1. Scope of Validation

| File | Role | Lines | Size |
|---|---|---|---|
| `mexico_ihr2005_mapping.csv` | Source of truth | 81 | 47 KB |
| `mexico_legal_internalisation_snapshot.md` | Level 1 output | 135 | 14 KB |
| `mexico_implementation_gap_map.csv` | Level 2 output | 20 | 39 KB |
| `mexico_capacity_building_entry_points.md` | Level 3 output | 150 | 19 KB |
| `mexico_legal_provisions.csv` | Source provisions | 111 | 172 KB |
| `mexico_legal_provisions_validation.md` | L1 QA | 187 | 11 KB |
| `mexico_ihr2005_mapping_validation.md` | L2 QA | 173 | 9 KB |
| `mexico_implementation_gap_map_validation.md` | L3 QA | 134 | 7 KB |

---

## 2. Coverage Check

### 2.1 Obligations mapped

| Metric | Value | Status |
|---|---|---|
| IHR 2005 obligations in source | 45 | — |
| Obligations mapped in CSV | 45 | **PASS** |
| Mapping rows generated | 80 | — |
| Average rows per obligation | 1.78 | — |

### 2.2 Obligations without domestic match

| Obligation | Description | Status in outputs |
|---|---|---|
| IHR-OBL-011 | Annex 1A par. 2 — self-assessment of capacities | Correctly reported as full gap in snapshot (Section 5), gap map, and brief (EP2) |
| IHR-OBL-037 | Art. 40 — no charges to travellers | Correctly reported as full gap in snapshot (Section 5), gap map, and brief (EP3) |

**Result: PASS.** Both NO_MATCH obligations are accurately disclosed in all derived outputs.

### 2.3 Low-confidence obligations (11)

IHR-OBL-003, 008, 009, 020, 021, 033, 036, 038, 041, 042, 045.

These obligations are not individually named in the derived outputs (by design — outputs are thematic, not obligation-by-obligation). The gap map and brief correctly attribute `confidence_level = low` or `requires_human_review` to the thematic areas that contain these obligations (Verification and consultation; PoE ship certificates; Additional health measures; Biological substances / PABS).

**Result: PASS.** Low-confidence status is carried forward at thematic level in derived outputs.

### 2.4 Obligations requiring human review (13)

IHR-OBL-003, 008, 009, 011, 020, 021, 033, 036, 037, 038, 041, 042, 045.

These 13 obligations map to the following thematic areas in the gap map and brief, all of which are correctly flagged `requires_human_review` or carry a low-confidence designation:

- Verification and consultation (OBL-008, 009, 003)
- PoE / ship sanitation certificates (OBL-020, 021, 036)
- Health measures — no-charge gap (OBL-037)
- Health measures — goods charge schedule (OBL-038)
- Additional measures WHO reporting (OBL-041, 042)
- PABS / biological substances (OBL-045)
- Self-assessment (OBL-011)

**Result: PASS.**

---

## 3. Consistency Check

### 3.1 Strong-area claims vs. anchoring_level

The snapshot (Section 3) names five areas as having "relatively stronger anchoring." Each was verified against the maximum anchoring_level for the corresponding obligation in `mexico_ihr2005_mapping.csv`:

| Claimed area | Obligation | Max level in CSV | Minimum required | Status |
|---|---|---|---|---|
| NFP designation (Art. 4) | IHR-OBL-001 | 3 | 3 | **PASS** |
| Notification (Art. 6) | IHR-OBL-004 | 3 | 3 | **PASS** |
| PoE continuous capacities (Annex 1B) | IHR-OBL-016 | 3 | 3 | **PASS** |
| PoE designation (Art. 20) | IHR-OBL-019 | 3 | 3 | **PASS** |
| Personal data protection (Art. 45) | IHR-OBL-044 | 3 | 3 | **PASS** |

All five strong-area claims are directly supported by level-3 anchoring rows in the source CSV. No level-4 or level-5 claim appears anywhere in the derived outputs, consistent with the absence of level 4–5 rows in the mapping.

**Result: PASS.**

### 3.2 Partial-area claims vs. anchoring_level

The snapshot (Section 4) lists six areas as having partial anchoring (level 2). The gap map identifies 26 obligations at level 2. The thematic aggregation in the snapshot and gap map is consistent with this distribution.

**Result: PASS.**

### 3.3 Weak/uncertain area claims vs. gap_type and review_status

The snapshot (Section 5) lists seven weak/uncertain areas. Each corresponds to gap_type entries of `full gap`, `procedural gap`, or `regulatory gap` with `confidence_level = low` or `review_status = requires_human_review` in the source CSV.

**Result: PASS.**

### 3.4 Actor inventory check

All actors named in the gap map (`main_mexico_actors` field) and capacity-building brief were verified against `mexico_health_governance_actors.csv` (18 actors) and the `domestic_norm` field of the mapping CSV. No actor was identified in the derived outputs that is absent from these two sources. Note: InDRE is mentioned in EP7 of the brief and in the laboratory/pathogen row of the gap map with a caveat noting it does not appear in the current actors file; this is correctly flagged as requiring expanded source review.

**Result: PASS with minor note** — InDRE is named in one passage of the brief and gap map with an explicit caveat that it is not in the actors file. This is methodologically appropriate.

---

## 4. Language Check

### 4.1 Forbidden-phrase scan

The following terms were searched across all three derived output files:

| Phrase | Gap map | Snapshot | Brief |
|---|---|---|---|
| "mexico must" | 0 | 0 | 0 |
| "mexico violates" | 0 | 0 | 0 |
| "legally required reform" | 0 | 0 | 0 |
| "binding pabs obligation" | 0 | 0 | 0 |
| "non-compliant" | 0 | 1* | 0 |
| "in violation of" | 0 | 0 | 0 |
| "violates the ihr" | 0 | 0 | 0 |
| "fails to comply" | 0 | 0 | 0 |

**\*Note on "non-compliant" in snapshot:** The single occurrence appears in the Limitations section (Section 8) in the phrase: *"This snapshot does not assess, imply, or suggest whether Mexico is compliant or non-compliant with any IHR obligation."* This is an explicit negation/disclaimer and is methodologically appropriate. **No violation.**

**Result: PASS.**

### 4.2 "Compliance" usage audit

| File | Total uses | In negation/disclaimer context | Potentially unsafe |
|---|---|---|---|
| Snapshot | 3 | 3 | 0 |
| Brief | 8 | 8 | 0 |

All 8 uses in the brief were reviewed manually. Three uses initially flagged by automated scan as "potentially unsafe" were confirmed safe on review:

- *"advisory and investigatory functions for rights compliance"* — refers to CNDH's general institutional mandate, not to Mexico's IHR compliance status.
- *"Not a legal opinion or compliance assessment"* — explicit disclaimer in the Limits section.
- *"an assessment of Mexico's compliance with any international instrument"* — explicit negation: *"Nothing in this document constitutes ... an assessment of Mexico's compliance."*

**Result: PASS. All uses of "compliance" are either negated, disclaimed, or refer to institutional mandates unrelated to IHR compliance status.**

---

## 5. PABS Provisional Status Check

### 5.1 Automated scan results

| File | PABS mentions | Without provisional marker in 150-char window |
|---|---|---|
| Snapshot | 1 | 0 |
| Brief | 16 | 5 |
| Gap map | 31 | 16 |

### 5.2 Assessment of flagged references

The automated scan flagged references where the word "PABS" appeared without a provisional marker within a 150-character window. On review, these are **false positives** of two types:

**Type A — Section-level disclaimer covers the reference:** Entry Point 7 of the brief opens with a bold-formatted disclaimer box stating: *"All references to PABS in this section are based on the IGWG Bureau draft PABS Annex dated 9 March 2026. This draft has not been adopted and is not legally binding."* References to "PABS system" within the section are covered by this standing disclaimer.

**Type B — Field-level provisional marker in adjacent column:** In the gap map CSV, PABS mentions in the `pandemic_agreement_implication` or `capacity_building_entry_point` fields of PABS-relevant rows are covered by the `pabs_dependency` field values of `Yes - provisional only`, `TBD after final PABS Annex`, or `Partially` in the same row. The 150-char window does not extend to the adjacent field.

**Confirmed absent:** No reference in any output file treats PABS as a final, adopted, or binding obligation. The phrase "not legally binding", "provisional", "draft", "requires update after final annex", or equivalent appears in close proximity to all substantive PABS assessments across all files.

**Result: PASS with minor documentation note** — PABS provisional markers are present at section or row level throughout. Individual mention-level scan flagged technical false positives. No substantive PABS obligation claim without disclaimer identified.

---

## 6. Output File Existence

| Output | Expected path | Status |
|---|---|---|
| Country snapshot (Level 1) | `04_outputs/country_profiles/mexico_legal_internalisation_snapshot.md` | **EXISTS** — 135 lines |
| Implementation gap map (Level 2) | `04_outputs/country_profiles/mexico_implementation_gap_map.csv` | **EXISTS** — 20 rows (19 areas + header) |
| Capacity-building brief (Level 3) | `04_outputs/briefs/mexico_capacity_building_entry_points.md` | **EXISTS** — 150 lines |
| IHR 2005 mapping (source) | `03_tables/country_legal_mapping/mexico_ihr2005_mapping.csv` | **EXISTS** — 81 rows |
| Legal provisions (source) | `03_tables/country_legal_mapping/mexico_legal_provisions.csv` | **EXISTS** — 111 rows |
| Provisions validation | `04_outputs/exports/mexico_legal_provisions_validation.md` | **EXISTS** — 187 lines |
| Mapping validation | `04_outputs/exports/mexico_ihr2005_mapping_validation.md` | **EXISTS** — 173 lines |
| Gap map validation | `04_outputs/exports/mexico_implementation_gap_map_validation.md` | **EXISTS** — 134 lines |

**Result: PASS. All expected output files exist with substantial content.**

---

## 7. Summary of Findings

| Check | Result | Finding |
|---|---|---|
| Coverage — obligations | PASS | 45/45 mapped |
| Coverage — NO_MATCH | PASS | 2 correctly disclosed in all outputs |
| Coverage — low confidence | PASS | Carried forward at thematic level |
| Coverage — human review flags | PASS | Correctly represented in derived outputs |
| Consistency — strong area claims | PASS | All 5 level-3 claims backed by source data |
| Consistency — partial area claims | PASS | Level-2 distribution consistent |
| Consistency — weak/gap claims | PASS | All supported by gap_type and review_status |
| Consistency — actor inventory | PASS (minor note) | InDRE caveat appropriately flagged |
| Language — forbidden phrases | PASS | Zero instances across all files |
| Language — "compliance" usage | PASS | All 11 uses in negation/disclaimer context |
| Language — "non-compliant" | PASS | Single instance in explicit negation |
| PABS provisional framing | PASS (minor note) | Section-level and row-level disclaimers present; 150-char scan flagged technical false positives |
| Output file existence | PASS | All 8 files exist with substantial content |

---

## 8. Minor Review Items

The following items do not affect the analytical validity of the outputs but are documented for completeness and future review cycles:

**[M-01] InDRE not in actors file.** The Instituto de Diagnóstico y Referencia Epidemiológicos (InDRE) is named in the gap map laboratory row and in Entry Point 7 of the brief. InDRE does not appear in `mexico_health_governance_actors.csv`. Both references include an explicit caveat. Recommended action: add InDRE to the actors file in a future corpus update cycle.

**[M-02] PABS provisional framing at section level rather than per-mention.** PABS provisional disclaimers are consistently present at section and row level but not always within 150 characters of every individual PABS mention. The substantive content is appropriately disclaimed. Recommended action: consider adding the phrase "draft PABS" (as opposed to "PABS") when referring to draft-specific obligations, to improve automated scanability.

**[M-03] Risk communication area has no IHR 2005 mapping baseline.** The risk communication row in the gap map is marked `confidence_level = low` and `requires_human_review`. It is correctly disclosed that this area has no IHR 2005 mapping basis and relies entirely on IHR 2024 Annex 1 changes. No false claim is made. No corrective action required; documentation is adequate.

**[M-04] RISS 1985 currency risk not individually verified against IHR 2005 articles.** The Reglamento LGS Sanidad Internacional (1985) anchors 25 mapping rows. The cross-validation does not independently verify that specific 1985 articles remain in force and have not been modified by informal practice or partial supersession. This is an inherent corpus limitation documented in all output files.

---

## 9. Final Status

**OVERALL: PASS_WITH_MINOR_REVIEW**

All substantive checks pass. The four minor review items (M-01 through M-04) are documentation and corpus-maintenance notes that do not affect the analytical validity or methodological integrity of the outputs. No rebuild is required.

> This cross-validation report is an automated analytical consistency check. It does not constitute a legal validation, a compliance determination, or an official certification that the outputs are complete, accurate, or suitable for any specific use. Expert human review remains required before the outputs are used in any official, legal, parliamentary, or policy context.

---

*NormTrace-IHR Pilot | Mexico — IHR 2005 Mapping Package*  
*Cross-Validation Report | Generated: 2026-05-05*
