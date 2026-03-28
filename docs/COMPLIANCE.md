# Compliance Notes

## Traceability (EU AI Act Art. 12)

- Log every AI decision with UTC timestamp, request id (UUID), model, and token estimates.
- Persist logs through the audit pipeline (no PII; use UUIDs only).
- Memory consolidation (AutoDream) must log cycle metadata and line counts.

## Technical Documentation (EU AI Act Art. 11)

- Document reasoning chains for architectural decisions.
- Flag any new AI decision points for mandatory logging.

## Security and Privacy

- Secrets and API keys only via environment variables.
- No shell execution from backend code. Use safe process APIs only where allowed.
- No raw SQL with string interpolation. SQLAlchemy ORM/query builder only.
- Timezone-aware UTC timestamps everywhere.

## Data and Content

- Content versioning is append-only (do not overwrite content rows).
- Use soft-delete via status flags; hard-delete only via admin endpoints.
- All content fields must have _de and _en variants.
