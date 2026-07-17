---
title: Mexico Legal System Profile for NormTrace-IHR
short_title: Mexico Legal System Profile
version: v0.1 (preliminary)
status: requires legal validation
corpus_version: 17 instruments total (15 active + 2 archived) — updated 2026-05-05
created: 2026-05-05
last_updated: 2026-05-05
author: NormTrace-IHR analysis pipeline
do_not_cite_as: legal authority
---

# Mexico Legal System Profile for NormTrace-IHR

**Version:** v0.1 — Preliminary  
**Status:** Requires expert legal validation  
**Corpus as of:** 2026-05-05 (17 instruments total; 15 active + 2 archived)  
**Do not cite as legal authority**

---

## 1. Purpose and Scope

This profile provides a structured description of the Mexican legal system for use within the NormTrace-IHR analytical framework. Its purpose is to map the domestic normative architecture against which international health obligations — primarily under the International Health Regulations (IHR 2005 and its 2024 amendments) and the WHO Pandemic Agreement — must be assessed for domestic anchoring.

This document does not evaluate Mexico's compliance with any international instrument. It does not propose legislative reforms. It does not substitute legal advice or judicial interpretation. It identifies the structural features of the Mexican legal order that determine whether, and at what normative level, international obligations can operate domestically.

The profile describes: the constitutional framework; the legal effect of international treaties; the hierarchy and typology of domestic normative instruments; the federal structure and distribution of competences; the health governance architecture; the administrative legality framework; legislative drafting conventions; oversight and accountability mechanisms; and the rules used in NormTrace to classify the type of anchoring that each international obligation requires.

The profile assumes that Mexico must be analysed as a federal constitutional state with a distributed system of competences over health matters. Analysis of any single obligation therefore requires attention to at least three levels: the constitutional basis, the federal statutory framework, and the sub-national implementation architecture.

**Scope exclusions at this stage:** This profile does not yet address: state-level legislation; specific IHR or Pandemic Agreement article mapping; gap assessment; compliance scoring; or reform recommendations. These are outputs generated at subsequent NormTrace stages.

---

## 2. Source Corpus and Classification Logic

### 2.1 Corpus composition

The corpus currently loaded in NormTrace-IHR for Mexico comprises seventeen (17) instruments in total (fifteen active + two archived), converted from official PDF or DOC sources to Markdown and paired with structured metadata files. All sources are located at `01_sources/mexico/md/` and `01_sources/mexico/metadata/`. The full index is maintained at `03_tables/country_legal_mapping/mexico_normative_corpus_index.csv`.

Sources were drawn from: the Cámara de Diputados del H. Congreso de la Unión consolidated texts portal, the Diario Oficial de la Federación (DOF), and the Secretaría de Salud. The Cámara de Diputados compilation is informative rather than legally definitive; the DOF is the official source of record for all federal normative instruments.

### 2.2 Classification axes

Each instrument in the corpus is classified along five axes:

**Normative hierarchy** assigns each instrument a functional tier (1 = constitution; 2 = international treaty; 3 = general law; 4 = federal or national law; 5 = executive regulation; 6 = internal regulation; 7 = NOM or technical standard; 8 = administrative agreement). This classification is used in NormTrace for analytical purposes and does not represent a definitive doctrinal thesis on Mexican legal hierarchy. Where hierarchy involves complexity or doctrinal controversy — notably the post-2011 position of human rights treaties, and the precise rank of Consejo de Salubridad General resolutions — instruments are flagged `requires_manual_review = Yes`.

**Sector** classifies each instrument by subject-matter domain: constitutional; health; public administration; international law and treaties; budget and public finance; data protection; transparency; planning; quality infrastructure and standards; and others.

**Instrument type** distinguishes: constitution; general law; federal law; organic law; executive regulation; internal regulation; NOM or technical standard; and administrative agreement.

**Issuing authority** records the constitutional or legal body responsible for the instrument: Congress, the Presidency of the Republic, the Secretaría de Salud, the Consejo de Salubridad General, or a designated secretaría.

**Legal function** captures the operative role of each instrument: establishes constitutional principles; distributes competences; creates institutional mandates; regulates health governance; regulates emergency powers; governs administrative procedure; creates technical standards; governs data or information; governs planning or budgeting; incorporates or governs international commitments; creates oversight mechanisms.

### 2.3 Corpus coverage table

The following table summarises the current corpus. `source_status = converted markdown from PDF` indicates that the Markdown file was machine-converted and may contain formatting artefacts; provisions should be verified against the official DOF source before legal coding.

| norm_title | instrument_type | normative_hierarchy | sector | last_amendment_date | source_status |
|---|---|---|---|---|---|
| Constitución Política de los Estados Unidos Mexicanos (CPEUM) | constitution | 1_constitution | constitutional; health; public administration | 2026-04-23 | converted markdown from PDF |
| Ley General de Salud (LGS) | general law | 3_general_law | health; public administration | 2026-01-15 | converted markdown from PDF |
| Ley sobre la Celebración de Tratados (LSCelTrat) | federal law | 4_federal_or_national_law | international law / treaties | 2025-11-14 | converted markdown from PDF |
| Ley sobre la Aprobación de Tratados en Materia Económica | federal law | 4_federal_or_national_law | international law / treaties | 2004-09-02 | converted markdown from PDF |
| Ley Federal de Procedimiento Administrativo (LFPA) | federal law | 4_federal_or_national_law | public administration | 2025-11-14 | converted markdown from PDF |
| Ley Federal de Presupuesto y Responsabilidad Hacendaria (LFPRH) | federal law | 4_federal_or_national_law | budget / public finance | 2026-04-09 | converted markdown from PDF |
| Ley General de Protección de Datos Personales — Sujetos Obligados (LGPDPPSO) | general law | 3_general_law | data protection | 2025-11-14 | converted markdown from PDF |
| Ley General de Transparencia y Acceso a la Información Pública (LGTAIP) | general law | 3_general_law | transparency | 2025-03-20 | converted markdown from PDF |
| Ley Orgánica de la Administración Pública Federal (LOAPF) | organic law | 4_federal_or_national_law | public administration | 2025-07-16 | converted markdown from PDF |
| Ley de Planeación (LPlan) | federal law | 4_federal_or_national_law | planning | 2026-01-15 | converted markdown from PDF |
| Ley de Infraestructura de la Calidad (LICal) | federal law | 4_federal_or_national_law | quality infrastructure / standards | 2020-07-01 | converted markdown from PDF |
| NOM-017-SSA2-2012 (vigilancia epidemiológica) | NOM / technical standard | 7_NOM_or_technical_standard | health | 2013-02-19 (TBD_REVIEW) | converted markdown from PDF |
| [ARCHIVED] Reforma Reglamento Interior Comisión Compendio Nacional de Insumos 2023 | administrative agreement | 8_administrative_agreement | health; regulatory governance | 2023-06-30 | superseded / archived / not active |
| [ARCHIVED] Reforma Reglamento Interior Secretaría de Salud 2018 | decree | 6_internal_regulation | health; public administration | 2018-02-07 | superseded / archived / not active |
| Reglamento LGS — Investigación para la Salud | regulation | 5_regulation | health; science | 2014-04-02 | converted markdown from PDF |
| Reglamento LGS — Sanidad Internacional | regulation | 5_regulation | health; international law | 1985-02-18 (TBD_REVIEW) | converted markdown from PDF |
| Reglamento Interior de la Secretaría de Salud 2025 (MEX-017) | internal regulation | 6_internal_regulation | health; public administration; health governance | 2025-02-27 | converted markdown from PDF — **active source** |

### 2.4 Expandability

The corpus is open. It does not represent the totality of Mexican federal law relevant to health governance. The Reglamento Interior de la Secretaría de Salud 2025 (MEX-017, DOF 2025-02-27) was added in the 2026-05-05 update as the active source for SS internal organization. Instruments not yet loaded include: reglamentos interiores for COFEPRIS and other deconcentrated bodies, sector-specific NOMs, acuerdos secretariales, lineamientos, programas, the Presupuesto de Egresos de la Federación, SCJN jurisprudence, and normative frameworks governing ports, airports, customs, migration, biosafety, laboratories, and genomic data. The update protocol is specified in Section 14.

