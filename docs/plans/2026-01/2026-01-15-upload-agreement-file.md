# Upload Agreement File

- **Status**: ✅ Complete
- **Created**: 2026-01-15 21:30 -03
- **Approved**: 2026-01-16 09:15 -03
- **Finished**: 2026-01-16 18:27 -03
- **Commit Prefix**: Agreement Upload

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: Infrastructure](#phase-1-infrastructure)
3. [Phase 2: Database Schema](#phase-2-database-schema)
4. [Phase 3: Repository Layer](#phase-3-repository-layer)
5. [Phase 4: Service Layer](#phase-4-service-layer)
6. [Phase 5: GraphQL Layer](#phase-5-graphql-layer)
7. [Phase 6: Run Migration](#phase-6-run-migration)
8. [Phase 7: Manual Testing](#phase-7-manual-testing)
9. [Bugfixes During Testing](#bugfixes-during-testing)
10. [Critical Files](#critical-files)

---

## Overview

Add mutations to manage agreement files for connections. The `uploadAgreement` mutation uploads a PDF file to S3 and stores the reference in a new database table. The `deleteAgreement` mutation removes the file from S3 and the database. Each agreement is associated with a connection between the user's organization and a connected organization.

### Requirements

| Requirement | Details |
|-------------|---------|
| Mutations | `uploadAgreement(connectedOrgId: ID!, file: Upload!) -> AgreementResponse!` |
| | `deleteAgreement(connectedOrgId: ID!) -> Boolean!` |
| File Storage | AWS S3 bucket |
| Database | New `connect_pos` schema with `agreements` table |
| Constraint | One agreement per connected_org_id (tenant isolation is implicit) |
| Multitenancy | Schema/table created in all tenant databases |

### Business Rules

- Agreement is tied to connection relationship (tenant → connected org)
- All users in an organization see the same agreement for a connected org
- `connected_org_id` is the UUID from the remote `subscription.orgs` table
- If an agreement already exists, uploading replaces the previous file
- Tenant isolation is implicit (table exists per tenant database)
- Only connections with `connectionStatus: ACCEPTED` can have agreements
- Agreements can be deleted (removes from S3 and database)

### Architecture

```
GraphQL Mutation (uploadAgreement)
    │
    ▼
AgreementService
    │
    ├──────────────────┐
    ▼                  ▼
AgreementRepository    S3Service
(PostgreSQL)           (AWS S3)
```

### Data Flow

```
1. User uploads PDF → Mutation receives file
2. Validate connected org exists and user has connection
3. Upload file to S3 → get s3_key
4. Upsert agreement record (replace if exists)
5. Return AgreementResponse with presigned URL
```

---

## Phase 1: Infrastructure

_Add S3 configuration and provider._

### 1.1 GREEN: Create S3Settings ✅

**File**: [`app/core/s3/settings.py`](../../app/core/s3/settings.py)

**Data structure**:
- `aws_access_key_id: str`
- `aws_secret_access_key: str`
- `aws_endpoint_url: str` (default: `https://nyc3.digitaloceanspaces.com`)
- `aws_bucket_name: str` (default: `flowrms-connect`)
- `aws_default_region: str` (default: `nyc3`)

Follow `WorkOSSettings` pattern with `SettingsConfigDict`.

### 1.2 GREEN: Create S3 provider ✅

**File**: [`app/core/s3/provider.py`](../../app/core/s3/provider.py)

**Function**: `create_s3_service(settings: S3Settings, auth_info: AuthInfo) -> S3Service`
- Use `commons.s3.service.S3Service`
- Pass `tenant_name` from `auth_info` for S3 key namespacing

**Provider**: `aioinject.Scoped(create_s3_service)`

### 1.3 GREEN: Register S3 in container ✅

**File**: [`app/core/providers.py`](../../app/core/providers.py)

- Add `S3Settings` from `app.core.s3.settings` to `settings_classes`
- Add `app.core.s3.provider` to `modules`

### 1.4 VERIFY: Run `task all` ✅

---

## Phase 2: Database Schema

_Create the connect_pos schema and agreements table._

### 2.1 GREEN: Create PyConnectPosBaseModel ✅

**File**: [`app/core/db/base_models.py`](../../app/core/db/base_models.py)

Create a base model class `PyConnectPosBaseModel` that inherits from `BaseModel` and sets the schema to `connect_pos` via `__table_args__`.

Models using this base should also extend `HasCreatedBy` and `HasCreatedAt` mixins (from `commons.db.v6.base`) following the Factory model pattern.

### 2.2 GREEN: Create Agreement model ✅

**File**: [`app/graphql/pos/models/agreement.py`](../../app/graphql/pos/models/agreement.py)

**Table**: `connect_pos.agreements`

**Inherits from**: `PyConnectPosBaseModel`, `HasCreatedBy`, `HasCreatedAt`

**Fields from mixins**:
- `id: UUID` - Primary key (from BaseModel)
- `created_by_id: UUID` - Foreign key to User (from HasCreatedBy)
- `created_at: TIMESTAMP(tz)` - Not null, default now (from HasCreatedAt)

**Fields to define**:
- `connected_org_id: UUID` - Not null
- `s3_key: String(500)` - Not null
- `file_name: String(255)` - Not null
- `file_size: Integer` - Not null
- `file_sha: String(64)` - Not null

**Constraints**:
- Unique: `connected_org_id`

### 2.3 GREEN: Create Alembic migration ✅

**File**: [`alembic/versions/20260116_create_connect_pos_schema.py`](../../alembic/versions/20260116_create_connect_pos_schema.py)

Migration should:
1. Create `connect_pos` schema if not exists
2. Create `agreements` table with all fields
3. Create unique constraint on `connected_org_id`

**IMPORTANT**: Only create the migration file. Do NOT run `alembic upgrade`.

### 2.4 VERIFY: Run `task all` ✅

---

## Phase 3: Repository Layer

_Create repository for agreement CRUD operations._

### 3.1 RED: Write failing tests for AgreementRepository ✅

**File**: [`tests/graphql/pos/test_agreement_repository.py`](../../tests/graphql/pos/test_agreement_repository.py)

**Test scenarios**:
- `test_create_agreement_success` - Creates new agreement record
- `test_get_by_connected_org_id_found` - Retrieves existing agreement
- `test_get_by_connected_org_id_not_found` - Returns None when no agreement exists
- `test_upsert_creates_when_not_exists` - Insert on first upload
- `test_upsert_updates_when_exists` - Update on subsequent upload
- `test_delete_existing_agreement` - Deletes agreement record
- `test_delete_nonexistent_returns_false` - Returns False when no agreement exists

### 3.2 GREEN: Implement AgreementRepository ✅

**File**: [`app/graphql/pos/repositories/agreement_repository.py`](../../app/graphql/pos/repositories/agreement_repository.py)

**Class**: `AgreementRepository`

**Constructor**:
- `session: AsyncSession`

**Methods**:
- `async def create(self, agreement: Agreement) -> Agreement`
- `async def get_by_connected_org_id(self, connected_org_id: UUID) -> Agreement | None`
- `async def upsert(self, agreement: Agreement) -> Agreement` - Uses PostgreSQL ON CONFLICT
- `async def delete(self, connected_org_id: UUID) -> bool` - Returns True if deleted, False if not found

### 3.3 REFACTOR: Clean up and ensure type safety ✅

### 3.4 VERIFY: Run `task all` ✅

---

## Phase 4: Service Layer

_Create service that orchestrates S3 upload and database storage with error handling._

### 4.1 GREEN: Create custom exceptions ✅

**File**: [`app/graphql/pos/exceptions.py`](../../app/graphql/pos/exceptions.py)

**Exceptions**:
- `AgreementError` - Base exception for agreement operations
- `S3ConnectionError(AgreementError)` - S3 connection failed
- `S3UploadError(AgreementError)` - S3 upload failed
- `AgreementNotFoundError(AgreementError)` - Agreement not found for deletion
- `ConnectionNotAcceptedError(AgreementError)` - Connection status is not ACCEPTED

### 4.2 RED: Write failing tests for AgreementService ✅

**File**: [`tests/graphql/pos/test_agreement_service.py`](../../tests/graphql/pos/test_agreement_service.py)

**Test scenarios**:
- `test_upload_creates_new_agreement` - First upload for connection
- `test_upload_replaces_existing_agreement` - Subsequent upload with different filename deletes old S3 file
- `test_upload_stores_file_in_s3` - Verifies S3 upload called with correct params
- `test_upload_fails_when_connection_not_accepted` - Raises ConnectionNotAcceptedError
- `test_upload_raises_s3_error_on_connection_failure` - Wraps S3 connection errors
- `test_upload_raises_s3_error_on_upload_failure` - Wraps S3 upload errors
- `test_get_presigned_url_returns_valid_url` - Generates URL for download
- `test_delete_removes_from_s3_and_db` - Deletes from both S3 and database
- `test_delete_raises_not_found_error` - Raises AgreementNotFoundError when not exists

### 4.3 GREEN: Implement AgreementService ✅

**File**: [`app/graphql/pos/services/agreement_service.py`](../../app/graphql/pos/services/agreement_service.py)

**Class**: `AgreementService`

**Constructor**:
- `repository: AgreementRepository`
- `s3_service: S3Service`
- `connection_repository: ConnectionRepository` - To validate connection status
- `auth_info: AuthInfo`

**Methods**:
- `async def upload_agreement(self, connected_org_id: UUID, file_content: bytes, file_name: str) -> Agreement`
  1. Validate connection status is ACCEPTED (raise `ConnectionNotAcceptedError` if not)
  2. Check if agreement already exists
  3. Generate S3 key: `agreements/{connected_org_id}/{filename}`
  4. **If existing agreement has different S3 key, delete old S3 file** (prevents orphaned files)
  5. Upload new file to S3 (wrap errors in `S3UploadError`)
  6. Calculate file SHA and size
  7. Upsert agreement record
  8. Return agreement

- `async def _delete_s3_object(self, s3_key: str) -> None` (private helper)
  - Delete object from S3 using underlying client
  - Used by both `upload_agreement` (file replacement) and `delete_agreement`

- `async def get_agreement(self, connected_org_id: UUID) -> Agreement | None`
  - Query repository by connected_org_id

- `async def get_presigned_url(self, agreement: Agreement) -> str`
  - Generate presigned URL from S3 service

- `async def delete_agreement(self, connected_org_id: UUID) -> None`
  1. Get existing agreement (raise `AgreementNotFoundError` if not found)
  2. Delete from S3
  3. Delete from database

### 4.4 REFACTOR: Clean up and ensure type safety ✅

### 4.5 VERIFY: Run `task all` ✅

---

## Phase 5: GraphQL Layer

_Add mutations, response types, and update OrganizationLiteResponse._

### 5.1 GREEN: Create AgreementResponse type ✅

**File**: [`app/graphql/pos/strawberry/agreement_response.py`](../../app/graphql/pos/strawberry/agreement_response.py)

**Type**: `AgreementResponse`

**Fields**:
- `id: strawberry.ID`
- `connected_org_id: strawberry.ID`
- `file_name: str`
- `file_size: int`
- `presigned_url: str`
- `created_at: datetime`

**Class method**: `from_model(agreement: Agreement, presigned_url: str) -> AgreementResponse`

### 5.2 GREEN: Create AgreementMutations ✅

**File**: [`app/graphql/pos/mutations/agreement_mutations.py`](../../app/graphql/pos/mutations/agreement_mutations.py)

**Class**: `AgreementMutations`

**Mutations**:
- `upload_agreement(connected_org_id: ID!, file: Upload!) -> AgreementResponse!`
- `delete_agreement(connected_org_id: ID!) -> Boolean!`

### 5.3 GREEN: Update OrganizationLiteResponse ✅

**File**: [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py)

Add optional `agreement: AgreementResponse | None` field to `OrganizationLiteResponse`.

The agreement field should only be populated when `connectionStatus == ACCEPTED`. Update the resolver/factory method to fetch agreement data when applicable.

**Also updated**: [`app/graphql/organizations/services/manufacturer_service.py`](../../app/graphql/organizations/services/manufacturer_service.py) to fetch agreements for ACCEPTED connections.

### 5.4 GREEN: Update schema to include mutations ✅

**File**: [`app/graphql/schemas/schema.py`](../../app/graphql/schemas/schema.py)

Make `Mutation` inherit from both `ConnectionMutations` and `AgreementMutations`.

### 5.5 GREEN: Register POS providers ✅

**File**: [`app/graphql/di/repository_providers.py`](../../app/graphql/di/repository_providers.py)

Add `app.graphql.pos` to discovered modules.

**File**: [`app/graphql/di/service_providers.py`](../../app/graphql/di/service_providers.py)

Add `app.graphql.pos` to discovered modules.

### 5.6 GREEN: Generate GraphQL schema ✅

Run: `task gql`

### 5.7 VERIFY: Run `task all` ✅

---

## Phase 6: Run Migration

_Apply database migration to all tenant databases before manual testing._

### 6.1 Run multi-tenant migration ✅

**⚠️ REMINDER**: This is a multi-tenant system. The migration must be applied to ALL tenant databases using the `run_migrations.py` script (not `alembic upgrade head`).

```bash
python run_migrations.py --env dev
```

**How it works**:
1. Loads all active tenants from the central `tenants` table in the base database
2. For each tenant that needs migration (where `alembic_version` is behind):
   - Connects to the tenant's database
   - Creates the `connect_pos` schema if it doesn't exist
   - Creates the `agreements` table
   - Updates the tenant's `alembic_version` in the base database
3. Processes tenants in parallel (chunks of 2)

**For other environments**:
- Staging: `python run_migrations.py --env staging`
- Production: `python run_migrations.py --env prod`

This step must be done by the user (Claude cannot run database migrations).

---

## Phase 7: Manual Testing

_Manual testing in GraphQL Playground._

### 7.1 Test mutations

**Upload Agreement**:
```graphql
mutation UploadAgreement($file: Upload!) {
  uploadAgreement(
    connectedOrgId: "9133da7c-3b98-4673-91dc-0dc58cc8740c"
    file: $file
  ) {
    id
    fileName
    fileSize
    presignedUrl
    createdAt
  }
}
```

**Delete Agreement**:
```graphql
mutation DeleteAgreement {
  deleteAgreement(connectedOrgId: "9133da7c-3b98-4673-91dc-0dc58cc8740c")
}
```

**Query Organization with Agreement**:
```graphql
query GetConnections {
  connections {
    id
    connectionStatus
    agreement {
      id
      fileName
      presignedUrl
    }
  }
}
```

**Test cases**:
1. ✅ Upload to ACCEPTED connection → Creates new agreement
2. ✅ Upload to non-ACCEPTED connection → Returns error
3. ✅ Second upload (same connection) → Replaces agreement
4. ✅ Different connected org → Creates separate agreement
5. ✅ Download via presigned URL → File accessible
6. ✅ Delete agreement → Removes from S3 and database
7. ✅ Query connections → Shows agreement only for ACCEPTED connections

---

## Bugfixes During Testing

_Issues discovered and fixed during Phase 7 manual testing._

### BF-1: ConnectionStatus enum mismatch ✅

**Problem**: Our enum had `ACCEPTED = "accepted"` but remote DB uses `"active"`.

**File**: [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py)

**Fix**: Changed to `ACCEPTED = "active"` with comment explaining the mapping.

### BF-2: User org UUID lookup ✅

**Problem**: `auth_info.tenant_id` contains WorkOS org_id format (`org_01KEE...`), not a UUID. Using `uuid.UUID(auth_info.tenant_id)` failed with "badly formed hexadecimal UUID string".

**Files**:
- [`app/graphql/pos/services/agreement_service.py`](../../app/graphql/pos/services/agreement_service.py) - Added `user_org_repository` dependency
- [`tests/graphql/pos/test_agreement_service.py`](../../tests/graphql/pos/test_agreement_service.py) - Added mock for new dependency

**Fix**: Use `UserOrgRepository.get_user_org_id(auth_provider_id)` to look up the actual org UUID.

### BF-3: ManufacturerService test fixtures ✅

**Problem**: Phase 5 added `agreement_service` to `ManufacturerService` constructor, but tests were missing the mock.

**File**: [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py)

**Fix**: Added `mock_agreement_service` fixture.

### BF-4: Tenant resolution mismatch ✅

**Problem**: Database queries fail with "table not found" errors even though the migration ran successfully and the table exists.

**Root cause**: WorkOS JWT authentication sets `auth_info.tenant_name` from the JWT's `org_name` field (e.g., "Flow"), but the `MultiTenantController` stores database engines keyed by `tenant.url` (e.g., "app"). When the middleware calls `scoped_session("Flow")`, it looks for `engine["Flow"]` but the engine is stored as `engine["app"]`.

**File**: [`app/core/middleware/graphql_middleware.py`](../../app/core/middleware/graphql_middleware.py)

**Fix**: Added `_resolve_tenant_url()` helper function that:
1. After `Context.set_context()` returns, checks if `auth_info.tenant_id` is set (WorkOS org_id)
2. Queries the `tenants` table: `SELECT url FROM tenants WHERE org_id = :org_id`
3. Updates `auth_info.tenant_name` with the tenant's `url` field
4. This ensures `MultiTenantController` uses the correct engine key

**Note**: This fix does not require modifying the `commons` package.

### BF-5: TenantSession type disambiguation ✅

**Problem**: After BF-4, queries still failed with "table not found" despite tenant resolution logging correctly. The aioinject container was injecting the wrong database session.

**Root cause**: The system has two database contexts:
- **ORGS_DB_URL**: Central database with `subscription.orgs` table
- **Multi-tenant DBs**: Per-tenant databases with `connect_pos.agreements` table

Both `create_session()` and `create_orgs_session()` returned `AsyncSession`, causing aioinject to use the first registered provider (orgs session) instead of the tenant session.

**Files**:
- [`app/core/db/transient_session.py`](../../app/core/db/transient_session.py) - Added `TenantSession` marker class
- [`app/core/db/db_provider.py`](../../app/core/db/db_provider.py) - Changed return type to `TenantSession`
- [`app/graphql/pos/repositories/agreement_repository.py`](../../app/graphql/pos/repositories/agreement_repository.py) - Changed dependency to `TenantSession`

**Fix**: Created `TenantSession(AsyncSession)` marker class to disambiguate tenant sessions from orgs sessions in dependency injection.

### BF-6: Remove FK constraint on created_by_id ✅

**Problem**: Upload mutation failed with FK constraint violation: `insert or update on table "agreements" violates foreign key constraint "agreements_created_by_id_fkey"`.

**Root cause**: The `created_by_id` column references `pyuser.users.id`, but users uploading agreements may not exist in the tenant's local users table (they exist in the central orgs database).

**File**: [`alembic/versions/20260116_create_connect_pos_schema.py`](../../alembic/versions/20260116_create_connect_pos_schema.py)

**Fix**: Removed the FK constraint from the original migration file. The column is kept for auditing purposes but without the cross-database FK reference.

### BF-VERIFY: Run `task all` ✅

---

## Critical Files

| File | Purpose | Status |
|------|---------|--------|
| [`app/core/s3/settings.py`](../../app/core/s3/settings.py) | S3 configuration | ✅ |
| [`app/core/s3/provider.py`](../../app/core/s3/provider.py) | S3Service DI provider | ✅ |
| [`app/core/db/base_models.py`](../../app/core/db/base_models.py) | PyConnectPosBaseModel | ✅ |
| [`app/graphql/pos/models/agreement.py`](../../app/graphql/pos/models/agreement.py) | Agreement SQLAlchemy model | ✅ |
| [`app/graphql/pos/exceptions.py`](../../app/graphql/pos/exceptions.py) | Custom exceptions | ✅ |
| [`alembic/versions/20260116_create_connect_pos_schema.py`](../../alembic/versions/20260116_create_connect_pos_schema.py) | Database migration | ✅ |
| [`app/graphql/pos/repositories/agreement_repository.py`](../../app/graphql/pos/repositories/agreement_repository.py) | Data access layer | ✅ |
| [`app/graphql/pos/services/agreement_service.py`](../../app/graphql/pos/services/agreement_service.py) | Business logic | ✅ |
| [`app/graphql/pos/strawberry/agreement_response.py`](../../app/graphql/pos/strawberry/agreement_response.py) | GraphQL response type | ✅ |
| [`app/graphql/pos/mutations/agreement_mutations.py`](../../app/graphql/pos/mutations/agreement_mutations.py) | GraphQL mutations | ✅ |
| [`app/graphql/organizations/strawberry/organization_types.py`](../../app/graphql/organizations/strawberry/organization_types.py) | Updated with agreement field | ✅ |
| [`tests/graphql/pos/test_agreement_repository.py`](../../tests/graphql/pos/test_agreement_repository.py) | Repository tests | ✅ |
| [`tests/graphql/pos/test_agreement_service.py`](../../tests/graphql/pos/test_agreement_service.py) | Service tests | ✅ |
| [`app/core/db/transient_session.py`](../../app/core/db/transient_session.py) | TenantSession marker class (BF-5) | ✅ |
| [`app/core/middleware/graphql_middleware.py`](../../app/core/middleware/graphql_middleware.py) | Tenant resolution fix (BF-4) | ✅ |
| [`app/graphql/connections/models/enums.py`](../../app/graphql/connections/models/enums.py) | ConnectionStatus enum fix (BF-1) | ✅ |
| [`tests/graphql/organizations/test_manufacturer_service.py`](../../tests/graphql/organizations/test_manufacturer_service.py) | ManufacturerService test fixtures (BF-3) | ✅ |

---

## Notes

### S3 Key Structure

Files are stored with tenant isolation:
```
{tenant_name}/agreements/{connected_org_id}/{filename}
```

The `tenant_name` prefix is automatically added by `S3Service.get_full_key()`. Since each tenant has its own database and S3 namespace, `user_org_id` is not needed in the path.

### Why Upsert?

Using PostgreSQL's `ON CONFLICT` upsert pattern on `connected_org_id` ensures:
1. Atomic operation (no race conditions)
2. Simple API (one method for create/update)
3. Replaces old file reference when uploading new

### Connected Org ID

The `connected_org_id` is a UUID from the remote `subscription.orgs` table. This is the organization that the user's organization is connected with. We use this ID directly since connections are already validated in the connections package.

### Multi-Tenant Schema Isolation

**Important**: This project shares tenant databases with `flow-py-backend`. To avoid migration conflicts, each application uses a separate schema for Alembic version tracking:

| Application | Version Table Schema | Feature Schemas |
|-------------|---------------------|-----------------|
| flow-py-backend | `public` | `public.*` |
| flow-py-connect | `connect` | `connect_pos`, `connect_*` |

This is configured in `alembic.ini`:
```ini
version_table_schema = connect
version_table = alembic_version
```

The `connect` schema is created automatically by `alembic/env.py` before any migrations run. Feature tables go in their own schemas (e.g., `connect_pos.agreements`).

---

## Results

| Metric | Value |
|--------|-------|
| Duration | ~21 hours (elapsed) |
| Phases | 7 |
| Bugfixes | 6 |
| Files Modified | 17 |
| Tests Added | 2 test files (14 test cases) |