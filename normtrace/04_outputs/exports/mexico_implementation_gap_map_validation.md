# NormTrace-IHR — Validation Report
## mexico_implementation_gap_map.csv (v0.1 — preliminary)

**Generated:** 2026-05-05  
**Analyst:** NormTrace automated build (human review required)  
**Output file:** `04_outputs/country_profiles/mexico_implementation_gap_map.csv`

---

## 1. Areas Covered

The gap map covers 19 policy areas derived from the IHR 2005 obligations mapping and expanded to incorporate IHR 2024 changes, Pandemic Agreement obligations, and draft PABS provisions:

1. National IHR Focal Point / National IHR Authority
2. Surveillance and early warning
3. Notification and information-sharing
4. Verification and consultation
5. Public health response capacities
6. Risk communication
7. Points of entry
8. Health measures and travellers
9. Digital / non-digital health documentation
10. Additional health measures (IHR Art. 43)
11. Collaboration and assistance
12. Financing and sustainable capacities
13. Reporting and review
14. Equitable access to relevant health products
15. Laboratories and pathogen-related governance
16. Data protection and information governance
17. Federal-state coordination
18. Parliamentary and oversight mechanisms
19. PABS-related implementation

---

## 2. Sources Used

| Source | File | Use in gap map |
|---|---|---|
| IHR 2005 mapping (Mexico) | `mexico_ihr2005_mapping.csv` | Anchoring pattern, main actors, gap type for all 19 areas |
| IHR 2024 changes | `ihr_2024_changes.csv` | `ihr2024_implication` field — 57 changes reviewed |
| Pandemic Agreement obligations | `pandemic_agreement_obligations.csv` | `pandemic_agreement_implication` field — 83 obligations reviewed |
| PABS draft | `pabs_draft_obligations.csv` | `pabs_dependency` field — 38 draft elements reviewed |
| Mexico health governance actors | `mexico_health_governance_actors.csv` | `main_mexico_actors` field — 18 actors reviewed |

---

## 3. Confidence Level Distribution

| Confidence | Areas | Policy areas |
|---|---|---|
| High | 4 | NFP/National IHR Authority; Notification; Points of entry; Data protection |
| Medium | 10 | Surveillance; Verification; Response capacities; Health measures; Documentation; Additional health measures; Collaboration; Reporting; Federal-state; Parliamentary |
| Low | 5 | Risk communication; Financing; Equitable access; Laboratories/pathogen; PABS |

**Low-confidence areas should not be used as the basis for policy conclusions without prior expert legal review.**

---

## 4. Areas with PABS Dependency

| Area | PABS dependency |
|---|---|
| Surveillance and early warning | Partially |
| Collaboration and assistance | Partially |
| Financing and sustainable capacities | TBD after final PABS Annex |
| Reporting and review | TBD after final PABS Annex |
| Parliamentary and oversight mechanisms | TBD after final PABS Annex |
| Equitable access to relevant health products | Yes — provisional only |
| Laboratories and pathogen-related governance | Yes — provisional only |
| PABS-related implementation | Yes — provisional only |

**Important:** All PABS-dependent assessments are based on the IGWG Bureau draft PABS Annex dated 9 March 2026. This draft has not been adopted and is not legally binding. All PABS-related assessments must be updated after the final PABS Annex is adopted and its legal status is confirmed.

---

## 5. Areas Where the Mexican Corpus Is Insufficient

The following areas have limited or no coverage in the current IHR 2005 mapping corpus, reducing the reliability of the anchoring assessment:

| Area | Corpus limitation |
|---|---|
| Risk communication | No standalone IHR 2005 obligation mapped; assessment based on IHR 2024 Annex 1 changes only |
| Financing and sustainable capacities | No specific IHR 2005 mapping; LFPRH/Ley Planeación provide indirect anchoring only |
| Equitable access to relevant health products | Not directly present as IHR 2005 obligation; entirely based on IHR 2024 new provisions |
| Laboratories and pathogen-related governance | Only OBL-045 at level 1; InDRE and national laboratory governance not covered in corpus |
| PABS-related implementation | Only OBL-045 (IHR Art. 46) at level 1; no domestic pathogen access framework identified |
| Federal-state coordination | State-level legislation and federal-state convenios not in corpus |
| Parliamentary and oversight mechanisms | Not addressed in IHR 2005 mapping; based on actors file and IHR 2024/PA review mechanism provisions |
| Digital / non-digital health documentation | SCT (aviation/maritime) regulatory competence not covered in corpus |

---

## 6. Areas Requiring Human Review (7 areas with `requires_human_review`)

| Area | Reason |
|---|---|
| Verification and consultation | No 24-hour WHO verification/consultation procedures found in corpus |
| Risk communication | Not in IHR 2005 mapping; requires dedicated review |
| Additional health measures | No Art. 43(3)/(5)/(6) WHO reporting procedures found |
| Financing and sustainable capacities | No specific IHR financing mechanism in domestic corpus; new IHR 2024 obligation |
| Equitable access to relevant health products | No domestic equitable access framework identified; requires regulatory review |
| Laboratories and pathogen-related governance | No Art. 46 domestic framework; PABS provisional only |
| PABS-related implementation | No domestic PABS-relevant framework identified; requires legal review |

---

## 7. Compliance Assessment Confirmation

**This gap map does not assess, declare, imply, or suggest whether Mexico is compliant or non-compliant with any obligation under:**
- The International Health Regulations (IHR 2005)
- The IHR 2024 amendments (WHA77.17)
- The WHO Pandemic Agreement (adopted May 2025)
- The draft PABS Annex (IGWG Bureau draft, 9 March 2026)

The gap map identifies patterns in the available legal corpus and analytical observations about areas where domestic anchoring may be relatively stronger, partial, or difficult to trace with available sources. All assessments are preliminary, AI-assisted, and require expert legal validation before use in any official, legal, or policy context.

---

## 8. Update Requirements

This gap map should be updated when:

- IHR 2024 amendments (WHA77.17) enter into force for Mexico and their domestic implementation status is assessed
- The WHO Pandemic Agreement is ratified by Mexico and implementing legislation is identified
- The PABS final Annex is adopted; all 3 PABS-dependent areas and 2 partially-dependent areas must be re-assessed
- New or amended Mexican laws, regulations, or NOMs affecting IHR or Pandemic Agreement implementation are added to the corpus
- State-level legislation and federal-state convenios for IHR implementation are added to the corpus
- Expert legal review validates or corrects preliminary assessments

---

*NormTrace-IHR Pilot | Mexico — IHR 2005 / IHR 2024 / WHO Pandemic Agreement Gap Map*  
*Output generated: 2026-05-05 | Corpus version: 18 instruments | Mapping version: v0.1*