---

## 3. Constitutional Architecture

*Primary source: CPEUM (MEX-004) — last reform DOF 23-04-2026.*

### 3.1 Federal republic and division of powers

Mexico is constituted as a representative, democratic, secular, and federal republic composed of free and sovereign states in their interior regime, and by Mexico City, united in a federation (`CPEUM, art. 40`). The supreme power of the federation is divided for its exercise into Legislative, Executive, and Judicial branches, and no two may be united in a single person or body (`CPEUM, art. 49`).

The federal structure has three territorial levels: the Federation, the thirty-one states plus Mexico City (*entidades federativas*), and municipalities (*municipios*). Each level exercises competences defined by the Constitution. Residual competences — those not expressly granted to federal officials — are reserved to states or Mexico City (`CPEUM, art. 124`).

### 3.2 Human rights and the principle of legality

Since the 2011 constitutional reform, all persons in Mexico enjoy the human rights recognised both in the Constitution and in international treaties to which Mexico is party, as well as guarantees for their protection (`CPEUM, art. 1, párr. 1`). Norms relating to human rights are interpreted in conformity with the Constitution and international treaties, always favouring the broadest protection for the person (*principio pro persona*) (`CPEUM, art. 1, párr. 2`). All authorities, within the scope of their competences, are obliged to promote, respect, protect, and guarantee human rights in accordance with the principles of universality, interdependence, indivisibility, and progressivity (`CPEUM, art. 1, párr. 3`).

No treaty may be concluded that alters the human rights recognised by the Constitution or by international human rights treaties to which Mexico is party (`CPEUM, art. 15`).

The principle of administrative legality derives from the combined reading of arts. 14, 16, and 128 CPEUM: no authority may act except on the basis of a written mandate that founds and motivates the legal cause of the procedure (`CPEUM, art. 16`); public officials must swear to uphold the Constitution and the laws that derive from it (`CPEUM, art. 128`); and retroactive application of law to prejudice persons is prohibited (`CPEUM, art. 14`).

### 3.3 Right to health protection

Every person has the right to the protection of health (*derecho a la protección de la salud*). The law defines the bases and modalities for access to health services and establishes the concurrence of the Federation and states in matters of *salubridad general*, in accordance with article 73, fraction XVI of the Constitution (`CPEUM, art. 4, párr. 4`). The right to health is a fundamental right with constitutional rank.

### 3.4 Congressional competences

The Congress has the faculty to legislate on nationality, citizenship, naturalisation, colonisation, emigration, immigration, and *salubridad general* of the Republic (`CPEUM, art. 73, fracc. XVI`). Fraction XVI further establishes that: (1) the Consejo de Salubridad General depends directly on the President of the Republic, without the intervention of any secretaría, and its general dispositions are mandatory throughout the country; (2) Congress has authority to legislate to combat alcoholism; (3) health-related executive actions are subject to congressional oversight. The Consejo de Salubridad General's constitutional status as a body whose resolutions have general mandatory character nationwide is a notable feature of Mexican health governance (`CPEUM, art. 73, fracc. XVI, 1a`).

Congress is also competent to legislate on federal budget and expenditure (`CPEUM, art. 73, fracc. VII`), administrative procedure (derived from art. 73 in conjunction with art. 90), data protection and transparency (leyes generales under art. 6 and art. 16), and planning (`CPEUM, art. 26`).

### 3.5 Executive competences

The President of the Republic has the following faculties directly relevant to this analysis: to promulgate and execute the laws issued by Congress, with the faculty to issue regulations (*reglamentos*) in matters of administrative competence (`CPEUM, art. 89, fracc. I`); to direct foreign policy, conclude treaties with foreign powers and submit them to Senate ratification (`CPEUM, art. 89, fracc. X`); and to appoint and remove secretaries of state (`CPEUM, art. 89, fracc. II`). All presidential regulations, decrees, agreements, and orders must be countersigned (*refrendados*) by the relevant secretary of state (`CPEUM, art. 92`).

### 3.6 Senate and treaty approval

The exclusive faculties of the Senate include: to approve the international treaties and diplomatic conventions concluded by the Executive Branch (`CPEUM, art. 76, fracc. I`). Treaty approval is a senatorial function; the Chamber of Deputies does not participate in this process.

### 3.7 Federal public administration

The federal public administration will be centralised and parastate, in accordance with the organic law issued by Congress, which distributes the administrative affairs of the Federation among the Secretarías de Estado and defines the general bases for the creation of parastate entities (`CPEUM, art. 90`). The LOAPF implements this constitutional mandate.

### 3.8 Federalism: states and municipalities

States adopt for their interior regime a republican, representative, democratic, secular, and popular form of government, with the free municipality as the base of their territorial division and political and administrative organisation (`CPEUM, art. 115`). Municipal competences in health matters derive from the LGS framework and state-level legislation; they are not directly constitutionally specified in the health domain. The residual competence rule (`CPEUM, art. 124`) means that any federal health competence must be expressly granted.

The Constitution authorises the executive powers of states to publish and enforce federal laws (`CPEUM, art. 120`).

### 3.9 Constitutional supremacy and treaties

The Constitution, the laws of Congress that derive from it, and all treaties concluded in accordance with it by the President of the Republic with Senate approval, constitute the Supreme Law of the Union. Judges of each state must conform to this law despite contrary provisions in state constitutions or laws (`CPEUM, art. 133`).

The precise normative rank of ratified international human rights treaties relative to the Constitution — after the 2011 reform to art. 1 — remains a matter of doctrinal and jurisprudential complexity at the Supreme Court of Justice of the Nation (SCJN). The corpus index flags CPEUM (MEX-004) as `requires_manual_review = Yes` on this point. For NormTrace purposes, the functional classification treats ratified treaties as supralegislative (above federal statutes) but subject to constitutional review. This classification requires expert validation before use in litigation or policy advocacy.

No payment may be made that is not included in the Budget (*Presupuesto*) or determined by a subsequent law (`CPEUM, art. 126`), a provision with direct implications for the financial sustainability of internationally mandated obligations.

---

## 4. International Treaties and Their Domestic Legal Effect

*Primary sources: CPEUM (MEX-004); Ley sobre la Celebración de Tratados (MEX-003) — last reform DOF 14-11-2025.*

### 4.1 Scope and definitions

The Ley sobre la Celebración de Tratados (LSCelTrat) regulates the conclusion of treaties (*tratados*) and interinstitutional agreements (*acuerdos interinstitucionales*) in the international sphere (`LSCelTrat, art. 1`).

A **treaty** (*tratado*) is a convention governed by public international law, concluded in writing between the Government of Mexico and one or more subjects of international law, by which Mexico assumes commitments, regardless of denomination. Treaties must be approved by the Senate and, when in conformity with the Constitution, are the Supreme Law of the Union (`LSCelTrat, art. 2, fracc. I`, in conjunction with `CPEUM, arts. 76, fracc. I and 133`).

An **interinstitutional agreement** (*acuerdo interinstitucional*) is a convention governed by public international law concluded in writing between a dependency or decentralised organism of the federal, state, or municipal public administration — or the Fiscalía General — and one or more foreign governmental bodies or international organisations. Its material scope must be strictly limited to the attributed competences of the signing entities (`LSCelTrat, art. 2, fracc. II`). An acuerdo interinstitucional does not require Senate approval but must be notified to and registered by the Secretaría de Relaciones Exteriores.

### 4.2 Procedural stages

The treaty cycle comprises: (1) negotiation and signature, including the grant of full powers (*plenos poderes*) by the President (`LSCelTrat, art. 3`); (2) submission to the Senate for approval (`CPEUM, art. 76, fracc. I`; `LSCelTrat, art. 4`); (3) expression of Mexico's consent to be bound through exchange of diplomatic notes, deposit or exchange of the ratification instrument (`LSCelTrat, art. 5`); and (4) mandatory publication in the Diario Oficial de la Federación, which is a condition for the treaty to be binding in national territory (`LSCelTrat, art. 4, párr. 2`).

The Secretaría de Relaciones Exteriores (SRE) coordinates actions necessary for the conclusion of any treaty, formulates an opinion on the advisability of subscribing to it, and, once subscribed, registers it (`LSCelTrat, art. 6`). Dependencies and decentralised organisms must keep SRE informed of any interinstitutional agreements they intend to conclude (`LSCelTrat, art. 7`).

