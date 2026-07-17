# Cross-Validation Report — Mexico Tables (Tablas 4, 5 & 6)
**NormTrace-IHR Pilot | Mexico**
Generated: 2026-05-05

Tables assessed:
- **Tabla 4** — `03_tables/country_legal_mapping/mexico_normative_corpus_index.csv` (16 norms, MEX-001 to MEX-016)
- **Tabla 5** — `03_tables/actors/mexico_health_governance_actors.csv` (16 actors)
- **Tabla 6** — `03_tables/country_legal_mapping/mexico_legal_provisions.csv` (60 provisions)

---

## Check 1: norm_id Consistency (Tablas 4 ↔ 6)

**Question:** Do all `norm_id` values in Tabla 6 correspond to norm_ids registered in Tabla 4?

| Result | Value |
|---|---|
| Provision norm_ids not found in corpus | 0 |
| Status | **PASS** |

Every norm_id used in the 60 provision rows (MEX-002, MEX-003, MEX-004, MEX-005, MEX-007, MEX-008, MEX-009, MEX-011, MEX-012, MEX-016) exists in the corpus index. No orphaned provisions.

**Corpus norm_ids with no provisions extracted** (documented, not a consistency failure):

| norm_id | Short title | Reason |
|---|---|---|
| MEX-001 | Ley aprobación tratados materia económica | Outside pilot priority scope |
| MEX-006 | LFPRH | Budget law; deferred phase |
| MEX-010 | Ley de Planeación | Planning law; deferred phase |
| MEX-013 | Reforma Comisión Compendio Insumos 2023 | Partial MD; flagged manual review |
| MEX-014 | Reforma Reglamento Interior SS 2018 | Partial MD; flagged manual review |
| MEX-015 | Reglamento LGS Investigación para la Salud | Research regulation; deferred phase |

---

## Check 2: norm_title Consistency (Tablas 4 ↔ 6)

**Question:** Do `norm_title` values in Tabla 6 match exactly those in Tabla 4 for every norm_id?

| Result | Value |
|---|---|
| Title mismatches | 0 |
| Status | **PASS** |

All 60 provision rows carry `norm_title` values that match exactly the corresponding entry in Tabla 4.

---

## Check 3: hierarchy_level Consistency (Tablas 4 ↔ 6)

**Question:** Do `hierarchy_level` values in Tabla 6 match `normative_hierarchy` values in Tabla 4?

| Result | Value |
|---|---|
| Hierarchy mismatches | 0 |
| Status | **PASS** |

The eight-level hierarchy coding is consistent across all 60 provision rows and their corpus entries.

---

## Check 4: version_date Consistency (Tablas 4 ↔ 6)

**Question:** Do `version_date` values in Tabla 6 match corpus `version_date` values where the corpus value is not TBD_REVIEW?

| Result | Value |
|---|---|
| Date mismatches (non-TBD corpus dates) | 0 |
| Corpus entries with TBD_REVIEW dates (skipped) | 7 |
| Status | **PASS** |

Where the corpus records a confirmed version_date, the provisions table carries the identical date.

---

## Check 5: provision_id Uniqueness (Tabla 6 internal)

**Question:** Are all `provision_id` values in Tabla 6 unique?

| Result | Value |
|---|---|
| Duplicate provision_ids | 0 |
| Total provision_ids | 60 |
| Status | **PASS** |

All 60 provision_ids follow the mandated format `MEX_PROV_[NORMID]_[ARTICLE]_[###]` and are unique.

---

## Check 6: Actor norm_id References (Tablas 5 ↔ 4)

**Question:** Do all explicit MEX-NNN norm_id references in Tabla 5 correspond to registered corpus entries?

| Result | Value |
|---|---|
| Actor-referenced norm_ids not in corpus | 0 |
| Status | **PASS** |

No actor row references a norm_id absent from the corpus index.

---

## Check 7: Actor ↔ Provision Coverage Alignment (Tablas 5 ↔ 6)

**Question:** For norms that actors cite as legal basis, are those norms covered in the provisions table?

| Norm acronym (norm_id) | Actors citing | Norm in provisions | Alignment |
|---|---|---|---|
| CPEUM (MEX-004) | 11 | Yes (12 provisions) | ✓ |
| LGS (MEX-002) | 8 | Yes (18 provisions) | ✓ |
| LOAPF (MEX-009) | 7 | Yes (5 provisions) | ✓ |
| NOM-017 (MEX-012) | 1 | Yes (5 provisions) | ✓ |
| LGTAIP (MEX-008) | 1 | Yes (2 provisions) | ✓ |
| LGPDPPSO (MEX-007) | 1 | Yes (2 provisions) | ✓ |
| LSCT (MEX-003) | 0 | Yes (5 provisions) | ✓ (provisions exceed actor citations) |
| LFPA (MEX-005) | 0 | Yes (2 provisions) | ✓ (provisions exceed actor citations) |
| RISI (MEX-016) | 0 | Yes (7 provisions) | ✓ (provisions exceed actor citations) |
| LICal (MEX-011) | 0 | Yes (2 provisions) | ✓ (provisions exceed actor citations) |

