# Webapp Actor Network Derivation Note

**Status:** UI-Derived Supporting Data
**File:** `05_webapp/public/data/derived/actor_network_edges_derived.csv`

## Overview
The actor network displayed in the NormTrace-IHR webapp v0.3 is derived from structural relationships defined in the Mexican legal corpus, specifically:
- **Ley General de Salud (LGS)**
- **Reglamento Interior de la Secretaría de Salud (RI-SS-2025)**
- **Ley Orgánica de la Administración Pública Federal (LOAPF)**

## Derivation Logic
1. **Nodes**: Institutional actors were extracted from `mexico_health_governance_actors_clean.csv`.
2. **Edges**: Relationships (oversight, subordination, coordination) were mapped based on the "competences" and "hierarchy" provisions identified in the corpus.
3. **IHR Areas**: Specific IHR functions (Surveillance, Notification, Points of Entry) were assigned to actors based on the `ihr_relevance` field in the actor profile and the `mexico_ihr2005_mapping_clean.csv`.

## Limitations
- This network represents **statutory/de jure** relationships.
- It does not reflect **de facto** operational coordination or informal networks.
- Coordination edges with non-health sectors (SRE, Customs) are preliminary and based on general administrative mandates.

## Deployment
This file is used by the webapp's Relationship Map view to provide a detailed table of legal bases for institutional links.
