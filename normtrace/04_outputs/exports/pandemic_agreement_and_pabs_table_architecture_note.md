# NormTrace-IHR — Table Architecture Note
## Pandemic Agreement and PABS System: Methodological Separation of Tables

**NormTrace-IHR Pilot · Tabla A and Tabla B**
**Date:** 2026-05-05

---

## 1. The Two Tables and Their Rationale

NormTrace-IHR maintains two separate tables for the WHO Pandemic Agreement and the PABS System:

**Tabla A — `pandemic_agreement_obligations.csv`**
Source: WHO Pandemic Agreement, adopted by the Seventy-eighth World Health Assembly under resolution WHA78.1, 20 May 2025.

**Tabla B — `pabs_draft_obligations.csv`**
Source: IGWG Bureau draft PABS Annex, version of 9 March 2026.

The tables are separated because these are two instruments at fundamentally different stages of the international legal process.

---

## 2. Legal Status of Each Instrument

### 2.1 WHO Pandemic Agreement (Tabla A)

The WHO Pandemic Agreement was adopted by the Seventy-eighth World Health Assembly on 20 May 2025 under resolution WHA78.1, pursuant to Article 19 of the WHO Constitution. Its adoption is a completed international legal act.

However, adoption is not the same as entry into force. The Agreement is **not yet open for signature**: under Article 31.2 of the Agreement, it shall be open for signature only **after adoption of the PABS Annex** (the instrument governing the PABS System under Article 12) by the Health Assembly. The PABS Annex has not yet been adopted.

The Agreement will enter into force on the thirtieth day following deposit of the sixtieth instrument of ratification, acceptance, approval, formal confirmation or accession (Art. 33.1). Until then, no State is legally bound as a Party, and the Agreement's obligations are not formally applicable under international law.

**Implication for Tabla A:** The table may be used for preliminary analysis of the Agreement's structure, domestic implementation implications, and ratification preparedness. All obligations identified in Tabla A are presented as obligations of the adopted text, but their legal binding force depends on each State's ratification process and the Agreement's entry into force. The Agreement's provisions apply between parties once it enters into force; prior to that, any implementation is voluntary.

### 2.2 Draft PABS Annex (Tabla B)

The only PABS-related document available in the NormTrace-IHR repository is the IGWG Bureau draft of 9 March 2026. This document was prepared by the Bureau of the Intergovernmental Working Group (IGWG) to present proposals for sections of the draft PABS Annex, building upon on-screen text and discussions at the fifth IGWG meeting, in advance of the sixth meeting of the IGWG.

This document is **draft negotiation text only**. It is:
- Not adopted by the World Health Assembly
- Not legally binding on any State
- Subject to further negotiation, modification or rejection in its entirety
- Not equivalent in any legal sense to the adopted WHO Pandemic Agreement text

**Implication for Tabla B:** All entries in `pabs_draft_obligations.csv` are coded as provisional. No entry in Tabla B should be used to assess State compliance, identify binding national obligations, or support closed legislative recommendations. The table serves exclusively as anticipatory architecture — mapping the legal terrain that may emerge if the draft text or elements thereof are retained in the final PABS Annex.

---

## 3. Rules for Use of Each Table

### 3.1 Tabla A — Uses that are methodologically appropriate

- Preliminary analysis of obligations in the adopted Agreement to assess implementation implications.
- Identifying which provisions require domestic legislative or regulatory action once the Agreement enters into force.
- Planning ratification readiness: what domestic reforms may be needed before or concurrent with ratification.
- Identifying PABS-dependent provisions within the adopted text that cannot be implemented until the PABS Annex is adopted.
- Comparative analysis with other States' domestic frameworks to assess relative readiness.

### 3.2 Tabla A — Uses that are NOT appropriate at this stage

- Asserting that a State is legally non-compliant with the Agreement (no State is bound as a Party).
- Treating Tabla A obligations as currently binding (the Agreement is not yet in force and has not been signed).
- Using Tabla A PABS rows (PA_ART12_001 through PA_ART12_006) as a substitute for analysis of the final PABS Annex content.

### 3.3 Tabla B — Uses that are methodologically appropriate