**Status: PASS.** Every norm referenced by actors as a legal basis is present in the provisions table. Four norms (LSCT, LFPA, RISI, LICal) have provisions extracted even though no actor row cites them explicitly — correct, as those instruments govern procedures and technical standards rather than institutional actors.

---

## Check 8: Key Actors Mentioned in Provisions (Tablas 5 ↔ 6)

**Question:** Are the principal institutional actors registered in Tabla 5 also mentioned in Tabla 6 provision texts?

| Actor | In actors table | Mentioned in provisions |
|---|---|---|
| Secretaría de Salud | Yes | Yes |
| Consejo de Salubridad General | Yes | Yes |
| DGE (Dirección General de Epidemiología) | Yes | Yes |
| SINAVE | Yes | Yes |
| CONAVE | Yes | Yes |
| Secretaría de Relaciones Exteriores | Yes | Yes |

**Status: PASS.** All six principal actors are consistent across both tables.

---

## Check 9: source_url Coverage (Tabla 6 internal)

**Question:** Do all 60 provision rows carry a `source_url`?

| Result | Value |
|---|---|
| Rows with empty source_url | 0 |
| Status | **PASS** |

---

## Check 10: Missing Metadata Flags

**Question:** Are TBD_REVIEW or empty values in mandatory fields documented and accounted for?

| Field | Affected rows | Status |
|---|---|---|
| actor_mentioned | 2 rows (MEX_PROV_NOM017_SEC3115_001; MEX_PROV_LFPA_ART002_001) | Substantively justified; documented in validation report §4.1 |
| All other mandatory fields | 0 | Clean |

**Status: PASS WITH MINOR REVIEW.**

---

## Check 11: Corpus Source Conversion Quality

**Question:** Are any provisions derived from corpus entries with known conversion quality issues?

| norm_id | Source status | Disposition |
|---|---|---|
| MEX-013 | .doc conversion; partial MD | No provisions extracted; flagged for manual review |
| MEX-014 | .doc conversion; partial MD | No provisions extracted; flagged for manual review |
| MEX-012 | PDF conversion; partial structure | 5 provisions from detected sections; appendices incomplete |
| MEX-016 | PDF conversion; full structure | 7 provisions extracted; currency risk (1985 regulation) |

**Status: PASS WITH MINOR REVIEW.**

---

## Summary Table — All Checks

| Check | Description | Result | Status |
|---|---|---|---|
| 1 | norm_id: provisions → corpus | 0 orphaned provision norms | **PASS** |
| 2 | norm_title: provisions ↔ corpus | 0 mismatches | **PASS** |
| 3 | hierarchy_level: provisions ↔ corpus | 0 mismatches | **PASS** |
| 4 | version_date: provisions ↔ corpus | 0 mismatches (TBD skipped) | **PASS** |
| 5 | provision_id uniqueness | 0 duplicates | **PASS** |
| 6 | Actor norm_id refs → corpus | 0 orphaned actor refs | **PASS** |
| 7 | Actor legal basis → provision coverage | 10/10 norms covered | **PASS** |
| 8 | Key actors: actors table ↔ provisions | 6/6 actors consistent | **PASS** |
| 9 | source_url coverage | 0 empty | **PASS** |
| 10 | TBD/empty mandatory fields | 2 rows; substantively justified | **PASS WITH MINOR REVIEW** |
| 11 | Source conversion quality | 2 excluded (MEX-013/014); documented | **PASS WITH MINOR REVIEW** |

---

## Final Status

> ### PASS_WITH_MINOR_REVIEW
>
> All structural and cross-table consistency checks pass. The two minor review items — empty `actor_mentioned` in two definitional provisions, and partial source conversion for MEX-012 and MEX-016 — are documented, substantively justified, and require only reviewer confirmation, not data reconstruction. The three missing norms (Ley de Amparo, Ley General de Mejora Regulatoria, Ley Orgánica del Congreso) are reported as a corpus gap, not a consistency failure.
>
> **Recommended action:** Reviewer clears two TBD flags in Tabla 6 after confirmation. Corpus manager initiates acquisition of three missing norms. Currency of MEX-016 (1985) and MEX-012 (2012) verified against DOF before anchoring analysis proceeds.

---

*End of cross-validation report.*
