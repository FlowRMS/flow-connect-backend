-- Migration: Users from v5 (user.users) to v6 (pyuser.users)
-- Run order: 01
-- Dependencies: None (users are referenced by most other tables)

-- Insert users from v5 to v6
-- v5 schema: user.users (id, username, first_name, last_name, email, enabled, role_id, inside, outside, keycloak_id)
-- v6 schema: pyuser.users (id, username, first_name, last_name, email, auth_provider_id, role, enabled, inside, outside, created_at)

INSERT INTO pyuser.users (
    id,
    username,
    first_name,
    last_name,
    email,
    auth_provider_id,
    role,
    enabled,
    inside,
    outside,
    created_at
)
SELECT
    u.id,
    u.username,
    u.first_name,
    u.last_name,
    u.email,
    u.keycloak_id::varchar,  -- Map keycloak_id to auth_provider_id
    CASE
        WHEN ur.name = 'admin' THEN 1
        WHEN ur.name = 'manager' THEN 2
        WHEN ur.name = 'sales_rep' THEN 3
        ELSE 4  -- Default to regular user
    END AS role,
    u.enabled,
    COALESCE(u.inside, false),
    COALESCE(u.outside, false),
    COALESCE(u.entry_date, now())
FROM "user".users u
LEFT JOIN "user".user_roles ur ON u.role_id = ur.id
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    auth_provider_id = EXCLUDED.auth_provider_id,
    role = EXCLUDED.role,
    enabled = EXCLUDED.enabled,
    inside = EXCLUDED.inside,
    outside = EXCLUDED.outside;
