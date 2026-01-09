-- Migration: Users from v4 (public.users) to v6 (pyuser.users)
-- Run order: 01
-- Dependencies: None (users are referenced by most other tables)

-- v4 schema: public.users (id, username, email, firstname, lastname, is_outside, is_inside, status, fullname, keycloak_role, session_id)
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
    u.firstname,
    u.lastname,
    u.email,
    NULL,  -- No auth_provider_id in v4
    CASE
        WHEN u.keycloak_role = 1 THEN 1  -- admin
        WHEN u.keycloak_role = 2 THEN 2  -- manager
        WHEN u.keycloak_role = 3 THEN 3  -- sales_rep
        ELSE 4  -- Default to regular user
    END AS role,
    COALESCE(u.status, true),
    COALESCE(u.is_inside, false),
    COALESCE(u.is_outside, false),
    now()
FROM public.users u
ON CONFLICT (id) DO UPDATE SET
    username = EXCLUDED.username,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    role = EXCLUDED.role,
    enabled = EXCLUDED.enabled,
    inside = EXCLUDED.inside,
    outside = EXCLUDED.outside;
