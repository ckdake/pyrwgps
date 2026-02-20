# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-20

First release tracked in this changelog.

### Added

- **v1 API authentication** — `authenticate()` now uses `POST /api/v1/auth_tokens.json`
  with email, password, and API key (no OAuth required). The returned token works for
  both v1 and legacy endpoints.
- **v1 API support** — all HTTP methods (`get`, `post`, `put`, `patch`, `delete`, `list`)
  work against `/api/v1/` endpoints with automatic `page`/`page_size` pagination.
  Initial v1 coverage includes: Trips, Routes, Collections, Events, Club Members,
  Points of Interest, Sync, and Users.
- **Dual pagination** — `list()` detects v1 vs legacy endpoints automatically and applies
  the correct pagination strategy (`page`/`page_size` for v1; `offset`/`limit` for legacy).
