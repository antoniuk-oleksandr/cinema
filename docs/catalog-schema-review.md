# Catalog schema review

This document describes the proposed first schema only. No migration has been
generated or applied yet.

## Schema rollout

The schema will grow incrementally as each domain is implemented. Django will
generate the numbered migration files automatically; migration numbers are not
planned or maintained manually in advance.

The expected domain order is:

1. Catalog
2. Screenings and seats
3. Booking holds
4. Carts, orders, and payments

Only the Django models for the catalog are prepared currently. The later
domains must not be added until their lifecycle and transactional boundaries
are reviewed.

## Current type and constraint decisions

- Django's `BigAutoField` is the default primary-key type, producing PostgreSQL `BIGINT` keys.
- Human-readable names use bounded `VARCHAR` columns through Django `CharField(max_length=...)`.
- Movie ratings use a bounded enum-like `TextChoices` field.
- Movie duration and release year use positive small integer fields.
- Movie-to-reference relationships use Django many-to-many tables with foreign keys and unique pairs.
- Foreign keys use `PROTECT` for shared catalog reference data such as languages.
- Slugs and reference names are unique.
- Indexes cover common movie filtering and person/name lookup paths; query profiling should guide later indexes.

## Before generating `0001_initial_catalog`

Review the model names, maximum lengths, deletion behavior, rating values,
year/duration validation, and expected search patterns. After approval:

```bash
just makemigrations
just migrate-check
```

Do not run `just migrate` until the generated migration has been reviewed.
