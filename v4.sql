--
-- PostgreSQL database dump
--

\restrict nUTjWcTDM7VExUVh7WPvGUvIfItvpJirBAbNGZqCne7HHkpAXA682qzQ1NJP1g9

-- Dumped from database version 15.15
-- Dumped by pg_dump version 17.7 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: aiven_extras; Type: SCHEMA; Schema: -; Owner: doadmin
--

CREATE SCHEMA aiven_extras;


ALTER SCHEMA aiven_extras OWNER TO doadmin;

--
-- Name: aiven_extras; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS aiven_extras WITH SCHEMA aiven_extras;


--
-- Name: EXTENSION aiven_extras; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION aiven_extras IS 'aiven_extras';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: postgres_fdw; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgres_fdw WITH SCHEMA public;


--
-- Name: EXTENSION postgres_fdw; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgres_fdw IS 'foreign-data wrapper for remote PostgreSQL servers';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: audit_trigger_func(); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.audit_trigger_func() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
                BEGIN
                    EXECUTE format('INSERT INTO %I (uuid, timestamp, operation, changed_data)
                                VALUES ($1, $2, $3, $4)', TG_ARGV[0])
                        USING
                        CASE TG_OP
                            WHEN 'INSERT' THEN NEW.uuid
                            WHEN 'UPDATE' THEN NEW.uuid
                            WHEN 'DELETE' THEN OLD.uuid
                        END,
                        current_timestamp,
                        CASE TG_OP
                            WHEN 'INSERT' THEN 'create'
                            WHEN 'UPDATE' THEN 'update'
                            WHEN 'DELETE' THEN 'delete'
                        END,
                        CASE TG_OP
                            WHEN 'INSERT' THEN jsonb_build_object('new', row_to_json(NEW.*))
                            WHEN 'UPDATE' THEN jsonb_build_object('old', row_to_json(OLD.*), 'new', row_to_json(NEW.*))
                            WHEN 'DELETE' THEN jsonb_build_object('old', row_to_json(OLD.*))
                        END;
                    RETURN NULL;
                END;
            $_$;


ALTER FUNCTION public.audit_trigger_func() OWNER TO springuser;

--
-- Name: bulk_order_detail_info(json[]); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.bulk_order_detail_info(order_details json[]) RETURNS TABLE(orderdetailid integer, orderid integer, itemnumber integer, productid integer, originalquery json)
    LANGUAGE plpgsql
    AS $$
        BEGIN
            -- Create temporary table
            CREATE TEMP TABLE IF NOT EXISTS tmp_table (
                insertion_order serial PRIMARY KEY,
                order_number character varying(255 ),
                part_number character varying(255 ),
                quantity integer,
                unit_price real,
                item_number integer
            );
        INSERT INTO tmp_table (order_number, part_number, quantity, unit_price, item_number)
        SELECT
            (detail ->> 'order_number')::text,
            (detail ->> 'part_number')::text,
            (detail ->> 'quantity')::integer,
            (detail ->> 'unit_price')::real,
            (detail ->> 'item_number')::integer
        FROM
            unnest(order_details)
            WITH ORDINALITY AS detail (detail, insertion_order);
            RETURN QUERY WITH tmp AS (
                SELECT
                    coalesce(OD.order_detail_id, NULL) AS orderDetailId,
                    coalesce(OD.order_id, NULL) AS orderId,
                    coalesce(OD.item_number, NULL) AS itemNumber,
                    coalesce(P.product_id, NULL) AS productId,
                    TOD.insertion_order,
                    json_build_object('orderNumber', TOD.order_number, 'partNumber', TOD.part_number, 'quantity', TOD.quantity, 'unitPrice', TOD.unit_price, 'itemNumber', TOD.item_number) AS originalQuery,
                    GREATEST (SIMILARITY (lower(TOD.part_number), lower(P.factory_part_number)), SIMILARITY (lower(PCPN.customer_part_number), lower(TOD.part_number)), 0) AS similarity_score,
                    CASE WHEN TOD.unit_price            <> 0 THEN
                        abs((((abs(OD.unit_price) - abs(TOD.unit_price)) / ((abs(OD.unit_price) + abs(TOD.unit_price)) / 2)) * 100))
                    ELSE
                        NULL
                    END AS unit_price_diff,
                    abs((OD.quantity - TOD.quantity)) AS quantity_abs
                FROM
                    tmp_table TOD
                LEFT JOIN orders O ON O.order_number = TOD.order_number
                LEFT JOIN order_details OD ON OD.order_id = O.order_id
                LEFT JOIN products P ON OD.product_id = P.product_id
                LEFT JOIN product_cpn PCPN ON PCPN.product_id = P.product_id
            WHERE
                O.order_number = TOD.order_number
                AND ((OD.unit_price = 0
                        AND TOD.unit_price = 0)
                    OR (TOD.unit_price <> 0
                        AND (((abs(OD.unit_price) - abs(TOD.unit_price)) / ((abs(OD.unit_price) + abs(TOD.unit_price)) / 2)) * 100) BETWEEN -10 AND 10))
                AND (SIMILARITY (lower(TOD.part_number), lower(P.factory_part_number)) >.1
                    OR SIMILARITY (lower(PCPN.customer_part_number), lower(TOD.part_number)) >.5
                    OR OD.quantity = TOD.quantity
                    OR OD.shipping_balance = TOD.quantity)
        ),
        tmp2 AS (
            SELECT
                *,
                row_number() OVER (PARTITION BY tmp.originalQuery::text ORDER BY tmp.similarity_score DESC NULLS LAST,
                    tmp.unit_price_diff ASC NULLS LAST,
                    tmp.quantity_abs ASC NULLS LAST) AS rn
            FROM
                tmp
        ),
        duplicate_ranks AS (
            SELECT
                insertion_order,
                similarity_score,
                unit_price_diff,
                quantity_abs
            FROM
                tmp2
            WHERE
                rn <= 2
        ),
        filtered_duplicates AS (
            SELECT
                insertion_order
            FROM
                duplicate_ranks
            GROUP BY
                insertion_order,
                similarity_score,
                unit_price_diff,
                quantity_abs
            HAVING
                count(*) > 1
        ),
        filtered_rows AS (
            SELECT
                tmp2.orderDetailId,
                tmp2.orderId,
                tmp2.itemNumber,
                tmp2.productId,
                tmp2.originalQuery,
                tmp2.insertion_order
            FROM
                tmp2
                LEFT JOIN filtered_duplicates ON tmp2.insertion_order = filtered_duplicates.insertion_order
            WHERE
                tmp2.rn = 1
                AND filtered_duplicates.insertion_order IS NULL
        )
        SELECT
            fr.orderDetailId,
            fr.orderId,
            fr.itemNumber,
            fr.productId,
            coalesce(fr.originalQuery, json_build_object('orderNumber', TOD.order_number, 'partNumber', TOD.part_number, 'quantity', TOD.quantity, 'unitPrice', TOD.unit_price, 'itemNumber', TOD.item_number), NULL) AS originalQuery
        FROM
            tmp_table TOD
            LEFT JOIN filtered_rows fr ON TOD.insertion_order = fr.insertion_order
        ORDER BY
            TOD.insertion_order ASC;
            DROP TABLE IF EXISTS tmp_table;
        END;
        $$;


ALTER FUNCTION public.bulk_order_detail_info(order_details json[]) OWNER TO springuser;

--
-- Name: change_ownership(text, text); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.change_ownership(old_owner text, new_owner text) RETURNS void
    LANGUAGE plpgsql
    AS $$
        DECLARE
            r RECORD;
        BEGIN
            -- Change ownership of tables
            FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tableowner = old_owner LOOP
                EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' OWNER TO ' || quote_ident(new_owner);
            END LOOP;
            
            -- Change ownership of sequences
            FOR r IN SELECT c.relname AS sequence_name
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    JOIN pg_roles ro ON ro.oid = c.relowner
                    WHERE c.relkind = 'S' -- 'S' stands for sequence
                    AND n.nspname = 'public'
                    AND ro.rolname = old_owner
            LOOP
                EXECUTE 'ALTER SEQUENCE ' || quote_ident(r.sequence_name) || ' OWNER TO ' || quote_ident(new_owner);
            END LOOP;
            
            -- Change ownership of functions
            FOR r IN SELECT proname, oidvectortypes(proargtypes) as argtypes 
                    FROM pg_proc 
                    INNER JOIN pg_namespace ns ON (pg_proc.pronamespace = ns.oid) 
                    WHERE ns.nspname = 'public'
                    AND pg_proc.proowner = (SELECT oid FROM pg_roles WHERE rolname = old_owner) LOOP
                EXECUTE 'ALTER FUNCTION public.' || quote_ident(r.proname) || '(' || r.argtypes || ') OWNER TO ' || quote_ident(new_owner);
            END LOOP;
            
            -- Change ownership of views
            FOR r IN SELECT c.relname AS view_name
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    JOIN pg_roles ro ON ro.oid = c.relowner
                    WHERE c.relkind = 'v' 
                    AND n.nspname = 'public'
                    AND ro.rolname = old_owner
            LOOP
                EXECUTE 'ALTER VIEW ' || quote_ident(r.view_name) || ' OWNER TO ' || quote_ident(new_owner);
            END LOOP;

            RAISE NOTICE 'Ownership changed from % to %', old_owner, new_owner;
        END;
        $$;


ALTER FUNCTION public.change_ownership(old_owner text, new_owner text) OWNER TO springuser;

--
-- Name: get_created_by(text, integer[]); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.get_created_by(table_name text, ids integer[]) RETURNS TABLE(entity_id integer, created_by uuid)
    LANGUAGE plpgsql
    AS $$
                DECLARE pk_field text;
                BEGIN
                    SELECT a.attname INTO pk_field
                    FROM pg_index i
                        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                    WHERE
                        i.indrelid = table_name::regclass AND i.indisprimary;

                    RETURN QUERY
                        EXECUTE FORMAT(
                            'SELECT %s, r.created_by FROM %s r WHERE %s = ANY(%L)',
                            pk_field,
                            table_name,
                            pk_field,
                            ids
                        );
                END;
            $$;


ALTER FUNCTION public.get_created_by(table_name text, ids integer[]) OWNER TO springuser;

--
-- Name: get_current_option(); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.get_current_option() RETURNS character varying
    LANGUAGE plpgsql
    AS $$
            BEGIN
                RETURN COALESCE(NULLIF(current_setting('request.user.option', true), ''), 'all');
            END;
        $$;


ALTER FUNCTION public.get_current_option() OWNER TO springuser;

--
-- Name: get_current_resource(); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.get_current_resource() RETURNS character varying
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RETURN COALESCE(NULLIF(current_setting('request.user.resource', true), ''), 'all');
        END;
        $$;


ALTER FUNCTION public.get_current_resource() OWNER TO springuser;

--
-- Name: get_user_id(); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.get_user_id() RETURNS character varying
    LANGUAGE plpgsql
    AS $$
            BEGIN
                RETURN current_setting('request.user.sub', true);
            END;
        $$;


ALTER FUNCTION public.get_user_id() OWNER TO springuser;

--
-- Name: set_role_and_permissions(uuid, character varying, character varying); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.set_role_and_permissions(user_id uuid, role_option character varying, resource character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN
            PERFORM set_config('request.user.sub', user_id::text, true);
            PERFORM set_config('request.user.option', role_option, true);
            PERFORM set_config('request.user.resource', resource, true);
        END;
        $$;


ALTER FUNCTION public.set_role_and_permissions(user_id uuid, role_option character varying, resource character varying) OWNER TO springuser;

--
-- Name: update_update_date_column(); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.update_update_date_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.update_date = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_update_date_column() OWNER TO springuser;

--
-- Name: update_user_and_references(uuid, uuid, text, text, text, text, boolean, boolean, boolean); Type: FUNCTION; Schema: public; Owner: springuser
--

CREATE FUNCTION public.update_user_and_references(old_id uuid, new_id uuid, new_username text, new_email text, new_firstname text, new_lastname text, new_is_outside boolean, new_is_inside boolean, new_is_administrator boolean) RETURNS void
    LANGUAGE plpgsql
    AS $$
            BEGIN
                -- Insert new user
                INSERT INTO public.users (id, username, email, firstname, lastname, is_outside, is_inside, is_administrator)
                VALUES (new_id, 'temp-' || new_username, 'temp-' || new_email, new_firstname, new_lastname, new_is_outside, new_is_inside, new_is_administrator);

                -- Update other tables
                UPDATE quote_details
                SET outside_rep_id = new_id
                WHERE outside_rep_id = old_id;

                UPDATE order_details
                SET outside_rep_id = new_id
                WHERE outside_rep_id = old_id;

                UPDATE invoice_details
                SET outside_rep_id = new_id
                WHERE outside_rep_id = old_id;

                UPDATE customers
                SET inside_rep_id = new_id
                WHERE inside_rep_id = old_id;

                UPDATE customers
                SET outside_rep_id = new_id
                WHERE outside_rep_id = old_id;

                UPDATE quote_sales_rep_split
                SET user_id = new_id
                WHERE user_id = old_id;

                UPDATE order_sales_rep_split
                SET user_id = new_id
                WHERE user_id = old_id;

                UPDATE quotes
                SET outside_rep_id = new_id
                WHERE outside_rep_id = old_id;

                -- Delete the old user
                DELETE FROM public.users WHERE id = old_id;

                -- Update username and email of the new user
                UPDATE users
                SET username = new_username,
                    email = new_email
                WHERE id = new_id;
            END;
        $$;


ALTER FUNCTION public.update_user_and_references(old_id uuid, new_id uuid, new_username text, new_email text, new_firstname text, new_lastname text, new_is_outside boolean, new_is_inside boolean, new_is_administrator boolean) OWNER TO springuser;

--
-- Name: tenant; Type: SERVER; Schema: -; Owner: doadmin
--

CREATE SERVER tenant FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    dbname 'tenantcontroller',
    host 'flow-production-do-user-14032072-0.b.db.ondigitalocean.com',
    port '25060'
);


ALTER SERVER tenant OWNER TO doadmin;

--
-- Name: USER MAPPING doadmin SERVER tenant; Type: USER MAPPING; Schema: -; Owner: doadmin
--

CREATE USER MAPPING FOR doadmin SERVER tenant OPTIONS (
    password 'AVNS_RpnK85noplYw_-a6ebE',
    "user" 'doadmin'
);


--
-- Name: USER MAPPING springuser SERVER tenant; Type: USER MAPPING; Schema: -; Owner: doadmin
--

CREATE USER MAPPING FOR springuser SERVER tenant;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: acl_privilege; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_privilege (
    privilege_id integer NOT NULL,
    privilege character varying NOT NULL
);


ALTER TABLE public.acl_privilege OWNER TO springuser;

--
-- Name: acl_privilege_option; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_privilege_option (
    privilege_option_id integer NOT NULL,
    detail character varying NOT NULL
);


ALTER TABLE public.acl_privilege_option OWNER TO springuser;

--
-- Name: acl_privilege_option_privilege_option_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

ALTER TABLE public.acl_privilege_option ALTER COLUMN privilege_option_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.acl_privilege_option_privilege_option_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: acl_privilege_option_relation; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_privilege_option_relation (
    privilege_id integer NOT NULL,
    privilege_option_id integer NOT NULL
);


ALTER TABLE public.acl_privilege_option_relation OWNER TO springuser;

--
-- Name: acl_privilege_privilege_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

ALTER TABLE public.acl_privilege ALTER COLUMN privilege_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.acl_privilege_privilege_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: acl_resource; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_resource (
    resource_id integer NOT NULL,
    resource character varying NOT NULL,
    is_private boolean DEFAULT false NOT NULL
);


ALTER TABLE public.acl_resource OWNER TO springuser;

--
-- Name: acl_resource_resource_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

ALTER TABLE public.acl_resource ALTER COLUMN resource_id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.acl_resource_resource_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: acl_role_option; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_role_option (
    uuid uuid NOT NULL,
    role character varying NOT NULL,
    key character varying NOT NULL,
    value character varying NOT NULL
);


ALTER TABLE public.acl_role_option OWNER TO springuser;

--
-- Name: acl_role_resource; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.acl_role_resource (
    role character varying NOT NULL,
    resource_id integer NOT NULL,
    privilege_id integer NOT NULL,
    privilege_option_id integer
);


ALTER TABLE public.acl_role_resource OWNER TO springuser;

--
-- Name: activity; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.activity (
    activity_id integer NOT NULL,
    activity_type character varying(255),
    user_id integer,
    activity_date_time timestamp without time zone
);


ALTER TABLE public.activity OWNER TO springuser;

--
-- Name: addresses; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.addresses (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    source_id integer NOT NULL,
    address_type character varying(255) NOT NULL,
    address_line_one character varying(255),
    address_line_two character varying(255),
    city character varying(255),
    state character varying(255),
    zip character varying(255),
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL
);


ALTER TABLE public.addresses OWNER TO springuser;

--
-- Name: COLUMN addresses.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN addresses.source_id; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses.source_id IS 'Used to associate with a customer or factory.';


--
-- Name: COLUMN addresses.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN addresses.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses.created_by IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN addresses.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: addresses_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.addresses_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.addresses_log OWNER TO springuser;

--
-- Name: COLUMN addresses_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN addresses_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN addresses_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN addresses_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.addresses_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: alerts; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.alerts (
    alertid integer NOT NULL,
    message character varying(255) NOT NULL,
    create_date timestamp without time zone,
    user_for uuid
);


ALTER TABLE public.alerts OWNER TO springuser;

--
-- Name: ar_report_metrics; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.ar_report_metrics (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    metric_type character varying(255) NOT NULL,
    metric_value numeric NOT NULL,
    computed_month character varying(255) NOT NULL,
    additional_info json
);


ALTER TABLE public.ar_report_metrics OWNER TO springuser;

--
-- Name: ar_report_model; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.ar_report_model (
    id integer NOT NULL,
    model_type character varying NOT NULL,
    model_path character varying NOT NULL,
    algorithm character varying NOT NULL,
    meta json NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.ar_report_model OWNER TO springuser;

--
-- Name: ar_report_model_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

ALTER TABLE public.ar_report_model ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.ar_report_model_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auto_generated_settings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.auto_generated_settings (
    uuid uuid NOT NULL,
    prefix character varying(255),
    starts_at integer,
    counter integer,
    allow_auto_generation boolean DEFAULT true,
    type character varying(255)
);


ALTER TABLE public.auto_generated_settings OWNER TO springuser;

--
-- Name: branches; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.branches (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    title character varying(255),
    status boolean
);


ALTER TABLE public.branches OWNER TO springuser;

--
-- Name: cb; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.cb (
    title character varying(255) NOT NULL,
    factory_total_current_year double precision,
    factory_total_prior_year double precision,
    difference double precision
);


ALTER TABLE public.cb OWNER TO springuser;

--
-- Name: checks; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.checks (
    check_id integer NOT NULL,
    check_date date,
    check_number character varying(255) NOT NULL,
    factory integer,
    commission_amount numeric,
    expected_commission_amount numeric,
    post_date character varying(255),
    commission_month character varying(255),
    locked boolean,
    posted boolean,
    create_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL,
    paid_commission_sum numeric,
    commission_balance numeric,
    commission_difference numeric
);

ALTER TABLE ONLY public.checks FORCE ROW LEVEL SECURITY;


ALTER TABLE public.checks OWNER TO springuser;

--
-- Name: COLUMN checks.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN checks.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN checks.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN checks.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: checks_details; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.checks_details (
    checks_detail_id integer NOT NULL,
    commission_amount numeric,
    check_id integer,
    invoice integer,
    paid boolean
);


ALTER TABLE public.checks_details OWNER TO springuser;

--
-- Name: checks_imports; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.checks_imports (
    id integer NOT NULL,
    batch_id character varying(255),
    check_number character varying(255),
    commission_due double precision,
    commission_rate double precision,
    customer character varying(255),
    end_user character varying(255),
    factory_id integer,
    invoice_amount double precision,
    invoice_date character varying(255),
    invoice_number character varying(255),
    order_number character varying(255),
    pay_commission double precision,
    sales_rep character varying(255),
    insert_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by integer NOT NULL,
    key character varying(255),
    level character varying(255),
    message character varying(255),
    processed boolean,
    update_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_by integer NOT NULL,
    file_name character varying(255),
    check_date timestamp without time zone,
    invoice_id integer
);


ALTER TABLE public.checks_imports OWNER TO springuser;

--
-- Name: checks_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.checks_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.checks_log OWNER TO springuser;

--
-- Name: COLUMN checks_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN checks_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN checks_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN checks_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.checks_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: commission_discount_per_rep; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.commission_discount_per_rep (
    id uuid NOT NULL,
    user_id uuid,
    order_detail_order_detail_id integer,
    quote_detail_quote_detail_id integer,
    invoice_detail_invoice_detail_id integer,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount numeric,
    discount_rate numeric,
    sales_rep_commission_rate numeric,
    create_date timestamp without time zone NOT NULL
);


ALTER TABLE public.commission_discount_per_rep OWNER TO springuser;

--
-- Name: company_targets; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.company_targets (
    company_targets_id integer NOT NULL,
    commission_goal real,
    goal_month integer,
    goal_year integer,
    new_orders_goal integer,
    new_quotes_goal integer,
    sales_goal real
);


ALTER TABLE public.company_targets OWNER TO springuser;

--
-- Name: contacts; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.contacts (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    bg_color character varying(255),
    can_email boolean,
    can_text boolean,
    contact_order integer,
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    email character varying(255),
    first_name character varying(255),
    full_name character varying(255),
    image_url character varying(255),
    last_name character varying(255),
    phone character varying(255),
    source_id integer,
    title character varying(255) NOT NULL,
    is_primary boolean,
    creation_type character varying(255) NOT NULL
);


ALTER TABLE public.contacts OWNER TO springuser;

--
-- Name: COLUMN contacts.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN contacts.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN contacts.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN contacts.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: contacts_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.contacts_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.contacts_log OWNER TO springuser;

--
-- Name: COLUMN contacts_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN contacts_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN contacts_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN contacts_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.contacts_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: customer_alias; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.customer_alias (
    uuid uuid NOT NULL,
    customer_uuid uuid NOT NULL,
    alias character varying NOT NULL
);


ALTER TABLE public.customer_alias OWNER TO springuser;

--
-- Name: customers; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    company_name character varying(255),
    contact_email character varying(255),
    contact_name character varying(255),
    contact_number character varying(255),
    customer_type integer,
    alias text[],
    is_parent boolean,
    parent_id integer,
    draft boolean,
    inside_rep_id uuid,
    outside_rep_id uuid,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    outside_rep_splits uuid,
    status boolean DEFAULT true,
    territory_id uuid,
    branch_id uuid,
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL
);


ALTER TABLE public.customers OWNER TO springuser;

--
-- Name: COLUMN customers.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN customers.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN customers.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN customers.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: customer_customerid_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.customer_customerid_seq
    AS integer
    START WITH 1000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_customerid_seq OWNER TO springuser;

--
-- Name: customer_customerid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public.customer_customerid_seq OWNED BY public.customers.customer_id;


--
-- Name: customer_rankings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.customer_rankings (
    ranking_id integer NOT NULL,
    commission_rank integer,
    customer_id integer NOT NULL,
    customer_name character varying(255) NOT NULL,
    paid_commissions double precision,
    rank_month character varying NOT NULL,
    rank_year timestamp without time zone NOT NULL,
    sales_rank integer,
    total_commissions double precision,
    invoices_count integer,
    orders_count integer,
    quotes_count integer,
    total_sales double precision
);


ALTER TABLE public.customer_rankings OWNER TO springuser;

--
-- Name: customers_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.customers_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.customers_log OWNER TO springuser;

--
-- Name: COLUMN customers_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN customers_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN customers_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN customers_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.customers_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: databasechangelog; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.databasechangelog (
    id character varying(255) NOT NULL,
    author character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    dateexecuted timestamp without time zone NOT NULL,
    orderexecuted integer NOT NULL,
    exectype character varying(10) NOT NULL,
    md5sum character varying(35),
    description character varying(255),
    comments character varying(255),
    tag character varying(255),
    liquibase character varying(20),
    contexts character varying(255),
    labels character varying(255),
    deployment_id character varying(10)
);


ALTER TABLE public.databasechangelog OWNER TO springuser;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE public.databasechangeloglock OWNER TO springuser;

--
-- Name: default_outside_rep_customer_split; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.default_outside_rep_customer_split (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    customer_id integer NOT NULL,
    split_rate numeric,
    created_by uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.default_outside_rep_customer_split OWNER TO springuser;

--
-- Name: COLUMN default_outside_rep_customer_split.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.default_outside_rep_customer_split.created_by IS 'Creator''s UUID';


--
-- Name: default_outside_rep_split; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.default_outside_rep_split (
    id uuid NOT NULL,
    user_id uuid,
    split_rate numeric,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    selection_id uuid,
    created_by uuid
);


ALTER TABLE public.default_outside_rep_split OWNER TO springuser;

--
-- Name: email_settings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.email_settings (
    uuid uuid NOT NULL,
    host character varying(255),
    port character varying(255),
    username character varying(255),
    password character varying(255),
    send_from_name character varying(255),
    smtp_auth boolean,
    tls_enabled boolean
);


ALTER TABLE public.email_settings OWNER TO springuser;

--
-- Name: expense; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.expense (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    expense_number character varying(255) NOT NULL,
    expense_date date NOT NULL,
    expense_amount numeric NOT NULL,
    locked boolean DEFAULT false NOT NULL,
    expense_category_uuid uuid,
    note character varying(5000),
    user_uuids uuid[],
    factory_uuid uuid,
    customer_uuid uuid
);


ALTER TABLE public.expense OWNER TO springuser;

--
-- Name: expense_category; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.expense_category (
    uuid uuid NOT NULL,
    title character varying(255) NOT NULL,
    category_order integer NOT NULL
);


ALTER TABLE public.expense_category OWNER TO springuser;

--
-- Name: expense_check; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.expense_check (
    expense_uuid uuid NOT NULL,
    check_uuid uuid,
    create_date timestamp without time zone
);


ALTER TABLE public.expense_check OWNER TO springuser;

--
-- Name: expense_sales_rep_split; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.expense_sales_rep_split (
    uuid uuid NOT NULL,
    expense_uuid uuid,
    user_id uuid,
    split_rate numeric NOT NULL
);


ALTER TABLE public.expense_sales_rep_split OWNER TO springuser;

--
-- Name: factories; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.factories (
    factory_id integer NOT NULL,
    account_number character varying(255),
    base_commission numeric DEFAULT 0 NOT NULL,
    commission_discount numeric DEFAULT 0 NOT NULL,
    discount_type character varying(255),
    email character varying(255),
    freight_terms character varying(255),
    overall_discount numeric DEFAULT 0 NOT NULL,
    payment_terms text,
    pays_shipping boolean,
    phone character varying(255),
    ship_time integer DEFAULT 0 NOT NULL,
    status boolean DEFAULT true,
    title character varying(255) NOT NULL,
    commission_payment_time integer DEFAULT 0 NOT NULL,
    projected_ship_time numeric DEFAULT 0 NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    lead_time character varying(255),
    additional_information character varying(10000),
    external_payment_terms character varying(10000),
    alias text[],
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL,
    draft boolean DEFAULT true NOT NULL,
    inside_rep_id uuid
);


ALTER TABLE public.factories OWNER TO springuser;

--
-- Name: COLUMN factories.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN factories.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN factories.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories.created_by IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN factories.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: factories_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.factories_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.factories_log OWNER TO springuser;

--
-- Name: COLUMN factories_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN factories_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN factories_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN factories_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.factories_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: factory_alias; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.factory_alias (
    uuid uuid NOT NULL,
    factory_uuid uuid NOT NULL,
    alias character varying NOT NULL
);


ALTER TABLE public.factory_alias OWNER TO springuser;

--
-- Name: factory_metrics; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.factory_metrics (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    metric_type character varying(255) NOT NULL,
    metric_value numeric NOT NULL,
    computed_month character varying(255) NOT NULL,
    additional_info json,
    factory_uuid uuid NOT NULL
);


ALTER TABLE public.factory_metrics OWNER TO springuser;

--
-- Name: factory_rankings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.factory_rankings (
    ranking_id integer NOT NULL,
    commission_rank integer,
    factory_id integer NOT NULL,
    factory_name character varying(255) NOT NULL,
    paid_commissions double precision,
    rank_month timestamp without time zone NOT NULL,
    rank_year timestamp without time zone NOT NULL,
    sales_rank integer,
    total_commissions double precision,
    invoices_count integer,
    orders_count integer,
    quotes_count integer,
    total_sales double precision,
    average_shipping_time integer
);


ALTER TABLE public.factory_rankings OWNER TO springuser;

--
-- Name: faq_categories; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.faq_categories (
    id uuid NOT NULL,
    slug character varying(255) NOT NULL,
    title character varying(255) NOT NULL
);


ALTER TABLE public.faq_categories OWNER TO springuser;

--
-- Name: faqs; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.faqs (
    id uuid NOT NULL,
    answer character varying(255) NOT NULL,
    question character varying(255) NOT NULL,
    category_id uuid
);


ALTER TABLE public.faqs OWNER TO springuser;

--
-- Name: file_upload; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.file_upload (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    entity_type character varying(255),
    file_path character varying(255) NOT NULL,
    meta_data json
);


ALTER TABLE public.file_upload OWNER TO springuser;

--
-- Name: file_upload_process; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.file_upload_process (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    file_upload_uuid uuid,
    status character varying(255) NOT NULL,
    meta_data json,
    errors json,
    current_flow character varying(255),
    next_flow character varying(255),
    dtos json,
    parent_process_uuid uuid
);


ALTER TABLE public.file_upload_process OWNER TO springuser;

--
-- Name: guide_categories; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.guide_categories (
    id uuid NOT NULL,
    slug character varying(255) NOT NULL,
    title character varying(255) NOT NULL
);


ALTER TABLE public.guide_categories OWNER TO springuser;

--
-- Name: guides; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.guides (
    id uuid NOT NULL,
    content character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    sub_title character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    category_id uuid
);


ALTER TABLE public.guides OWNER TO springuser;

--
-- Name: hard_copies; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.hard_copies (
    hard_copy_id integer NOT NULL,
    file_name character varying(255),
    file_size character varying(255),
    file_type character varying(255),
    file_uri character varying(255),
    transaction_id integer,
    transaction_type character varying(255),
    upload_by integer,
    upload_date timestamp without time zone
);


ALTER TABLE public.hard_copies OWNER TO springuser;

--
-- Name: hibernate_sequence; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.hibernate_sequence
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hibernate_sequence OWNER TO springuser;

--
-- Name: history; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.history (
    uuid uuid NOT NULL,
    source_uuid uuid NOT NULL,
    insert_date timestamp without time zone NOT NULL,
    inserted_by uuid NOT NULL,
    entity character varying(255) NOT NULL,
    action character varying(255) NOT NULL,
    user_name character varying(255) NOT NULL,
    version_detail uuid
);


ALTER TABLE public.history OWNER TO springuser;

--
-- Name: instance_prediction; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.instance_prediction (
    id integer NOT NULL,
    ar_report_model_id integer NOT NULL,
    instance_id integer NOT NULL,
    instance_type character varying NOT NULL,
    prediction json NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    ignore boolean DEFAULT false
);


ALTER TABLE public.instance_prediction OWNER TO springuser;

--
-- Name: instance_prediction_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

ALTER TABLE public.instance_prediction ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.instance_prediction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: invoice_details; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.invoice_details (
    invoice_detail_id integer NOT NULL,
    invoice_id integer,
    product_id integer,
    commission_discount numeric,
    commission numeric,
    commission_rate numeric,
    unit_price numeric,
    total numeric,
    discount numeric,
    quantity_shipped integer,
    shipped_date character varying(255),
    order_detail_id integer,
    item_number integer,
    status integer,
    end_user integer,
    outside_rep_id uuid,
    discount_rate double precision,
    commission_discount_rate double precision
);


ALTER TABLE public.invoice_details OWNER TO springuser;

--
-- Name: invoice_status; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.invoice_status (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.invoice_status OWNER TO springuser;

--
-- Name: invoice_status_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.invoice_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_status_id_seq OWNER TO springuser;

--
-- Name: invoice_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public.invoice_status_id_seq OWNED BY public.invoice_status.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.invoices (
    invoice_id integer NOT NULL,
    create_date timestamp without time zone NOT NULL,
    due_date timestamp without time zone,
    invoice_date timestamp without time zone,
    invoice_number character varying(255) NOT NULL,
    status integer NOT NULL,
    order_id integer,
    factory_id integer,
    "totalItemsCount" integer,
    quantity_shipped integer,
    "shippingBalance" integer,
    "customerName" character varying(255),
    closed boolean,
    paid boolean,
    locked boolean,
    "updateDate" timestamp without time zone,
    invoice_type character varying(255) DEFAULT 'normal'::character varying,
    customer_id integer,
    import_id character varying,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    draft boolean,
    created_by uuid NOT NULL,
    "updatedBy" uuid,
    batch_id uuid,
    creation_type character varying(255) NOT NULL,
    invoice_amount numeric,
    commission_rate numeric,
    commission numeric,
    paid_amount numeric,
    commission_paid_amount numeric
);

ALTER TABLE ONLY public.invoices FORCE ROW LEVEL SECURITY;


ALTER TABLE public.invoices OWNER TO springuser;

--
-- Name: COLUMN invoices.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN invoices.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN invoices.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN invoices.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: invoices_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.invoices_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.invoices_log OWNER TO springuser;

--
-- Name: COLUMN invoices_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN invoices_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN invoices_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN invoices_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.invoices_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: lost_reasons; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.lost_reasons (
    uuid uuid NOT NULL,
    title character varying(255)
);


ALTER TABLE public.lost_reasons OWNER TO springuser;

--
-- Name: COLUMN lost_reasons.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.lost_reasons.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: notes; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.notes (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    content text,
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    source_id integer,
    create_name character varying,
    creation_type character varying(255) NOT NULL
);


ALTER TABLE public.notes OWNER TO springuser;

--
-- Name: COLUMN notes.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN notes.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN notes.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN notes.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: notes_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.notes_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.notes_log OWNER TO springuser;

--
-- Name: COLUMN notes_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN notes_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN notes_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN notes_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.notes_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: notifier_settings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.notifier_settings (
    uuid uuid NOT NULL,
    user_id uuid,
    alert_type integer NOT NULL,
    visibility boolean NOT NULL,
    location integer NOT NULL
);


ALTER TABLE public.notifier_settings OWNER TO springuser;

--
-- Name: order_acknowledgements; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.order_acknowledgements (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    oa_number character varying(255),
    create_date timestamp without time zone NOT NULL,
    item_number integer,
    ship_date timestamp without time zone,
    order_id integer NOT NULL,
    order_detail_id integer,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL
);


ALTER TABLE public.order_acknowledgements OWNER TO springuser;

--
-- Name: COLUMN order_acknowledgements.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.order_acknowledgements.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN order_acknowledgements.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.order_acknowledgements.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN order_acknowledgements.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.order_acknowledgements.created_by IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN order_acknowledgements.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.order_acknowledgements.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: order_details; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.order_details (
    order_detail_id integer NOT NULL,
    commission numeric,
    commission_rate numeric,
    unit_price numeric,
    total numeric,
    quantity integer,
    order_id integer,
    product_id integer,
    commission_discount numeric,
    order_balance numeric,
    commission_balance numeric,
    quote_detail_id integer,
    "invoiceDetailAmount" numeric(19,2) DEFAULT 0,
    "invoiceDetailCommRate" numeric(19,2) DEFAULT 0,
    "invoiceDetailCommission" numeric(19,2) DEFAULT 0,
    shipping_balance integer DEFAULT 0,
    item_number integer DEFAULT 0,
    discount numeric,
    commission_discount_rate numeric,
    outside_rep_id uuid,
    end_user integer,
    discount_rate numeric,
    status integer,
    lead_time character varying(255),
    refund_amount numeric,
    refund_quantity integer,
    refund_commission_amount numeric
);


ALTER TABLE public.order_details OWNER TO springuser;

--
-- Name: order_sales_rep_split; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.order_sales_rep_split (
    id uuid NOT NULL,
    user_id uuid,
    order_detail_id integer,
    split_rate numeric,
    create_date timestamp without time zone NOT NULL
);


ALTER TABLE public.order_sales_rep_split OWNER TO springuser;

--
-- Name: order_status; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.order_status (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.order_status OWNER TO springuser;

--
-- Name: order_status_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.order_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_status_id_seq OWNER TO springuser;

--
-- Name: order_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public.order_status_id_seq OWNED BY public.order_status.id;


--
-- Name: orderidcounter; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.orderidcounter
    START WITH 32102
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orderidcounter OWNER TO springuser;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    order_number character varying(255),
    create_date timestamp without time zone NOT NULL,
    order_date timestamp without time zone,
    ship_date timestamp without time zone,
    revise_date timestamp without time zone,
    due_date timestamp without time zone,
    status integer,
    fact_so_number character varying(255),
    pro_number character varying(255),
    payment_terms character varying(255),
    freight_terms character varying(255),
    job_name character varying(255),
    customer_ref character varying(255),
    customer integer,
    factory_id integer,
    quote_id integer,
    reconciled boolean,
    order_balance numeric,
    created_by uuid NOT NULL,
    quantity integer,
    commission_balance numeric,
    shipping_balance integer,
    order_type integer NOT NULL,
    commission_discount numeric,
    discount numeric,
    locked boolean,
    import_id character varying(255),
    draft boolean,
    creation_type character varying(255) NOT NULL,
    order_amount numeric,
    commission_rate numeric,
    commission numeric,
    user_uuids uuid[],
    refund_amount numeric,
    refund_quantity integer,
    refund_commission_amount numeric
);

ALTER TABLE ONLY public.orders FORCE ROW LEVEL SECURITY;


ALTER TABLE public.orders OWNER TO springuser;

--
-- Name: COLUMN orders.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN orders.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN orders.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN orders.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: orders_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.orders_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.orders_log OWNER TO springuser;

--
-- Name: COLUMN orders_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN orders_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN orders_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN orders_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.orders_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: precious_metals; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.precious_metals (
    metals_id integer NOT NULL,
    aluminum_price double precision,
    copper_price double precision,
    gold_price double precision,
    record_date timestamp without time zone,
    silver_price double precision
);


ALTER TABLE public.precious_metals OWNER TO springuser;

--
-- Name: pricing_imports; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.pricing_imports (
    id integer NOT NULL,
    batch_id character varying(255),
    created_by integer,
    product_id integer,
    insert_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    unit_price double precision,
    key character varying(255),
    level character varying(255),
    message character varying(255),
    processed boolean,
    update_date timestamp without time zone,
    updated_by integer,
    file_name character varying(255)
);


ALTER TABLE public.pricing_imports OWNER TO springuser;

--
-- Name: product_alias; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.product_alias (
    uuid uuid NOT NULL,
    product_uuid uuid NOT NULL,
    alias character varying NOT NULL
);


ALTER TABLE public.product_alias OWNER TO springuser;

--
-- Name: product_categories; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.product_categories (
    title character varying(255) NOT NULL,
    commission_rate numeric(19,2),
    factory_id integer NOT NULL,
    uuid uuid NOT NULL
);


ALTER TABLE public.product_categories OWNER TO springuser;

--
-- Name: product_cpn; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.product_cpn (
    product_cpn_id integer DEFAULT nextval('public.hibernate_sequence'::regclass) NOT NULL,
    product_id integer NOT NULL,
    customer_id integer NOT NULL,
    customer_part_number character varying(255),
    unit_price numeric,
    commission_rate numeric,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL
);


ALTER TABLE public.product_cpn OWNER TO springuser;

--
-- Name: product_dimensions; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.product_dimensions (
    unit_count integer DEFAULT 1,
    unit_length double precision DEFAULT 1,
    unit_width double precision DEFAULT 1,
    unit_height double precision DEFAULT 1,
    unit_cube double precision DEFAULT 1,
    unit_weight double precision DEFAULT 1,
    inner_pack_count integer DEFAULT 1,
    inner_pack_length double precision DEFAULT 1,
    inner_pack_width double precision DEFAULT 1,
    inner_pack_height double precision DEFAULT 1,
    inner_pack_cube double precision DEFAULT 1,
    inner_pack_weight double precision DEFAULT 1,
    case_quantity_count integer DEFAULT 1,
    case_quantity_length double precision DEFAULT 1,
    case_quantity_width double precision DEFAULT 1,
    case_quantity_height double precision DEFAULT 1,
    case_quantity_cube double precision DEFAULT 1,
    case_quantity_weight double precision DEFAULT 1,
    cases_per_pallet integer DEFAULT 0,
    dimensions_id uuid NOT NULL
);


ALTER TABLE public.product_dimensions OWNER TO springuser;

--
-- Name: product_tags; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.product_tags (
    product_tag_id integer NOT NULL,
    tag character varying(255) NOT NULL
);


ALTER TABLE public.product_tags OWNER TO springuser;

--
-- Name: products; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    alternate_ean character varying(255),
    base_price numeric,
    case_upc character varying(255),
    commission_rate numeric,
    unit_price numeric,
    description character varying(500),
    ean character varying(255),
    image_url character varying(255),
    ind_upc character varying(255),
    list_price numeric,
    min_order_qty integer,
    factory_part_number character varying(255),
    status boolean,
    uom character varying(255),
    factory_id integer,
    approval_comments character varying(255),
    approval_date character varying(255),
    approval_needed boolean,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    lead_time character varying(255),
    price_by character varying(255),
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type character varying(255) NOT NULL,
    uom_id uuid NOT NULL,
    dimensions_id uuid,
    commission_discount_rate numeric,
    discount_rate numeric,
    visibility boolean DEFAULT false,
    category_uuid uuid
);


ALTER TABLE public.products OWNER TO springuser;

--
-- Name: COLUMN products.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN products.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN products.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products.created_by IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN products.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: products_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.products_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.products_log OWNER TO springuser;

--
-- Name: COLUMN products_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN products_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN products_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN products_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.products_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: quantity_pricing; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quantity_pricing (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    product_id integer NOT NULL,
    quantity_high integer NOT NULL,
    quantity_low integer NOT NULL,
    unit_price double precision NOT NULL
);


ALTER TABLE public.quantity_pricing OWNER TO springuser;

--
-- Name: quote_details; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quote_details (
    quote_detail_id integer NOT NULL,
    commission numeric,
    commission_rate numeric,
    unit_price numeric,
    total numeric,
    quantity integer,
    product_id integer,
    quote_id integer NOT NULL,
    discount numeric,
    item_number integer,
    end_user integer,
    commission_discount numeric,
    commission_discount_rate numeric,
    discount_rate numeric,
    outside_rep_id uuid,
    status integer,
    lead_time character varying(255),
    lost_reason uuid,
    lost_reason_other character varying
);


ALTER TABLE public.quote_details OWNER TO springuser;

--
-- Name: quote_sales_rep_split; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quote_sales_rep_split (
    id uuid NOT NULL,
    user_id uuid,
    quote_detail_id integer,
    split_rate numeric,
    create_date timestamp without time zone NOT NULL
);


ALTER TABLE public.quote_sales_rep_split OWNER TO springuser;

--
-- Name: quote_status; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quote_status (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    uuid uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.quote_status OWNER TO springuser;

--
-- Name: quote_status_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.quote_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.quote_status_id_seq OWNER TO springuser;

--
-- Name: quote_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public.quote_status_id_seq OWNED BY public.quote_status.id;


--
-- Name: quotes; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quotes (
    quote_id integer NOT NULL,
    accept_date character varying(255),
    commission numeric(19,3) NOT NULL,
    commission_rate numeric(19,3) NOT NULL,
    create_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    customer_ref character varying(255),
    exp_date character varying(255),
    freight_terms character varying(255),
    job_name character varying(255),
    lost_reason character varying(255),
    payment_terms character varying(255),
    total numeric(19,3) NOT NULL,
    quote_date date,
    quote_number character varying(255) NOT NULL,
    quote_type boolean,
    revise_date character varying(255),
    status integer,
    terms character varying(255),
    total_items integer,
    update_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    customer integer,
    end_user integer,
    factory_id integer,
    outside_rep_id uuid,
    draft boolean,
    created_by uuid NOT NULL,
    updated_by uuid,
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    discount double precision,
    commission_discount double precision,
    creation_type character varying(255) NOT NULL,
    blanket boolean DEFAULT false,
    user_uuids uuid[]
);

ALTER TABLE ONLY public.quotes FORCE ROW LEVEL SECURITY;


ALTER TABLE public.quotes OWNER TO springuser;

--
-- Name: COLUMN quotes.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes.create_date IS 'This is used for easier filter queries. Main history is found in the history table';


--
-- Name: COLUMN quotes.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes.created_by IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: COLUMN quotes.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN quotes.creation_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes.creation_type IS 'This is used for audit entity. Main history is found in the history table';


--
-- Name: quotes_log; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.quotes_log (
    uuid uuid NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    operation character varying(10) NOT NULL,
    changed_data jsonb,
    version_id uuid DEFAULT public.uuid_generate_v4()
);


ALTER TABLE public.quotes_log OWNER TO springuser;

--
-- Name: COLUMN quotes_log.uuid; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes_log.uuid IS 'This is used for audit entity. Main history is linked by this field in the history table as sourceId';


--
-- Name: COLUMN quotes_log."timestamp"; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes_log."timestamp" IS 'Timestamp of the change';


--
-- Name: COLUMN quotes_log.operation; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes_log.operation IS 'Type of operation (create, update, delete)';


--
-- Name: COLUMN quotes_log.changed_data; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.quotes_log.changed_data IS 'Data that was changed (as JSON)';


--
-- Name: refund; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.refund (
    uuid uuid NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    order_id integer NOT NULL,
    factory_uuid uuid NOT NULL,
    refund_number character varying(255) NOT NULL,
    refund_date date NOT NULL,
    external_id uuid,
    locked boolean DEFAULT false NOT NULL,
    user_uuids uuid[],
    udate_order_option character varying
);


ALTER TABLE public.refund OWNER TO springuser;

--
-- Name: refund_balance; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.refund_balance (
    refund_uuid uuid NOT NULL,
    quantity integer,
    amount numeric NOT NULL,
    commission numeric DEFAULT 0 NOT NULL
);


ALTER TABLE public.refund_balance OWNER TO springuser;

--
-- Name: refund_check; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.refund_check (
    refund_uuid uuid NOT NULL,
    check_uuid uuid
);


ALTER TABLE public.refund_check OWNER TO springuser;

--
-- Name: refund_detail; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.refund_detail (
    uuid uuid NOT NULL,
    refund_uuid uuid,
    order_detail_id integer NOT NULL,
    refund_reason_uuid uuid,
    quantity integer,
    amount numeric NOT NULL,
    refund_reason_other character varying(255),
    unit_amount numeric DEFAULT 0 NOT NULL,
    commission_rate numeric DEFAULT 0 NOT NULL,
    commission numeric DEFAULT 0 NOT NULL,
    order_detail_id_cancelled integer
);


ALTER TABLE public.refund_detail OWNER TO springuser;

--
-- Name: refund_reason; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.refund_reason (
    uuid uuid NOT NULL,
    type character varying(255) NOT NULL,
    title character varying(255) NOT NULL
);


ALTER TABLE public.refund_reason OWNER TO springuser;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(20)
);


ALTER TABLE public.roles OWNER TO springuser;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO springuser;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: sales_rep_meta; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.sales_rep_meta (
    sales_rep_meta_id integer NOT NULL,
    calls_goal integer,
    commission_goal double precision,
    goal_month integer,
    goal_year integer,
    meetings_goal integer,
    sales_goal double precision,
    sales_rep_id uuid
);


ALTER TABLE public.sales_rep_meta OWNER TO springuser;

--
-- Name: sales_rep_selection; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.sales_rep_selection (
    id uuid NOT NULL,
    customer integer NOT NULL,
    factory integer NOT NULL,
    create_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    customer_selection_type character varying(255) NOT NULL
);


ALTER TABLE public.sales_rep_selection OWNER TO springuser;

--
-- Name: COLUMN sales_rep_selection.id; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.id IS 'Primary key';


--
-- Name: COLUMN sales_rep_selection.customer; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.customer IS 'Reference to Customers';


--
-- Name: COLUMN sales_rep_selection.factory; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.factory IS 'Reference to Factories';


--
-- Name: COLUMN sales_rep_selection.create_date; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.create_date IS 'Creation timestamp';


--
-- Name: COLUMN sales_rep_selection.created_by; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.created_by IS 'Creator''s UUID';


--
-- Name: COLUMN sales_rep_selection.customer_selection_type; Type: COMMENT; Schema: public; Owner: springuser
--

COMMENT ON COLUMN public.sales_rep_selection.customer_selection_type IS 'Whether to use the end user or customer during the selection process.  Mostly used for frontend and flowBot';


--
-- Name: session; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.session (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    expiration_date timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.session OWNER TO springuser;

--
-- Name: shortcuts; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.shortcuts (
    "shortcutsId" integer NOT NULL,
    description character varying(255),
    icon character varying(255),
    label character varying(255),
    link character varying(255),
    "useRouter" character varying(255)
);


ALTER TABLE public.shortcuts OWNER TO springuser;

--
-- Name: shortcuts_shortcutsId_seq; Type: SEQUENCE; Schema: public; Owner: springuser
--

CREATE SEQUENCE public."shortcuts_shortcutsId_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."shortcuts_shortcutsId_seq" OWNER TO springuser;

--
-- Name: shortcuts_shortcutsId_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: springuser
--

ALTER SEQUENCE public."shortcuts_shortcutsId_seq" OWNED BY public.shortcuts."shortcutsId";


--
-- Name: site_options; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.site_options (
    uuid uuid NOT NULL,
    key character varying(255) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.site_options OWNER TO springuser;

--
-- Name: site_settings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.site_settings (
    uuid uuid NOT NULL,
    company_name text,
    logo character varying(10485760),
    street_address text,
    address_two text,
    city text,
    state text,
    zip integer,
    create_date timestamp without time zone DEFAULT now(),
    email text,
    phone text,
    owner_id uuid,
    logo_width integer DEFAULT 192,
    logo_height integer
);


ALTER TABLE public.site_settings OWNER TO springuser;

--
-- Name: status; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.status (
    statusid integer NOT NULL,
    title character varying(255)
);


ALTER TABLE public.status OWNER TO springuser;

--
-- Name: support; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.support (
    "supportID" integer NOT NULL,
    email character varying(255) NOT NULL,
    message character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    subject character varying(255) NOT NULL,
    "inquiryType" character varying,
    "appPart" character varying,
    create_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.support OWNER TO springuser;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.tasks (
    id uuid NOT NULL,
    task_type character varying(255),
    created_at timestamp without time zone NOT NULL,
    read_at timestamp without time zone,
    completed_at timestamp without time zone,
    archived_at timestamp without time zone,
    task_body text,
    read boolean,
    archived boolean,
    completed boolean,
    urgent boolean,
    user_uuid uuid,
    assigned_by uuid,
    source_object character varying(255),
    source_id uuid,
    due_date timestamp without time zone
);


ALTER TABLE public.tasks OWNER TO springuser;

--
-- Name: territories; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.territories (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    title character varying(255) NOT NULL
);


ALTER TABLE public.territories OWNER TO springuser;

--
-- Name: tmp_checks; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.tmp_checks (
    "Customer" text,
    "End User" text,
    "Invoice" bigint,
    "PO" bigint,
    "FPN" text,
    "ORDER DATE" text,
    "INVOICE DATE" text,
    "QUANTITY" bigint,
    "UNIT PRICE" text,
    "total Invoice " text,
    "Commission" text
);


ALTER TABLE public.tmp_checks OWNER TO springuser;

--
-- Name: tmp_invoices_to_delete; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.tmp_invoices_to_delete (
    invoice_number text,
    factory text
);


ALTER TABLE public.tmp_invoices_to_delete OWNER TO springuser;

--
-- Name: unit_of_measures; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.unit_of_measures (
    title character varying(255) NOT NULL,
    uom_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    multiply boolean DEFAULT false,
    multiply_by double precision DEFAULT 1,
    description character varying(10000)
);


ALTER TABLE public.unit_of_measures OWNER TO springuser;

--
-- Name: upload_exceptions; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.upload_exceptions (
    upload_exception_id integer NOT NULL,
    uuid uuid NOT NULL,
    import_type character varying(255),
    file_name character varying(255),
    rows_with_alerts integer,
    rows_imported integer,
    rows_total integer,
    created_date timestamp without time zone,
    created_by uuid,
    created_by_name character varying(255),
    fields json
);


ALTER TABLE public.upload_exceptions OWNER TO springuser;

--
-- Name: upload_exceptions_details; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.upload_exceptions_details (
    upload_exception_detail_id integer NOT NULL,
    uuid uuid NOT NULL,
    upload_exception_id integer,
    error_message character varying(255),
    error_code integer,
    data json
);


ALTER TABLE public.upload_exceptions_details OWNER TO springuser;

--
-- Name: user_dashboard; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.user_dashboard (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version integer NOT NULL,
    last_updated timestamp without time zone,
    last_accessed timestamp without time zone,
    components json,
    user_uuid uuid,
    title character varying(255),
    sub_title character varying(255)
);


ALTER TABLE public.user_dashboard OWNER TO springuser;

--
-- Name: user_settings; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.user_settings (
    settings_id integer NOT NULL,
    theme character varying(255),
    scheme character varying(255),
    layout character varying(255),
    font_size character varying(255),
    id uuid
);


ALTER TABLE public.user_settings OWNER TO springuser;

--
-- Name: users; Type: TABLE; Schema: public; Owner: springuser
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying(255),
    email character varying(255),
    firstname character varying(255),
    lastname character varying(255),
    is_outside boolean DEFAULT false,
    is_inside boolean DEFAULT false,
    status boolean DEFAULT true,
    fullname character varying(255),
    keycloak_role integer NOT NULL,
    session_id uuid
);


ALTER TABLE public.users OWNER TO springuser;

--
-- Name: invoice_status id; Type: DEFAULT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_status ALTER COLUMN id SET DEFAULT nextval('public.invoice_status_id_seq'::regclass);


--
-- Name: order_status id; Type: DEFAULT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_status ALTER COLUMN id SET DEFAULT nextval('public.order_status_id_seq'::regclass);


--
-- Name: quote_status id; Type: DEFAULT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_status ALTER COLUMN id SET DEFAULT nextval('public.quote_status_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: shortcuts shortcutsId; Type: DEFAULT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.shortcuts ALTER COLUMN "shortcutsId" SET DEFAULT nextval('public."shortcuts_shortcutsId_seq"'::regclass);


--
-- Name: acl_privilege_option acl_privilege_option_detail_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege_option
    ADD CONSTRAINT acl_privilege_option_detail_key UNIQUE (detail);


--
-- Name: acl_privilege_option acl_privilege_option_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege_option
    ADD CONSTRAINT acl_privilege_option_pkey PRIMARY KEY (privilege_option_id);


--
-- Name: acl_privilege acl_privilege_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege
    ADD CONSTRAINT acl_privilege_pkey PRIMARY KEY (privilege_id);


--
-- Name: acl_privilege acl_privilege_privilege_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege
    ADD CONSTRAINT acl_privilege_privilege_key UNIQUE (privilege);


--
-- Name: acl_resource acl_resource_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_resource
    ADD CONSTRAINT acl_resource_pkey PRIMARY KEY (resource_id);


--
-- Name: acl_resource acl_resource_resource_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_resource
    ADD CONSTRAINT acl_resource_resource_key UNIQUE (resource);


--
-- Name: acl_role_option acl_role_option_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_option
    ADD CONSTRAINT acl_role_option_pkey PRIMARY KEY (uuid);


--
-- Name: addresses_log addresses_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.addresses_log
    ADD CONSTRAINT addresses_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: ar_report_metrics ar_report_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.ar_report_metrics
    ADD CONSTRAINT ar_report_metrics_pkey PRIMARY KEY (uuid);


--
-- Name: ar_report_model ar_report_model_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.ar_report_model
    ADD CONSTRAINT ar_report_model_pkey PRIMARY KEY (id);


--
-- Name: auto_generated_settings auto_generated_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.auto_generated_settings
    ADD CONSTRAINT auto_generated_settings_pkey PRIMARY KEY (uuid);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (uuid);


--
-- Name: checks_log checks_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_log
    ADD CONSTRAINT checks_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: company_targets company_targets_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.company_targets
    ADD CONSTRAINT company_targets_pkey PRIMARY KEY (company_targets_id);


--
-- Name: contacts_log contacts_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.contacts_log
    ADD CONSTRAINT contacts_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: customer_alias customer_alias_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customer_alias
    ADD CONSTRAINT customer_alias_pkey PRIMARY KEY (uuid);


--
-- Name: customer_rankings customer_rankings_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customer_rankings
    ADD CONSTRAINT customer_rankings_pkey PRIMARY KEY (ranking_id);


--
-- Name: customers_log customers_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers_log
    ADD CONSTRAINT customers_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: expense_category expense_category_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_category
    ADD CONSTRAINT expense_category_pkey PRIMARY KEY (uuid);


--
-- Name: expense_check expense_check_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_check
    ADD CONSTRAINT expense_check_pkey PRIMARY KEY (expense_uuid);


--
-- Name: expense expense_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT expense_pkey PRIMARY KEY (uuid);


--
-- Name: expense_sales_rep_split expense_sales_rep_split_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_sales_rep_split
    ADD CONSTRAINT expense_sales_rep_split_pkey PRIMARY KEY (uuid);


--
-- Name: factories_log factories_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factories_log
    ADD CONSTRAINT factories_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: factory_alias factory_alias_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_alias
    ADD CONSTRAINT factory_alias_pkey PRIMARY KEY (uuid);


--
-- Name: factory_metrics factory_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_metrics
    ADD CONSTRAINT factory_metrics_pkey PRIMARY KEY (uuid);


--
-- Name: factory_rankings factory_rankings_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_rankings
    ADD CONSTRAINT factory_rankings_pkey PRIMARY KEY (ranking_id);


--
-- Name: faq_categories faqcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.faq_categories
    ADD CONSTRAINT faqcategories_pkey PRIMARY KEY (id);


--
-- Name: file_upload file_upload_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload
    ADD CONSTRAINT file_upload_pkey PRIMARY KEY (uuid);


--
-- Name: file_upload_process file_upload_process_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload_process
    ADD CONSTRAINT file_upload_process_pkey PRIMARY KEY (uuid);


--
-- Name: guide_categories guidecategories_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.guide_categories
    ADD CONSTRAINT guidecategories_pkey PRIMARY KEY (id);


--
-- Name: guides guides_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.guides
    ADD CONSTRAINT guides_pkey PRIMARY KEY (id);


--
-- Name: hard_copies hard_copies_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.hard_copies
    ADD CONSTRAINT hard_copies_pkey PRIMARY KEY (hard_copy_id);


--
-- Name: instance_prediction instance_prediction_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.instance_prediction
    ADD CONSTRAINT instance_prediction_pkey PRIMARY KEY (id);


--
-- Name: invoices invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoice_pkey PRIMARY KEY (invoice_id);


--
-- Name: invoice_status invoice_status_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_status
    ADD CONSTRAINT invoice_status_pkey PRIMARY KEY (id);


--
-- Name: invoices_log invoices_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoices_log
    ADD CONSTRAINT invoices_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: lost_reasons lost_reasons_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.lost_reasons
    ADD CONSTRAINT lost_reasons_pkey PRIMARY KEY (uuid);


--
-- Name: notes_log notes_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.notes_log
    ADD CONSTRAINT notes_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: notifier_settings notifier_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.notifier_settings
    ADD CONSTRAINT notifier_settings_pkey PRIMARY KEY (uuid);


--
-- Name: order_acknowledgements order_acknowledgements_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_acknowledgements
    ADD CONSTRAINT order_acknowledgements_pkey PRIMARY KEY (uuid);


--
-- Name: order_status order_status_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_status
    ADD CONSTRAINT order_status_pkey PRIMARY KEY (id);


--
-- Name: orders_log orders_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders_log
    ADD CONSTRAINT orders_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: orders orders_order_number_customer_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_order_number_customer_key UNIQUE (order_number, customer);


--
-- Name: acl_role_resource pk_acl_role_resource; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_resource
    ADD CONSTRAINT pk_acl_role_resource PRIMARY KEY (role, resource_id, privilege_id);


--
-- Name: activity pk_activity; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.activity
    ADD CONSTRAINT pk_activity PRIMARY KEY (activity_id);


--
-- Name: addresses pk_addresses; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.addresses
    ADD CONSTRAINT pk_addresses PRIMARY KEY (uuid);


--
-- Name: alerts pk_alerts; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT pk_alerts PRIMARY KEY (alertid);


--
-- Name: cb pk_cb; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.cb
    ADD CONSTRAINT pk_cb PRIMARY KEY (title);


--
-- Name: checks pk_checks; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT pk_checks PRIMARY KEY (check_id);


--
-- Name: checks_details pk_checks_details; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_details
    ADD CONSTRAINT pk_checks_details PRIMARY KEY (checks_detail_id);


--
-- Name: checks_imports pk_checks_imports; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_imports
    ADD CONSTRAINT pk_checks_imports PRIMARY KEY (id);


--
-- Name: commission_discount_per_rep pk_commission_discount_per_rep; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.commission_discount_per_rep
    ADD CONSTRAINT pk_commission_discount_per_rep PRIMARY KEY (id);


--
-- Name: contacts pk_contacts; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT pk_contacts PRIMARY KEY (uuid);


--
-- Name: customers pk_customers; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);


--
-- Name: email_settings pk_email_settings; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.email_settings
    ADD CONSTRAINT pk_email_settings PRIMARY KEY (uuid);


--
-- Name: factories pk_factories; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT pk_factories PRIMARY KEY (factory_id);


--
-- Name: faqs pk_faqs; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT pk_faqs PRIMARY KEY (id);


--
-- Name: history pk_history; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.history
    ADD CONSTRAINT pk_history PRIMARY KEY (uuid);


--
-- Name: invoice_details pk_invoice_details; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT pk_invoice_details PRIMARY KEY (invoice_detail_id);


--
-- Name: notes pk_notes; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT pk_notes PRIMARY KEY (uuid);


--
-- Name: order_details pk_order_details; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT pk_order_details PRIMARY KEY (order_detail_id);


--
-- Name: order_sales_rep_split pk_order_sales_rep_split; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_sales_rep_split
    ADD CONSTRAINT pk_order_sales_rep_split PRIMARY KEY (id);


--
-- Name: orders pk_orders; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT pk_orders PRIMARY KEY (order_id);


--
-- Name: product_categories pk_product_categories; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT pk_product_categories PRIMARY KEY (uuid);


--
-- Name: products pk_products; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT pk_products PRIMARY KEY (product_id);


--
-- Name: quote_details pk_quote_details; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT pk_quote_details PRIMARY KEY (quote_detail_id);


--
-- Name: quote_sales_rep_split pk_quote_sales_rep_split; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_sales_rep_split
    ADD CONSTRAINT pk_quote_sales_rep_split PRIMARY KEY (id);


--
-- Name: quotes pk_quotes; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT pk_quotes PRIMARY KEY (quote_id);


--
-- Name: sales_rep_meta pk_sales_rep_meta; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.sales_rep_meta
    ADD CONSTRAINT pk_sales_rep_meta PRIMARY KEY (sales_rep_meta_id);


--
-- Name: session pk_session; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT pk_session PRIMARY KEY (id);


--
-- Name: site_settings pk_site_settings; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.site_settings
    ADD CONSTRAINT pk_site_settings PRIMARY KEY (uuid);


--
-- Name: status pk_status; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.status
    ADD CONSTRAINT pk_status PRIMARY KEY (statusid);


--
-- Name: upload_exceptions pk_upload_exceptions; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.upload_exceptions
    ADD CONSTRAINT pk_upload_exceptions PRIMARY KEY (upload_exception_id);


--
-- Name: upload_exceptions_details pk_upload_exceptions_details; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.upload_exceptions_details
    ADD CONSTRAINT pk_upload_exceptions_details PRIMARY KEY (upload_exception_detail_id);


--
-- Name: user_settings pk_user_settings; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT pk_user_settings PRIMARY KEY (settings_id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: precious_metals preciousMetals_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.precious_metals
    ADD CONSTRAINT "preciousMetals_pkey" PRIMARY KEY (metals_id);


--
-- Name: pricing_imports pricing_imports_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.pricing_imports
    ADD CONSTRAINT pricing_imports_pkey PRIMARY KEY (id);


--
-- Name: product_alias product_alias_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_alias
    ADD CONSTRAINT product_alias_pkey PRIMARY KEY (uuid);


--
-- Name: product_cpn product_cpn_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_cpn
    ADD CONSTRAINT product_cpn_pkey PRIMARY KEY (uuid);


--
-- Name: product_dimensions product_dimensions_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_dimensions
    ADD CONSTRAINT product_dimensions_pkey PRIMARY KEY (dimensions_id);


--
-- Name: product_tags product_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_tags
    ADD CONSTRAINT product_tags_pkey PRIMARY KEY (product_tag_id);


--
-- Name: products_log products_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products_log
    ADD CONSTRAINT products_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: quantity_pricing quantity_pricing_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quantity_pricing
    ADD CONSTRAINT quantity_pricing_pkey PRIMARY KEY (id);


--
-- Name: quote_status quote_status_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_status
    ADD CONSTRAINT quote_status_pkey PRIMARY KEY (id);


--
-- Name: quotes_log quotes_log_pk; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes_log
    ADD CONSTRAINT quotes_log_pk PRIMARY KEY (uuid, operation, "timestamp");


--
-- Name: quotes quotes_quote_number_factory_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT quotes_quote_number_factory_key UNIQUE (quote_number, factory_id);


--
-- Name: refund_balance refund_balance_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_balance
    ADD CONSTRAINT refund_balance_pkey PRIMARY KEY (refund_uuid);


--
-- Name: refund_check refund_check_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_check
    ADD CONSTRAINT refund_check_pkey PRIMARY KEY (refund_uuid);


--
-- Name: refund_detail refund_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_detail
    ADD CONSTRAINT refund_detail_pkey PRIMARY KEY (uuid);


--
-- Name: refund refund_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund
    ADD CONSTRAINT refund_pkey PRIMARY KEY (uuid);


--
-- Name: refund_reason refund_reason_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_reason
    ADD CONSTRAINT refund_reason_pkey PRIMARY KEY (uuid);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sales_rep_selection sales_rep_selection_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.sales_rep_selection
    ADD CONSTRAINT sales_rep_selection_pkey PRIMARY KEY (id);


--
-- Name: shortcuts shortcuts_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.shortcuts
    ADD CONSTRAINT shortcuts_pkey PRIMARY KEY ("shortcutsId");


--
-- Name: site_options site_options_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.site_options
    ADD CONSTRAINT site_options_pkey PRIMARY KEY (uuid);


--
-- Name: support support_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.support
    ADD CONSTRAINT support_pkey PRIMARY KEY ("supportID");


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: territories territories_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.territories
    ADD CONSTRAINT territories_pkey PRIMARY KEY (uuid);


--
-- Name: users uc_74165e195b2f7b25de690d14a; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uc_74165e195b2f7b25de690d14a UNIQUE (email);


--
-- Name: users uc_77584fbe74cc86922be2a3560; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uc_77584fbe74cc86922be2a3560 UNIQUE (username);


--
-- Name: product_categories uc_category_title_factory; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT uc_category_title_factory UNIQUE (title, factory_id);


--
-- Name: checks uc_check_number_factory; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT uc_check_number_factory UNIQUE (check_number, factory);


--
-- Name: checks_details uc_checks_details_invoice; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_details
    ADD CONSTRAINT uc_checks_details_invoice UNIQUE (invoice);


--
-- Name: sales_rep_selection uc_customer_factory; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.sales_rep_selection
    ADD CONSTRAINT uc_customer_factory UNIQUE (customer, factory);


--
-- Name: customers uc_customers_company_name; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT uc_customers_company_name UNIQUE (company_name);


--
-- Name: factories uc_factories_title; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT uc_factories_title UNIQUE (title);


--
-- Name: invoices uc_invoice_number_factory; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT uc_invoice_number_factory UNIQUE (invoice_number, factory_id);


--
-- Name: notifier_settings uc_notifier_settings_user_id_alert_type; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.notifier_settings
    ADD CONSTRAINT uc_notifier_settings_user_id_alert_type UNIQUE (user_id, alert_type);


--
-- Name: order_sales_rep_split uc_order_detail_split_rate_per_user; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_sales_rep_split
    ADD CONSTRAINT uc_order_detail_split_rate_per_user UNIQUE (order_detail_id, split_rate, user_id);


--
-- Name: product_categories uc_product_categories_uuid; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT uc_product_categories_uuid UNIQUE (uuid);


--
-- Name: product_cpn uc_product_customer_part_number; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_cpn
    ADD CONSTRAINT uc_product_customer_part_number UNIQUE (product_id, customer_id, customer_part_number);


--
-- Name: products uc_products_factory_part_number_factory_id; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT uc_products_factory_part_number_factory_id UNIQUE (factory_part_number, factory_id);


--
-- Name: quote_sales_rep_split uc_quote_detail_split_rate_per_user; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_sales_rep_split
    ADD CONSTRAINT uc_quote_detail_split_rate_per_user UNIQUE (quote_detail_id, split_rate, user_id);


--
-- Name: upload_exceptions_details uc_upload_exceptions_details_uuid; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.upload_exceptions_details
    ADD CONSTRAINT uc_upload_exceptions_details_uuid UNIQUE (uuid);


--
-- Name: upload_exceptions uc_upload_exceptions_uuid; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.upload_exceptions
    ADD CONSTRAINT uc_upload_exceptions_uuid UNIQUE (uuid);


--
-- Name: checks uc_uuid_checks; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT uc_uuid_checks UNIQUE (uuid);


--
-- Name: customers uc_uuid_customers; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT uc_uuid_customers UNIQUE (uuid);


--
-- Name: factories uc_uuid_factories; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT uc_uuid_factories UNIQUE (uuid);


--
-- Name: products uc_uuid_products; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT uc_uuid_products UNIQUE (uuid);


--
-- Name: product_tags uk_5urwbjsgtuors6s29yxk33uum; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_tags
    ADD CONSTRAINT uk_5urwbjsgtuors6s29yxk33uum UNIQUE (tag);


--
-- Name: acl_role_option uk_acl_role_option_role_key; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_option
    ADD CONSTRAINT uk_acl_role_option_role_key UNIQUE (role, key);


--
-- Name: ar_report_metrics uk_ar_report_metrics_metric_type_computed_month; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.ar_report_metrics
    ADD CONSTRAINT uk_ar_report_metrics_metric_type_computed_month UNIQUE (metric_type, computed_month);


--
-- Name: customer_alias uk_customer_alias_customer_uuid_alias; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customer_alias
    ADD CONSTRAINT uk_customer_alias_customer_uuid_alias UNIQUE (customer_uuid, alias);


--
-- Name: expense_category uk_expense_category_title; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_category
    ADD CONSTRAINT uk_expense_category_title UNIQUE (title);


--
-- Name: factory_alias uk_factory_alias_factory_uuid_alias; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_alias
    ADD CONSTRAINT uk_factory_alias_factory_uuid_alias UNIQUE (factory_uuid, alias);


--
-- Name: file_upload uk_file_upload_file_name; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload
    ADD CONSTRAINT uk_file_upload_file_name UNIQUE (file_path);


--
-- Name: product_alias uk_product_alias_product_uuid_alias; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_alias
    ADD CONSTRAINT uk_product_alias_product_uuid_alias UNIQUE (product_uuid, alias);


--
-- Name: refund uk_refund_factory_uuid_refund_number; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund
    ADD CONSTRAINT uk_refund_factory_uuid_refund_number UNIQUE (factory_uuid, refund_number);


--
-- Name: refund_reason uk_refund_reason_type_title; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_reason
    ADD CONSTRAINT uk_refund_reason_type_title UNIQUE (type, title);


--
-- Name: instance_prediction unique_instance_prediction; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.instance_prediction
    ADD CONSTRAINT unique_instance_prediction UNIQUE (instance_id, instance_type);


--
-- Name: unit_of_measures unit_of_measures_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.unit_of_measures
    ADD CONSTRAINT unit_of_measures_pkey PRIMARY KEY (uom_id);


--
-- Name: user_dashboard user_dashboard_pkey; Type: CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.user_dashboard
    ADD CONSTRAINT user_dashboard_pkey PRIMARY KEY (id);


--
-- Name: idx_addresses_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_addresses_history_change ON public.addresses_log USING btree (uuid, operation);


--
-- Name: idx_checks_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_checks_history_change ON public.checks_log USING btree (uuid, operation);


--
-- Name: idx_contacts_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_contacts_history_change ON public.contacts_log USING btree (uuid, operation);


--
-- Name: idx_customers_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_customers_history_change ON public.customers_log USING btree (uuid, operation);


--
-- Name: idx_factories_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_factories_history_change ON public.factories_log USING btree (uuid, operation);


--
-- Name: idx_invoices_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_invoices_history_change ON public.invoices_log USING btree (uuid, operation);


--
-- Name: idx_is_inside; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_is_inside ON public.users USING btree (is_inside);


--
-- Name: idx_is_outside; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_is_outside ON public.users USING btree (is_outside);


--
-- Name: idx_keycloak_role; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_keycloak_role ON public.users USING btree (keycloak_role);


--
-- Name: idx_notes_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_notes_history_change ON public.notes_log USING btree (uuid, operation);


--
-- Name: idx_orders_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_orders_history_change ON public.orders_log USING btree (uuid, operation);


--
-- Name: idx_products_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_products_history_change ON public.products_log USING btree (uuid, operation);


--
-- Name: idx_quotes_history_change; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX idx_quotes_history_change ON public.quotes_log USING btree (uuid, operation);


--
-- Name: lower_case_customer_part_number; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX lower_case_customer_part_number ON public.product_cpn USING btree (lower((customer_part_number)::text));


--
-- Name: lower_case_factory_part_number; Type: INDEX; Schema: public; Owner: springuser
--

CREATE INDEX lower_case_factory_part_number ON public.products USING btree (lower((factory_part_number)::text));


--
-- Name: addresses addresses_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER addresses_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.addresses FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('addresses_log');


--
-- Name: checks checks_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER checks_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.checks FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('checks_log');


--
-- Name: contacts contacts_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER contacts_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.contacts FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('contacts_log');


--
-- Name: customers customers_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER customers_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.customers FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('customers_log');


--
-- Name: factories factories_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER factories_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.factories FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('factories_log');


--
-- Name: invoices invoices_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER invoices_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.invoices FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('invoices_log');


--
-- Name: notes notes_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER notes_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.notes FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('notes_log');


--
-- Name: orders orders_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER orders_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('orders_log');


--
-- Name: products products_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER products_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.products FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('products_log');


--
-- Name: quotes quotes_log_trigger; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER quotes_log_trigger AFTER INSERT OR DELETE OR UPDATE ON public.quotes FOR EACH ROW EXECUTE FUNCTION public.audit_trigger_func('quotes_log');


--
-- Name: quotes update_update_date_column; Type: TRIGGER; Schema: public; Owner: springuser
--

CREATE TRIGGER update_update_date_column BEFORE UPDATE ON public.quotes FOR EACH ROW EXECUTE FUNCTION public.update_update_date_column();


--
-- Name: guides fk4o4gcg6lca9l9cmy5s89h8xhs; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.guides
    ADD CONSTRAINT fk4o4gcg6lca9l9cmy5s89h8xhs FOREIGN KEY (category_id) REFERENCES public.guide_categories(id);


--
-- Name: invoices fk5etmb6cv3jhg896xsnitiqm5m; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT fk5etmb6cv3jhg896xsnitiqm5m FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: acl_privilege_option_relation fk_acl_privilege_option_relation_privilege_id_on_acl_privilege; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege_option_relation
    ADD CONSTRAINT fk_acl_privilege_option_relation_privilege_id_on_acl_privilege FOREIGN KEY (privilege_id) REFERENCES public.acl_privilege(privilege_id) ON DELETE CASCADE;


--
-- Name: acl_privilege_option_relation fk_acl_privilege_option_relation_privilege_option_id_on_acl_pri; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_privilege_option_relation
    ADD CONSTRAINT fk_acl_privilege_option_relation_privilege_option_id_on_acl_pri FOREIGN KEY (privilege_option_id) REFERENCES public.acl_privilege_option(privilege_option_id) ON DELETE CASCADE;


--
-- Name: acl_role_resource fk_acl_role_resource_privilege_option_id_on_acl_privilege_optio; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_resource
    ADD CONSTRAINT fk_acl_role_resource_privilege_option_id_on_acl_privilege_optio FOREIGN KEY (privilege_option_id) REFERENCES public.acl_privilege_option(privilege_option_id);


--
-- Name: acl_role_resource fk_acl_role_resource_resource_id_on_acl_privilege; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_resource
    ADD CONSTRAINT fk_acl_role_resource_resource_id_on_acl_privilege FOREIGN KEY (privilege_id) REFERENCES public.acl_privilege(privilege_id) ON DELETE CASCADE;


--
-- Name: acl_role_resource fk_acl_role_resource_resource_id_on_acl_resource; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.acl_role_resource
    ADD CONSTRAINT fk_acl_role_resource_resource_id_on_acl_resource FOREIGN KEY (resource_id) REFERENCES public.acl_resource(resource_id) ON DELETE CASCADE;


--
-- Name: alerts fk_alerts_on_user_for; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.alerts
    ADD CONSTRAINT fk_alerts_on_user_for FOREIGN KEY (user_for) REFERENCES public.users(id);


--
-- Name: instance_prediction fk_ar_report_model_id; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.instance_prediction
    ADD CONSTRAINT fk_ar_report_model_id FOREIGN KEY (ar_report_model_id) REFERENCES public.ar_report_model(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: checks_details fk_checks_details_on_check; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_details
    ADD CONSTRAINT fk_checks_details_on_check FOREIGN KEY (check_id) REFERENCES public.checks(check_id);


--
-- Name: checks_details fk_checks_details_on_invoice; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks_details
    ADD CONSTRAINT fk_checks_details_on_invoice FOREIGN KEY (invoice) REFERENCES public.invoices(invoice_id);


--
-- Name: checks fk_checks_on_factory; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.checks
    ADD CONSTRAINT fk_checks_on_factory FOREIGN KEY (factory) REFERENCES public.factories(factory_id);


--
-- Name: customer_alias fk_customer_alias_customer_uuid_on_customers; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customer_alias
    ADD CONSTRAINT fk_customer_alias_customer_uuid_on_customers FOREIGN KEY (customer_uuid) REFERENCES public.customers(uuid) ON DELETE CASCADE;


--
-- Name: customers fk_customers_branch_id; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT fk_customers_branch_id FOREIGN KEY (branch_id) REFERENCES public.branches(uuid);


--
-- Name: default_outside_rep_customer_split fk_customers_default_outside_rep_customer_split; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.default_outside_rep_customer_split
    ADD CONSTRAINT fk_customers_default_outside_rep_customer_split FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- Name: customers fk_customers_on_inside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT fk_customers_on_inside_rep FOREIGN KEY (inside_rep_id) REFERENCES public.users(id);


--
-- Name: customers fk_customers_on_outside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT fk_customers_on_outside_rep FOREIGN KEY (outside_rep_id) REFERENCES public.users(id);


--
-- Name: customers fk_customers_territory_id; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT fk_customers_territory_id FOREIGN KEY (territory_id) REFERENCES public.territories(uuid);


--
-- Name: default_outside_rep_split fk_default_sales_rep_selection; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.default_outside_rep_split
    ADD CONSTRAINT fk_default_sales_rep_selection FOREIGN KEY (selection_id) REFERENCES public.sales_rep_selection(id) ON DELETE CASCADE;


--
-- Name: expense_check fk_expense_check_check_uuid_on_checks; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_check
    ADD CONSTRAINT fk_expense_check_check_uuid_on_checks FOREIGN KEY (check_uuid) REFERENCES public.checks(uuid) ON DELETE CASCADE;


--
-- Name: expense_check fk_expense_check_expense_uuid_on_expense; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_check
    ADD CONSTRAINT fk_expense_check_expense_uuid_on_expense FOREIGN KEY (expense_uuid) REFERENCES public.expense(uuid) ON DELETE CASCADE;


--
-- Name: expense fk_expense_created_by_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT fk_expense_created_by_on_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: expense fk_expense_customer_uuid_on_customers; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT fk_expense_customer_uuid_on_customers FOREIGN KEY (customer_uuid) REFERENCES public.customers(uuid);


--
-- Name: expense fk_expense_expense_category_on_expense_category; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT fk_expense_expense_category_on_expense_category FOREIGN KEY (expense_category_uuid) REFERENCES public.expense_category(uuid);


--
-- Name: expense fk_expense_factory_uuid_on_factories; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense
    ADD CONSTRAINT fk_expense_factory_uuid_on_factories FOREIGN KEY (factory_uuid) REFERENCES public.factories(uuid);


--
-- Name: expense_sales_rep_split fk_expense_sales_rep_split_expense_uuid_on_expense; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_sales_rep_split
    ADD CONSTRAINT fk_expense_sales_rep_split_expense_uuid_on_expense FOREIGN KEY (expense_uuid) REFERENCES public.expense(uuid);


--
-- Name: expense_sales_rep_split fk_expense_sales_rep_split_user_id_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.expense_sales_rep_split
    ADD CONSTRAINT fk_expense_sales_rep_split_user_id_on_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: factories fk_factories_inside_rep_id_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT fk_factories_inside_rep_id_on_users FOREIGN KEY (inside_rep_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: factory_alias fk_factory_alias_factory_uuid_on_factories; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_alias
    ADD CONSTRAINT fk_factory_alias_factory_uuid_on_factories FOREIGN KEY (factory_uuid) REFERENCES public.factories(uuid) ON DELETE CASCADE;


--
-- Name: factory_metrics fk_factory_metrics_factory_uuid_on_factories; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.factory_metrics
    ADD CONSTRAINT fk_factory_metrics_factory_uuid_on_factories FOREIGN KEY (factory_uuid) REFERENCES public.factories(uuid) ON DELETE CASCADE;


--
-- Name: faqs fk_faqs_on_categoryid; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT fk_faqs_on_categoryid FOREIGN KEY (category_id) REFERENCES public.faq_categories(id);


--
-- Name: file_upload fk_file_upload_created_by_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload
    ADD CONSTRAINT fk_file_upload_created_by_on_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: file_upload_process fk_file_upload_process_file_upload_uuid_on_file_upload; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload_process
    ADD CONSTRAINT fk_file_upload_process_file_upload_uuid_on_file_upload FOREIGN KEY (file_upload_uuid) REFERENCES public.file_upload(uuid);


--
-- Name: file_upload_process fk_file_upload_process_parent_process_uuid_on_file_upload_proce; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.file_upload_process
    ADD CONSTRAINT fk_file_upload_process_parent_process_uuid_on_file_upload_proce FOREIGN KEY (parent_process_uuid) REFERENCES public.file_upload_process(uuid);


--
-- Name: invoice_details fk_invoice_details_on_end_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT fk_invoice_details_on_end_user FOREIGN KEY (end_user) REFERENCES public.customers(customer_id);


--
-- Name: invoice_details fk_invoice_details_on_invoice; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT fk_invoice_details_on_invoice FOREIGN KEY (invoice_id) REFERENCES public.invoices(invoice_id);


--
-- Name: invoice_details fk_invoice_details_on_outside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT fk_invoice_details_on_outside_rep FOREIGN KEY (outside_rep_id) REFERENCES public.users(id);


--
-- Name: invoice_details fk_invoice_details_on_product; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT fk_invoice_details_on_product FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: invoice_details fk_invoice_details_on_status; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoice_details
    ADD CONSTRAINT fk_invoice_details_on_status FOREIGN KEY (status) REFERENCES public.invoice_status(id);


--
-- Name: order_details fk_order_details_on_end_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT fk_order_details_on_end_user FOREIGN KEY (end_user) REFERENCES public.customers(customer_id);


--
-- Name: order_details fk_order_details_on_order; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT fk_order_details_on_order FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- Name: order_details fk_order_details_on_outside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT fk_order_details_on_outside_rep FOREIGN KEY (outside_rep_id) REFERENCES public.users(id);


--
-- Name: order_details fk_order_details_on_product; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT fk_order_details_on_product FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: order_details fk_order_details_on_status; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_details
    ADD CONSTRAINT fk_order_details_on_status FOREIGN KEY (status) REFERENCES public.order_status(id);


--
-- Name: order_sales_rep_split fk_order_sales_rep_split_on_detail; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.order_sales_rep_split
    ADD CONSTRAINT fk_order_sales_rep_split_on_detail FOREIGN KEY (order_detail_id) REFERENCES public.order_details(order_detail_id);


--
-- Name: orders fk_orders_on_customer; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_on_customer FOREIGN KEY (customer) REFERENCES public.customers(customer_id);


--
-- Name: orders fk_orders_on_factory; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_on_factory FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: orders fk_orders_on_status; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_on_status FOREIGN KEY (status) REFERENCES public.order_status(id);


--
-- Name: default_outside_rep_split fk_outside_rep_split_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.default_outside_rep_split
    ADD CONSTRAINT fk_outside_rep_split_user FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: product_alias fk_product_alias_product_uuid_on_products; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_alias
    ADD CONSTRAINT fk_product_alias_product_uuid_on_products FOREIGN KEY (product_uuid) REFERENCES public.products(uuid) ON DELETE CASCADE;


--
-- Name: product_categories fk_product_categories_factories; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_categories
    ADD CONSTRAINT fk_product_categories_factories FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: product_cpn fk_product_cpn_on_customers; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_cpn
    ADD CONSTRAINT fk_product_cpn_on_customers FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- Name: product_cpn fk_product_cpn_on_product; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.product_cpn
    ADD CONSTRAINT fk_product_cpn_on_product FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


--
-- Name: products fk_product_dimensions; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_product_dimensions FOREIGN KEY (dimensions_id) REFERENCES public.product_dimensions(dimensions_id);


--
-- Name: quantity_pricing fk_product_qty_pricing; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quantity_pricing
    ADD CONSTRAINT fk_product_qty_pricing FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: products fk_product_unit_of_measures; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_product_unit_of_measures FOREIGN KEY (uom_id) REFERENCES public.unit_of_measures(uom_id);


--
-- Name: products fk_products_on_category_uuid; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_on_category_uuid FOREIGN KEY (category_uuid) REFERENCES public.product_categories(uuid);


--
-- Name: products fk_products_on_factory; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_on_factory FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: quote_details fk_quote_details_on_end_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT fk_quote_details_on_end_user FOREIGN KEY (end_user) REFERENCES public.customers(customer_id);


--
-- Name: quote_details fk_quote_details_on_outside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT fk_quote_details_on_outside_rep FOREIGN KEY (outside_rep_id) REFERENCES public.users(id);


--
-- Name: quote_details fk_quote_details_on_product; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT fk_quote_details_on_product FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: quote_details fk_quote_details_on_quote; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT fk_quote_details_on_quote FOREIGN KEY (quote_id) REFERENCES public.quotes(quote_id);


--
-- Name: quote_details fk_quote_details_on_status; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_details
    ADD CONSTRAINT fk_quote_details_on_status FOREIGN KEY (status) REFERENCES public.quote_status(id);


--
-- Name: quote_sales_rep_split fk_quote_sales_rep_split_on_detail; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quote_sales_rep_split
    ADD CONSTRAINT fk_quote_sales_rep_split_on_detail FOREIGN KEY (quote_detail_id) REFERENCES public.quote_details(quote_detail_id);


--
-- Name: quotes fk_quotes_on_customer; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT fk_quotes_on_customer FOREIGN KEY (customer) REFERENCES public.customers(customer_id);


--
-- Name: quotes fk_quotes_on_end_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT fk_quotes_on_end_user FOREIGN KEY (end_user) REFERENCES public.customers(customer_id);


--
-- Name: quotes fk_quotes_on_factory; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT fk_quotes_on_factory FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: quotes fk_quotes_on_outside_rep; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.quotes
    ADD CONSTRAINT fk_quotes_on_outside_rep FOREIGN KEY (outside_rep_id) REFERENCES public.users(id);


--
-- Name: refund_balance fk_refund_balance_refund_uuid_on_refund; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_balance
    ADD CONSTRAINT fk_refund_balance_refund_uuid_on_refund FOREIGN KEY (refund_uuid) REFERENCES public.refund(uuid) ON DELETE CASCADE;


--
-- Name: refund_detail fk_refund_balance_refund_uuid_on_refund; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_detail
    ADD CONSTRAINT fk_refund_balance_refund_uuid_on_refund FOREIGN KEY (refund_uuid) REFERENCES public.refund(uuid) ON DELETE CASCADE;


--
-- Name: refund_check fk_refund_check_check_uuid_on_checks; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_check
    ADD CONSTRAINT fk_refund_check_check_uuid_on_checks FOREIGN KEY (check_uuid) REFERENCES public.checks(uuid) ON DELETE CASCADE;


--
-- Name: refund_check fk_refund_check_refund_uuid_on_refund; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_check
    ADD CONSTRAINT fk_refund_check_refund_uuid_on_refund FOREIGN KEY (refund_uuid) REFERENCES public.refund(uuid) ON DELETE CASCADE;


--
-- Name: refund fk_refund_created_by_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund
    ADD CONSTRAINT fk_refund_created_by_on_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: refund_detail fk_refund_detail_order_detail_id_cancelled_on_order_details; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_detail
    ADD CONSTRAINT fk_refund_detail_order_detail_id_cancelled_on_order_details FOREIGN KEY (order_detail_id_cancelled) REFERENCES public.order_details(order_detail_id);


--
-- Name: refund_detail fk_refund_detail_order_detail_id_on_order_details; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_detail
    ADD CONSTRAINT fk_refund_detail_order_detail_id_on_order_details FOREIGN KEY (order_detail_id) REFERENCES public.order_details(order_detail_id) ON DELETE CASCADE;


--
-- Name: refund_detail fk_refund_detail_refund_reason_uuid_on_refund_reason; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund_detail
    ADD CONSTRAINT fk_refund_detail_refund_reason_uuid_on_refund_reason FOREIGN KEY (refund_reason_uuid) REFERENCES public.refund_reason(uuid);


--
-- Name: refund fk_refund_factory_uuid_on_factories; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund
    ADD CONSTRAINT fk_refund_factory_uuid_on_factories FOREIGN KEY (factory_uuid) REFERENCES public.factories(uuid);


--
-- Name: refund fk_refund_order_id_on_orders; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.refund
    ADD CONSTRAINT fk_refund_order_id_on_orders FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: sales_rep_selection fk_sales_rep_selection_customer; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.sales_rep_selection
    ADD CONSTRAINT fk_sales_rep_selection_customer FOREIGN KEY (customer) REFERENCES public.customers(customer_id);


--
-- Name: sales_rep_selection fk_sales_rep_selection_factory; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.sales_rep_selection
    ADD CONSTRAINT fk_sales_rep_selection_factory FOREIGN KEY (factory) REFERENCES public.factories(factory_id);


--
-- Name: tasks fk_tasks_assigned_by; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_assigned_by FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: tasks fk_tasks_user; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_uuid) REFERENCES public.users(id);


--
-- Name: upload_exceptions_details fk_upload_details_on_upload_exceptions; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.upload_exceptions_details
    ADD CONSTRAINT fk_upload_details_on_upload_exceptions FOREIGN KEY (upload_exception_id) REFERENCES public.upload_exceptions(upload_exception_id);


--
-- Name: user_dashboard fk_user_dashboard_user_uuid_on_users; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.user_dashboard
    ADD CONSTRAINT fk_user_dashboard_user_uuid_on_users FOREIGN KEY (user_uuid) REFERENCES public.users(id);


--
-- Name: default_outside_rep_customer_split fk_user_id_on_default_outside_rep_customer_split; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.default_outside_rep_customer_split
    ADD CONSTRAINT fk_user_id_on_default_outside_rep_customer_split FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: default_outside_rep_split fk_user_id_on_default_outside_rep_split; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.default_outside_rep_split
    ADD CONSTRAINT fk_user_id_on_default_outside_rep_split FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: session fk_user_id_on_session; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT fk_user_id_on_session FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_settings fk_user_settings_on_id; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT fk_user_settings_on_id FOREIGN KEY (id) REFERENCES public.users(id);


--
-- Name: users fk_users_keycloak_role; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_keycloak_role FOREIGN KEY (keycloak_role) REFERENCES public.roles(id);


--
-- Name: notifier_settings fk_users_notifier_settings; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.notifier_settings
    ADD CONSTRAINT fk_users_notifier_settings FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: invoices fkeul9e1byynvvkcon3pt0rs9os; Type: FK CONSTRAINT; Schema: public; Owner: springuser
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT fkeul9e1byynvvkcon3pt0rs9os FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- Name: checks; Type: ROW SECURITY; Schema: public; Owner: springuser
--

ALTER TABLE public.checks ENABLE ROW LEVEL SECURITY;

--
-- Name: checks checks_policy; Type: POLICY; Schema: public; Owner: springuser
--

CREATE POLICY checks_policy ON public.checks TO springuser USING (
CASE
    WHEN ((public.get_current_option())::text = 'all'::text) THEN true
    WHEN (((public.get_current_resource())::text = 'checks'::text) AND ((public.get_current_option())::text = 'own'::text)) THEN (created_by = (public.get_user_id())::uuid)
    ELSE true
END) WITH CHECK (true);


--
-- Name: invoices; Type: ROW SECURITY; Schema: public; Owner: springuser
--

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

--
-- Name: invoices invoices_policy; Type: POLICY; Schema: public; Owner: springuser
--

CREATE POLICY invoices_policy ON public.invoices TO springuser USING ((((public.get_current_option())::text = 'all'::text) OR (EXISTS ( SELECT 1
   FROM public.orders o
  WHERE ((o.order_id = invoices.order_id) AND ((public.get_user_id())::uuid = ANY (o.user_uuids))))))) WITH CHECK (true);


--
-- Name: orders; Type: ROW SECURITY; Schema: public; Owner: springuser
--

ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

--
-- Name: orders orders_policy; Type: POLICY; Schema: public; Owner: springuser
--

CREATE POLICY orders_policy ON public.orders TO springuser USING ((((public.get_current_option())::text = 'all'::text) OR ((public.get_current_resource())::text <> 'orders'::text) OR ((public.get_user_id())::uuid = ANY (user_uuids)))) WITH CHECK (true);


--
-- Name: quotes; Type: ROW SECURITY; Schema: public; Owner: springuser
--

ALTER TABLE public.quotes ENABLE ROW LEVEL SECURITY;

--
-- Name: quotes quotes_policy; Type: POLICY; Schema: public; Owner: springuser
--

CREATE POLICY quotes_policy ON public.quotes TO springuser USING ((((public.get_current_option())::text = 'all'::text) OR ((public.get_current_resource())::text <> 'quotes'::text) OR ((public.get_user_id())::uuid = ANY (user_uuids)))) WITH CHECK (true);


--
-- Name: SCHEMA aiven_extras; Type: ACL; Schema: -; Owner: doadmin
--

REVOKE ALL ON SCHEMA aiven_extras FROM doadmin;
GRANT CREATE ON SCHEMA aiven_extras TO doadmin;
GRANT USAGE ON SCHEMA aiven_extras TO doadmin WITH GRANT OPTION;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;
GRANT ALL ON SCHEMA public TO springuser;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO doadmin WITH GRANT OPTION;


--
-- Name: FOREIGN DATA WRAPPER postgres_fdw; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON FOREIGN DATA WRAPPER postgres_fdw TO doadmin WITH GRANT OPTION;


--
-- Name: FOREIGN SERVER tenant; Type: ACL; Schema: -; Owner: doadmin
--

GRANT ALL ON FOREIGN SERVER tenant TO springuser;


--
-- Name: TABLE pg_stat_replication; Type: ACL; Schema: aiven_extras; Owner: postgres
--

GRANT SELECT ON TABLE aiven_extras.pg_stat_replication TO doadmin WITH GRANT OPTION;


--
-- Name: TABLE acl_privilege; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_privilege TO kamal;


--
-- Name: TABLE acl_privilege_option; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_privilege_option TO kamal;


--
-- Name: TABLE acl_privilege_option_relation; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_privilege_option_relation TO kamal;


--
-- Name: TABLE acl_resource; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_resource TO kamal;


--
-- Name: TABLE acl_role_option; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_role_option TO kamal;


--
-- Name: TABLE acl_role_resource; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.acl_role_resource TO kamal;


--
-- Name: TABLE activity; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.activity TO kamal;


--
-- Name: TABLE addresses; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.addresses TO kamal;


--
-- Name: TABLE addresses_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.addresses_log TO kamal;


--
-- Name: TABLE alerts; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.alerts TO kamal;


--
-- Name: TABLE ar_report_metrics; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.ar_report_metrics TO kamal;


--
-- Name: TABLE ar_report_model; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.ar_report_model TO kamal;


--
-- Name: TABLE auto_generated_settings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.auto_generated_settings TO kamal;


--
-- Name: TABLE branches; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.branches TO kamal;


--
-- Name: TABLE cb; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.cb TO kamal;


--
-- Name: TABLE checks; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.checks TO kamal;


--
-- Name: TABLE checks_details; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.checks_details TO kamal;


--
-- Name: TABLE checks_imports; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.checks_imports TO kamal;


--
-- Name: TABLE checks_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.checks_log TO kamal;


--
-- Name: TABLE commission_discount_per_rep; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.commission_discount_per_rep TO kamal;


--
-- Name: TABLE company_targets; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.company_targets TO kamal;


--
-- Name: TABLE contacts; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.contacts TO kamal;


--
-- Name: TABLE contacts_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.contacts_log TO kamal;


--
-- Name: TABLE customer_alias; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.customer_alias TO kamal;


--
-- Name: TABLE customers; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.customers TO kamal;


--
-- Name: TABLE customer_rankings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.customer_rankings TO kamal;


--
-- Name: TABLE customers_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.customers_log TO kamal;


--
-- Name: TABLE databasechangelog; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.databasechangelog TO kamal;


--
-- Name: TABLE databasechangeloglock; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.databasechangeloglock TO kamal;


--
-- Name: TABLE default_outside_rep_customer_split; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.default_outside_rep_customer_split TO kamal;


--
-- Name: TABLE default_outside_rep_split; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.default_outside_rep_split TO kamal;


--
-- Name: TABLE email_settings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.email_settings TO kamal;


--
-- Name: TABLE expense; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.expense TO kamal;


--
-- Name: TABLE expense_category; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.expense_category TO kamal;


--
-- Name: TABLE expense_check; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.expense_check TO kamal;


--
-- Name: TABLE expense_sales_rep_split; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.expense_sales_rep_split TO kamal;


--
-- Name: TABLE factories; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.factories TO kamal;


--
-- Name: TABLE factories_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.factories_log TO kamal;


--
-- Name: TABLE factory_alias; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.factory_alias TO kamal;


--
-- Name: TABLE factory_metrics; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.factory_metrics TO kamal;


--
-- Name: TABLE factory_rankings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.factory_rankings TO kamal;


--
-- Name: TABLE faq_categories; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.faq_categories TO kamal;


--
-- Name: TABLE faqs; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.faqs TO kamal;


--
-- Name: TABLE file_upload; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.file_upload TO kamal;


--
-- Name: TABLE file_upload_process; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.file_upload_process TO kamal;


--
-- Name: TABLE guide_categories; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.guide_categories TO kamal;


--
-- Name: TABLE guides; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.guides TO kamal;


--
-- Name: TABLE hard_copies; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.hard_copies TO kamal;


--
-- Name: TABLE history; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.history TO kamal;


--
-- Name: TABLE instance_prediction; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.instance_prediction TO kamal;


--
-- Name: TABLE invoice_details; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.invoice_details TO kamal;


--
-- Name: TABLE invoice_status; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.invoice_status TO kamal;


--
-- Name: TABLE invoices; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.invoices TO kamal;


--
-- Name: TABLE invoices_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.invoices_log TO kamal;


--
-- Name: TABLE lost_reasons; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.lost_reasons TO kamal;


--
-- Name: TABLE notes; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.notes TO kamal;


--
-- Name: TABLE notes_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.notes_log TO kamal;


--
-- Name: TABLE notifier_settings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.notifier_settings TO kamal;


--
-- Name: TABLE order_acknowledgements; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.order_acknowledgements TO kamal;


--
-- Name: TABLE order_details; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.order_details TO kamal;


--
-- Name: TABLE order_sales_rep_split; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.order_sales_rep_split TO kamal;


--
-- Name: TABLE order_status; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.order_status TO kamal;


--
-- Name: TABLE orders; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.orders TO kamal;


--
-- Name: TABLE orders_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.orders_log TO kamal;


--
-- Name: TABLE precious_metals; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.precious_metals TO kamal;


--
-- Name: TABLE pricing_imports; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.pricing_imports TO kamal;


--
-- Name: TABLE product_alias; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.product_alias TO kamal;


--
-- Name: TABLE product_categories; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.product_categories TO kamal;


--
-- Name: TABLE product_cpn; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.product_cpn TO kamal;


--
-- Name: TABLE product_dimensions; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.product_dimensions TO kamal;


--
-- Name: TABLE product_tags; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.product_tags TO kamal;


--
-- Name: TABLE products; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.products TO kamal;


--
-- Name: TABLE products_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.products_log TO kamal;


--
-- Name: TABLE quantity_pricing; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quantity_pricing TO kamal;


--
-- Name: TABLE quote_details; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quote_details TO kamal;


--
-- Name: TABLE quote_sales_rep_split; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quote_sales_rep_split TO kamal;


--
-- Name: TABLE quote_status; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quote_status TO kamal;


--
-- Name: TABLE quotes; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quotes TO kamal;


--
-- Name: TABLE quotes_log; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.quotes_log TO kamal;


--
-- Name: TABLE refund; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.refund TO kamal;


--
-- Name: TABLE refund_balance; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.refund_balance TO kamal;


--
-- Name: TABLE refund_check; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.refund_check TO kamal;


--
-- Name: TABLE refund_detail; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.refund_detail TO kamal;


--
-- Name: TABLE refund_reason; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.refund_reason TO kamal;


--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.roles TO kamal;


--
-- Name: TABLE sales_rep_meta; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.sales_rep_meta TO kamal;


--
-- Name: TABLE sales_rep_selection; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.sales_rep_selection TO kamal;


--
-- Name: TABLE session; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.session TO kamal;


--
-- Name: TABLE shortcuts; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.shortcuts TO kamal;


--
-- Name: TABLE site_options; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.site_options TO kamal;


--
-- Name: TABLE site_settings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.site_settings TO kamal;


--
-- Name: TABLE status; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.status TO kamal;


--
-- Name: TABLE support; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.support TO kamal;


--
-- Name: TABLE tasks; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.tasks TO kamal;


--
-- Name: TABLE territories; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.territories TO kamal;


--
-- Name: TABLE tmp_checks; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.tmp_checks TO kamal;


--
-- Name: TABLE tmp_invoices_to_delete; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.tmp_invoices_to_delete TO kamal;


--
-- Name: TABLE unit_of_measures; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.unit_of_measures TO kamal;


--
-- Name: TABLE upload_exceptions; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.upload_exceptions TO kamal;


--
-- Name: TABLE upload_exceptions_details; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.upload_exceptions_details TO kamal;


--
-- Name: TABLE user_dashboard; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.user_dashboard TO kamal;


--
-- Name: TABLE user_settings; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.user_settings TO kamal;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: springuser
--

GRANT SELECT ON TABLE public.users TO kamal;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: doadmin
--

ALTER DEFAULT PRIVILEGES FOR ROLE doadmin IN SCHEMA public GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO springuser;


--
-- PostgreSQL database dump complete
--

\unrestrict nUTjWcTDM7VExUVh7WPvGUvIfItvpJirBAbNGZqCne7HHkpAXA682qzQ1NJP1g9

