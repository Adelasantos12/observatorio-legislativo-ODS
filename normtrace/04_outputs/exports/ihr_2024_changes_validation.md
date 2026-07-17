# Validation File — Tabla 2: IHR 2024 Amendment Changes
**NormTrace-IHR Pilot · Dataset: `ihr_2024_changes.csv`**
**Source instrument:** WHA77.17 (1 June 2024) — Amendments to the International Health Regulations (2005)
**Generated:** 2026-05-05
**Validated against:** Full text of WHA77.17 Annex (3113 lines); IHR 2005 Third Edition

---

## 1. Row Count

| Metric | Value |
|---|---|
| Total data rows | 57 |
| ID range | IHR24-CHG-001 → IHR24-CHG-057 |
| Header row | 1 |
| Total file lines | 58 |

---

## 2. Articles and Annexes Covered

The following 37 articles/annexes have at least one entry in Tabla 2:

**Articles:** 1 · 2 · 3 · 4 · 5 · 6 · 8 · 10 · 11 · 12 · 13 · 15 · 16 · 17 · 18 · 19 · 20 · 21 · 24 · 27 · 28 · 35 · 37 · 43 · 44 · 44 bis · 45 · 48 · 49 · 54 · 54 bis

**Annexes:** Annex 1 · Annex 2 · Annex 3 · Annex 4 · Annex 6 · Annex 8

**Articles with NO entry (no normative change identified in WHA77.17):**
Arts. 7, 9, 14, 22, 23, 25, 26, 29–34 (most PoE articles), 36, 38–42, 46–47, 50–53; Annexes 5 and 7.
Note: Annexes 5 and 7 were not amended by WHA77.17. Art. 20 and 21 have WHO-facing obligations tracked but no State Party domestic requirement triggered.

---

## 3. Rows Where `relevant_ihr2005_obligation_id = TBD_REVIEW`

These 20 rows have no direct counterpart in Tabla 1 (IHR-OBL-001 → IHR-OBL-045), either because the obligation is WHO-facing, the 2024 concept is entirely new with no IHR 2005 predecessor, or the cross-reference is ambiguous and requires expert legal review before assignment.

| change_id | article_or_annex | type_of_change | new_or_modified_concept | Reason for TBD_REVIEW |
|---|---|---|---|---|
| IHR24-CHG-002 | Article 1 | new definition | pandemic emergency | New PHEIC sub-category not present in IHR 2005; no Tabla 1 obligation maps to this concept |
| IHR24-CHG-003 | Article 1 | new definition | relevant health products | New cross-cutting concept; no Tabla 1 analogue |
| IHR24-CHG-004 | Article 2 | modified principle | preparedness added to IHR purpose | Scope/purpose change; no single Tabla 1 obligation corresponds |
| IHR24-CHG-005 | Article 3 | modified principle | equity and solidarity added to implementation principles | New principle; no Tabla 1 analogue |
| IHR24-CHG-014 | Article 11 | modified notification/information requirement | WHO information sharing triggered by pandemic emergency | New trigger concept; WHO-facing; ambiguous Tabla 1 cross-reference |
| IHR24-CHG-015 | Article 12 | modified PHEIC determination procedure | pandemic emergency as sub-determination of PHEIC | New sub-category; DG-facing determination; no State Party Tabla 1 counterpart |
| IHR24-CHG-016 | Article 12 | modified PHEIC determination procedure | multi-State Party consultation for PHEIC determination | Procedural change at WHO level; no Tabla 1 obligation maps directly |
| IHR24-CHG-020 | Article 13 | modified response obligation | WHO obligation to facilitate equitable access to relevant health products | WHO-facing; State Party dimension requires review |
| IHR24-CHG-022 | Article 15 | modified recommendation framework | temporary recommendations scope includes pandemic emergency and relevant health products | Recommendation framework change; ambiguous whether one or multiple Tabla 1 entries apply |
| IHR24-CHG-023 | Article 16 | modified recommendation framework | standing recommendations scope includes relevant health products and access information | Recommendation framework change; same ambiguity |
| IHR24-CHG-024 | Article 17 | modified recommendation framework | availability and accessibility of relevant health products as new criterion | New criterion for WHO decision-making; partially State Party-facing |
| IHR24-CHG-025 | Article 18 | modified recommendation framework | WHO recommendations must consider health/care workers, humanitarian situations, supply chains | WHO decision-making criteria; State Party obligations indirect |
| IHR24-CHG-031 | Article 28 | modified points of entry requirement | free pratique paragraph reference corrected | Technical/drafting correction; no substantive Tabla 1 obligation affected |
| IHR24-CHG-039 | Article 44 bis | new financing mechanism | Coordinating Financial Mechanism established | Entirely new article; no IHR 2005 predecessor |
| IHR24-CHG-041 | Article 48 | modified emergency committee procedure | Emergency Committee scope includes pandemic emergency | EC procedural; WHO-facing; no Tabla 1 State Party obligation |
| IHR24-CHG-042 | Article 48 | modified emergency committee procedure | Emergency Committee subject to WHO Advisory Panel Regulations | WHO internal governance; no Tabla 1 counterpart |
| IHR24-CHG-043 | Article 48 | modified emergency committee procedure | Emergency Committee membership: expert from affected State Party strengthened | WHO governance; indirect State Party interest but no domestic obligation |
| IHR24-CHG-044 | Article 49 | modified emergency committee procedure | DG communications include pandemic emergency | WHO procedural; no direct Tabla 1 counterpart |
| IHR24-CHG-045 | Article 54 | modified reporting/review requirement | IHR functioning review must include financing | Review mandate expanded; may map to reporting obligations but requires review |
| IHR24-CHG-046 | Article 54 bis | new implementation committee | States Parties Committee for Implementation established | Entirely new article; no IHR 2005 predecessor |
| IHR24-CHG-053 | Annex 2 | annex amendment | decision instrument middle box expanded: clusters of severe acute respiratory disease | New notification trigger criteria; Tabla 1 cross-reference ambiguous across multiple obligations |

