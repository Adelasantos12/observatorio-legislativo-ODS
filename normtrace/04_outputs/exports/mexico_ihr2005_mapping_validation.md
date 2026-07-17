# NormTrace-IHR — Validation Report
## Tabla 7: mexico_ihr2005_mapping.csv (v0.1 — preliminary)

**Generated:** 2026-05-05  
**Analyst:** NormTrace automated build (human review required)  
**Output file:** `03_tables/country_legal_mapping/mexico_ihr2005_mapping.csv`  
**Source obligations:** `02_instruments/ihr_2005/IHR-2005_obligations_domestic-anchoring.csv` (45 rows)  
**Source provisions:** `03_tables/country_legal_mapping/mexico_legal_provisions.csv` (v0.2, 110 rows)

---

## 1. Row and Coverage Statistics

| Metric | Value |
|---|---|
| Total mapping rows generated | 80 |
| IHR 2005 obligations mapped | 45 / 45 (100%) |
| Obligations with at least one domestic provision | 43 / 45 (95.6%) |
| NO_MATCH_IDENTIFIED obligations | 2 (IHR-OBL-011, IHR-OBL-037) |
| Rows requiring human review | 13 |
| Rows marked preliminary | 67 |
| Average rows per obligation | 1.78 |

---

## 2. Anchoring Level Distribution

### By individual row

| Anchoring Level | Rows | % |
|---|---|---|
| 0 — No anchoring | 2 | 2.5% |
| 1 — Contextual / weak | 19 | 23.7% |
| 2 — Partial | 51 | 63.8% |
| 3 — Moderate | 8 | 10.0% |
| 4 — Strong | 0 | — |
| 5 — Integrated | 0 | — |

### By obligation (maximum level across all rows for that obligation)

| Level | Count | Obligations |
|---|---|---|
| 0 | 2 | IHR-OBL-011, IHR-OBL-037 |
| 1 | 12 | IHR-OBL-003, 007, 008, 009, 020, 021, 033, 036, 038, 041, 042, 045 |
| 2 | 26 | IHR-OBL-002, 005, 006, 010, 012, 013, 014, 015, 017, 018, 022, 023, 024, 025, 026, 027, 028, 029, 030, 031, 032, 034, 035, 039, 040, 043 |
| 3 | 5 | IHR-OBL-001, 004, 016, 019, 044 |

**Note:** No obligation reaches anchoring level 4 or 5. Levels 4-5 require strong or complete anchoring across all five dimensions (actor, procedure, coordination, enforcement, rights safeguard); this threshold is not met at this preliminary stage.

---

## 3. Match Type Distribution

| Match Type | Rows |
|---|---|
| regulatory | 29 |
| indirect statutory | 26 |
| direct statutory | 7 |
| actor-only | 7 |
| contextual constitutional | 6 |
| coordination | 3 |
| no match identified | 2 |

---

## 4. Gap Type Distribution

| Gap Type | Rows |
|---|---|
| procedural gap | 27 |
| regulatory gap | 24 |
| partial regulatory gap | 10 |
| rights safeguard gap | 10 |
| full gap | 5 |
| coordination gap | 2 |
| none | 2 |

**Dominant gap pattern:** Procedural gaps (33.8%) are most frequent, indicating that Mexico has the statutory and regulatory authority structure for most IHR obligations, but operational procedures — response time windows, WHO notification formats, escalation chains — are not domestically codified. These gaps may be filled by administrative circulars or informal protocols not captured in the legal corpus.

---

## 5. Norms Used in Mapping

| Norm | Rows |
|---|---|
| Reglamento de la LGS en Materia de Sanidad Internacional (MEX-016) | 25 |
| Ley General de Salud (MEX-002) | 24 |
| Reglamento Interior de la Secretaría de Salud (MEX-017) | 13 |
| NOM-017-SSA2-2012 (MEX-012) | 6 |
| Constitución Política de los Estados Unidos Mexicanos (MEX-004) | 5 |
| Ley Aduanera (MEX-018) | 3 |
| Ley Orgánica de la Administración Pública Federal (MEX-009) | 1 |
| Ley General de Protección de Datos Personales — Sujetos Obligados (MEX-007) | 1 |

**Observation:** MEX-016 and MEX-002 together account for 61% of all mapping anchors, confirming their central role in Mexico's IHR domestic implementation framework.

---

## 6. Obligations with NO_MATCH_IDENTIFIED

### IHR-OBL-011 — Annex 1A par. 2: Self-assessment of capacities
No domestic provision requires Mexico to conduct or report a formal IHR core capacity self-assessment within two years of IHR entry into force. The obligation to assess and communicate to WHO on surveillance and response capacity gaps is not reflected in any corpus provision.

**Gap severity:** High — foundational capacity planning obligation.

### IHR-OBL-037 — Art. 40: No charges to travellers for health measures
No domestic provision prohibits charging travellers for health examination, vaccination, prophylaxis, or health documents required under IHR. The corpus does not contain a traveller health measures fee framework.

**Gap severity:** Medium — rights-protection obligation affecting traveller treatment.

---

## 7. Obligations Requiring Human Review (13 rows)