### 4.3 Relevance for RSI and Pandemic Agreement

The RSI 2005 and the WHO Pandemic Agreement (adopted WHA78, 2025) fall within the category of treaties (*tratados*): they are conventions governed by public international law, concluded by the Government of Mexico with the World Health Organization, by which Mexico assumes international commitments. They require Senate approval and DOF publication to become binding domestically. Mexico is a member state of WHO; RSI 2005 has been in force for Mexico since 2007. The 2024 IHR amendments and the Pandemic Agreement: `requires source verification` as to their specific ratification status and DOF publication date in Mexico.

### 4.4 Self-execution and domestic development

The fact that a treaty is in force domestically does not mean that all its obligations are self-executing (*autoejecutables*). Under Mexican constitutional doctrine, treaty obligations that create competences, establish procedures, require institutional structures, or restrict rights generally require domestic legal development to become operative. The question of self-execution must be assessed obligation by obligation. NormTrace-IHR classifies each obligation individually for its anchoring requirement — statutory, regulatory, administrative, or operational — precisely because the self-execution analysis cannot be resolved globally.

An additional structural consideration: Mexico has not enacted a comprehensive statute that systematically translates IHR 2005 obligations into domestic law. Domestic implementation of RSI obligations operates through the existing health governance framework (LGS, regulations, NOMs, administrative practice) rather than through a purpose-built implementing statute. This feature conditions the anchoring analysis throughout.

---

## 5. Legal Hierarchy and Types of Domestic Legal Instruments

*Primary sources: CPEUM (MEX-004); LSCelTrat (MEX-003); LGS (MEX-002); LOAPF (MEX-009); LFPA (MEX-005); LICal (MEX-011); corpus index (MEX-001 through MEX-016).*

### 5.1 Overview

The Mexican legal system operates through a structured hierarchy of normative instruments. For NormTrace purposes, the hierarchy is treated as a functional classification that determines the legal sufficiency of domestic anchoring for international obligations. The hierarchy is not a simple pyramid: some tiers involve doctrinal complexity that requires expert review, as noted below.

**Tier 1 — Constitution (CPEUM):** The apex norm. All other instruments must conform to it. Constitutional reform requires a two-thirds vote in Congress plus approval by a majority of state legislatures (`CPEUM, art. 135`).

**Tier 2 — International human rights treaties (post-2011 art. 1 reform):** The precise rank of ratified human rights treaties relative to the CPEUM is subject to ongoing SCJN jurisprudential development. For NormTrace, these are classified as supralegislative but subject to constitutional review. Health-related treaties (RSI, Pandemic Agreement) sit at this level once ratified and published. `Requires_manual_review` for definitive hierarchy classification.

**Tier 3 — Leyes generales:** Enacted by federal Congress to distribute competences in concurrent matters between the Federation, states, and municipalities. They bind all three levels of government. Examples in the corpus: LGS (MEX-002), LGPDPPSO (MEX-007), LGTAIP (MEX-008). Leyes generales are a constitutionally recognised mechanism for managing federal-state-municipal concurrence.

**Tier 4 — Leyes federales and leyes nacionales:** Enacted by federal Congress. Leyes federales apply to federal jurisdiction; leyes nacionales apply throughout the national territory regardless of government level (used in certain procedural and criminal law contexts). Examples: LFPA (MEX-005), LFPRH (MEX-006), LOAPF (MEX-009), LICal (MEX-011), LSCelTrat (MEX-003), LPlan (MEX-010). Note: in NormTrace, organic laws (*leyes orgánicas*) are classified at this tier; they do not hold supralegislative rank in Mexico despite their name.

**Tier 5 — Reglamentos (executive regulations):** Issued by the President of the Republic under `CPEUM, art. 89, fracc. I` to develop and detail statutory mandates. They require an express statutory basis (*habilitación legal*) and cannot exceed or contradict the statute they implement. Examples: Reglamento LGS-SI (MEX-016), Reglamento LGS-Inv (MEX-015). Reglamentos open with a formal preamble (*CONSIDERANDO*) citing constitutional and statutory foundations.

**Tier 6 — Reglamentos interiores:** Internal organisational regulations issued by the Executive to establish the internal structure, units, and competences of each secretaría or public body. Legally, they are reglamentos but with scope limited to the internal organisation of the issuing body. They cannot create obligations for third parties. Example in corpus: reform decrees to the Reglamento Interior de la Secretaría de Salud (MEX-013, MEX-014).

**Tier 7 — Normas Oficiales Mexicanas (NOMs):** Mandatory technical regulations issued by the competent secretaría under the framework of the LICal (MEX-011) and the applicable sectoral statute. In health, NOMs are issued by the Secretaría de Salud under LGS authority. They develop technical and operational content of statutory and regulatory mandates. They use decimal numbering (not articles and fracciones). Example: NOM-017-SSA2-2012 (MEX-012). NOMs can operationalise existing competences but cannot independently create new competences, rights, or third-party obligations.

**Tier 8 — Acuerdos administrativos, lineamientos, programas, manuales, and actos administrativos:** These instruments operate within the scope of existing legal and regulatory authorisations. Their normative force is limited: they cannot create binding obligations for parties outside their administrative scope, cannot establish new institutional structures, and cannot authorise coercive measures. They are classified in NormTrace as administrative or operational anchoring instruments — appropriate for obligations that are organisational in nature but insufficient for obligations requiring statutory or regulatory form.

**Jurisprudencia:** Binding judicial interpretation issued by the SCJN, federal circuit tribunals, and electoral courts. In Mexico, jurisprudencia established through five consistent rulings in the same direction binds all courts and authorities, including administrative bodies. NormTrace treats jurisprudence as interpretive context but does not code it as a normative source in the provisions table. Jurisprudential positions relevant to specific analytical questions are flagged for human expert review.

### 5.2 Instrument typology table

The following table presents the functional classification used in NormTrace. The normative hierarchy column reflects analytical position, not a definitive doctrinal determination.

| instrument_type | normative_hierarchy | issuing_authority | legal_function | relevance_for_international_implementation |
|---|---|---|---|---|
| Constitution | 1 — apex | Constituent Congress (1917) / reform procedure (art. 135) | establishes constitutional principles; distributes competences | Foundation for all other instruments; determines treaty rank and self-execution framework |
| International treaty (human rights / health) | 2 — supralegislative (requires_manual_review) | President + Senate approval + DOF publication | incorporates international commitments; may create direct obligations | Direct domestic legal basis for IHR and Pandemic Agreement; triggers statutory development where not self-executing |
| Ley general | 3 — supralegislative over leyes federales in concurrent matters | Federal Congress | distributes competences; creates institutional mandates; regulates health governance | Core anchoring instrument for concurrent matters including health; binding on all government levels |
| Ley federal / organic law / ley nacional | 4 — federal statutory | Federal Congress | creates institutional mandates; regulates administrative procedure; governs planning and budget | Sector-specific statutory anchoring; functional base for regulations and NOMs |
| Reglamento | 5 — sub-statutory executive | President of the Republic | develops and details statutory mandates; regulates implementation | Secondary anchoring; requires statutory habilitación; cannot create new competences |
| Reglamento interior | 6 — internal administrative | President of the Republic | organises internal structure and competences of public bodies | Internal anchoring only; no third-party obligations |
| NOM / technical standard | 7 — technical-normative | Secretaría de Salud (or other competent secretaría) under LICal | creates mandatory technical standards; operationalises statutory and regulatory mandates | Operational anchoring for surveillance, laboratory, and sanitary control obligations |
| Acuerdo administrativo / lineamiento / programa / manual | 8 — administrative | Secretaría de Estado or autonomous body | implements within existing authorisations; organises internal coordination | Administrative or operational anchoring only; insufficient for obligations requiring statutory form |

### 5.3 Categorisation note

NormTrace uses five analytical dimensions to characterise each provision: (A) normative hierarchy; (B) instrument type; (C) sector or subject matter; (D) issuing authority; and (E) function for international implementation. These dimensions are recorded separately in the corpus index. A provision may be at a high normative level but have low relevance for a specific obligation (e.g., a constitutional provision on military affairs), or it may be at a lower level but highly operative (e.g., a NOM directly governing epidemiological notification procedures). Relevance is assessed at the provision level, not at the instrument level.

