# Methodology Note — NormTrace-IHR

**Version:** 0.1.0-pilot  
**Date:** 2026-05-05  
**Status:** Draft — subject to revision

---

## 1. Purpose

This note describes the analytical methodology applied in NormTrace-IHR to assess the degree to which international health law obligations are anchored in domestic legal and institutional frameworks.

The methodology is **hermeneutic and structural**, not keyword-based. It reads legal texts for meaning, delegation, structure, omission, and silences — not only for the presence of specific terms.

---

## 2. Anchoring score (0–5)

Each obligation is assigned an anchoring score reflecting the quality and specificity of its domestic legal basis.

| Score | Label | Description |
|---|---|---|
| **0** | No identifiable anchoring | No constitutional, statutory, regulatory, or administrative provision can be identified that addresses the obligation, even indirectly. |
| **1** | Indirect contextual anchoring | A general or tangential provision exists (e.g., a broad health mandate) but it does not specifically address the IHR obligation. The anchoring is inferential and weak. |
| **2** | Administrative or operational anchoring | The obligation is addressed through administrative instruments (e.g., guidelines, circulars, operational plans) but lacks a statutory or constitutional basis. Fragile and potentially non-binding. |
| **3** | Partial statutory anchoring | A statutory provision addresses the obligation but incompletely: e.g., it covers part of the obligation, or applies only to certain actors, territories, or circumstances. |
| **4** | Strong statutory-administrative anchoring | A statutory provision clearly and specifically addresses the obligation, supported by implementing regulations or administrative structures. Implementation is operationally grounded. |
| **5** | Integrated implementation anchoring | The obligation is embedded in a coherent statutory-regulatory-institutional framework: clear legal mandate, designated actor, defined procedure, coordination mechanism, oversight, and monitoring. |

**Scoring is conservative.** When in doubt between two scores, assign the lower one and flag for expert review.

---

## 3. Gap typology

When anchoring is incomplete or absent, the nature of the gap is classified using the following typology. A single obligation may present more than one gap type.

| Gap type | Description |
|---|---|
| **legal silence** | No legal provision addresses the obligation at any level of the normative hierarchy. |
| **competence ambiguity** | It is unclear which institution or governmental level holds formal competence for the obligation. |
| **administrative-only anchoring** | The obligation is addressed exclusively at the administrative level, without a statutory basis. |
| **procedural gap** | A statutory basis exists but no procedure is defined for how the obligation is to be carried out. |
| **coordination gap** | The obligation requires inter-institutional or intergovernmental coordination, but no formal mechanism exists or is clearly designated. |
| **federal implementation gap** | In federal systems: the obligation rests on federal law but implementation depends on subnational levels without a binding coordination mechanism. |
| **rights-safeguard gap** | The obligation involves rights of persons (e.g., travellers, affected communities, isolated individuals) and no domestic provision protects those rights in the relevant context. |
| **oversight gap** | No mechanism exists for accountability, review, or judicial control over the exercise of the relevant competence. |
| **budget/capacity gap** | The legal basis exists but no resource allocation or institutional capacity is designated to operationalise it. (Flag only when identifiable from legal texts; do not assess factual capacity.) |
| **update-review needed** | The domestic provision predates the IHR 2005 or IHR 2024 amendments and may not reflect current obligations; a revision is likely needed. |

---

## 4. Source traceability

Every row in the mapping tables must be traceable to:
- A specific article and paragraph of the IHR (2005 or 2024 amendment);
- A specific provision of domestic law (identified by instrument, article, and paragraph); or
- A note of uncertainty explaining why no provision could be identified and what was searched.

Rows without source traceability are not considered complete. The `review_status` field must remain `preliminary` until source traceability is confirmed.

---

## 5. Limitations

- Legal texts are analysed in their official versions; informal or draft texts are excluded.
- The analysis covers the text of the law, not its judicial interpretation or administrative practice.
- Regulatory gaps may exist that are not visible from statutory text alone.
- AI-assisted preliminary extraction is used (see `ai_use_disclosure.md`); all outputs require expert review.
- The methodology does not assess whether legal provisions are in fact applied or enforced.