**Total TBD_REVIEW rows: 21**
*(Note: IHR24-CHG-039 and IHR24-CHG-046 appear both in creates_new_domestic_requirement = Yes and TBD_REVIEW because the concepts are new with no IHR 2005 predecessor, but their domestic legal implications are clear.)*

---

## 4. Rows Where `requires_legal_review = Yes`

These 43 rows were coded as requiring domestic legal review — meaning the change either creates new obligations, modifies existing ones in ways that require legislative or regulatory adjustment, or introduces concepts that implicate fundamental rights or institutional competence.

| change_id | article_or_annex | concept |
|---|---|---|
| IHR24-CHG-001 | Article 1 | National IHR Authority (new definition) |
| IHR24-CHG-002 | Article 1 | pandemic emergency (new definition) |
| IHR24-CHG-003 | Article 1 | relevant health products (new definition) |
| IHR24-CHG-004 | Article 2 | preparedness added to IHR purpose |
| IHR24-CHG-005 | Article 3 | equity and solidarity added to implementation principles |
| IHR24-CHG-006 | Article 4 | National IHR Authority designation or establishment |
| IHR24-CHG-007 | Article 4 | National IHR Authority coordination function |
| IHR24-CHG-008 | Article 4 | domestic legislative and administrative adjustments |
| IHR24-CHG-009 | Article 4 | WHO notification of National IHR Authority contact details |
| IHR24-CHG-010 | Article 5 | core capacities expanded to include prevention |
| IHR24-CHG-012 | Article 8 | consultation obligation strengthened from 'may' to 'should' |
| IHR24-CHG-013 | Article 10 | WHO collaboration offer triggered earlier |
| IHR24-CHG-015 | Article 12 | pandemic emergency as sub-determination of PHEIC |
| IHR24-CHG-017 | Article 13 | title expanded to include equitable access to relevant health products |
| IHR24-CHG-018 | Article 13 | core capacities expanded to include prevention, preparedness, humanitarian settings |
| IHR24-CHG-020 | Article 13 | WHO obligation to facilitate equitable access to relevant health products |
| IHR24-CHG-021 | Article 13 | State Party collaboration for equitable access and WHO-coordinated response |
| IHR24-CHG-022 | Article 15 | temporary recommendations scope includes pandemic emergency and relevant health products |
| IHR24-CHG-023 | Article 16 | standing recommendations scope includes relevant health products and access information |
| IHR24-CHG-029 | Article 24 | conveyance operators health measures extended to embarkation and disembarkation |
| IHR24-CHG-030 | Article 27 | quarantine added explicitly to affected conveyances measures |
| IHR24-CHG-032 | Article 35 | health documents may be in digital or non-digital format |
| IHR24-CHG-033 | Article 37 | Maritime Declaration of Health renamed to Maritime Ship Declaration of Health |
| IHR24-CHG-034 | Article 43 | consultation mechanism for additional health measures expanded |
| IHR24-CHG-035 | Article 44 | title expanded to include financing |
| IHR24-CHG-037 | Article 44 | domestic funding obligation and sustainable financing for IHR implementation |
| IHR24-CHG-038 | Article 44 | inter-State coordination on financing entities and Coordinating Financial Mechanism |
| IHR24-CHG-039 | Article 44 bis | Coordinating Financial Mechanism established |
| IHR24-CHG-040 | Article 45 | processing order for personal data clarified |
| IHR24-CHG-044 | Article 49 | DG communications include pandemic emergency |
| IHR24-CHG-045 | Article 54 | IHR functioning review must include financing |
| IHR24-CHG-046 | Article 54 bis | States Parties Committee for Implementation established |
| IHR24-CHG-047 | Annex 1 | title and section heading expanded to include prevention and preparedness |
| IHR24-CHG-048 | Annex 1 | Par. 2 cross-references updated |
| IHR24-CHG-049 | Annex 1 | local level core capacities expanded: health services access and community engagement |
| IHR24-CHG-050 | Annex 1 | intermediate level capacities expanded: coordination, risk communication, misinformation/disinformation |
| IHR24-CHG-051 | Annex 1 | national level capacities expanded: surveillance, clinical guidance, health product access, risk communication |
| IHR24-CHG-052 | Annex 1 | PoE PHEIC response capacity: laboratories added to affected traveller care arrangements |
| IHR24-CHG-053 | Annex 2 | decision instrument middle box expanded: clusters of severe acute respiratory disease |
| IHR24-CHG-055 | Annex 4 | technical requirements for conveyances: health measures during embarkation/disembarkation |
| IHR24-CHG-056 | Annex 6 | vaccination certificates: digital format authorized |
| IHR24-CHG-057 | Annex 8 | Maritime Declaration of Health renamed to Maritime Ship Declaration of Health |