---

## 6. Federalism and Distribution of Competences

*Primary sources: CPEUM (MEX-004); LGS (MEX-002); LOAPF (MEX-009).*

### 6.1 Federal competences

The Federation holds exclusive competences over matters expressly assigned by the Constitution, including: *salubridad general* (`CPEUM, art. 73, fracc. XVI`); international treaties and foreign policy (`CPEUM, arts. 76, fracc. I and 89, fracc. X`); immigration and emigration (`CPEUM, art. 73, fracc. XVI`); federal budget and taxation; and federal public administration (`CPEUM, art. 90`). Matters of *salubridad general* — which include epidemic control, international sanitary control, epidemiological surveillance, and health emergencies — are federally competent in their regulation, even where their implementation involves state actors.

### 6.2 Concurrent competences and general laws

Health services constitute a concurrent competence: the Federation establishes the general normative framework through leyes generales (primarily the LGS) while states organise and operate health services within their territory in accordance with federal frameworks (`CPEUM, art. 4; LGS, art. 13`). The LGS is the key instrument distributing this concurrence.

Article 13 of the LGS establishes a bipartite table of competences. Under Apartado A, the Federation through the Secretaría de Salud is responsible for: establishing and conducting national health policy; coordinating the National Health System; exercising extraordinary action in matters of *salubridad general*; promoting and planning the National Health System; enforcing the LGS and applicable norms throughout national territory; and verifying compliance with general health standards across all service providers nationwide (`LGS, art. 13, apart. A`). Under Apartado B, state governments are responsible for: organising, operating, supervising, and evaluating the provision of *salubridad general* services within their jurisdiction; and contributing to the National Health System (`LGS, art. 13, apart. B`).

### 6.3 Municipalities

Municipalities are the third tier of government. Municipal health competences in Mexico derive from state-level legislation and from coordination agreements with federal and state authorities, not from direct constitutional specification in the health domain. Municipal participation in health governance is relevant for services delivery, sanitation, and environmental health, but primary regulatory authority over *salubridad general* rests at the federal and state levels.

### 6.4 Leyes generales as distribution mechanisms

Leyes generales — enacted by federal Congress — distribute competences in concurrent matters among all three levels of government and bind all of them. The LGS is the primary ley general for health governance. The LGPDPPSO distributes data protection competences across federal and subnational obligated subjects. The LGTAIP distributes transparency obligations across all government levels. This architecture means that in concurrent matters, a single federal general law may simultaneously create obligations at federal, state, and municipal levels, without those levels having enacted their own corresponding statutes — though state implementing legislation typically also exists.

### 6.5 Federal-state coordination instruments

The LGS establishes mechanisms for formal federal-state coordination: bases and modalities for coordinated exercise of federation-state competences in health service delivery (`LGS, art. 18`); coordination agreements (*acuerdos de coordinación*) that specify the type and operational characteristics of jointly provided services (`LGS, art. 21`); and financing arrangements for *salubridad general* services (`LGS, art. 19`). The National Health System itself is defined as the coordination mechanism among health-sector dependencies and entities (`LGS, art. 5`).

### 6.6 Analytical risks

Three structural features of Mexican federalism generate analytical risk in NormTrace assessments:

**Competence ambiguity:** The boundary between federal *salubridad general* competences and state public health competences is not always precise in the LGS or in practice. Some obligations — particularly those involving points of entry, border health, and emergency declaration — may have contested or unclear attribution between federal and state actors.

**Fragmentation:** Implementation of federally mandated obligations depends on state and municipal capacity, which varies significantly across Mexico's 32 entities. A federal statutory anchor may exist without consistent subnational implementation.

**Implementation gap:** Federal law may establish a standard that states are obliged to meet, but no federal mechanism may effectively ensure compliance. The absence of enforcement mechanisms at the federal-state interface constitutes a structural gap in the NormTrace classification as a *federal implementation gap*.

---

## 7. Health Governance Architecture

*Primary sources: CPEUM (MEX-004); LGS (MEX-002); LOAPF (MEX-009); NOM-017-SSA2-2012 (MEX-012); Reglamento LGS-SI (MEX-016).*

### 7.1 Constitutional and statutory basis for health governance

The right to health protection is constitutionally recognised (`CPEUM, art. 4`). The *salubridad general* competence assigns federal Congress the power to legislate on public health and confers constitutional status on the Consejo de Salubridad General (`CPEUM, art. 73, fracc. XVI`). The LGS is enacted as the reglamentary law of this constitutional right and framework (`LGS, art. 1`). It defines the subject matter of *salubridad general* in a broad enumeration at article 3, which includes: epidemiological surveillance (fracc. XV); international sanitary control (fracc. XVI); health emergencies; health products; laboratory services; and environmental health, among others.

### 7.2 Health authorities (*autoridades sanitarias*)

The LGS defines *autoridades sanitarias* as: the Secretaría de Salud; the Consejo de Salubridad General; the Comisión Federal para la Protección contra Riesgos Sanitarios (COFEPRIS — now restructured, see below); and state and municipal health authorities (`LGS, art. 4`).

The **Secretaría de Salud** (SS) is the federal lead authority for health governance. Under the LOAPF, article 39 assigns the SS a broad enumeration of competences including: the regulation, control, and surveillance of sanitary inputs, services, and establishments; health promotion and epidemiological surveillance; international sanitary control at ports, airports, and border crossings; and coordination of the National Health System (`LOAPF, art. 39`). The LOAPF was last reformed on 16 July 2025.

The **Consejo de Salubridad General (CSG)** is a constitutional body that depends directly on the President of the Republic, without the intervention of any secretaría, and whose general dispositions are mandatory throughout the country (`CPEUM, art. 73, fracc. XVI, 1a`; `LGS, art. 15`). The CSG is composed of the head of the Secretaría de Salud as its president and other members designated by the President of the Republic. Its competences include: establishing general hygiene provisions; defining preventive measures against epidemics; regulating the Compendio Nacional de Insumos para la Salud; and proposing the declaration of health emergencies (`LGS, art. 17`). The CSG's constitutional independence from any secretaría and its capacity to issue mandatory national dispositions make it a significant actor in IHR-relevant governance — particularly for emergency declaration and intersectoral coordination.

**COFEPRIS / Comisión Federal:** The LGS (art. 17 Bis) establishes a decentralised body (*órgano desconcentrado*) of the Secretaría de Salud with competences for sanitary regulation, control, and surveillance. Institutional reform to this body has occurred through the reforms noted in MEX-013 and MEX-014. Given that MEX-013 and MEX-014 are reform instruments with only partial Markdown capture, the current precise institutional name and structure of this body `requires_manual_review`.

**State and municipal health authorities:** State secretarías of health (*secretarías de salud estatales*) and municipal health authorities hold competences under state legislation and coordination agreements with the federal health system. Their specific normative frameworks are not yet in the NormTrace corpus.

### 7.3 National Health System

The National Health System (Sistema Nacional de Salud — SNS) is composed of the dependencies and entities of the federal public administration and the state governments that provide health services, as well as persons providing private health services (`LGS, art. 5`). Coordination of the SNS is assigned to the Secretaría de Salud (`LGS, art. 7`). The SNS is the primary framework through which federal health mandates are operationalised across all levels of government.

### 7.4 Epidemiological surveillance

The domestic operationalisation of epidemiological surveillance obligations rests primarily on: LGS Title V on epidemiological control and surveillance; and NOM-017-SSA2-2012 (MEX-012), the mandatory technical standard that governs the national epidemiological surveillance system. NOM-017 establishes the surveillance system components, notification procedures, laboratory networks, and inter-institutional participation across federal and state actors (`NOM-017-SSA2, numerales 1–15`). It is the most direct domestic operational correlate of IHR surveillance and notification obligations.

NOM-017 was published in the DOF on 19 February 2013 (elaboration year: 2012). Its currency relative to IHR 2024 amendments and the Pandemic Agreement `requires_manual_review` — the corpus index flags this instrument for this reason.

### 7.5 International sanitary control