| Mapping ID | Obligation | Reason for review flag |
|---|---|---|
| MEX_MAP_IHR2005_003_002 | IHR-OBL-003 | No Art. 5(2) extension reporting procedure found |
| MEX_MAP_IHR2005_008_001 | IHR-OBL-008 | No 24-hour Art. 9(2) non-state-source verification procedure |
| MEX_MAP_IHR2005_009_001 | IHR-OBL-009 | No Art. 10(2) WHO verification response procedure |
| MEX_MAP_IHR2005_011_001 | IHR-OBL-011 | Full gap — no self-assessment mandate |
| MEX_MAP_IHR2005_020_001 | IHR-OBL-020 | No SSCEC/SSCC issuance or renewal procedure found |
| MEX_MAP_IHR2005_021_001 | IHR-OBL-021 | No Art. 20(3) authorized-ports list mechanism found |
| MEX_MAP_IHR2005_033_001 | IHR-OBL-033 | No Annex 6 vaccine standards domestic implementation |
| MEX_MAP_IHR2005_036_001 | IHR-OBL-036 | No SSCEC/SSCC issuance procedure found |
| MEX_MAP_IHR2005_037_001 | IHR-OBL-037 | Full gap — no Art. 40 charge prohibition found |
| MEX_MAP_IHR2005_038_001 | IHR-OBL-038 | No published charge schedule for goods found |
| MEX_MAP_IHR2005_041_001 | IHR-OBL-041 | No Art. 43(3)/(5) WHO reporting procedure |
| MEX_MAP_IHR2005_042_001 | IHR-OBL-042 | No Art. 43(6) review cycle procedure |
| MEX_MAP_IHR2005_045_001 | IHR-OBL-045 | No Art. 46 biological substances procedure |

---

## 8. Critical Warnings

> **[W-01] PRELIMINARY MAPPING — NOT VALIDATED**  
> All rows carry `review_status = preliminary` or `requires_human_review`. No assessments constitute legal advice, compliance certification, or official government review.

> **[W-02] ANCHORING LEVEL CEILING AT 3**  
> No obligation reaches level 4 or 5. Mexico has the statutory and institutional framework for most IHR obligations, but operational procedures are largely absent from the corpus. This is a structural finding, not a scoring error.

> **[W-03] PROCEDURAL GAP PREVALENCE**  
> Procedural gaps account for 34% of all rows. Obligations-specific time windows (24h/48h), WHO notification formats, and internal escalation chains are not domestically codified. These may be filled by administrative circulars or DGRI diplomatic protocols outside the corpus.

> **[W-04] RISS 1985 CURRENCY RISK**  
> MEX-016 (RLGS Sanidad Internacional, 1985) anchors 25 rows — the largest single-norm contribution. This regulation has never been formally updated to align with IHR 2005 (in force for Mexico since 2007). Provisions mapped as direct regulatory anchors should be reviewed for potential normative obsolescence or conflict with the 2005 text.

> **[W-05] CORPUS GAPS AFFECTING MAPPING**  
> Three expected norms absent from corpus: Ley General de Mejora Regulatoria, Ley de Amparo, Ley Orgánica del Congreso. Their absence may affect completeness for obligations touching oversight (IHR-OBL-003, 041, 042) and administrative review mechanisms.

> **[W-06] SHIP SANITATION CERTIFICATES (OBL-020, 021, 036)**  
> Three obligations relating to Ship Sanitation Certificates have weak or no domestic anchoring. Priority human review recommended to confirm whether implementing procedures exist outside the corpus (COFEPRIS administrative circulars, port health guidelines).

> **[W-07] RIGHTS SAFEGUARD GAPS (10 ROWS)**  
> Ten rows identify rights safeguard gaps in obligations under IHR Arts. 23, 24, 31, 32, 40, 42. Constitutional protections exist (CPEUM Arts. 1, 14, 16, 29) but implementing health-sector regulations do not operationalise these protections for IHR health measure contexts.

> **[W-08] CONFIDENCE LEVEL DISTRIBUTION**  
> High: 25 rows (31%) | Medium: 44 rows (55%) | Low: 11 rows (14%). Low-confidence rows overlap with `requires_human_review` flags and should not be used for analytical conclusions without prior expert validation.

---

## 9. Recommended Next Steps

1. **Priority human review:** Rows flagged `requires_human_review` (13 rows), particularly OBL-011, OBL-020, OBL-021, OBL-036, OBL-037.
2. **Operational procedures audit:** Identify whether DGE, DGRI, and COFEPRIS have internal protocols or administrative circulars that fill procedural gaps identified in this mapping.
3. **MEX-016 update assessment:** Evaluate whether the 1985 RLGS Sanidad Internacional requires formal amendment to align with IHR 2005, particularly for PoE capacity requirements (OBL-016, 017, 018) and traveller rights provisions (OBL-028–031).
4. **Rights safeguard review:** Commission a review of IHR Arts. 23, 31, 32, 40, 42 obligations against Mexico's human rights law framework, potentially involving CNDH.
5. **Corpus expansion:** Add Ley General de Mejora Regulatoria, Ley de Amparo, and Ley Orgánica del Congreso to complete coverage for oversight and review mechanisms.
6. **Upgrade to v0.2:** After human review of flagged rows, update `review_status` to `validated` and adjust anchoring levels where operational procedures are confirmed.

---

*NormTrace-IHR Pilot | Mexico–IHR 2005 Domestic Anchoring Analysis*  
*This report was generated by automated build on 2026-05-05 and has not been reviewed by a qualified legal professional.*
