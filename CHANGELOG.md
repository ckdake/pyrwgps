# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-03-02

### Added

- **`download_trip_file(trip_id, file_format)`** — download a trip as a raw file.
  Supports `"gpx"`, `"tcx"`, and `"kml"` formats via the legacy endpoint
  (`GET /trips/{id}.{format}`), which is not yet available in the v1 API.
  Returns raw `bytes` for both API key and OAuth auth methods.

## [0.2.0] - 2026-02-28

### Added

- **OAuth 2.0 support** — `RideWithGPS` now accepts `client_id=` + `client_secret=` to use
  the OAuth 2.0 authorization code flow. Use `authorization_url()` to redirect users and
  `exchange_code()` to obtain an access token. Requests are authenticated with
  `Authorization: Bearer <token>`.
- Both auth methods are supported by the single `RideWithGPS` class; the constructor
  determines the mode based on which credentials are supplied.

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