The Reglamento de la Ley General de Salud en Materia de Sanidad Internacional (MEX-016) governs international sanitary control at ports, airports, and border crossings. It was originally published on 18 February 1985, predating IHR 2005 by twenty years. No amendment date has been identified in the metadata. This regulation represents the most directly IHR-relevant domestic regulatory instrument; its currency and alignment with current IHR standards `requires_manual_review`. The gap between this 1985 reglamento and IHR 2005 obligations is a structurally significant feature of Mexico's domestic health governance architecture.

### 7.6 Health emergencies and security measures

The LGS provides for extraordinary action (*acción extraordinaria*) in matters of *salubridad general*, assigned to the Federation (`LGS, art. 13, apart. A, fracc. V`). The CSG has competence to propose health emergency declarations and to adopt preventive measures against epidemics (`LGS, art. 17`). The LGS also regulates *medidas de seguridad sanitaria* — preventive or emergency intervention powers including temporary or permanent closure, suspension of activities or services, destruction or denaturing of products, and market withdrawal — in its Title on sanctions and security measures.

### 7.7 Federal-state health coordination

Health services coordination between the Federation and states occurs through: acuerdos de coordinación (`LGS, arts. 18–21`); the SNS framework; and the planning system under the Ley de Planeación. The SS is expressly assigned the role of coordinating the SNS and promoting intersectoral coordination for health (`LGS, art. 7`). The *salubridad general* framework assigns the Federation the function of exercising extraordinary action and national enforcement, while states organise and operate services within their jurisdiction.

---

## 8. Federal Public Administration

*Primary sources: CPEUM (MEX-004); LOAPF (MEX-009) — last reform DOF 16-07-2025; LFPA (MEX-005) — last reform DOF 14-11-2025; Reforma RI-SS 2018 (MEX-014).*

### 8.1 Centralised and parastate administration

The Federal Public Administration (*Administración Pública Federal* — APF) is divided into: (a) the centralised administration, comprising the Secretarías de Estado and other directly subordinate bodies; and (b) the parastate sector, comprising decentralised organisms (*organismos descentralizados*), state-owned enterprises, development banks, and similar entities (`CPEUM, art. 90; LOAPF, arts. 1, 45`). The LOAPF defines the structure and competences of each.

### 8.2 Secretarías de Estado

The LOAPF establishes a list of Secretarías de Estado (`LOAPF, art. 26`), including the Secretaría de Salud (art. 26, fracc. XVI). Each secretaría's specific competences are enumerated in individual articles. The Secretaría de Salud's competences are set out in LOAPF article 39, which assigns it a broad range of functions including: regulatory authority over health establishments and products; coordination of the National Health System; international sanitary control at ports, airports, and border crossings; epidemiological surveillance; and health emergency response. The LOAPF is the primary federal statute establishing the Secretaría de Salud's institutional mandate and the legal basis for its regulatory and enforcement activities.

### 8.3 Órganos desconcentrados

Desconcentrated organs (*órganos desconcentrados*) are administrative units that, while hierarchically subordinate to a secretaría, hold specific technical or regulatory functions with some operational autonomy. They are created by statute or decree and do not have separate legal personality. The LGS (art. 17 Bis) establishes the health sanitary regulatory body as an órgano desconcentrado of the Secretaría de Salud. CENAPRECE (Centro Nacional de Programas Preventivos y Control de Enfermedades) and InDRE (Instituto de Diagnóstico y Referencia Epidemiológicos) are operational units with health surveillance functions: `requires source verification` as to their current precise normative status following recent institutional reforms.

### 8.4 Organismos descentralizados

Decentralised organisms are created by Congress or the Executive and have their own legal personality and patrimony (`LOAPF, art. 45`). Social security institutions (IMSS, ISSSTE, IMSS-Bienestar) are relevant actors in the National Health System and hold their own regulatory frameworks. These institutions are not yet fully represented in the NormTrace corpus.

### 8.5 Reglamentos interiores and attributed competences

Each secretaría operates under a *reglamento interior* that specifies its internal structure, the competences of each administrative unit (subsecretarías, direcciones generales, órganos desconcentrados), and the delegation of authority. Reglamentos interiores are issued by presidential decree. The corpus includes two reform decrees to the Reglamento Interior de la Secretaría de Salud (MEX-013, MEX-014), but the complete underlying text is not in the corpus. Internal competence assignments relevant to IHR-related functions (e.g., the unit responsible for international sanitary control, epidemiological surveillance, or the IHR National Focal Point designation) `requires_manual_review` until the complete Reglamento Interior is loaded.

### 8.6 Distinction: legal mandate, regulatory attribution, administrative practice

A central analytical distinction in NormTrace is between: (1) a **legal mandate** (*mandato legal*): an obligation or competence established by statute or constitutional provision, binding and enforceable; (2) a **regulatory attribution** (*atribución reglamentaria*): a competence or procedure established by reglamento or NOM, operative within the bounds of the statutory mandate; and (3) **administrative practice**: informal coordination, protocols, or operational procedures that exist within existing authorisations but do not constitute binding normative instruments and cannot be invoked against third parties. For international obligation anchoring purposes, only categories (1) and (2) constitute normative anchors. Category (3) may reflect operational capacity but not legal sufficiency.

The LFPA provides the general procedural framework for federal administrative acts: where sectoral law does not govern a specific procedure, the LFPA applies as a supplementary statute to federal public administration (`LFPA, art. 1`). This is relevant for procedural anchoring of obligations that require enforceable administrative procedures but where the sectoral statute does not specify them.

---

## 9. Administrative Legality and Regulatory Instruments

*Primary sources: CPEUM (MEX-004); LFPA (MEX-005); LICal (MEX-011); LGS (MEX-002).*

### 9.1 Principle of administrative legality

Under Mexican constitutional law, no administrative authority may act without written mandate that grounds and motivates the legal cause of the procedure (`CPEUM, art. 16`). This means every administrative action must have: (a) a legal basis (*fundamento legal*) — an explicit norm that confers the authority to act; and (b) an adequate motivation (*motivación*) — the reasons why the specific circumstances require the action. Any administrative act that lacks either element is legally defective and subject to challenge through administrative appeal (*recurso de revisión*) or *amparo*.

For IHR anchoring analysis, the principle of administrative legality means that an authority cannot exercise a power over persons or property unless that power is expressly attributed by statute or regulation. The mere existence of a general health mandate does not authorise specific coercive measures unless a specific provision does so.

### 9.2 Administrative acts and procedures

The LFPA governs the issuance, validity, notification, and challenge of federal administrative acts. It establishes: mandatory requirements for valid administrative acts (articles 3–4); notification rules; administrative appeal (*recurso de revisión*) against acts that violate rights or interests; and procedural guarantees. The LFPA has supplementary application throughout the federal public administration where sector-specific law does not provide otherwise.

Reglamentos and NOMs are general-scope regulatory instruments; they are not individual administrative acts. They have mandatory force erga omnes within their stated scope. Individual administrative acts (permits, authorisations, sanctions, orders) derive from the general regulatory framework.

### 9.3 Normas Oficiales Mexicanas (NOMs)

NOMs are mandatory technical regulations. They are issued under the LICal framework (MEX-011) by the competent secretaría — for health NOMs, the Secretaría de Salud under LGS authority. The NOM elaboration and issuance process involves: preparation of a draft standard (*PROY-NOM*); publication of the draft for a sixty-day public consultation period; response to comments; and formal issuance. This process is documented in each NOM's preamble (*CONSIDERANDO*) (`NOM-017-SSA2-2012, considerando`).

NOMs are cited by numeral (not by article). Their mandatory scope is declared in numeral 1.2 of each NOM. They use a decimal numbering system compatible with international standards. NOM-017-SSA2-2012 (MEX-012) is the operative domestic standard governing the national epidemiological surveillance system and constitutes the primary technical-normative anchoring instrument for IHR surveillance and notification obligations at the domestic operational level.

**Key limitation:** A NOM can develop, specify, and operationalise existing competences. It cannot independently create new competences, rights, or obligations for parties not already subject to statutory authorisation. For obligations that require new powers, third-party obligations, or rights restrictions, statutory or regulatory anchoring is required before NOM-level implementation is legally sufficient.

