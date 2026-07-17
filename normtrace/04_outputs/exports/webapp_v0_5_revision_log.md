# Webapp v0.5 Revision Log

- **actor relationship map restored**: yes
- **relationship edge source used**: 05_webapp/public/data/derived/actor_network_edges_derived.csv
- **Actor Inventory public labels cleaned**: yes
- **debug data check moved/hidden**: yes (moved to collapsible details section)
- **methodology source deduplicated**: yes
- **callouts rendered correctly**: yes (using custom HTML blocks and Tailwind styling)
- **Mermaid rendered or replaced with workflow cards**: replaced with static CSS/HTML workflow cards
- **tables rendered correctly**: yes (remark-gfm enabled, responsive scrolling added)
- **build result**: success
- **remaining known issues**: none identified in this scope.

## Hotfix (Revision 0.5.1)
- **bug fixed**: ReferenceError: React is not defined in ProvisionsExplorer.tsx
- **fix applied**: added missing `import React` to ProvisionsExplorer.tsx to support `React.Fragment` in production build.
