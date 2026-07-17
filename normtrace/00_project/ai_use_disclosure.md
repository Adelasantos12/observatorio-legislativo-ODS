# AI Use Disclosure — NormTrace-IHR

**Version:** 0.1.0-pilot  
**Date:** 2026-05-05

---

## 1. Role of AI in this project

Artificial intelligence tools — specifically large language model (LLM) assistants — are used in NormTrace-IHR as **structural and analytical aids**. Their role is to support, not replace, expert legal judgment.

AI is used for the following tasks in this project:

- **Repository and infrastructure structuring:** designing folder organisation, file schemas, and data dictionaries.
- **Preliminary text extraction:** identifying potentially relevant provisions in legal instruments based on search prompts; summarising article content for initial review.
- **Preliminary classification:** assigning tentative anchoring scores and gap type labels based on text review; these are always marked as `preliminary` and flagged for expert validation.
- **Format conversion:** assisting in converting PDF or HTML legal texts to structured Markdown.
- **Drafting analytical notes:** generating first-draft summaries and descriptions that are then reviewed and revised by the human analyst.

---

## 2. What AI does not do in this project

- AI does **not** substitute for expert legal review of national legislation.
- AI does **not** issue legal interpretations with authority.
- AI does **not** determine final scores, classifications, or gap assessments without human review.
- AI outputs do **not** constitute legal advice of any kind.
- AI is **not** used to access or process confidential, personal, or sensitive data.

---

## 3. Traceability requirement

All AI-assisted outputs must meet the traceability standard described in `methodology_note.md`:

> Every row in the mapping tables must be traceable to a specific article and paragraph of the IHR, a specific provision of domestic law, or a note of uncertainty explaining what was searched and why no provision was identified.

AI-generated content that does not meet this standard must be flagged and excluded from outputs until it is verified.

---

## 4. Review and validation

All AI-assisted classifications, scores, and summaries are marked with `review_status: preliminary` until reviewed by a qualified legal expert. The review process is documented in the `03_tables/review_flags/` directory.

No output from this repository should be cited, published, or relied upon for policy or legal purposes without expert validation.

---

## 5. Transparency

This disclosure is published as part of the repository to ensure methodological transparency. Users of NormTrace-IHR outputs are encouraged to read this note and the methodology note before using any data or tables.

---

## 6. Tools used

| Tool | Purpose | Notes |
|---|---|---|
| Claude (Anthropic) | Structural assistance, preliminary extraction, drafting | Used via Cowork mode |

*This table will be updated as additional tools are used.*
