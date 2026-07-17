# Validation File — Tabla A: pandemic_agreement_obligations.csv
**NormTrace-IHR Pilot · WHO Pandemic Agreement Obligations**
**Source:** WHA78.1, 20 May 2025 — WHO Pandemic Agreement (adopted text)
**Generated:** 2026-05-05

---

## 1. Row Count

| Metric | Value |
|---|---|
| Total data rows | 83 |
| ID range | PA_ART01_001 → PA_GENERAL_001 |
| Header row | 1 |
| Total file lines | 84 |

---

## 2. Articles Covered

All substantive articles of the WHO Pandemic Agreement are covered. The following 24 articles generated at least one entry:

| Article | Subject | Number of rows |
|---|---|---|
| Article 1 | Use of terms | 3 |
| Article 2 | Objective | 1 |
| Article 3 | Principles and approaches | 1 |
| Article 4 | Pandemic prevention and surveillance | 12 |
| Article 5 | One Health approach | 4 |
| Article 6 | Preparedness, readiness and health system resilience | 4 |
| Article 7 | Health and care workforce | 5 |
| Article 8 | Regulatory systems strengthening | 5 |
| Article 9 | Research and development | 5 |
| Article 10 | Sustainable and geographically diversified local production | 2 |
| Article 11 | Transfer of technology and know-how | 5 |
| Article 12 | Pathogen Access and Benefit-Sharing System | 6 |
| Article 13 | Supply chain and logistics | 2 |
| Article 14 | Procurement and distribution | 5 |
| Article 15 | Whole-of-government and whole-of-society approaches | 6 |
| Article 16 | Communication and public awareness | 2 |
| Article 17 | International cooperation and support for implementation | 3 |
| Article 18 | Sustainable financing | 3 |
| Article 19 | Conference of the Parties | 2 |
| Article 21 | Reports to the Conference of the Parties | 2 |
| Article 22 | Secretariat (sovereignty safeguard) | 1 |
| Article 24 | Relationship with other international agreements | 1 |
| Articles 31–33 | Signature, ratification, entry into force | 3 |
| General cross-cutting | PABS pre-signature status note | 1 |

**Articles not generating standalone entries** (no State Party domestic obligation): Arts. 20 (right to vote), 23 (settlement of disputes), 25 (reservations), 26 (declarations), 27 (amendments), 28 (annexes), 29 (protocols), 30 (withdrawal), 34 (depositary), 35 (authentic texts). These articles address institutional or treaty mechanics not generating independent domestic implementation obligations.

---

## 3. Themes Covered

| Theme | Rows |
|---|---|
| prevention | 6 |
| preparedness | 6 |
| surveillance | 4 |
| One Health | 5 |
| health systems | 6 |
| health workforce | 5 |
| research and development | 5 |
| technology transfer | 5 |
| local/regional production | 2 |
| equitable access | 3 |
| supply chain | 3 |
| procurement and distribution | 2 |
| financing | 3 |
| international cooperation | 4 |
| national governance | 6 |
| information and reporting | 4 |
| implementation and review | 7 |
| PABS | 6 |
| legal and administrative measures | 1 |

---

## 4. Rows with `depends_on_pabs_annex = Yes` or `Partially`

These 11 rows cannot be fully analyzed or implemented until the PABS Annex is adopted by the Health Assembly. They should not be used for domestic legal recommendations regarding PABS implementation until the Annex is finalized.

| pa_obligation_id | article | concept | depends_on_pabs_annex |
|---|---|---|---|
| PA_ART01_002 | Article 1 | Definition of pandemic-related health products | Partially |
| PA_ART12_001 | Article 12 | PABS System establishment | Partially |
| PA_ART12_002 | Article 12 | PABS Instrument governing operational details | Yes |
| PA_ART12_003 | Article 12 | 20% real-time production target | Yes |
| PA_ART12_004 | Article 12 | Benefit sharing during PHEIC | Yes |
| PA_ART12_005 | Article 12 | Additional benefit sharing provisions | Yes |
| PA_ART12_006 | Article 12 | Review and alignment of national ABS measures | Yes |
| PA_ART31_001 | Article 31 | Signature contingent on PABS Annex adoption | Yes |
| PA_ART32_001 | Article 32 | Ratification process | Yes |
| PA_ART33_001 | Article 33 | Entry into force | Yes |
| PA_GENERAL_001 | Arts. 12 / 31 / 32 | Agreement not yet open for signature | Yes |

**Key finding:** The Agreement cannot be signed until the PABS Annex is adopted (Art. 31.2). Domestic ratification processes should not be initiated before the Annex is in place.

---

## 5. Rows Where `requires_ratification_implementation_review = Yes`

62 of 83 rows are coded `Yes` — the majority of Agreement obligations require domestic legal, regulatory or institutional action post-ratification. Key clusters:

- **Surveillance and prevention** (Arts. 4, 5): Multisectoral plans, One Health strategies, biosafety/biosecurity frameworks, AMR regulatory frameworks.
- **Health system and workforce** (Arts. 6, 7, 8): Health system resilience legislation, workforce protection law, regulatory authority mandates, expedited authorization frameworks.
- **R&D and technology transfer** (Arts. 9, 10, 11): Publicly funded R&D grant policy, IP legislation review (Art. 11.6 'should review'), local production investment frameworks, TRIPS flexibility operationalization.
- **Procurement and supply chain** (Arts. 13, 14): Procurement transparency, GSCL participation, stockpile management policy.
- **Governance** (Arts. 15, 16, 18, 21): Multisectoral coordination mechanism, Indigenous Peoples engagement frameworks, domestic financing obligations, periodic reporting systems.
- **Ratification/entry into force** (Arts. 31–33): Constitutional ratification processes, parliamentary approval.