### 9.4 Regulatory improvement framework

The LICal establishes the framework for the planning, elaboration, issuance, modification, updating, and cancellation of regulatory instruments in Mexico. It replaced the former Ley Federal sobre Metrología y Normalización, and governs: Mexican Official Standards (NOMs); standardisation (Normas Mexicanas — NMX); accreditation and conformity assessment; regulatory impact assessment; and the Single Business Registry (*Registro Único de Manejo*). For NormTrace, the LICal is relevant because it defines the legal basis, procedural requirements, and binding character of NOMs in the health domain.

### 9.5 Sufficiency of acuerdos, lineamientos, and programmes

Administrative agreements (*acuerdos secretariales*), guidelines (*lineamientos*), operational programmes (*programas*), and manuals can constitute valid instruments for implementing international obligations that are purely organisational, involve internal coordination of already-authorised actors, and do not create new obligations, powers, or restrictions. However, they are insufficient as sole anchors where the obligation: creates new competences; imposes obligations on third parties; restricts rights; requires coercive enforcement; involves mandatory data treatment; or requires coordination mechanisms that bind subnational governments. The rules governing this distinction are detailed in Section 12.

---

## 10. Legislative Technique and Document Structure

*Primary source: `02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md` — corpus version: 16 instruments, 2026-05-05.*

### 10.1 Structural units of Mexican legislation

Mexican legal drafting uses a hierarchical set of internal structural units. From largest to smallest: *Libro* (present only in complex statutes such as the LICal); *Título* (main thematic division); *Capítulo* (subdivision within a Título); *Sección* (subdivision within a Capítulo, less common); *Artículo* (the fundamental unit, numbered sequentially); *Párrafo* (unnumbered block within an article, referenced positionally); *Fracción* (numbered subdivision using uppercase Roman numerals: I, II, III); *Inciso* (lettered sub-item within a fracción: a., b., c.); and *Apartado* (uppercase lettered division within an article: A., B., C., used in the CPEUM and in some reglamentos interiores).

Leyes generales and federal laws follow: Títulos → Capítulos → Artículos → Fracciones → Incisos. The LGS uses interpolated numbering for articles added by later reforms: *Bis*, *Ter*, *Quater* (e.g., art. 17 Bis, art. 51 Bis 1, art. 71 Ter). Fracciones similarly use Bis notation for interpolations. This reflects a consolidation practice rather than a systematic recodification.

Reglamentos follow: CONSIDERANDO preamble (citing legal basis) → Capítulos → Artículos → Fracciones, without the Título level in most cases. The preamble is not operative normative content but contains the legal grounding.

NOMs use decimal numbering: 1. Objetivo; 2. Referencias; 3. Términos; 5–15. operative sections; 16. Bibliografía; 18. Observancia; Apéndices. They are cited by numeral, not by article.

Reglamentos interiores and reform decrees use the *ARTÍCULO ÚNICO* structure: a single operative article listing all provisions being reformed, added, or derogated.

### 10.2 Citation conventions

| Instrument | Citation format |
|---|---|
| CPEUM | `CPEUM, art. N` or `CPEUM, art. N, fracc. Roman` or `CPEUM, art. N, apart. Letter, fracc. Roman` |
| Ley General de Salud | `LGS, art. N` or `LGS, art. N, fracc. Roman` |
| LOAPF | `LOAPF, art. N, fracc. Roman` |
| LFPA | `LFPA, art. N` |
| LSCelTrat | `LSCelTrat, art. N` |
| Ley de Planeación | `LPlan, art. N` |
| LGPDPPSO | `LGPDPPSO, art. N` |
| LGTAIP | `LGTAIP, art. N` |
| Regl. LGS — Sanidad Internacional | `Regl. LGS-SI, art. N` |
| NOM-017-SSA2-2012 | `NOM-017-SSA2, numeral N.N` |
| Reglamento Interior SS (underlying) | `RI-SS, art. N, apart. Letter, fracc. Roman` — mark `TBD_REVIEW` until full text is loaded |

### 10.3 Identification of key legal effects

For NormTrace extraction, the following linguistic markers in Mexican legal texts signal specific normative effects:

*Obligations:* `"deberá" / "deberán"` (canonical mandatory obligation marker); `"tiene la obligación de"`.

*Discretionary faculties:* `"podrá" / "podrán"` (canonical discretionary power marker; the organ may but is not required to act).

*Competence attributions:* `"corresponde a"`, `"son atribuciones de"`, `"le corresponde el despacho de los siguientes asuntos"` (LOAPF pattern).

*Prohibitions:* `"queda prohibido"`, `"está prohibido"`, `"se prohíbe"`.

*Mandatory coordination:* `"en coordinación con"` (obligatory joint action); `"por sí o en coordinación con"` (discretionary coordination).

*Normative remission:* `"en términos de"`, `"de conformidad con"`, `"conforme a las disposiciones aplicables"` (unspecified remission, requiring identification of the applicable norm).

*Conditional or circumstantial power:* `"cuando así lo considere"`, `"cuando las circunstancias lo exijan"`.

Inline reform annotations in consolidated texts (e.g., `Fracción reformada DOF 14-01-2013`) are editorial metadata, not operative content, and must be excluded from provision extraction.

### 10.4 Implications for NormTrace extraction

Each provision extracted for NormTrace tables should be identified at the article level as the primary unit, with the fracción as the secondary unit when the article contains multiple distinct normative effects. For NOMs, extraction occurs at the numeral level. Reform instruments (MEX-013, MEX-014) contain encoding artefacts from DOC-to-Markdown conversion and require text normalisation before automated processing. The complete Reglamento Interior de la Secretaría de Salud is not yet in the corpus; provisions from the underlying text should be marked `TBD_REVIEW` until it is loaded.

---

## 11. Oversight and Accountability Mechanisms

*Primary sources: CPEUM (MEX-004); LFPA (MEX-005); LGTAIP (MEX-008); LGPDPPSO (MEX-007); LFPRH (MEX-006).*

### 11.1 Judicial control: amparo and constitutional review

The *juicio de amparo* is the primary mechanism for judicial protection of constitutional rights in Mexico. It allows individuals and legal entities to challenge acts of authority that violate their constitutional rights or the rights recognised in international human rights treaties (`CPEUM, arts. 103–107`). The SCJN exercises constitutional review through: controversias constitucionales (between branches or levels of government); acciones de inconstitucionalidad (abstract review of norms); and amparo. For IHR-related governance, amparo is the most relevant mechanism: any administrative measure affecting the rights of individuals — including quarantine orders, health restrictions, or data collection — is subject to challenge through amparo on grounds of constitutional rights violation or lack of legal basis.

The principle of judicial protection of rights means that administrative measures implementing international health obligations must have adequate constitutional and statutory grounding to survive challenge.

### 11.2 Administrative control

Federal public administration operates under a system of internal control through Órganos Internos de Control (OIC) — internal oversight bodies within each secretaría and parastate entity, technically subordinate to the Secretaría de la Función Pública (SFP). OICs investigate irregularities, impose administrative sanctions on public servants, and audit compliance with legal obligations. The LFPA provides for administrative appeals (*recursos de revisión*) against administrative acts by affected parties.

### 11.3 Parliamentary control

Congress exercises control over the Executive through: budgetary approval (Chamber of Deputies approves the federal budget; the LFPRH governs the programming, approval, exercise, control, and evaluation of federal expenditure — `LFPRH, art. 1`); appearances (*comparecencias*) before congressional committees; legislative oversight through commissions; and audit through the Auditoría Superior de la Federación (ASF), which audits federal public account and reports to the Chamber of Deputies. Health sector expenditure, including expenditure related to IHR implementation, is subject to ASF audit.

### 11.4 Transparency and access to information

The LGTAIP (MEX-008 — nueva ley DOF 20-03-2025, reglamentary of `CPEUM, art. 6`) establishes transparency obligations applicable to all obligated subjects (*sujetos obligados*) at federal, state, and municipal levels: proactive disclosure of specified categories of public information; duty to respond to access to information requests; and sanctions for non-compliance. Health authorities are obligated subjects. Information related to epidemiological surveillance data, health emergency decisions, and international reporting obligations falls within the scope of transparency obligations, subject to applicable exceptions.

