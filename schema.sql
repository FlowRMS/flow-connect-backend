--
-- PostgreSQL database dump
--

\restrict b9NgO7dr9hbTexDIXshuMKMjAxdMgTsL0x1exaWHoxTRqwg8kzg6VcqUZIBYvry

-- Dumped from database version 17.7 (bdc8956)
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
-- Name: pycommission; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA pycommission;


ALTER SCHEMA pycommission OWNER TO neondb_owner;

--
-- Name: pycore; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA pycore;


ALTER SCHEMA pycore OWNER TO neondb_owner;

--
-- Name: pycrm; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA pycrm;


ALTER SCHEMA pycrm OWNER TO neondb_owner;

--
-- Name: pyfiles; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA pyfiles;


ALTER SCHEMA pyfiles OWNER TO neondb_owner;

--
-- Name: pyuser; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA pyuser;


ALTER SCHEMA pyuser OWNER TO neondb_owner;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO neondb_owner;

--
-- Name: order_balances; Type: TABLE; Schema: pycommission; Owner: neondb_owner
--

CREATE TABLE pycommission.order_balances (
    quantity numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    subtotal numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    shipping_balance numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    cancelled_balance numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    freight_charge_balance numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycommission.order_balances OWNER TO neondb_owner;

--
-- Name: order_details; Type: TABLE; Schema: pycommission; Owner: neondb_owner
--

CREATE TABLE pycommission.order_details (
    order_id uuid NOT NULL,
    item_number integer NOT NULL,
    quantity numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    unit_price numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    subtotal numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total_line_commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    division_factor numeric(18,6),
    product_id uuid,
    product_name_adhoc character varying(255),
    product_description_adhoc text,
    factory_id uuid,
    end_user_id uuid,
    uom_id uuid,
    lead_time character varying(255),
    note character varying(2000),
    status smallint DEFAULT '1'::smallint NOT NULL,
    freight_charge numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    shipping_balance numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    cancelled_balance numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycommission.order_details OWNER TO neondb_owner;

--
-- Name: order_inside_reps; Type: TABLE; Schema: pycommission; Owner: neondb_owner
--

CREATE TABLE pycommission.order_inside_reps (
    user_id uuid NOT NULL,
    split_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    order_detail_id uuid
);


ALTER TABLE pycommission.order_inside_reps OWNER TO neondb_owner;

--
-- Name: order_split_rates; Type: TABLE; Schema: pycommission; Owner: neondb_owner
--

CREATE TABLE pycommission.order_split_rates (
    order_detail_id uuid NOT NULL,
    user_id uuid NOT NULL,
    split_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycommission.order_split_rates OWNER TO neondb_owner;

--
-- Name: orders; Type: TABLE; Schema: pycommission; Owner: neondb_owner
--

CREATE TABLE pycommission.orders (
    order_number character varying(255) NOT NULL,
    entity_date date NOT NULL,
    due_date date NOT NULL,
    sold_to_customer_id uuid NOT NULL,
    bill_to_customer_id uuid,
    published boolean DEFAULT false NOT NULL,
    creation_type smallint DEFAULT '0'::smallint NOT NULL,
    status smallint DEFAULT '1'::smallint NOT NULL,
    order_type smallint DEFAULT '1'::smallint NOT NULL,
    header_status smallint DEFAULT '1'::smallint NOT NULL,
    factory_id uuid,
    shipping_terms character varying(255),
    freight_terms character varying(255),
    mark_number character varying(255),
    ship_date date,
    projected_ship_date date,
    fact_so_number character varying(255),
    quote_id uuid,
    balance_id uuid NOT NULL,
    id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    job_id uuid
);


ALTER TABLE pycommission.orders OWNER TO neondb_owner;

--
-- Name: addresses; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.addresses (
    id uuid NOT NULL,
    source_id uuid NOT NULL,
    source_type smallint NOT NULL,
    address_type smallint DEFAULT '4'::smallint NOT NULL,
    line_1 character varying(255) NOT NULL,
    line_2 character varying(255),
    city character varying(100) NOT NULL,
    state character varying(100),
    zip_code character varying(20) NOT NULL,
    country character varying(100) NOT NULL,
    notes text,
    is_primary boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.addresses OWNER TO neondb_owner;

--
-- Name: customer_factory_sales_reps; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.customer_factory_sales_reps (
    id uuid NOT NULL,
    customer_id uuid NOT NULL,
    factory_id uuid NOT NULL,
    user_id uuid NOT NULL,
    rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.customer_factory_sales_reps OWNER TO neondb_owner;

--
-- Name: customer_split_rates; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.customer_split_rates (
    user_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    rep_type smallint NOT NULL,
    "position" integer NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.customer_split_rates OWNER TO neondb_owner;

--
-- Name: customers; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.customers (
    company_name character varying NOT NULL,
    parent_id uuid,
    published boolean NOT NULL,
    is_parent boolean NOT NULL,
    id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.customers OWNER TO neondb_owner;

--
-- Name: factories; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.factories (
    title character varying NOT NULL,
    account_number character varying(255),
    email character varying(255),
    phone character varying(50),
    logo_id uuid,
    lead_time integer,
    payment_terms integer,
    base_commission_rate numeric(5,2) NOT NULL,
    commission_discount_rate numeric(5,2) NOT NULL,
    overall_discount_rate numeric(5,2) NOT NULL,
    additional_information text,
    freight_terms text,
    external_payment_terms text,
    published boolean NOT NULL,
    freight_discount_type smallint NOT NULL,
    creation_type smallint NOT NULL,
    id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.factories OWNER TO neondb_owner;

--
-- Name: factory_split_rates; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.factory_split_rates (
    user_id uuid NOT NULL,
    factory_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    "position" integer NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.factory_split_rates OWNER TO neondb_owner;

--
-- Name: product_categories; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.product_categories (
    title character varying NOT NULL,
    commission_rate numeric NOT NULL,
    factory_id uuid,
    parent_id uuid,
    grandparent_id uuid,
    id uuid NOT NULL
);


ALTER TABLE pycore.product_categories OWNER TO neondb_owner;

--
-- Name: product_cpns; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.product_cpns (
    product_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    customer_part_number character varying NOT NULL,
    unit_price double precision NOT NULL,
    commission_rate double precision NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycore.product_cpns OWNER TO neondb_owner;

--
-- Name: product_quantity_pricing; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.product_quantity_pricing (
    product_id uuid NOT NULL,
    quantity_low numeric NOT NULL,
    quantity_high numeric NOT NULL,
    unit_price numeric NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycore.product_quantity_pricing OWNER TO neondb_owner;

--
-- Name: product_uoms; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.product_uoms (
    title character varying NOT NULL,
    creation_type smallint NOT NULL,
    description character varying,
    id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    division_factor numeric(18,6)
);


ALTER TABLE pycore.product_uoms OWNER TO neondb_owner;

--
-- Name: products; Type: TABLE; Schema: pycore; Owner: neondb_owner
--

CREATE TABLE pycore.products (
    factory_part_number character varying NOT NULL,
    unit_price numeric NOT NULL,
    default_commission_rate numeric NOT NULL,
    factory_id uuid NOT NULL,
    product_category_id uuid,
    product_uom_id uuid,
    published boolean NOT NULL,
    approval_needed boolean,
    description character varying,
    creation_type smallint NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    upc character varying(50),
    default_divisor numeric,
    min_order_qty numeric,
    lead_time integer,
    unit_price_discount_rate numeric,
    commission_discount_rate numeric,
    approval_date date,
    approval_comments text,
    tags character varying[]
);


ALTER TABLE pycore.products OWNER TO neondb_owner;

--
-- Name: campaign_criteria; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.campaign_criteria (
    campaign_id uuid NOT NULL,
    criteria_json jsonb NOT NULL,
    is_dynamic boolean NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycrm.campaign_criteria OWNER TO neondb_owner;

--
-- Name: campaign_recipients; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.campaign_recipients (
    campaign_id uuid NOT NULL,
    contact_id uuid NOT NULL,
    email_status smallint NOT NULL,
    sent_at timestamp with time zone,
    personalized_content text,
    id uuid NOT NULL
);


ALTER TABLE pycrm.campaign_recipients OWNER TO neondb_owner;

--
-- Name: campaign_send_logs; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.campaign_send_logs (
    campaign_id uuid NOT NULL,
    send_date date NOT NULL,
    emails_sent integer NOT NULL,
    last_sent_at timestamp with time zone,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.campaign_send_logs OWNER TO neondb_owner;

--
-- Name: campaigns; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.campaigns (
    name character varying(255) NOT NULL,
    recipient_list_type smallint NOT NULL,
    status smallint NOT NULL,
    description text,
    email_subject character varying(500),
    email_body text,
    ai_personalization_enabled boolean,
    send_pace smallint,
    max_emails_per_day integer,
    scheduled_at timestamp with time zone,
    send_immediately boolean,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.campaigns OWNER TO neondb_owner;

--
-- Name: companies; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.companies (
    name character varying(255) NOT NULL,
    company_source_type smallint NOT NULL,
    website character varying(255),
    phone character varying(50),
    tags character varying[],
    parent_company_id uuid,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.companies OWNER TO neondb_owner;

--
-- Name: contacts; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.contacts (
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255),
    phone character varying(50),
    role character varying(100),
    territory character varying(100),
    tags character varying[],
    notes text,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.contacts OWNER TO neondb_owner;

--
-- Name: gmail_user_tokens; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.gmail_user_tokens (
    user_id uuid NOT NULL,
    google_user_id character varying(255) NOT NULL,
    google_email character varying(255) NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    scope text NOT NULL,
    is_active boolean NOT NULL,
    last_used_at timestamp with time zone,
    token_type character varying(50) NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.gmail_user_tokens OWNER TO neondb_owner;

--
-- Name: job_statuses; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.job_statuses (
    name character varying(100) NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycrm.job_statuses OWNER TO neondb_owner;

--
-- Name: jobs; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.jobs (
    job_name character varying(255) NOT NULL,
    status_id uuid NOT NULL,
    start_date date,
    end_date date,
    job_type text,
    structural_details text,
    structural_information text,
    additional_information text,
    description text,
    requester_id uuid,
    job_owner_id uuid,
    tags character varying[],
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.jobs OWNER TO neondb_owner;

--
-- Name: link_relations; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.link_relations (
    source_entity_type smallint NOT NULL,
    source_entity_id uuid NOT NULL,
    target_entity_type smallint NOT NULL,
    target_entity_id uuid NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.link_relations OWNER TO neondb_owner;

--
-- Name: manufacturer_order; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.manufacturer_order (
    factory_id uuid NOT NULL,
    sort_order integer NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycrm.manufacturer_order OWNER TO neondb_owner;

--
-- Name: note_conversations; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.note_conversations (
    note_id uuid NOT NULL,
    content text NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.note_conversations OWNER TO neondb_owner;

--
-- Name: notes; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.notes (
    title character varying(255) NOT NULL,
    content text NOT NULL,
    tags character varying[],
    mentions uuid[],
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.notes OWNER TO neondb_owner;

--
-- Name: o365_user_tokens; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.o365_user_tokens (
    user_id uuid NOT NULL,
    microsoft_user_id character varying(255) NOT NULL,
    microsoft_email character varying(255) NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    scope text NOT NULL,
    is_active boolean NOT NULL,
    last_used_at timestamp with time zone,
    token_type character varying(50) NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.o365_user_tokens OWNER TO neondb_owner;

--
-- Name: pre_opportunities; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.pre_opportunities (
    status smallint NOT NULL,
    entity_number character varying(255) NOT NULL,
    entity_date date NOT NULL,
    exp_date date,
    revise_date date,
    accept_date date,
    sold_to_customer_id uuid NOT NULL,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    job_id uuid,
    balance_id uuid NOT NULL,
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    tags character varying[],
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.pre_opportunities OWNER TO neondb_owner;

--
-- Name: pre_opportunity_balances; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.pre_opportunity_balances (
    subtotal numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    total numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    quantity numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    discount numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycrm.pre_opportunity_balances OWNER TO neondb_owner;

--
-- Name: pre_opportunity_details; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.pre_opportunity_details (
    pre_opportunity_id uuid NOT NULL,
    quantity numeric(10,2) NOT NULL,
    item_number integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    total numeric(10,2) NOT NULL,
    subtotal numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    discount numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    product_id uuid NOT NULL,
    product_cpn_id uuid,
    end_user_id uuid NOT NULL,
    lead_time character varying(255),
    id uuid NOT NULL,
    quote_id uuid
);


ALTER TABLE pycrm.pre_opportunity_details OWNER TO neondb_owner;

--
-- Name: quote_balances; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quote_balances (
    quantity numeric(18,6) DEFAULT 0 NOT NULL,
    subtotal numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pycrm.quote_balances OWNER TO neondb_owner;

--
-- Name: quote_details; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quote_details (
    quote_id uuid NOT NULL,
    item_number integer NOT NULL,
    quantity numeric(18,6) DEFAULT 0 NOT NULL,
    unit_price numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    subtotal numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    total_line_commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    commission_discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    discount numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    product_id uuid,
    product_name_adhoc character varying(255),
    product_description_adhoc text,
    factory_id uuid,
    end_user_id uuid,
    lead_time character varying(255),
    note character varying(2000),
    status smallint DEFAULT '0'::smallint NOT NULL,
    lost_reason_id uuid,
    id uuid NOT NULL,
    uom_id uuid,
    division_factor numeric(18,6),
    order_id uuid
);


ALTER TABLE pycrm.quote_details OWNER TO neondb_owner;

--
-- Name: quote_inside_reps; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quote_inside_reps (
    user_id uuid NOT NULL,
    split_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    quote_detail_id uuid
);


ALTER TABLE pycrm.quote_inside_reps OWNER TO neondb_owner;

--
-- Name: quote_lost_reasons; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quote_lost_reasons (
    created_by_id uuid NOT NULL,
    title character varying NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.quote_lost_reasons OWNER TO neondb_owner;

--
-- Name: quote_split_rates; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quote_split_rates (
    quote_detail_id uuid NOT NULL,
    user_id uuid NOT NULL,
    split_rate numeric(18,6) DEFAULT '0'::numeric NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.quote_split_rates OWNER TO neondb_owner;

--
-- Name: quotes; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.quotes (
    quote_number character varying(255) NOT NULL,
    entity_date date NOT NULL,
    sold_to_customer_id uuid NOT NULL,
    bill_to_customer_id uuid,
    published boolean DEFAULT false NOT NULL,
    creation_type smallint DEFAULT '0'::smallint NOT NULL,
    status smallint DEFAULT '0'::smallint NOT NULL,
    pipeline_stage smallint DEFAULT '0'::smallint NOT NULL,
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    exp_date date,
    revise_date date,
    accept_date date,
    blanket boolean DEFAULT false NOT NULL,
    duplicated_from uuid,
    version_of uuid,
    balance_id uuid NOT NULL,
    id uuid NOT NULL,
    created_by_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    job_id uuid
);


ALTER TABLE pycrm.quotes OWNER TO neondb_owner;

--
-- Name: spec_sheet_highlight_regions; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.spec_sheet_highlight_regions (
    version_id uuid NOT NULL,
    page_number integer NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    width double precision NOT NULL,
    height double precision NOT NULL,
    shape_type character varying(50) NOT NULL,
    color character varying(20) NOT NULL,
    annotation text,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pycrm.spec_sheet_highlight_regions OWNER TO neondb_owner;

--
-- Name: spec_sheet_highlight_versions; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.spec_sheet_highlight_versions (
    spec_sheet_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    version_number integer NOT NULL,
    is_active boolean NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.spec_sheet_highlight_versions OWNER TO neondb_owner;

--
-- Name: spec_sheets; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.spec_sheets (
    factory_id uuid NOT NULL,
    file_name character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    upload_source character varying(50) NOT NULL,
    source_url text,
    file_url text NOT NULL,
    file_size bigint NOT NULL,
    categories character varying[] NOT NULL,
    tags character varying[],
    folder_path character varying(500),
    page_count integer NOT NULL,
    needs_review boolean NOT NULL,
    published boolean NOT NULL,
    usage_count integer NOT NULL,
    highlight_count integer NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.spec_sheets OWNER TO neondb_owner;

--
-- Name: task_conversations; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.task_conversations (
    task_id uuid NOT NULL,
    content text NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.task_conversations OWNER TO neondb_owner;

--
-- Name: tasks; Type: TABLE; Schema: pycrm; Owner: neondb_owner
--

CREATE TABLE pycrm.tasks (
    title character varying(255) NOT NULL,
    status smallint NOT NULL,
    priority smallint NOT NULL,
    description text,
    assigned_to_id uuid,
    due_date date,
    reminder_date date,
    tags character varying[],
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pycrm.tasks OWNER TO neondb_owner;

--
-- Name: files; Type: TABLE; Schema: pyfiles; Owner: neondb_owner
--

CREATE TABLE pyfiles.files (
    file_name character varying(500) NOT NULL,
    file_path character varying(2000) NOT NULL,
    file_size integer NOT NULL,
    file_type smallint,
    file_sha character varying(64),
    archived boolean NOT NULL,
    folder_id uuid,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pyfiles.files OWNER TO neondb_owner;

--
-- Name: folders; Type: TABLE; Schema: pyfiles; Owner: neondb_owner
--

CREATE TABLE pyfiles.folders (
    name character varying(255) NOT NULL,
    description text,
    parent_id uuid,
    archived boolean NOT NULL,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL
);


ALTER TABLE pyfiles.folders OWNER TO neondb_owner;

--
-- Name: rbac_permissions; Type: TABLE; Schema: pyuser; Owner: neondb_owner
--

CREATE TABLE pyuser.rbac_permissions (
    role integer NOT NULL,
    resource integer NOT NULL,
    privilege integer NOT NULL,
    option integer NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE pyuser.rbac_permissions OWNER TO neondb_owner;

--
-- Name: users; Type: TABLE; Schema: pyuser; Owner: neondb_owner
--

CREATE TABLE pyuser.users (
    username character varying NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    auth_provider_id character varying NOT NULL,
    role smallint NOT NULL,
    enabled boolean NOT NULL,
    inside boolean,
    outside boolean,
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE pyuser.users OWNER TO neondb_owner;

--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: order_balances order_balances_pkey; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_balances
    ADD CONSTRAINT order_balances_pkey PRIMARY KEY (id);


--
-- Name: order_details order_details_pkey; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_pkey PRIMARY KEY (id);


--
-- Name: order_inside_reps order_inside_reps_pkey; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_inside_reps
    ADD CONSTRAINT order_inside_reps_pkey PRIMARY KEY (id);


--
-- Name: order_split_rates order_split_rates_pkey; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_split_rates
    ADD CONSTRAINT order_split_rates_pkey PRIMARY KEY (id);


--
-- Name: orders orders_balance_id_key; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_balance_id_key UNIQUE (balance_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: customer_factory_sales_reps customer_factory_sales_reps_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_factory_sales_reps
    ADD CONSTRAINT customer_factory_sales_reps_pkey PRIMARY KEY (id);


--
-- Name: customer_split_rates customer_split_rates_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_split_rates
    ADD CONSTRAINT customer_split_rates_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: factories factories_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factories
    ADD CONSTRAINT factories_pkey PRIMARY KEY (id);


--
-- Name: factory_split_rates factory_split_rates_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factory_split_rates
    ADD CONSTRAINT factory_split_rates_pkey PRIMARY KEY (id);


--
-- Name: product_categories product_categories_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_categories
    ADD CONSTRAINT product_categories_pkey PRIMARY KEY (id);


--
-- Name: product_cpns product_cpns_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_cpns
    ADD CONSTRAINT product_cpns_pkey PRIMARY KEY (id);


--
-- Name: product_quantity_pricing product_quantity_pricing_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_quantity_pricing
    ADD CONSTRAINT product_quantity_pricing_pkey PRIMARY KEY (id);


--
-- Name: product_uoms product_uoms_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_uoms
    ADD CONSTRAINT product_uoms_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: customer_factory_sales_reps uq_customer_factory_user; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_factory_sales_reps
    ADD CONSTRAINT uq_customer_factory_user UNIQUE (customer_id, factory_id, user_id);


--
-- Name: customers uq_customers_company_name; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customers
    ADD CONSTRAINT uq_customers_company_name UNIQUE (company_name);


--
-- Name: factories uq_factories_title; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factories
    ADD CONSTRAINT uq_factories_title UNIQUE (title);


--
-- Name: product_categories uq_product_categories_title_factory; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_categories
    ADD CONSTRAINT uq_product_categories_title_factory UNIQUE (title, factory_id);


--
-- Name: product_uoms uq_product_uoms_title; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_uoms
    ADD CONSTRAINT uq_product_uoms_title UNIQUE (title);


--
-- Name: products uq_products_fpn_factory; Type: CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT uq_products_fpn_factory UNIQUE (factory_part_number, factory_id);


--
-- Name: campaign_criteria campaign_criteria_campaign_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT campaign_criteria_campaign_id_key UNIQUE (campaign_id);


--
-- Name: campaign_criteria campaign_criteria_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT campaign_criteria_pkey PRIMARY KEY (id);


--
-- Name: campaign_recipients campaign_recipients_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT campaign_recipients_pkey PRIMARY KEY (id);


--
-- Name: campaign_send_logs campaign_send_logs_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT campaign_send_logs_pkey PRIMARY KEY (id);


--
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: gmail_user_tokens gmail_user_tokens_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT gmail_user_tokens_pkey PRIMARY KEY (id);


--
-- Name: gmail_user_tokens gmail_user_tokens_user_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT gmail_user_tokens_user_id_key UNIQUE (user_id);


--
-- Name: job_statuses job_statuses_name_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.job_statuses
    ADD CONSTRAINT job_statuses_name_key UNIQUE (name);


--
-- Name: job_statuses job_statuses_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.job_statuses
    ADD CONSTRAINT job_statuses_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_job_name_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_job_name_key UNIQUE (job_name);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: link_relations link_relations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.link_relations
    ADD CONSTRAINT link_relations_pkey PRIMARY KEY (id);


--
-- Name: manufacturer_order manufacturer_order_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.manufacturer_order
    ADD CONSTRAINT manufacturer_order_pkey PRIMARY KEY (id);


--
-- Name: note_conversations note_conversations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.note_conversations
    ADD CONSTRAINT note_conversations_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: o365_user_tokens o365_user_tokens_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT o365_user_tokens_pkey PRIMARY KEY (id);


--
-- Name: o365_user_tokens o365_user_tokens_user_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT o365_user_tokens_user_id_key UNIQUE (user_id);


--
-- Name: pre_opportunities pre_opportunities_balance_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_balance_id_key UNIQUE (balance_id);


--
-- Name: pre_opportunities pre_opportunities_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_pkey PRIMARY KEY (id);


--
-- Name: pre_opportunity_balances pre_opportunity_balances_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_balances
    ADD CONSTRAINT pre_opportunity_balances_pkey PRIMARY KEY (id);


--
-- Name: pre_opportunity_details pre_opportunity_details_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT pre_opportunity_details_pkey PRIMARY KEY (id);


--
-- Name: quote_balances quote_balances_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_balances
    ADD CONSTRAINT quote_balances_pkey PRIMARY KEY (id);


--
-- Name: quote_details quote_details_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_pkey PRIMARY KEY (id);


--
-- Name: quote_inside_reps quote_inside_reps_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_inside_reps
    ADD CONSTRAINT quote_inside_reps_pkey PRIMARY KEY (id);


--
-- Name: quote_lost_reasons quote_lost_reasons_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_lost_reasons
    ADD CONSTRAINT quote_lost_reasons_pkey PRIMARY KEY (id);


--
-- Name: quote_split_rates quote_split_rates_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_split_rates
    ADD CONSTRAINT quote_split_rates_pkey PRIMARY KEY (id);


--
-- Name: quotes quotes_balance_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_balance_id_key UNIQUE (balance_id);


--
-- Name: quotes quotes_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_pkey PRIMARY KEY (id);


--
-- Name: spec_sheet_highlight_regions spec_sheet_highlight_regions_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_regions
    ADD CONSTRAINT spec_sheet_highlight_regions_pkey PRIMARY KEY (id);


--
-- Name: spec_sheet_highlight_versions spec_sheet_highlight_versions_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT spec_sheet_highlight_versions_pkey PRIMARY KEY (id);


--
-- Name: spec_sheets spec_sheets_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheets
    ADD CONSTRAINT spec_sheets_pkey PRIMARY KEY (id);


--
-- Name: task_conversations task_conversations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.task_conversations
    ADD CONSTRAINT task_conversations_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: campaign_send_logs uq_campaign_send_date; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT uq_campaign_send_date UNIQUE (campaign_id, send_date);


--
-- Name: quotes uq_quote_number_sold_to; Type: CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT uq_quote_number_sold_to UNIQUE (quote_number, sold_to_customer_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: folders folders_pkey; Type: CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (id);


--
-- Name: rbac_permissions rbac_permissions_pkey; Type: CONSTRAINT; Schema: pyuser; Owner: neondb_owner
--

ALTER TABLE ONLY pyuser.rbac_permissions
    ADD CONSTRAINT rbac_permissions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: pyuser; Owner: neondb_owner
--

ALTER TABLE ONLY pyuser.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_addresses_source; Type: INDEX; Schema: pycore; Owner: neondb_owner
--

CREATE INDEX ix_addresses_source ON pycore.addresses USING btree (source_type, source_id);


--
-- Name: ix_customer_factory_sales_reps_customer_factory; Type: INDEX; Schema: pycore; Owner: neondb_owner
--

CREATE INDEX ix_customer_factory_sales_reps_customer_factory ON pycore.customer_factory_sales_reps USING btree (customer_id, factory_id);


--
-- Name: ix_pycore_product_quantity_pricing_product_id; Type: INDEX; Schema: pycore; Owner: neondb_owner
--

CREATE INDEX ix_pycore_product_quantity_pricing_product_id ON pycore.product_quantity_pricing USING btree (product_id);


--
-- Name: ix_pycrm_manufacturer_order_factory_id; Type: INDEX; Schema: pycrm; Owner: neondb_owner
--

CREATE INDEX ix_pycrm_manufacturer_order_factory_id ON pycrm.manufacturer_order USING btree (factory_id);


--
-- Name: ix_pycrm_spec_sheet_highlight_regions_version_id; Type: INDEX; Schema: pycrm; Owner: neondb_owner
--

CREATE INDEX ix_pycrm_spec_sheet_highlight_regions_version_id ON pycrm.spec_sheet_highlight_regions USING btree (version_id);


--
-- Name: ix_pycrm_spec_sheet_highlight_versions_spec_sheet_id; Type: INDEX; Schema: pycrm; Owner: neondb_owner
--

CREATE INDEX ix_pycrm_spec_sheet_highlight_versions_spec_sheet_id ON pycrm.spec_sheet_highlight_versions USING btree (spec_sheet_id);


--
-- Name: ix_pycrm_spec_sheets_factory_id; Type: INDEX; Schema: pycrm; Owner: neondb_owner
--

CREATE INDEX ix_pycrm_spec_sheets_factory_id ON pycrm.spec_sheets USING btree (factory_id);


--
-- Name: ix_pycrm_spec_sheets_folder_path; Type: INDEX; Schema: pycrm; Owner: neondb_owner
--

CREATE INDEX ix_pycrm_spec_sheets_folder_path ON pycrm.spec_sheets USING btree (folder_path);


--
-- Name: order_details order_details_end_user_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_end_user_id_fkey FOREIGN KEY (end_user_id) REFERENCES pycore.customers(id);


--
-- Name: order_details order_details_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: order_details order_details_order_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_order_id_fkey FOREIGN KEY (order_id) REFERENCES pycommission.orders(id);


--
-- Name: order_details order_details_product_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_product_id_fkey FOREIGN KEY (product_id) REFERENCES pycore.products(id);


--
-- Name: order_details order_details_uom_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_details
    ADD CONSTRAINT order_details_uom_id_fkey FOREIGN KEY (uom_id) REFERENCES pycore.product_uoms(id);


--
-- Name: order_inside_reps order_inside_reps_order_detail_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_inside_reps
    ADD CONSTRAINT order_inside_reps_order_detail_id_fkey FOREIGN KEY (order_detail_id) REFERENCES pycommission.order_details(id);


--
-- Name: order_inside_reps order_inside_reps_user_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_inside_reps
    ADD CONSTRAINT order_inside_reps_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: order_split_rates order_split_rates_order_detail_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_split_rates
    ADD CONSTRAINT order_split_rates_order_detail_id_fkey FOREIGN KEY (order_detail_id) REFERENCES pycommission.order_details(id);


--
-- Name: order_split_rates order_split_rates_user_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.order_split_rates
    ADD CONSTRAINT order_split_rates_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: orders orders_balance_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES pycommission.order_balances(id);


--
-- Name: orders orders_bill_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_bill_to_customer_id_fkey FOREIGN KEY (bill_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: orders orders_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: orders orders_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: orders orders_job_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_job_id_fkey FOREIGN KEY (job_id) REFERENCES pycrm.jobs(id);


--
-- Name: orders orders_quote_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES pycrm.quotes(id);


--
-- Name: orders orders_sold_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycommission; Owner: neondb_owner
--

ALTER TABLE ONLY pycommission.orders
    ADD CONSTRAINT orders_sold_to_customer_id_fkey FOREIGN KEY (sold_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: customer_split_rates customer_split_rates_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_split_rates
    ADD CONSTRAINT customer_split_rates_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES pycore.customers(id);


--
-- Name: customer_split_rates customer_split_rates_user_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_split_rates
    ADD CONSTRAINT customer_split_rates_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: customers customers_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customers
    ADD CONSTRAINT customers_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: customers customers_parent_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customers
    ADD CONSTRAINT customers_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES pycore.customers(id);


--
-- Name: factories factories_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factories
    ADD CONSTRAINT factories_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: factories factories_logo_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factories
    ADD CONSTRAINT factories_logo_id_fkey FOREIGN KEY (logo_id) REFERENCES pyfiles.files(id);


--
-- Name: factory_split_rates factory_split_rates_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factory_split_rates
    ADD CONSTRAINT factory_split_rates_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: factory_split_rates factory_split_rates_user_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.factory_split_rates
    ADD CONSTRAINT factory_split_rates_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: customer_factory_sales_reps fk_customer_factory_sales_reps_customer_id; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_factory_sales_reps
    ADD CONSTRAINT fk_customer_factory_sales_reps_customer_id FOREIGN KEY (customer_id) REFERENCES pycore.customers(id);


--
-- Name: customer_factory_sales_reps fk_customer_factory_sales_reps_factory_id; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_factory_sales_reps
    ADD CONSTRAINT fk_customer_factory_sales_reps_factory_id FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: customer_factory_sales_reps fk_customer_factory_sales_reps_user_id; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.customer_factory_sales_reps
    ADD CONSTRAINT fk_customer_factory_sales_reps_user_id FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: product_categories product_categories_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_categories
    ADD CONSTRAINT product_categories_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: product_categories product_categories_grandparent_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_categories
    ADD CONSTRAINT product_categories_grandparent_id_fkey FOREIGN KEY (grandparent_id) REFERENCES pycore.product_categories(id);


--
-- Name: product_categories product_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_categories
    ADD CONSTRAINT product_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES pycore.product_categories(id);


--
-- Name: product_cpns product_cpns_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_cpns
    ADD CONSTRAINT product_cpns_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES pycore.customers(id);


--
-- Name: product_cpns product_cpns_product_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_cpns
    ADD CONSTRAINT product_cpns_product_id_fkey FOREIGN KEY (product_id) REFERENCES pycore.products(id);


--
-- Name: product_quantity_pricing product_quantity_pricing_product_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_quantity_pricing
    ADD CONSTRAINT product_quantity_pricing_product_id_fkey FOREIGN KEY (product_id) REFERENCES pycore.products(id);


--
-- Name: product_uoms product_uoms_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.product_uoms
    ADD CONSTRAINT product_uoms_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: products products_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT products_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: products products_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT products_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: products products_product_category_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT products_product_category_id_fkey FOREIGN KEY (product_category_id) REFERENCES pycore.product_categories(id);


--
-- Name: products products_product_uom_id_fkey; Type: FK CONSTRAINT; Schema: pycore; Owner: neondb_owner
--

ALTER TABLE ONLY pycore.products
    ADD CONSTRAINT products_product_uom_id_fkey FOREIGN KEY (product_uom_id) REFERENCES pycore.product_uoms(id);


--
-- Name: campaign_criteria campaign_criteria_campaign_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT campaign_criteria_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id);


--
-- Name: campaign_recipients campaign_recipients_campaign_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT campaign_recipients_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id);


--
-- Name: campaign_recipients campaign_recipients_contact_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT campaign_recipients_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES pycrm.contacts(id);


--
-- Name: campaign_send_logs campaign_send_logs_campaign_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT campaign_send_logs_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id);


--
-- Name: campaigns campaigns_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.campaigns
    ADD CONSTRAINT campaigns_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: companies companies_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.companies
    ADD CONSTRAINT companies_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: contacts contacts_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.contacts
    ADD CONSTRAINT contacts_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_quote_id_quotes; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_quote_id_quotes FOREIGN KEY (quote_id) REFERENCES pycrm.quotes(id);


--
-- Name: gmail_user_tokens gmail_user_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT gmail_user_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: jobs jobs_status_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_status_id_fkey FOREIGN KEY (status_id) REFERENCES pycrm.job_statuses(id);


--
-- Name: link_relations link_relations_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.link_relations
    ADD CONSTRAINT link_relations_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: note_conversations note_conversations_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.note_conversations
    ADD CONSTRAINT note_conversations_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: note_conversations note_conversations_note_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.note_conversations
    ADD CONSTRAINT note_conversations_note_id_fkey FOREIGN KEY (note_id) REFERENCES pycrm.notes(id);


--
-- Name: notes notes_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.notes
    ADD CONSTRAINT notes_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: o365_user_tokens o365_user_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT o365_user_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id) ON DELETE CASCADE;


--
-- Name: pre_opportunities pre_opportunities_balance_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES pycrm.pre_opportunity_balances(id);


--
-- Name: pre_opportunities pre_opportunities_bill_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_bill_to_customer_id_fkey FOREIGN KEY (bill_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: pre_opportunities pre_opportunities_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: pre_opportunities pre_opportunities_job_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_job_id_fkey FOREIGN KEY (job_id) REFERENCES pycrm.jobs(id);


--
-- Name: pre_opportunities pre_opportunities_sold_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_sold_to_customer_id_fkey FOREIGN KEY (sold_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: pre_opportunity_details pre_opportunity_details_end_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT pre_opportunity_details_end_user_id_fkey FOREIGN KEY (end_user_id) REFERENCES pycore.customers(id);


--
-- Name: pre_opportunity_details pre_opportunity_details_pre_opportunity_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT pre_opportunity_details_pre_opportunity_id_fkey FOREIGN KEY (pre_opportunity_id) REFERENCES pycrm.pre_opportunities(id);


--
-- Name: pre_opportunity_details pre_opportunity_details_product_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT pre_opportunity_details_product_id_fkey FOREIGN KEY (product_id) REFERENCES pycore.products(id);


--
-- Name: quote_details quote_details_end_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_end_user_id_fkey FOREIGN KEY (end_user_id) REFERENCES pycore.customers(id);


--
-- Name: quote_details quote_details_factory_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES pycore.factories(id);


--
-- Name: quote_details quote_details_lost_reason_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_lost_reason_id_fkey FOREIGN KEY (lost_reason_id) REFERENCES pycrm.quote_lost_reasons(id);


--
-- Name: quote_details quote_details_product_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_product_id_fkey FOREIGN KEY (product_id) REFERENCES pycore.products(id);


--
-- Name: quote_details quote_details_quote_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES pycrm.quotes(id);


--
-- Name: quote_details quote_details_uom_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_details
    ADD CONSTRAINT quote_details_uom_id_fkey FOREIGN KEY (uom_id) REFERENCES pycore.product_uoms(id);


--
-- Name: quote_inside_reps quote_inside_reps_quote_detail_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_inside_reps
    ADD CONSTRAINT quote_inside_reps_quote_detail_id_fkey FOREIGN KEY (quote_detail_id) REFERENCES pycrm.quote_details(id);


--
-- Name: quote_inside_reps quote_inside_reps_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_inside_reps
    ADD CONSTRAINT quote_inside_reps_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: quote_lost_reasons quote_lost_reasons_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_lost_reasons
    ADD CONSTRAINT quote_lost_reasons_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: quote_split_rates quote_split_rates_quote_detail_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_split_rates
    ADD CONSTRAINT quote_split_rates_quote_detail_id_fkey FOREIGN KEY (quote_detail_id) REFERENCES pycrm.quote_details(id);


--
-- Name: quote_split_rates quote_split_rates_user_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quote_split_rates
    ADD CONSTRAINT quote_split_rates_user_id_fkey FOREIGN KEY (user_id) REFERENCES pyuser.users(id);


--
-- Name: quotes quotes_balance_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES pycrm.quote_balances(id);


--
-- Name: quotes quotes_bill_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_bill_to_customer_id_fkey FOREIGN KEY (bill_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: quotes quotes_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: quotes quotes_job_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_job_id_fkey FOREIGN KEY (job_id) REFERENCES pycrm.jobs(id);


--
-- Name: quotes quotes_sold_to_customer_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.quotes
    ADD CONSTRAINT quotes_sold_to_customer_id_fkey FOREIGN KEY (sold_to_customer_id) REFERENCES pycore.customers(id);


--
-- Name: spec_sheet_highlight_regions spec_sheet_highlight_regions_version_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_regions
    ADD CONSTRAINT spec_sheet_highlight_regions_version_id_fkey FOREIGN KEY (version_id) REFERENCES pycrm.spec_sheet_highlight_versions(id);


--
-- Name: spec_sheet_highlight_versions spec_sheet_highlight_versions_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT spec_sheet_highlight_versions_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: spec_sheet_highlight_versions spec_sheet_highlight_versions_spec_sheet_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT spec_sheet_highlight_versions_spec_sheet_id_fkey FOREIGN KEY (spec_sheet_id) REFERENCES pycrm.spec_sheets(id);


--
-- Name: spec_sheets spec_sheets_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.spec_sheets
    ADD CONSTRAINT spec_sheets_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: task_conversations task_conversations_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.task_conversations
    ADD CONSTRAINT task_conversations_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: task_conversations task_conversations_task_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.task_conversations
    ADD CONSTRAINT task_conversations_task_id_fkey FOREIGN KEY (task_id) REFERENCES pycrm.tasks(id);


--
-- Name: tasks tasks_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: neondb_owner
--

ALTER TABLE ONLY pycrm.tasks
    ADD CONSTRAINT tasks_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: files files_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.files
    ADD CONSTRAINT files_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: files files_folder_id_fkey; Type: FK CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.files
    ADD CONSTRAINT files_folder_id_fkey FOREIGN KEY (folder_id) REFERENCES pyfiles.folders(id);


--
-- Name: folders folders_created_by_id_fkey; Type: FK CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.folders
    ADD CONSTRAINT folders_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES pyuser.users(id);


--
-- Name: folders folders_parent_id_fkey; Type: FK CONSTRAINT; Schema: pyfiles; Owner: neondb_owner
--

ALTER TABLE ONLY pyfiles.folders
    ADD CONSTRAINT folders_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES pyfiles.folders(id);


--
-- PostgreSQL database dump complete
--

\unrestrict b9NgO7dr9hbTexDIXshuMKMjAxdMgTsL0x1exaWHoxTRqwg8kzg6VcqUZIBYvry