**Total requires_legal_review = Yes: 43 rows**
**Rows coded No or Partial: 14**

---

## 5. Rows Where `creates_new_domestic_requirement = Yes`

26 rows introduce obligations that did not exist in IHR 2005 or extend existing obligations materially:

IHR24-CHG-001, 002, 004, 006, 007, 008, 009, 010, 018, 021, 029, 030, 032, 033, 037, 038, 039, 046, 047, 049, 050, 051, 052, 053, 057.

*(See Section 3 for full details on IHR24-CHG-039 and IHR24-CHG-046 which are simultaneously new and TBD_REVIEW for Tabla 1 cross-reference.)*

---

## 6. Extraction Uncertainty and Quality Notes

### 6.1 Confirmed sources
All 57 rows were extracted directly from the WHA77.17 Annex (full text, 3113 lines). No change was inferred or assumed — each entry corresponds to an explicit amendment in the adopted text.

### 6.2 Specific drafting artifacts noted in source text

- **Art. 48(1 bis)** — The WHA77.17 text contains an apparent drafting artifact: "Expert Committee expert committee" (duplicated phrase in the provision on WHO Advisory Panel Regulations). This was transcribed faithfully in IHR24-CHG-042 and flagged in the notes field.
- **Art. 48(2)** — The phrase "be an expert" appears in the amended membership provision, which may be a stylistic irregularity. It was not independently corrected and is flagged in IHR24-CHG-043 notes.
- **Art. 28 (IHR24-CHG-031)** — The change is a paragraph cross-reference correction (not a substantive amendment). It was included for completeness but flagged as a technical/drafting fix.

