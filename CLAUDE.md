# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Pyramid web service that acts as a JSON middleware between external scanners/clients and iMio's DMS (Document Management System). It receives document metadata and files via HTTP, validates them against versioned JSON schemas, stores records in PostgreSQL, and publishes messages to RabbitMQ for async processing by backend handlers.

## Build & Development

Uses zc.buildout (Python 2.7 virtualenv). Dependencies are checked out via mr.developer into `devel/` (imio.dataexchange.core, imio.dataexchange.db, imio.amqp).

```bash
# Bootstrap (creates virtualenv + installs buildout)
make bootstrap

# Run buildout (installs all eggs, generates bin/ scripts)
make buildout

# Start dev services (PostgreSQL on 5433, PostgreSQL test on 5432, RabbitMQ on 5672)
docker compose -f docker-compose-dev.yaml up

# Run the dev server (port 6543)
bin/pserve development.ini
```

## Testing

Tests require the `postgres_test` Docker service running (PostgreSQL on port 5432, database `test`). Test config is in `imiowebservicejson/test.ini`.

```bash
# Run all tests
bin/py.test

# Run a single test file
bin/py.test imiowebservicejson/tests/test_schema.py

# Run a single test
bin/py.test imiowebservicejson/tests/test_schema.py::TestClassName::test_method

# Run with coverage
bin/test-coverage
```

The `conftest.py` at `imiowebservicejson/conftest.py` sets up the test database session automatically.

## Architecture

### Request Flow

1. **Authentication**: HTTP Basic Auth checked against credentials in `.ini` config (`auth.login`, `auth.password`, `auth.secret`). Salt-based MD5 hashing in `authentication.py`.

2. **Two API styles coexist**:
   - **Legacy views** (`views/dms.py`, `views/file.py`): Pyramid `@view_config` with custom decorators for JSON schema validation, exception handling, and logging (`views/base.py`).
   - **Cornice services** (`views/request.py`, `views/router.py`, `views/openapi.py`): Use Cornice `Service` with Colander schemas for validation and auto-generated OpenAPI spec at `/__api__`.

3. **JSON Schema Validation** (legacy path): Schemas live in `imiowebservicejson/schema/{name}/{version}/in.json` and `out.json`. The `@json_validator` decorator loads the schema by name+version from the URL, validates input, then creates a Warlock model instance.

4. **Versioned Subscriber Validators**: Pyramid event subscribers on `ValidatorEvent` perform business-rule validation (date formats, uniqueness, external_id structure). The `version` predicate on subscribers (e.g., `version=">=1.2"`) enables version-gated validation rules. Predicates are in `predicates.py`.

5. **File Upload**: `FileUpload` class handles multipart upload → temp file → validation → move to blob storage path (`dms.storage.path` setting). Blob path is derived from zero-padded file ID split into 2-char directory segments.

6. **Async Processing**: POST to `/request` publishes messages to RabbitMQ (`ws.request.read` or `ws.request.write` queues). Background console scripts (`scripts/requesthandler.py`, `scripts/documentpublisher.py`, `scripts/requesterror.py`, `scripts/cleanup.py`) consume and process these messages.

### Key Patterns

- **Warlock models** (`models/base.py`, `models/dms_metadata.py`): Generated from JSON schemas at runtime via `warlock.model_factory`. `DMSMetadata` adds domain logic (client_id parsing, document type codes).
- **Zope interfaces** (`interfaces.py`): `IDMSMetadata`, `IFileUpload`, `IValidatorEvent` used by the `implement` subscriber predicate to dispatch validators to the correct model type.
- **Database**: All ORM mappers come from `imio.dataexchange.db` (File, Request, Router tables). `DBSession` is the global scoped session.

### Routes

| Route | View | Purpose |
|---|---|---|
| `/dms_metadata/{id}/{version}` | `views/dms.py` | Submit document metadata |
| `/file_upload/{version}/{id}` | `views/dms.py` | Upload file for a metadata record |
| `/file_upload/{id}` | `views/dms.py` | Upload file (defaults to v1.0) |
| `/file/{client_id}/{external_id}` | `views/file.py` | Get latest file |
| `/file/{client_id}/{external_id}/{version}` | `views/file.py` | Get file by version |
| `/request` (POST/GET) | `views/request.py` | Submit/poll async requests |
| `/router` (POST/PATCH) | `views/router.py` | Register/update app routes |
| `/route/{client_id}/{application_id}` | `views/router.py` | Get/delete a route |
| `/route/{client_id}` | `views/router.py` | Discover routes for a client |
| `/__api__` | `views/openapi.py` | OpenAPI spec (Cornice services only) |

### Console Scripts

Defined as entry points in `setup.py`, built by buildout into `bin/`:
- `document_publisher` — publishes documents to target applications
- `request_read_handler` / `request_write_handler` — consume RabbitMQ messages
- `request_error_handler` — handles failed requests
- `file_cleanup` — removes orphaned files
