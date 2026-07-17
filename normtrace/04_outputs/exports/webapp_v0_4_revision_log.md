# NormTrace-IHR Webapp v0.4 Repair Log

- IHR Mapping article/reference join fixed: yes
- IHR 2024 tab added: yes
- Pandemic Agreement/PABS tab added: yes
- Actor Inventory blank-card bug fixed: yes
- actor rows loaded: 18
- actor columns detected: 14 expected canonical columns
- Country Snapshot redesigned: yes
- raw Markdown snapshot hidden/collapsed: yes
- printable report route created: yes (`/report/print`)
- dark template-style blocks removed: yes (snapshot/mapping/actors refresh)
- build result: SUCCESS (`npm run build`)
- remaining known issues: large JS chunk warning (>500kB) from Vite; no Mermaid rendering plugin in current build; report print currently summarizes selected core sections without CSV download exposure.