11 rows coded `Partial / administrative implementation possible` (achievable without legislation). 10 rows coded `No` (purely institutional/international commitments not requiring domestic legal action). 0 rows coded `TBD after PABS Annex adoption` on this field, except the PABS-dependent rows.

---

## 6. Rows Where `requires_domestic_legal_anchoring = Yes`

55 of 83 rows are coded `Yes` — domestic legal anchoring is likely required for the majority of substantive obligations. Key areas:

- Article 4: Multisectoral pandemic prevention plans; biosafety/biosecurity frameworks; AMR regulatory frameworks.
- Article 5: One Health coordination mechanism — legal establishment may be needed in many systems.
- Article 6: Health system resilience and preparedness planning law.
- Article 7: Health workforce protection law; emergency health team designation.
- Article 8: Regulatory authority mandate; expedited authorization legal basis.
- Article 9: Publicly funded R&D IP conditions; clinical trial emergency facilitation.
- Article 11: IP legislation review; TRIPS flexibilities; State-owned patent licensing.
- Article 12 (PABS rows): ABS measure alignment — requires legislative review (pending Annex).
- Articles 15, 18, 21: Coordination mechanism establishment; financing; privacy-compliant reporting.
- Articles 31–33: Constitutional ratification procedures.

21 rows coded `Partial / administrative implementation possible`. 5 rows coded `No` (definitional, sovereignty-safeguard, or purely international). 2 rows coded `TBD after PABS Annex adoption`.

---

## 7. Implementation Domains Distribution

| Implementation domain | Rows |
|---|---|
| legal and regulatory framework | 12 |
| emergency preparedness and response | 7 |
| health system strengthening | 9 |
| public health surveillance | 5 |
| One Health governance | 5 |
| research and development | 6 |
| technology transfer and know-how | 4 |
| access to vaccines, diagnostics and therapeutics | 5 |
| procurement and supply chains | 6 |
| financing and budgetary planning | 5 |
| national coordination | 7 |
| international cooperation | 4 |
| reporting and accountability | 6 |
| parliamentary/legal review | 4 |
| laboratories | 1 |
| laboratories and pathogen sharing | 1 |
| licensing | 1 |

---

## 8. Legal Status Distribution

| legal_status | Rows |
|---|---|
| adopted agreement provision requiring future ratification/implementation | 52 |
| cooperation commitment | 7 |
| framework obligation | 6 |
| institutional commitment | 5 |
| implementation-oriented commitment | 7 |
| PABS-related provision pending annex | 4 |
| uncertain / requires review | 1 |
| adopted agreement provision | 1 |

---

## 9. Extraction Uncertainty and Quality Notes

### 9.1 Source confirmation
All 83 rows were extracted directly from the adopted text of the WHO Pandemic Agreement (WHA78.1 Annex, 20 May 2025). The PABS draft text was **not** used to populate this table. No obligation was inferred or invented.

### 9.2 Legal status caveat — Agreement not yet in force
The Agreement was adopted on 20 May 2025 but is not yet in force. It is not yet open for signature (contingent on PABS Annex adoption). All references to 'adopted agreement provisions' refer to the adopted legal text — not to currently binding obligations.

### 9.3 PABS rows are minimally populated
Rows PA_ART12_001 through PA_ART12_006 reflect only what the adopted Agreement text establishes about the PABS System — which is a framework and a set of requirements for the Annex, not operational rules. These rows are deliberately underdeveloped and marked `TBD after PABS Annex adoption`. They will require full revision once the Annex is finalized.

### 9.4 Article 4 obligation decomposition
Article 4 was decomposed into 12 rows (PA_ART04_001 through PA_ART04_012) because Art. 4.2 lists 10 substantive sub-areas (a)–(j) each with distinct implementation implications. This granular approach is methodologically consistent with the IHR Tabla 1 approach and facilitates cross-instrument analysis.

### 9.5 Article 11.6 — 'should review' formulation
PA_ART11_005 captures the Art. 11.6 obligation: 'Each Party should review and consider amending, as appropriate, its national and/or domestic legislation with a view to ensuring that it is able to implement this Article in a timely and effective manner.' This 'should' formulation is treated as a strong normative expectation and coded `requires_domestic_legal_anchoring = Yes` and `requires_ratification_implementation_review = Yes`, consistent with the interpretive approach applied throughout this table.

### 9.6 Art. 22.2 sovereignty safeguard
PA_ART22_001 captures the provision clarifying that the Agreement does not authorize WHO to direct national law or impose measures such as vaccination mandates or lockdowns. This was included for completeness because it has interpretive significance for the Agreement's legal scope; it does not generate a domestic obligation.

### 9.7 Entry into force contingency
PA_ART31_001, PA_ART32_001, and PA_ART33_001 and PA_GENERAL_001 flag the procedural preconditions for entry into force. These rows are essential to NormTrace's ratification-preparedness function but should not be confused with substantive implementation obligations.

---

*End of validation file. Read alongside `pandemic_agreement_obligations.csv` (Tabla A) and the architecture note `pandemic_agreement_and_pabs_table_architecture_note.md`.*