- Anticipatory mapping of possible future domestic implementation requirements.
- Identifying sectors, institutions and regulatory frameworks that may be relevant if the draft text is adopted.
- Preparing research architecture for updating NormTrace when the PABS Annex is finalized.
- Informing early-stage policy discussions on biosafety, biosecurity, export control, data protection, benefit-sharing, and traditional knowledge in the context of pathogen sharing.

### 3.4 Tabla B — Uses that are NOT appropriate

- Treating Tabla B entries as legal obligations.
- Asserting that a State is non-compliant with PABS draft provisions.
- Using Tabla B to make closed legislative recommendations (legislative analysis should await the final Annex text).
- Mixing Tabla B entries with Tabla A entries in the same analytical column without clear methodological flagging.

---

## 4. Relationship Between the Tables

### 4.1 Cross-reference via adopted Agreement Art. 12

Tabla A contains entries PA_ART12_001 through PA_ART12_006 covering the PABS-related provisions of the adopted Agreement. These entries identify that the Agreement establishes the PABS System as a framework obligation but **delegates all operational content to the PABS Instrument** (Annex). For these rows, Tabla A marks:
- `depends_on_pabs_annex = Yes` or `Partially`
- `requires_ratification_implementation_review = TBD after PABS Annex adoption`
- `requires_domestic_legal_anchoring = TBD after PABS Annex adoption`

Tabla B entries reference the `related_pandemic_agreement_article` field to indicate which adopted Agreement provision a given draft element would operationalize.

### 4.2 Future bridge table

Once the PABS Annex is adopted, a **bridge table** should be constructed linking:
- Finalized PABS Annex provisions
- Corresponding Tabla A PABS rows (PA_ART12_xxx)
- Superseded or confirmed Tabla B draft rows

Until this bridge table exists, Tabla A and Tabla B should be analyzed separately. They should not be merged in any analytical output.

---

## 5. Update Requirements

| Trigger event | Required update |
|---|---|
| PABS Annex adopted by WHA | Update all Tabla A PABS rows (TBD fields); archive Tabla B; create bridge table |
| Agreement opens for signature | Update PA_ART31_001; update GENERAL_001 status |
| Agreement enters into force (60 ratifications) | Update PA_ART33_001; update all `legal_status` fields from 'requiring ratification/implementation' to 'in force' |
| Country mapping phase begins | Populate `possible_domestic_actor` with country-specific actors; add federalism columns if applicable |
| IHR Art. 1 'pandemic emergency' further amended | Update PA_ART01_001 cross-reference note |
| COP adopts reporting format (Art. 21) | Update PA_ART21_001 notes on format and frequency |

---

## 6. Areas of Potential Domestic Legal Review Identified by Both Tables

Even in the absence of binding obligations, the combined analysis of Tabla A and Tabla B identifies the following as priority areas for anticipatory domestic legal review, subject to the caveats in Section 3:

- **Laboratories and pathogen sharing**: WCLN participation, biosafety/biosecurity standards, national authorization procedures.
- **Genomic sequence information**: data governance frameworks, upload obligations, persistent identifier systems.
- **Benefit-sharing contracts**: WHO PABS Contract mechanisms, participating manufacturer obligations.
- **Equitable access**: procurement law, stockpiling policy, donation and allocation frameworks.
- **Technology transfer and licensing**: IP legislation, TRIPS flexibilities, State-owned patent licensing.
- **Financing**: domestic funding obligations, coordinating financial mechanism participation.
- **Export control**: compatibility of existing export control law with pathogen sharing obligations.
- **Data protection**: application of national data protection frameworks to pathogen sequence data.
- **Traditional knowledge**: domestic FPIC frameworks for Indigenous Peoples and local communities.
- **Governance**: One Health coordination mechanisms, national multisectoral coordination, PABS Advisory Group participation.

None of these areas generates binding obligations at this stage. They are identified as areas for preparatory legal mapping only.

---

*This note is part of the NormTrace-IHR pilot dataset and should be read alongside `pandemic_agreement_obligations.csv` (Tabla A) and `pabs_draft_obligations.csv` (Tabla B).*