### 11.5 Personal data protection

The LGPDPPSO (MEX-007 — reglamentary of `CPEUM, arts. 6 and 16`) governs the treatment of personal data held by obligated subjects at all government levels. It establishes: rights of data subjects (*derechos ARCO*: access, rectification, cancellation, and opposition); principles of legality, purpose limitation, proportionality, and data minimisation; and security obligations for data custodians. For IHR-related surveillance, notification, and data-sharing obligations, the LGPDPPSO constitutes a structural constraint: treatment of personal health data by public health authorities must comply with data protection law, and mandatory international data-sharing obligations may require explicit legal authorisation in addition to technical data protection protocols.

### 11.6 Human rights bodies

The Comisión Nacional de los Derechos Humanos (CNDH) and state human rights commissions (*comisiones de derechos humanos*) receive complaints against government bodies for violations of constitutional rights. They issue non-binding recommendations. For IHR-related measures that restrict individual rights, these bodies constitute a parallel accountability channel alongside judicial amparo.

---

## 12. Rules for Legal Anchoring Assessment

*Primary source: `02_country_legal_brains/mexico/mexico_legal_reasoning_rules.md` — NormTrace-IHR v0.1, 2026-05-05.*

### 12.1 Anchoring categories

NormTrace classifies the domestic legal anchoring of each international obligation into one of four categories:

**A. Statutory anchoring** (*anclaje legislativo*): The obligation is grounded in a formal statute — a legal instrument issued by the legislative branch or by the executive in exercise of delegated legislative authority — with sufficient legal force to create competences, obligations, restrictions, procedures, rights, sanctions, or coordination mechanisms. Required when the obligation's content exceeds what can be established through regulatory or administrative instruments.

**B. Regulatory anchoring** (*anclaje reglamentario*): The obligation can be developed through a reglamento, reglamento interior, or NOM, provided that a sufficient statutory basis (*habilitación legal*) exists. Appropriate where the obligation involves technical detail, procedural specification, or operational development of statutory mandates, but does not independently create new competences or rights.

**C. Administrative anchoring** (*anclaje administrativo*): The obligation can be implemented through an acuerdo secretarial, lineamiento, protocol, or operational programme, provided that no new competences are created, no autonomous modification of rights occurs, and the instrument operates strictly within existing legal and regulatory authorisations. Inherently limited: cannot generate binding obligations for third parties, authorise coercive measures, or establish new institutional structures.

**D. Operational implementation only** (*implementación operativa*): The obligation's content is primarily technical or organisational and can be executed within existing attributed competences without any new normative instrument. Includes internal protocol updates, technical coordination among already-authorised actors, and logistical reorganisation within existing mandates.

### 12.2 Anchoring scale

Each obligation assessed by NormTrace receives a score from 0 to 5:

0 — No identifiable anchoring: no provision in Mexican law, at any level, provides even contextual support.  
1 — Indirect contextual anchoring: general or implicit provisions exist but do not directly address the obligation; anchoring is interpretively strained.  
2 — Administrative or operational anchoring only: addressed through administrative instruments without formal statutory or regulatory development; sufficient only for category C or D obligations.  
3 — Partial statutory anchoring: a statutory or regulatory provision exists but significant gaps remain in scope, implementing instruments, or procedural requirements.  
4 — Strong statutory-administrative anchoring: a statutory base plus at least one implementing instrument cover the principal elements; remaining gaps are secondary.  
5 — Integrated implementation anchoring: comprehensively grounded in a coherent statutory-regulatory-administrative framework; gaps, if present, are marginal.

Scores 0–2 must be accompanied by gap type notation. Scores 3–4 must note the principal remaining gap. Human-review flags are never suppressed.

### 12.3 Indicators of statutory or regulatory anchoring requirement

An international health obligation likely requires strong statutory or regulatory anchoring — and cannot be adequately implemented through administrative instruments alone — when any of the following conditions apply:

- It creates duties or competences for national authorities not already authorised by existing law.
- It creates binding obligations for private parties (individuals, legal entities, laboratories, health providers, airlines, port operators, etc.).
- It affects human rights, including the right to health, right to privacy, right to personal liberty, right to free movement, or due process rights.
- It authorises or requires restrictive measures, coercive actions, or the imposition of sanctions.
- It requires the collection, processing, transfer, or storage of personal data or sensitive personal data, as defined under LGPDPPSO.
- It requires mandatory information exchange — including surveillance data, genomic sequences, or epidemiological intelligence — with international organisations, foreign governments, or other national entities.
- It requires formal coordination between the Federation and states or municipalities in a manner that modifies or specifies competence boundaries.
- It requires recurrent budgetary allocation or creates long-term financial commitments under `CPEUM, art. 126`.
- It creates new institutional bodies, new functions, or new competences not currently attributed by law.
- It establishes or requires enforceable procedures involving administrative or judicial oversight.
- It affects travellers, international mobility, quarantine or isolation measures, points of entry (ports, airports, land border crossings), or the rights of persons subject to public health measures.
- It involves laboratories, pathogens, biological specimens, biosafety requirements, export controls, or access and benefit-sharing arrangements related to genetic resources or pathogen samples.

The presence of even one of these conditions indicates a need for statutory or regulatory analysis, regardless of the obligation's apparent operational simplicity.

### 12.4 Indicators of possible administrative sufficiency

An obligation may be adequately addressed through administrative implementation — without new statutory or regulatory instruments — only when all of the following conditions are simultaneously met:

- The obligation is limited to the internal organisation, procedures, or coordination of already-authorised public bodies.
- It does not create new obligations for authorities beyond existing legal authorisations.
- It creates no obligation, restriction, or burden on private parties.
- It does not affect or restrict rights in any manner requiring legal form.
- It falls clearly within existing attributed competences without exceeding them.
- It is implemented through technical protocols or operational guidelines that do not modify the legal status of implementing entities.
- It specifies or develops internal procedures already authorised by statute or regulation, without expanding their scope.
- It organises inter-institutional communication within existing frameworks without modifying competence allocations.

### 12.5 Gap typology

NormTrace uses the following gap types. Multiple types may apply to a single obligation:

*Legal silence*: no provision in Mexican law addresses the subject matter of the obligation, directly or by implication.  
*Competence ambiguity*: it is unclear which authority or level of government holds the legal competence to implement the obligation.  
*Administrative-only anchoring*: the obligation is addressed exclusively through administrative instruments that lack sufficient statutory or regulatory backing.  
*Procedural gap*: a substantive legal base exists, but no enforceable procedure has been established for its implementation.  
*Coordination gap*: no legal mechanism establishes how multiple actors must coordinate for implementation.  
*Federal implementation gap*: implementation requires state or municipal action, but no federal mechanism ensures consistent subnational compliance.  
*Rights-safeguard gap*: the obligation involves measures affecting individual rights without procedural guarantees, substantive limitations, or review mechanisms.  
*Oversight gap*: no mechanism exists for monitoring, auditing, or ensuring accountability for implementation.  
*Budget/capacity gap*: no budgetary allocation or institutional capacity supports implementation.  
*Update-review needed*: a provision exists but is outdated or predates the relevant international instrument.

### 12.6 Mexico-specific caution rules

The following guardrails apply to all NormTrace analyses of Mexican law:

1. Do not infer legal sufficiency solely from the existence of a general enabling provision.
2. Do not assume a NOM can create competences that require statutory or regulatory form.
3. Do not assume that an administrative agreement (*acuerdo*) is equivalent to a legislative mandate.
4. Do not treat administrative practice as strong normative anchoring.
5. Do not conflate federal health authority with state-level implementation capacity.
6. Do not assume that an international obligation is self-executing without reviewing its content and need for domestic development.
7. Flag for human expert review when the obligation involves: rights affected; personal or sensitive personal data; restrictive public health measures; travellers or points of entry; laboratories, pathogens, biological specimens, genomic sequences, or access and benefit-sharing arrangements.

---

## 13. Analytical Implications for IHR and Pandemic Governance

### 13.1 Why the RSI and Pandemic Agreement require legal anchoring analysis