### 6.3 Changes that were intentionally NOT included

The following were excluded because they are purely editorial (non-normative) or internal WHO governance with no State Party obligation:
- Annex 7 (unchanged by WHA77.17)
- Annex 5 (unchanged by WHA77.17)
- Minor grammar/punctuation corrections in Arts. 12(5) and 15 that do not alter legal content
- Recitals and preambular language in the WHA77.17 resolution (not part of the IHR text proper)

### 6.4 Rows requiring inter-article interpretation (legal judgment calls)

- **IHR24-CHG-019 through IHR24-CHG-021 (Art. 13):** The distinction between WHO-facing obligations (IHR24-CHG-020) and State Party obligations (IHR24-CHG-021) required interpretive judgment. The boundary was drawn by applying the IHR Art. 13 structure: paragraphs referring to "WHO shall" were coded WHO-facing; paragraphs referring to "States Parties shall" or "States Parties should" were coded State Party-facing.

- **IHR24-CHG-037 vs. IHR24-CHG-038 (Art. 44):** The new financing provisions in Art. 44 were split into two rows because they create two distinct types of obligation: a domestic funding obligation (IHR24-CHG-037) and an inter-State/WHO coordination obligation (IHR24-CHG-038). This split reflects a methodological choice consistent with the obligation-by-obligation approach used in Tabla 1.

- **IHR24-CHG-039 (Art. 44 bis):** The Coordinating Financial Mechanism is a new WHO-administered body, but its establishment entails State Party obligations (participation, contributions). It was coded `creates_new_domestic_requirement = Yes` and `relevant_ihr2005_obligation_id = TBD_REVIEW` simultaneously because (a) the mechanism is new with no IHR 2005 counterpart, and (b) further analysis is needed to determine whether the obligation maps to existing financial cooperation obligations in Tabla 1 or requires a new IHR-OBL entry.

### 6.5 Annex 3 and Annex 4 coverage

- **Annex 3** (IHR24-CHG-054): Technical amendment to ship sanitation certificate model forms — language aligned with renamed Maritime Ship Declaration of Health. Coded as formal/technical amendment.
- **Annex 4** (IHR24-CHG-055): Technical requirements for conveyances now expressly include health measures during embarkation and disembarkation — coded `requires_legal_review = Yes` because it extends operator obligations regulated domestically.

### 6.6 Definitional changes with systemic normative reach

Three new definitions in Art. 1 (IHR24-CHG-001, 002, 003) have systemic implications: they modify the interpretation of a large number of existing IHR provisions. Because their exact domestic impact varies by legal system, all three were coded `requires_legal_review = Yes` and assigned `TBD_REVIEW` where no specific Tabla 1 obligation was exclusively activated.

---

## 7. Summary Statistics

| Indicator | Count |
|---|---|
| Total rows | 57 |
| creates_new_domestic_requirement = Yes | 26 |
| creates_new_domestic_requirement = Partial | 9 |
| creates_new_domestic_requirement = No | 22 |
| requires_legal_review = Yes | 43 |
| requires_legal_review = No | 14 |
| relevant_ihr2005_obligation_id = TBD_REVIEW | 21 |
| Type: new definition | 3 |
| Type: new article | 2 (Arts. 44 bis, 54 bis) |
| Type: modified principle | 2 |
| Type: modified responsible authority requirement | 4 |
| Type: modified surveillance/core capacity requirement | 8 |
| Type: modified notification/information requirement | 5 |
| Type: modified PHEIC determination procedure | 3 |
| Type: modified response obligation | 5 |
| Type: modified recommendation framework | 4 |
| Type: modified points of entry requirement | 4 |
| Type: modified documentation requirement | 2 |
| Type: new financing mechanism | 3 |
| Type: modified personal data requirement | 1 |
| Type: modified emergency committee procedure | 5 |
| Type: modified reporting/review requirement | 1 |
| Type: annex amendment | 6 |

---

*End of validation file. This document is part of the NormTrace-IHR pilot dataset and should be read alongside `ihr_2024_changes.csv` (Tabla 2) and `IHR-2005_obligations_domestic-anchoring.csv` (Tabla 1).*
