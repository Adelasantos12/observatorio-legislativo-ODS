# Conversion log - Reglamento Interior de la Secretaría de Salud 2025

## Source converted

- `C_Reglamento_Interior_Secretaria_de_Salud.pdf`

## Outputs generated

- Markdown: `01_sources/domestic_legal_frameworks/mexico/md/mexico_reglamento_interior_secretaria_salud_2025.md`
- Metadata: `01_sources/domestic_legal_frameworks/mexico/metadata/mexico_reglamento_interior_secretaria_salud_2025_metadata.yml`

## Conversion method

- Extracted text from PDF using PyMuPDF.
- Removed recurring Diario Oficial page headers where detected.
- Preserved legal structure, including decree language, chapters, articles, roman-numeral clauses, alphabetic incisos, and transitory provisions.
- Inserted HTML page markers in the Markdown file: `<!-- Page X -->`.
- Converted `CAPÍTULO` headings to Markdown level 2 and `Artículo` headings to Markdown level 3.

## Extraction issues and manual review

- The source has 62 pages.
- The document is mostly structured as dense legal text with enumerated legal competences.
- No extraction-time table reconstruction was required.
- Manual legal validation is recommended for: long enumerated articles, cross-references, transitory provisions, and possible line-break artifacts from the Diario Oficial PDF layout.

## Pages flagged for manual review

- Page 19: annex reference.
- Page 43: annex reference.
- Page 47: transitory provisions.
- Page 62: transitory provisions.

## Repository placement

Intended repository root:

`/Users/adelasantos/Documents/NormTrace-IHR`

Copy the generated folders into that repository preserving the internal paths.