The IHR 2005, its 2024 amendments, and the Pandemic Agreement establish obligations across a broad spectrum: epidemiological surveillance and notification; core capacity requirements at national and subnational levels and at points of entry; National IHR Focal Point designation and operation; health emergency coordination; traveller health measures; laboratory and diagnostic capacity; access and benefit-sharing for pathogen samples and genomic sequences; health product supply chains; data governance; financing; and governance and accountability. These obligations are not uniform in legal character. Some are operational (requiring only internal procedure adjustments); others are legislative (requiring new statutory authority to become operative). NormTrace's function is precisely to classify each obligation within this spectrum.

### 13.2 Why Mexico must be analysed as a federal system

Mexico's federal structure distributes health competences across the Federation, states, and municipalities. An obligation that falls within federal *salubridad general* competence may be formally anchored at the federal level while facing implementation gaps at the state level — due to the absence of consistent state-level legislation, the variable capacity of state health authorities, or the absence of effective federal-state coordination mechanisms. Conversely, an obligation that requires state action (e.g., sub-national core capacity development) may have no direct federal enforcement mechanism to ensure compliance. The federal implementation gap is therefore a structural feature of Mexican health governance, not an aberration.

This means that domestic anchoring analysis for Mexico cannot stop at federal law. A complete assessment requires: (a) the federal statutory and regulatory framework; (b) the federal-state coordination architecture; and (c) the operative capacity and normative framework at subnational level. Only the first of these is fully represented in the current corpus.

### 13.3 Why the focus is not compliance versus non-compliance

The binary of "compliant / non-compliant" is analytically insufficient for the Mexican federal health system, for several reasons: (a) the same obligation may be partially anchored at the statutory level but lack implementing regulations; (b) it may be anchored federally but not at the state level; (c) it may have administrative practice as its only anchor, which is legally insufficient but operationally significant; (d) it may have a formal anchor that predates the relevant international instrument by twenty years (as with the Reglamento de Sanidad Internacional, 1985); or (e) it may be self-executing as a matter of treaty law but lack domestic institutional infrastructure for its operation.

NormTrace replaces the binary with a typology: anchoring category (A–D), anchoring score (0–5), and gap type(s). This allows for differentiated analysis of what specifically is missing — legal, administrative, competential, federal, procedural, budgetary, or oversight gaps — and what type of normative development would address each gap.

### 13.4 Types of gap in health governance

Based on the structural features of Mexican health law described in this profile, gaps in the domestic implementation of international health obligations are expected to fall into the following categories:

*Legal gaps*: obligations for which no statutory provision exists or where existing provisions predate the current international standard and have not been reconciled.  
*Regulatory gaps*: statutory provisions exist but have not been developed in executive regulations or technical standards.  
*Competence gaps*: the locus of authority for implementation is ambiguous, contested, or unassigned between the Federation, states, or specific agencies.  
*Federal implementation gaps*: federal anchoring exists, but no mechanism ensures consistent state or municipal implementation.  
*Procedural gaps*: the substantive obligation is anchored but no enforceable procedure for its exercise has been established.  
*Budget and capacity gaps*: normative anchoring exists but no recurrent budget allocation or institutional infrastructure supports sustained implementation.  
*Oversight gaps*: obligations are nominally anchored but no monitoring, reporting, or accountability mechanism operates.

Each of these gap types requires a different analytical and — eventually — reform-oriented response. Distinguishing between them is the primary analytical output of NormTrace-IHR before any compliance assessment or reform proposal is attempted.

---

## 14. Limitations and Update Protocol

### 14.1 Preliminary status

This profile is version 0.1 — preliminary. It has not been formally validated by legal experts in Mexican constitutional law, health law, international law, or administrative law. It is a structured analytical tool for research purposes. It does not constitute legal advice, a legal opinion, or a definitive determination of any legal question. Nothing in this profile binds any authority, court, or institution.

All anchoring classifications generated by NormTrace using this profile are preliminary analytical classifications. They require expert validation before use in litigation, advocacy, legislative submissions, or policy decisions.

### 14.2 Source reliability

All instruments were converted from official PDF or DOC sources to Markdown. The Cámara de Diputados consolidated texts are informative rather than legally definitive; the Diario Oficial de la Federación is the official source of record. Provisions should be verified against the DOF before any legal coding. Instruments converted from DOC files (MEX-013, MEX-014) contain encoding artefacts and require additional normalisation before automated extraction. Every instrument used should record: date of DOF publication; date of last reform; version date; and date of last consultation.

### 14.3 Update requirements

This profile must be updated when: (a) the CPEUM is amended in provisions relevant to health governance, treaty reception, federalism, or human rights; (b) the LGS or its implementing regulations are reformed; (c) the LOAPF is amended in provisions relevant to the Secretaría de Salud or intersectoral health coordination; (d) relevant NOMs are issued, updated, or cancelled; (e) Mexico ratifies or domestically enacts new international health instruments; (f) SCJN jurisprudence materially alters the interpretation of treaty hierarchy, the scope of *salubridad general*, or the application of *pro persona* to health obligations; or (g) new institutional arrangements modify the distribution of health governance functions.

The profile is not updated for every new administrative instrument or for minor operational changes. Updates are triggered only when the change modifies the general legal architecture described here.

### 14.4 Corpus expansion

The current corpus (16 instruments) is a starting set, not a closed collection. The following categories of instruments are expected to be incorporated in subsequent iterations:

- State-level legislation (state constitutions, state health laws, state NOMs equivalents)
- Additional federal health reglamentos (reglamento interior de la SS — complete text; reglamentos for specific health matters)
- Additional NOMs (border health, laboratory standards, biosafety, food safety, environmental health)
- Acuerdos secretariales and lineamientos
- SCJN jurisprudence (selected tesis and binding jurisprudencia relevant to health governance and treaty hierarchy)
- Federal budget instruments (Presupuesto de Egresos de la Federación; spending rules for health sector)
- Planning instruments (Plan Nacional de Desarrollo; Programa Sectorial de Salud)
- Normativa específica: ports, airports, customs, migration, biosafety laboratory networks, genomic data governance, and export control

### 14.5 Protocol for adding new instruments

Each new source is incorporated into NormTrace through four steps:

1. Markdown file placed in `01_sources/mexico/md/` with a consistent filename (descriptive, lowercase, underscores, no spaces; reform instruments prefixed `reforma_`).
2. Metadata file placed in `01_sources/mexico/metadata/` using the standard YAML template: title, short_title, instrument_type, normative_hierarchy, sector, issuing_authority, publication_date, last_amendment_date, version_date, official_source, source_status, structure_detected, main_internal_units, relevance fields, requires_manual_review, notes.
3. New row added to `03_tables/country_legal_mapping/mexico_normative_corpus_index.csv` with the next sequential `norm_id` (MEX-017, MEX-018, etc.), completing all 25 fields. Use `TBD_REVIEW` for any field that cannot be populated; do not leave fields blank.
4. This profile is updated only if the new instrument modifies the general legal architecture described herein. For instruments that add operational or sectoral detail without changing the structural framework, no profile update is required.

---

*Document status: Preliminary — NormTrace-IHR v0.1*  
*Last updated: 2026-05-05*  
*Corpus version: 16 instruments*  
*Do not cite as legal authority. For methodological and analytical use only.*  
*Sources: CPEUM (MEX-004, last reform 2026-04-23); LGS (MEX-002, last reform 2026-01-15); LSCelTrat (MEX-003, last reform 2025-11-14); LOAPF (MEX-009, last reform 2025-07-16); LFPA (MEX-005, last reform 2025-11-14); LICal (MEX-011, 2020-07-01); LGTAIP (MEX-008, 2025-03-20); LGPDPPSO (MEX-007, last reform 2025-11-14); LFPRH (MEX-006, last reform 2026-04-09); LPlan (MEX-010, last reform 2026-01-15); NOM-017-SSA2-2012 (MEX-012, 2013-02-19); Regl. LGS-SI (MEX-016, 1985, TBD_REVIEW); Regl. LGS-Inv (MEX-015, last reform 2014-04-02); MEX-013 (2023-06-30); MEX-014 (2018-02-07); MEX-001 (2004-09-02).*  
*mexico_legal_document_structure_patterns.md (NormTrace-IHR, 2026-05-05)*  
*mexico_legal_reasoning_rules.md (NormTrace-IHR v0.1, 2026-05-05)*
