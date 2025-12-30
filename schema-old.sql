--
-- PostgreSQL database dump
--

\restrict IS8fTqbWAwPcFszYgpIbxczmX0MgBDPvrKTp9wOwmuiUHMrKNVa7S0X1BrlMmgq

-- Dumped from database version 15.12 (Debian 15.12-1.pgdg110+1)
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
-- Name: ai; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA ai;


ALTER SCHEMA ai OWNER TO postgres;

--
-- Name: chats; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA chats;


ALTER SCHEMA chats OWNER TO postgres;

--
-- Name: commission; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA commission;


ALTER SCHEMA commission OWNER TO postgres;

--
-- Name: core; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA core;


ALTER SCHEMA core OWNER TO postgres;

--
-- Name: crm; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA crm;


ALTER SCHEMA crm OWNER TO postgres;

--
-- Name: files; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA files;


ALTER SCHEMA files OWNER TO postgres;

--
-- Name: pycrm; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pycrm;


ALTER SCHEMA pycrm OWNER TO postgres;

--
-- Name: report; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA report;


ALTER SCHEMA report OWNER TO postgres;

--
-- Name: uploader; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA uploader;


ALTER SCHEMA uploader OWNER TO postgres;

--
-- Name: user; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "user";


ALTER SCHEMA "user" OWNER TO postgres;

--
-- Name: warehouse; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA warehouse;


ALTER SCHEMA warehouse OWNER TO postgres;

--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


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

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "user";


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: entity_types; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.entity_types AS ENUM (
    'temp',
    'quotes',
    'orders',
    'invoices',
    'checks',
    'products',
    'customers',
    'factories',
    'users',
    'uoms',
    'pricings',
    'addresses',
    'product_categories',
    'customer_part_numbers',
    'order_acknowledgements',
    'credits',
    'expenses',
    'jobs',
    'pre_opportunities'
);


ALTER TYPE public.entity_types OWNER TO postgres;

--
-- Name: file_types; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.file_types AS ENUM (
    'PDF',
    'CSV',
    'XLS',
    'XLSX',
    'DOCX',
    'DOC',
    'TXT',
    'MSG',
    'EML',
    'OTHER',
    'PPTX',
    'PPT',
    'JPG',
    'JPEG',
    'PNG',
    'GIF'
);


ALTER TYPE public.file_types OWNER TO postgres;

--
-- Name: graphqlobjecttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.graphqlobjecttype AS ENUM (
    'TYPE',
    'INPUT',
    'SCALAR',
    'ENUM',
    'OTHER'
);


ALTER TYPE public.graphqlobjecttype OWNER TO postgres;

--
-- Name: graphqlquerytype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.graphqlquerytype AS ENUM (
    'QUERY',
    'MUTATION',
    'BOTH'
);


ALTER TYPE public.graphqlquerytype OWNER TO postgres;

--
-- Name: message_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.message_type AS ENUM (
    'QUERY',
    'RESPONSE'
);


ALTER TYPE public.message_type OWNER TO postgres;

--
-- Name: processstatusgql; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.processstatusgql AS ENUM (
    'NEW',
    'PAUSED',
    'COMPLETED',
    'IN_PROGRESS',
    'VERIFY_COLUMNS',
    'FAILED',
    'UNKNOWN',
    'EXCEPTION',
    'PLAYGROUND'
);


ALTER TYPE public.processstatusgql OWNER TO postgres;

--
-- Name: queue_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.queue_status AS ENUM (
    'QUEUED',
    'PROCESSING',
    'DONE',
    'PENDING'
);


ALTER TYPE public.queue_status OWNER TO postgres;

--
-- Name: user_search(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.user_search(uname text) RETURNS TABLE(usename name, passwd text)
    LANGUAGE sql SECURITY DEFINER
    AS $_$SELECT usename, passwd FROM pg_shadow WHERE usename=$1;$_$;


ALTER FUNCTION public.user_search(uname text) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE ai.alembic_version OWNER TO postgres;

--
-- Name: chat_message_feedback; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.chat_message_feedback (
    id uuid NOT NULL,
    feedback_type smallint NOT NULL,
    feedback_message text,
    message_id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.chat_message_feedback OWNER TO postgres;

--
-- Name: COLUMN chat_message_feedback.user_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.chat_message_feedback.user_id IS 'ID of the user who provided the feedback';


--
-- Name: chat_messages; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.chat_messages (
    id uuid NOT NULL,
    role smallint NOT NULL,
    message_type smallint DEFAULT '1'::smallint NOT NULL,
    content text,
    tool_name character varying(100),
    tool_args json,
    meta_data json,
    chat_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.chat_messages OWNER TO postgres;

--
-- Name: chats; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.chats (
    id uuid NOT NULL,
    title character varying(255),
    user_id uuid NOT NULL,
    session_id character varying(255),
    status smallint DEFAULT '1'::smallint NOT NULL,
    follow_up_suggestions character varying[],
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.chats OWNER TO postgres;

--
-- Name: COLUMN chats.user_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.chats.user_id IS 'ID of the user who created the chat';


--
-- Name: COLUMN chats.session_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.chats.session_id IS 'Session identifier to group related chats';


--
-- Name: COLUMN chats.follow_up_suggestions; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.chats.follow_up_suggestions IS 'List of suggested follow-up questions for the chat';


--
-- Name: cluster_contexts; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.cluster_contexts (
    id uuid NOT NULL,
    cluster_id uuid NOT NULL,
    file_id uuid NOT NULL,
    file_name character varying NOT NULL,
    converted_text_content text NOT NULL,
    file_type character varying NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.cluster_contexts OWNER TO postgres;

--
-- Name: document_clusters; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.document_clusters (
    id uuid NOT NULL,
    cluster_metadata jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    cluster_name character varying(500) NOT NULL,
    is_hidden boolean DEFAULT false NOT NULL
);


ALTER TABLE ai.document_clusters OWNER TO postgres;

--
-- Name: COLUMN document_clusters.cluster_metadata; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.document_clusters.cluster_metadata IS 'Cluster metadata including source_name and source_type';


--
-- Name: COLUMN document_clusters.cluster_name; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.document_clusters.cluster_name IS 'Name of the cluster derived from source_name and type';


--
-- Name: email_attachments; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.email_attachments (
    id uuid NOT NULL,
    email_id uuid NOT NULL,
    name character varying(500) NOT NULL,
    content_type character varying(255),
    size integer,
    s3_key character varying(1000),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    document_type character varying(100),
    classification_confidence double precision,
    document_description text,
    extracted_metadata jsonb
);


ALTER TABLE ai.email_attachments OWNER TO postgres;

--
-- Name: COLUMN email_attachments.s3_key; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.email_attachments.s3_key IS 'S3 key for the stored attachment';


--
-- Name: COLUMN email_attachments.document_type; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.email_attachments.document_type IS 'Classified document type (quote, order, invoice, etc.)';


--
-- Name: COLUMN email_attachments.classification_confidence; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.email_attachments.classification_confidence IS 'Confidence score for the document type classification';


--
-- Name: COLUMN email_attachments.document_description; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.email_attachments.document_description IS 'AI-generated description of the document content';


--
-- Name: COLUMN email_attachments.extracted_metadata; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.email_attachments.extracted_metadata IS 'Extracted metadata (reference numbers, pricing info, etc.)';


--
-- Name: emails; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.emails (
    id uuid NOT NULL,
    external_id character varying(255) NOT NULL,
    subject character varying(500) NOT NULL,
    conversation_id character varying(255) NOT NULL,
    from_email character varying(255) NOT NULL,
    to_email character varying(255) NOT NULL,
    body text NOT NULL,
    user_id uuid,
    status smallint DEFAULT '1'::smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    category character varying(100),
    urgency character varying(50),
    sentiment character varying(50),
    classification_confidence double precision,
    summary text,
    requires_response boolean,
    suggested_actions jsonb,
    extracted_entities jsonb
);


ALTER TABLE ai.emails OWNER TO postgres;

--
-- Name: COLUMN emails.external_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.external_id IS 'External identifier from the email provider';


--
-- Name: COLUMN emails.conversation_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.conversation_id IS 'Conversation thread identifier';


--
-- Name: COLUMN emails.user_id; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.user_id IS 'ID of the user associated with this email';


--
-- Name: COLUMN emails.category; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.category IS 'Primary email category (quote_request, order_request, etc.)';


--
-- Name: COLUMN emails.urgency; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.urgency IS 'Urgency level (critical, high, medium, low)';


--
-- Name: COLUMN emails.sentiment; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.sentiment IS 'Email sentiment (positive, neutral, negative, urgent)';


--
-- Name: COLUMN emails.classification_confidence; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.classification_confidence IS 'Confidence score for the classification (0.0 to 1.0)';


--
-- Name: COLUMN emails.summary; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.summary IS 'AI-generated summary of the email content';


--
-- Name: COLUMN emails.requires_response; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.requires_response IS 'Whether this email requires a response';


--
-- Name: COLUMN emails.suggested_actions; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.suggested_actions IS 'Suggested actions based on email content';


--
-- Name: COLUMN emails.extracted_entities; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.emails.extracted_entities IS 'Extracted entities (contacts, companies, jobs, products, etc.)';


--
-- Name: entity_match_candidates; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.entity_match_candidates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pending_entity_id uuid NOT NULL,
    existing_entity_id uuid NOT NULL,
    existing_entity_name character varying(255) NOT NULL,
    similarity_score numeric(5,4) NOT NULL,
    match_metadata jsonb,
    rank integer NOT NULL
);


ALTER TABLE ai.entity_match_candidates OWNER TO postgres;

--
-- Name: extracted_data_versions; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.extracted_data_versions (
    id uuid NOT NULL,
    pending_document_id uuid NOT NULL,
    version_number integer NOT NULL,
    change_description character varying(500) NOT NULL,
    change_type integer NOT NULL,
    user_instruction text,
    executed_code text,
    created_by uuid,
    meta_data jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb
);


ALTER TABLE ai.extracted_data_versions OWNER TO postgres;

--
-- Name: COLUMN extracted_data_versions.version_number; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.version_number IS 'Sequential version number starting from 1';


--
-- Name: COLUMN extracted_data_versions.change_description; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.change_description IS 'Description of what changed in this version';


--
-- Name: COLUMN extracted_data_versions.change_type; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.change_type IS 'Type of change that created this version';


--
-- Name: COLUMN extracted_data_versions.user_instruction; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.user_instruction IS 'User instruction that triggered this change (for ML training)';


--
-- Name: COLUMN extracted_data_versions.executed_code; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.executed_code IS 'Python code executed in sandbox (for ML training)';


--
-- Name: COLUMN extracted_data_versions.created_by; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.created_by IS 'Keycloak user ID who created this version';


--
-- Name: COLUMN extracted_data_versions.meta_data; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.extracted_data_versions.meta_data IS 'Additional metadata for extensibility';


--
-- Name: pending_document_correction_changes; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.pending_document_correction_changes (
    id uuid NOT NULL,
    pending_document_id uuid NOT NULL,
    correction_action character varying NOT NULL,
    old_value jsonb,
    new_value jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.pending_document_correction_changes OWNER TO postgres;

--
-- Name: COLUMN pending_document_correction_changes.correction_action; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.pending_document_correction_changes.correction_action IS 'Description of the correction action performed';


--
-- Name: COLUMN pending_document_correction_changes.old_value; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.pending_document_correction_changes.old_value IS 'Previous value before correction';


--
-- Name: COLUMN pending_document_correction_changes.new_value; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.pending_document_correction_changes.new_value IS 'New value after correction';


--
-- Name: pending_document_entities; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.pending_document_entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pending_document_id uuid NOT NULL,
    entity_id uuid NOT NULL,
    entity_type smallint NOT NULL,
    action smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.pending_document_entities OWNER TO postgres;

--
-- Name: pending_document_pages; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.pending_document_pages (
    id uuid NOT NULL,
    pending_document_id uuid NOT NULL,
    page_number integer NOT NULL,
    markdown_content text NOT NULL,
    entity_number character varying(255),
    page_type smallint NOT NULL,
    is_relevant_for_transactions boolean NOT NULL,
    reasoning text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    number_of_detail_lines integer
);


ALTER TABLE ai.pending_document_pages OWNER TO postgres;

--
-- Name: pending_documents; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.pending_documents (
    id uuid NOT NULL,
    file_id uuid NOT NULL,
    document_type smallint NOT NULL,
    document_sample_content character varying NOT NULL,
    entity_type smallint,
    source_type smallint,
    source_name character varying(500),
    similar_documents_json jsonb,
    extracted_data_json jsonb,
    converted_document_url character varying,
    additional_instructions_json jsonb NOT NULL,
    source_classification_json jsonb,
    status smallint NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    cluster_id uuid,
    original_presigned_url character varying NOT NULL,
    sha character varying,
    file_upload_process_id uuid,
    is_archived boolean DEFAULT false NOT NULL
);


ALTER TABLE ai.pending_documents OWNER TO postgres;

--
-- Name: COLUMN pending_documents.converted_document_url; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.pending_documents.converted_document_url IS 'URL to the converted document stored in cloud storage';


--
-- Name: COLUMN pending_documents.original_presigned_url; Type: COMMENT; Schema: ai; Owner: postgres
--

COMMENT ON COLUMN ai.pending_documents.original_presigned_url IS 'Presigned URL to the original document. For PDFs: the original PDF URL. For tabular: the converted original CSV URL';


--
-- Name: pending_entities; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.pending_entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_type smallint NOT NULL,
    pending_document_id uuid NOT NULL,
    source_line_numbers integer[],
    extracted_data jsonb NOT NULL,
    display_name character varying NOT NULL,
    best_match_id uuid,
    best_match_similarity numeric(5,4),
    confirmation_status smallint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now(),
    confirmed_at timestamp with time zone,
    confirmed_by_user_id uuid,
    flow_index_detail integer,
    best_match_name character varying,
    dto_ids uuid[]
);


ALTER TABLE ai.pending_entities OWNER TO postgres;

--
-- Name: workflow_executions; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.workflow_executions (
    id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    input_data jsonb,
    output_data jsonb,
    error_message text,
    execution_log text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.workflow_executions OWNER TO postgres;

--
-- Name: workflow_files; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.workflow_files (
    id uuid NOT NULL,
    workflow_id uuid NOT NULL,
    filename character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size integer NOT NULL,
    file_type character varying(100),
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE ai.workflow_files OWNER TO postgres;

--
-- Name: workflows; Type: TABLE; Schema: ai; Owner: postgres
--

CREATE TABLE ai.workflows (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    instruction text NOT NULL,
    workflow_json jsonb NOT NULL,
    generated_code text,
    pseudo_code text,
    status character varying(50) DEFAULT 'draft'::character varying NOT NULL,
    created_by uuid,
    is_public boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE ai.workflows OWNER TO postgres;

--
-- Name: chat_messages; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.chat_messages (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    chat_id uuid NOT NULL,
    query character varying NOT NULL,
    context character varying,
    message_type public.message_type NOT NULL,
    thumbs_up boolean
);


ALTER TABLE chats.chat_messages OWNER TO postgres;

--
-- Name: chats; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.chats (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    name character varying NOT NULL,
    last_updated_at timestamp without time zone NOT NULL,
    created_by_id uuid,
    actions json
);


ALTER TABLE chats.chats OWNER TO postgres;

--
-- Name: chats_alembic_version; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.chats_alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE chats.chats_alembic_version OWNER TO postgres;

--
-- Name: graphql_checksum; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.graphql_checksum (
    checksum character varying NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE chats.graphql_checksum OWNER TO postgres;

--
-- Name: queries; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.queries (
    id integer NOT NULL,
    name character varying NOT NULL,
    signature text NOT NULL,
    description text,
    query_type public.graphqlquerytype NOT NULL,
    embedding public.vector(1536) DEFAULT NULL::public.vector,
    parameters json,
    return_type text NOT NULL
);


ALTER TABLE chats.queries OWNER TO postgres;

--
-- Name: queries_id_seq; Type: SEQUENCE; Schema: chats; Owner: postgres
--

CREATE SEQUENCE chats.queries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE chats.queries_id_seq OWNER TO postgres;

--
-- Name: queries_id_seq; Type: SEQUENCE OWNED BY; Schema: chats; Owner: postgres
--

ALTER SEQUENCE chats.queries_id_seq OWNED BY chats.queries.id;


--
-- Name: types; Type: TABLE; Schema: chats; Owner: postgres
--

CREATE TABLE chats.types (
    id integer NOT NULL,
    name character varying NOT NULL,
    type public.graphqlobjecttype NOT NULL,
    signature text NOT NULL,
    description text,
    embedding public.vector(1536) DEFAULT NULL::public.vector,
    attributes json,
    sub_type_names json
);


ALTER TABLE chats.types OWNER TO postgres;

--
-- Name: types_id_seq; Type: SEQUENCE; Schema: chats; Owner: postgres
--

CREATE SEQUENCE chats.types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE chats.types_id_seq OWNER TO postgres;

--
-- Name: types_id_seq; Type: SEQUENCE OWNED BY; Schema: chats; Owner: postgres
--

ALTER SEQUENCE chats.types_id_seq OWNED BY chats.types.id;


--
-- Name: check_balances; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.check_balances (
    id uuid NOT NULL,
    commission_paid numeric NOT NULL,
    commission_expected numeric NOT NULL,
    commission_balance numeric NOT NULL,
    commission_difference numeric NOT NULL,
    commission_credit numeric DEFAULT 0 NOT NULL,
    commission_expense numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.check_balances OWNER TO postgres;

--
-- Name: check_balances_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.check_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    commission_paid numeric,
    commission_expected numeric,
    commission_balance numeric,
    commission_difference numeric,
    commission_credit numeric DEFAULT 0 NOT NULL,
    commission_expense numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.check_balances_aud OWNER TO postgres;

--
-- Name: check_details; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.check_details (
    id uuid NOT NULL,
    check_id uuid NOT NULL,
    invoice_id uuid,
    deduction_id uuid,
    adjustment_id uuid,
    credit numeric NOT NULL,
    debit numeric NOT NULL,
    total numeric NOT NULL,
    applied_amount numeric NOT NULL,
    applied_amount_rate numeric NOT NULL,
    balance numeric NOT NULL,
    paid boolean,
    check_detail_type smallint NOT NULL
);


ALTER TABLE commission.check_details OWNER TO postgres;

--
-- Name: check_details_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.check_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    check_id uuid,
    invoice_id uuid,
    deduction_id uuid,
    adjustment_id uuid,
    credit numeric,
    debit numeric,
    total numeric,
    applied_amount numeric,
    applied_amount_rate numeric,
    balance numeric,
    paid boolean,
    check_detail_type smallint
);


ALTER TABLE commission.check_details_aud OWNER TO postgres;

--
-- Name: checks; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.checks (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    balance_id uuid NOT NULL,
    status smallint NOT NULL,
    factory_id uuid NOT NULL,
    entity_date date NOT NULL,
    check_number character varying(255) NOT NULL,
    commission numeric NOT NULL,
    user_owner_ids uuid[],
    post_date date,
    commission_month date,
    participant_ids uuid[]
);


ALTER TABLE commission.checks OWNER TO postgres;

--
-- Name: checks_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.checks_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    balance_id uuid,
    status smallint,
    factory_id uuid,
    entity_date date,
    check_number character varying(255),
    commission numeric,
    post_date date,
    commission_month date,
    participant_ids uuid[]
);


ALTER TABLE commission.checks_aud OWNER TO postgres;

--
-- Name: credit_balances; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_balances (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    total numeric NOT NULL,
    commission numeric NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.credit_balances OWNER TO postgres;

--
-- Name: credit_balances_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quantity integer,
    total numeric,
    commission numeric,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.credit_balances_aud OWNER TO postgres;

--
-- Name: credit_details; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_details (
    id uuid NOT NULL,
    credit_id uuid NOT NULL,
    status smallint NOT NULL,
    quantity integer NOT NULL,
    total numeric NOT NULL,
    unit_price numeric NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    credit_reason_id uuid,
    credit_reason_other character varying(255),
    order_detail_id uuid NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.credit_details OWNER TO postgres;

--
-- Name: credit_details_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    credit_id uuid,
    status smallint,
    quantity integer,
    total numeric,
    unit_price numeric,
    commission_rate numeric,
    commission numeric,
    credit_reason_id uuid,
    credit_reason_other character varying(255),
    order_detail_id uuid,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.credit_details_aud OWNER TO postgres;

--
-- Name: credit_reasons; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_reasons (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE commission.credit_reasons OWNER TO postgres;

--
-- Name: credit_reasons_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credit_reasons_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    title character varying(255),
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE commission.credit_reasons_aud OWNER TO postgres;

--
-- Name: credits; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credits (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    published boolean NOT NULL,
    balance_id uuid NOT NULL,
    status smallint NOT NULL,
    entity_date date NOT NULL,
    credit_number character varying(255) NOT NULL,
    order_id uuid NOT NULL,
    update_order_option smallint,
    user_owner_ids uuid[]
);


ALTER TABLE commission.credits OWNER TO postgres;

--
-- Name: credits_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.credits_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    balance_id uuid,
    status smallint,
    entity_date date,
    credit_number character varying(255),
    order_id uuid,
    update_order_option smallint
);


ALTER TABLE commission.credits_aud OWNER TO postgres;

--
-- Name: databasechangelog; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.databasechangelog (
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


ALTER TABLE commission.databasechangelog OWNER TO postgres;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE commission.databasechangeloglock OWNER TO postgres;

--
-- Name: deduction_sales_reps; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.deduction_sales_reps (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid,
    "position" numeric DEFAULT 0 NOT NULL,
    user_id uuid NOT NULL,
    credit_detail_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    commission_amount numeric NOT NULL,
    sales_amount numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.deduction_sales_reps OWNER TO postgres;

--
-- Name: deduction_sales_reps_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.deduction_sales_reps_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    "position" numeric DEFAULT 0,
    user_id uuid,
    credit_detail_id uuid,
    split_rate numeric,
    commission_amount numeric,
    sales_amount numeric DEFAULT 0
);


ALTER TABLE commission.deduction_sales_reps_aud OWNER TO postgres;

--
-- Name: expense_categories; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expense_categories (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean NOT NULL,
    title character varying(255) NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.expense_categories OWNER TO postgres;

--
-- Name: expense_categories_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expense_categories_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    is_used boolean,
    title character varying(255),
    "position" numeric DEFAULT 0
);


ALTER TABLE commission.expense_categories_aud OWNER TO postgres;

--
-- Name: expense_split_rates; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expense_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    expense_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL,
    expense_amount numeric NOT NULL
);


ALTER TABLE commission.expense_split_rates OWNER TO postgres;

--
-- Name: expense_split_rates_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expense_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    expense_id uuid,
    split_rate numeric,
    "position" numeric DEFAULT 0,
    expense_amount numeric
);


ALTER TABLE commission.expense_split_rates_aud OWNER TO postgres;

--
-- Name: expenses; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expenses (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    status smallint NOT NULL,
    sold_to_customer_id uuid,
    entity_date date NOT NULL,
    expense_number character varying(255),
    expense_amount numeric,
    expense_category_id uuid NOT NULL,
    note text,
    sold_to_customer_address_id uuid
);


ALTER TABLE commission.expenses OWNER TO postgres;

--
-- Name: expenses_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.expenses_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    status smallint,
    sold_to_customer_id uuid,
    entity_date date,
    expense_number character varying(255),
    expense_amount numeric,
    expense_category_id uuid,
    note text,
    sold_to_customer_address_id uuid
);


ALTER TABLE commission.expenses_aud OWNER TO postgres;

--
-- Name: invoice_balances; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_balances (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    total numeric NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.invoice_balances OWNER TO postgres;

--
-- Name: invoice_balances_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quantity integer,
    total numeric,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    subtotal numeric DEFAULT 0
);


ALTER TABLE commission.invoice_balances_aud OWNER TO postgres;

--
-- Name: invoice_details; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_details (
    id uuid NOT NULL,
    invoice_id uuid NOT NULL,
    item_number integer NOT NULL,
    status smallint NOT NULL,
    quantity integer NOT NULL,
    total numeric NOT NULL,
    unit_price numeric NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount_rate numeric NOT NULL,
    discount numeric NOT NULL,
    order_detail_id uuid NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL
);


ALTER TABLE commission.invoice_details OWNER TO postgres;

--
-- Name: invoice_details_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    invoice_id uuid,
    item_number integer,
    status smallint,
    quantity integer,
    total numeric,
    unit_price numeric,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount_rate numeric,
    discount numeric,
    order_detail_id uuid,
    subtotal numeric DEFAULT 0,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL
);


ALTER TABLE commission.invoice_details_aud OWNER TO postgres;

--
-- Name: invoice_split_rates; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid,
    "position" numeric DEFAULT 0 NOT NULL,
    user_id uuid NOT NULL,
    invoice_detail_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    commission_amount numeric NOT NULL,
    sales_amount numeric DEFAULT 0 NOT NULL,
    order_split_rate_id uuid NOT NULL
);


ALTER TABLE commission.invoice_split_rates OWNER TO postgres;

--
-- Name: invoice_split_rates_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoice_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    "position" numeric DEFAULT 0,
    user_id uuid,
    invoice_detail_id uuid,
    split_rate numeric,
    commission_amount numeric,
    sales_amount numeric DEFAULT 0,
    order_split_rate_id uuid
);


ALTER TABLE commission.invoice_split_rates_aud OWNER TO postgres;

--
-- Name: invoices; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoices (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    published boolean NOT NULL,
    balance_id uuid NOT NULL,
    status smallint NOT NULL,
    factory_id uuid,
    entity_date date NOT NULL,
    due_date date,
    invoice_number character varying(255) NOT NULL,
    order_id uuid NOT NULL,
    locked boolean NOT NULL,
    user_owner_ids uuid[],
    participant_ids uuid[]
);


ALTER TABLE commission.invoices OWNER TO postgres;

--
-- Name: invoices_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.invoices_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    balance_id uuid,
    status smallint,
    factory_id uuid,
    entity_date date,
    due_date date,
    invoice_number character varying(255),
    order_id uuid,
    locked boolean,
    participant_ids uuid[]
);


ALTER TABLE commission.invoices_aud OWNER TO postgres;

--
-- Name: order_acknowledgements; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_acknowledgements (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    order_detail_id uuid NOT NULL,
    order_acknowledgement_number character varying(255) NOT NULL,
    entity_date date NOT NULL
);


ALTER TABLE commission.order_acknowledgements OWNER TO postgres;

--
-- Name: order_acknowledgements_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_acknowledgements_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    order_detail_id uuid,
    order_acknowledgement_number character varying(255),
    entity_date date
);


ALTER TABLE commission.order_acknowledgements_aud OWNER TO postgres;

--
-- Name: order_balances; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_balances (
    id uuid NOT NULL,
    quantity integer NOT NULL,
    shipping_balance integer NOT NULL,
    total numeric NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    credit_amount numeric DEFAULT 0 NOT NULL,
    credit_commission_amount numeric DEFAULT 0 NOT NULL,
    credit_quantity numeric DEFAULT 0 NOT NULL,
    order_balance numeric DEFAULT 0 NOT NULL,
    invoice_amount numeric DEFAULT 0 NOT NULL,
    invoice_commission_amount numeric DEFAULT 0 NOT NULL,
    invoice_quantity integer DEFAULT 0 NOT NULL,
    commission_balance numeric DEFAULT 0 NOT NULL,
    discount numeric DEFAULT 0 NOT NULL,
    discount_rate numeric DEFAULT 0 NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    cost numeric DEFAULT 0 NOT NULL,
    margin numeric DEFAULT 0 NOT NULL,
    freight_charge numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.order_balances OWNER TO postgres;

--
-- Name: order_balances_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quantity integer,
    total numeric,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    shipping_balance integer,
    credit_amount numeric,
    credit_commission_amount numeric,
    credit_quantity integer,
    order_balance numeric,
    invoice_amount numeric,
    invoice_commission_amount numeric,
    invoice_quantity integer,
    commission_balance numeric,
    discount numeric DEFAULT 0,
    discount_rate numeric DEFAULT 0,
    subtotal numeric DEFAULT 0,
    cost numeric,
    margin numeric,
    freight_charge numeric
);


ALTER TABLE commission.order_balances_aud OWNER TO postgres;

--
-- Name: order_details; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_details (
    id uuid NOT NULL,
    order_id uuid NOT NULL,
    item_number integer NOT NULL,
    status smallint NOT NULL,
    quantity integer NOT NULL,
    shipping_balance integer NOT NULL,
    total numeric NOT NULL,
    unit_price numeric NOT NULL,
    product_id uuid NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount_rate numeric NOT NULL,
    discount numeric NOT NULL,
    end_user_id uuid NOT NULL,
    lead_time character varying(255),
    quote_detail_id uuid,
    credit_amount numeric NOT NULL,
    credit_commission_amount numeric NOT NULL,
    credit_quantity numeric NOT NULL,
    order_detail_balance numeric NOT NULL,
    product_cpn_id uuid,
    invoice_amount numeric DEFAULT 0 NOT NULL,
    invoice_commission_amount numeric DEFAULT 0 NOT NULL,
    invoice_quantity integer DEFAULT 0 NOT NULL,
    commission_detail_balance numeric DEFAULT 0 NOT NULL,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    locked_split_rates boolean DEFAULT false NOT NULL,
    check_commission_paid numeric DEFAULT 0 NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    line_transaction_type smallint DEFAULT 0 NOT NULL,
    line_fulfillment_status smallint DEFAULT 1 NOT NULL,
    line_billing_status smallint DEFAULT 1 NOT NULL,
    line_commission_status smallint DEFAULT 1 NOT NULL,
    cost numeric DEFAULT 0 NOT NULL,
    margin numeric DEFAULT 0 NOT NULL,
    freight_charge numeric DEFAULT 0 NOT NULL
);


ALTER TABLE commission.order_details OWNER TO postgres;

--
-- Name: order_details_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    order_id uuid,
    item_number integer,
    status smallint,
    quantity integer,
    shipping_balance integer,
    total numeric,
    unit_price numeric,
    product_id uuid,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount_rate numeric,
    discount numeric,
    end_user_id uuid,
    lead_time character varying(255),
    quote_detail_id uuid,
    credit_amount numeric,
    credit_commission_amount numeric,
    credit_quantity integer,
    order_detail_balance numeric,
    product_cpn_id uuid,
    invoice_amount numeric,
    invoice_commission_amount numeric,
    invoice_quantity integer,
    commission_detail_balance numeric,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    locked_split_rates boolean DEFAULT false NOT NULL,
    check_commission_paid numeric DEFAULT 0 NOT NULL,
    subtotal numeric DEFAULT 0,
    line_transaction_type smallint,
    line_fulfillment_status smallint,
    line_billing_status smallint,
    line_commission_status smallint,
    cost numeric,
    margin numeric,
    freight_charge numeric
);


ALTER TABLE commission.order_details_aud OWNER TO postgres;

--
-- Name: order_inside_reps; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_inside_reps (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    order_id uuid NOT NULL
);


ALTER TABLE commission.order_inside_reps OWNER TO postgres;

--
-- Name: order_inside_reps_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_inside_reps_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    order_id uuid
);


ALTER TABLE commission.order_inside_reps_aud OWNER TO postgres;

--
-- Name: order_split_rates; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    order_detail_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    commission_amount numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL,
    sales_amount numeric DEFAULT 0 NOT NULL,
    created_by uuid NOT NULL
);


ALTER TABLE commission.order_split_rates OWNER TO postgres;

--
-- Name: order_split_rates_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.order_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    order_detail_id uuid,
    split_rate numeric,
    commission_amount numeric,
    "position" numeric DEFAULT 0,
    sales_amount numeric DEFAULT 0,
    created_by uuid
);


ALTER TABLE commission.order_split_rates_aud OWNER TO postgres;

--
-- Name: orders; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.orders (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    published boolean NOT NULL,
    balance_id uuid NOT NULL,
    status smallint NOT NULL,
    order_number character varying(255) NOT NULL,
    factory_id uuid,
    sold_to_customer_id uuid,
    job_name character varying(255),
    shipping_terms character varying(255),
    freight_terms character varying(255),
    mark_number character varying(255),
    order_type smallint NOT NULL,
    entity_date date NOT NULL,
    ship_date date,
    due_date date NOT NULL,
    fact_so_number character varying(255),
    quote_id uuid,
    user_owner_ids uuid[],
    job_id uuid,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    duplicated_from uuid,
    transaction_type smallint DEFAULT 0 NOT NULL,
    header_status smallint DEFAULT 1 NOT NULL,
    confirmation_status smallint DEFAULT 0 NOT NULL,
    fulfillment_status smallint DEFAULT 1 NOT NULL,
    billing_status smallint DEFAULT 1 NOT NULL,
    commission_status smallint DEFAULT 1 NOT NULL,
    participant_ids uuid[]
);


ALTER TABLE commission.orders OWNER TO postgres;

--
-- Name: orders_aud; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.orders_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    balance_id uuid,
    status smallint,
    order_number character varying(255),
    factory_id uuid,
    sold_to_customer_id uuid,
    job_name character varying(255),
    shipping_terms character varying(255),
    freight_terms character varying(255),
    mark_number character varying(255),
    order_type smallint,
    entity_date date,
    ship_date date,
    due_date date,
    fact_so_number character varying(255),
    quote_id uuid,
    job_id uuid,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    duplicated_from uuid,
    transaction_type smallint,
    header_status smallint,
    confirmation_status smallint,
    fulfillment_status smallint,
    billing_status smallint,
    commission_status smallint,
    participant_ids uuid[]
);


ALTER TABLE commission.orders_aud OWNER TO postgres;

--
-- Name: revinfo; Type: TABLE; Schema: commission; Owner: postgres
--

CREATE TABLE commission.revinfo (
    rev integer NOT NULL,
    revtstmp bigint
);


ALTER TABLE commission.revinfo OWNER TO postgres;

--
-- Name: revinfo_seq; Type: SEQUENCE; Schema: commission; Owner: postgres
--

CREATE SEQUENCE commission.revinfo_seq
    START WITH 1
    INCREMENT BY 50
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE commission.revinfo_seq OWNER TO postgres;

--
-- Name: addresses; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.addresses (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    entity_type smallint NOT NULL,
    source_id uuid NOT NULL,
    address_type smallint NOT NULL,
    address_line_one character varying NOT NULL,
    address_line_two character varying,
    locality character varying(255) NOT NULL,
    administrative_area character varying(255) NOT NULL,
    postal_code character varying(255) NOT NULL,
    user_owner_ids uuid[],
    address_line_three character varying(255),
    sub_administrative_area character varying(255),
    organization character varying(255),
    dependent_locality character varying(255),
    recipient character varying(255),
    sorting_code character varying(255),
    country_code character(2),
    subdivision_code character varying(16)
);


ALTER TABLE core.addresses OWNER TO postgres;

--
-- Name: addresses_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.addresses_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    entity_type smallint,
    source_id uuid,
    address_type smallint,
    address_line_one character varying(255),
    address_line_two character varying(255),
    locality character varying(255),
    administrative_area character varying(255),
    postal_code character varying(255),
    address_line_three character varying(255),
    sub_administrative_area character varying(255),
    organization character varying(255),
    dependent_locality character varying(255),
    recipient character varying(255),
    sorting_code character varying(255),
    country_code character(2),
    subdivision_code character varying(16)
);


ALTER TABLE core.addresses_aud OWNER TO postgres;

--
-- Name: auto_increment_id; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.auto_increment_id (
    id uuid NOT NULL,
    counter numeric NOT NULL
);


ALTER TABLE core.auto_increment_id OWNER TO postgres;

--
-- Name: contacts; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.contacts (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    entity_type smallint NOT NULL,
    source_id uuid,
    firstname character varying(255) NOT NULL,
    lastname character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    is_primary boolean NOT NULL,
    email character varying(255),
    can_email boolean NOT NULL,
    phone character varying(255),
    can_text boolean NOT NULL,
    user_owner_ids uuid[]
);


ALTER TABLE core.contacts OWNER TO postgres;

--
-- Name: contacts_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.contacts_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    entity_type smallint,
    source_id uuid,
    firstname character varying(255),
    lastname character varying(255),
    title character varying(255),
    is_primary boolean,
    email character varying(255),
    can_email boolean,
    phone character varying(255),
    can_text boolean
);


ALTER TABLE core.contacts_aud OWNER TO postgres;

--
-- Name: countries; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.countries (
    code character(2) NOT NULL,
    alpha3 character(3),
    "numeric" character(3),
    name character varying(150) NOT NULL,
    official_name character varying(200),
    postal_code_regex character varying(200),
    region character varying(100),
    subregion character varying(100),
    enabled boolean DEFAULT true NOT NULL
);


ALTER TABLE core.countries OWNER TO postgres;

--
-- Name: countries_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.countries_aud (
    rev integer NOT NULL,
    revtype smallint,
    code character(2) NOT NULL,
    alpha3 character(3),
    "numeric" character(3),
    name character varying(150) NOT NULL,
    official_name character varying(200),
    postal_code_regex character varying(200),
    region character varying(100),
    subregion character varying(100),
    enabled boolean DEFAULT true NOT NULL
);


ALTER TABLE core.countries_aud OWNER TO postgres;

--
-- Name: customer_branches; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_branches (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    title character varying(255) NOT NULL,
    published boolean NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE core.customer_branches OWNER TO postgres;

--
-- Name: customer_branches_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_branches_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    title character varying(255),
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE core.customer_branches_aud OWNER TO postgres;

--
-- Name: customer_levels; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_levels (
    id uuid NOT NULL,
    customer_id uuid NOT NULL,
    factory_id uuid,
    level_title character varying(255) NOT NULL,
    description character varying(255),
    level_rate numeric(19,2) NOT NULL
);


ALTER TABLE core.customer_levels OWNER TO postgres;

--
-- Name: customer_levels_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_levels_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    customer_id uuid,
    factory_id uuid,
    level_title character varying(255),
    description character varying(255),
    level_rate numeric(19,2)
);


ALTER TABLE core.customer_levels_aud OWNER TO postgres;

--
-- Name: customer_split_rates; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL
);


ALTER TABLE core.customer_split_rates OWNER TO postgres;

--
-- Name: customer_split_rates_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    customer_id uuid,
    split_rate numeric,
    "position" numeric DEFAULT 0
);


ALTER TABLE core.customer_split_rates_aud OWNER TO postgres;

--
-- Name: customer_territories; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territories (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    title character varying(255) NOT NULL,
    published boolean NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    color character varying(16),
    territory_mode character varying(16),
    scope_tag character varying(64)
);


ALTER TABLE core.customer_territories OWNER TO postgres;

--
-- Name: customer_territories_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territories_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    title character varying(255),
    is_used boolean DEFAULT false NOT NULL,
    territory_mode character varying(16),
    scope_tag character varying(64),
    color character varying(16)
);


ALTER TABLE core.customer_territories_aud OWNER TO postgres;

--
-- Name: customer_territory_boundaries; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_boundaries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    territory_id uuid NOT NULL,
    geojson text NOT NULL,
    centroid_lat numeric(10,7),
    centroid_lon numeric(10,7),
    bbox_min_lat numeric(10,7),
    bbox_min_lon numeric(10,7),
    bbox_max_lat numeric(10,7),
    bbox_max_lon numeric(10,7)
);


ALTER TABLE core.customer_territory_boundaries OWNER TO postgres;

--
-- Name: customer_territory_boundaries_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_boundaries_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    territory_id uuid,
    geojson text,
    centroid_lat numeric(10,7),
    centroid_lon numeric(10,7),
    bbox_min_lat numeric(10,7),
    bbox_min_lon numeric(10,7),
    bbox_max_lat numeric(10,7),
    bbox_max_lon numeric(10,7),
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[]
);


ALTER TABLE core.customer_territory_boundaries_aud OWNER TO postgres;

--
-- Name: customer_territory_customers; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_customers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    territory_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    assignment_type character varying(32) NOT NULL,
    reason character varying(128),
    assigned_at timestamp without time zone DEFAULT now() NOT NULL,
    priority integer
);


ALTER TABLE core.customer_territory_customers OWNER TO postgres;

--
-- Name: customer_territory_customers_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_customers_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    territory_id uuid,
    customer_id uuid,
    assignment_type character varying(32),
    reason character varying(128),
    assigned_at timestamp without time zone,
    priority integer,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[]
);


ALTER TABLE core.customer_territory_customers_aud OWNER TO postgres;

--
-- Name: customer_territory_regions; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_regions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    territory_id uuid NOT NULL,
    region_type character varying(16) NOT NULL,
    region_code character varying(32) NOT NULL,
    region_name character varying(128),
    source character varying(32)
);


ALTER TABLE core.customer_territory_regions OWNER TO postgres;

--
-- Name: customer_territory_regions_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customer_territory_regions_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    territory_id uuid,
    region_type character varying(16),
    region_code character varying(32),
    region_name character varying(128),
    source character varying(32),
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[]
);


ALTER TABLE core.customer_territory_regions_aud OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customers (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    company_name character varying(255) NOT NULL,
    is_parent boolean NOT NULL,
    parent_id uuid,
    contact_email character varying(255),
    contact_number character varying(255),
    published boolean NOT NULL,
    customer_branch_id uuid,
    customer_territory_id uuid,
    logo_url text,
    inside_rep_id uuid,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    type character varying(50)
);


ALTER TABLE core.customers OWNER TO postgres;

--
-- Name: customers_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.customers_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    company_name character varying(255),
    is_parent boolean,
    parent_id uuid,
    contact_email character varying(255),
    contact_number character varying(255),
    logo_url text,
    published boolean,
    customer_branch_id uuid,
    customer_territory_id uuid,
    inside_rep_id uuid,
    is_used boolean DEFAULT false NOT NULL,
    type character varying(50)
);


ALTER TABLE core.customers_aud OWNER TO postgres;

--
-- Name: databasechangelog; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.databasechangelog (
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


ALTER TABLE core.databasechangelog OWNER TO postgres;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE core.databasechangeloglock OWNER TO postgres;

--
-- Name: document_templates; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.document_templates (
    id uuid NOT NULL,
    tenant_id character varying(64) NOT NULL,
    entity_type character varying(64) NOT NULL,
    name character varying(128) NOT NULL,
    description character varying(256),
    subject_template text,
    format character varying(32) NOT NULL,
    body_template text NOT NULL,
    default_template boolean NOT NULL,
    created_by character varying(64),
    updated_by character varying(64)
);


ALTER TABLE core.document_templates OWNER TO postgres;

--
-- Name: factories; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factories (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    title character varying(255) NOT NULL,
    account_number character varying(255),
    email character varying(255),
    phone character varying(255),
    external_terms text,
    additional_information text,
    published boolean NOT NULL,
    freight_terms text,
    freight_discount_type smallint NOT NULL,
    lead_time character varying(255),
    payment_terms text,
    commission_rate numeric,
    commission_discount_rate numeric,
    overall_discount_rate numeric,
    logo_url text,
    inside_rep_id uuid,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    external_payment_terms character varying(255),
    overage_allowed boolean DEFAULT false NOT NULL,
    overage_allowed_type character varying(255),
    rep_overage_share numeric(19,2),
    commission_policy character varying(255) DEFAULT 'STANDARD'::character varying NOT NULL,
    direct_commission_allowed boolean DEFAULT true NOT NULL,
    warehouse_commission_allowed boolean DEFAULT false NOT NULL,
    buy_sell_allowed boolean DEFAULT false NOT NULL,
    inventory_source_factory_allowed boolean DEFAULT false NOT NULL,
    inventory_source_rep_allowed boolean DEFAULT false NOT NULL,
    invoice_party_factory_allowed boolean DEFAULT false NOT NULL,
    invoice_party_rep_allowed boolean DEFAULT false NOT NULL
);


ALTER TABLE core.factories OWNER TO postgres;

--
-- Name: factories_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factories_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    title character varying(255),
    account_number character varying(255),
    email character varying(255),
    phone character varying(255),
    logo_url text,
    external_terms text,
    additional_information text,
    published boolean,
    freight_terms text,
    freight_discount_type smallint,
    lead_time character varying(255),
    payment_terms text,
    commission_rate numeric,
    commission_discount_rate numeric,
    overall_discount_rate numeric,
    inside_rep_id uuid,
    is_used boolean DEFAULT false NOT NULL,
    external_payment_terms character varying(255),
    overage_allowed boolean,
    overage_allowed_type character varying(255),
    rep_overage_share numeric(19,2),
    commission_policy character varying(255),
    direct_commission_allowed boolean,
    warehouse_commission_allowed boolean,
    buy_sell_allowed boolean,
    inventory_source_factory_allowed boolean DEFAULT false,
    inventory_source_rep_allowed boolean DEFAULT false,
    invoice_party_factory_allowed boolean DEFAULT false,
    invoice_party_rep_allowed boolean DEFAULT false
);


ALTER TABLE core.factories_aud OWNER TO postgres;

--
-- Name: factory_commission_bands; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_commission_bands (
    id uuid NOT NULL,
    factory_id uuid NOT NULL,
    lower numeric(19,2),
    upper numeric(19,2),
    rate numeric(19,2)
);


ALTER TABLE core.factory_commission_bands OWNER TO postgres;

--
-- Name: factory_commission_bands_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_commission_bands_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    factory_id uuid,
    lower numeric(19,2),
    upper numeric(19,2),
    rate numeric(19,2)
);


ALTER TABLE core.factory_commission_bands_aud OWNER TO postgres;

--
-- Name: factory_customer_ids; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_customer_ids (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    factory_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    factory_customer_id character varying(255) NOT NULL
);


ALTER TABLE core.factory_customer_ids OWNER TO postgres;

--
-- Name: factory_customer_ids_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_customer_ids_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    factory_id uuid,
    customer_id uuid,
    factory_customer_id character varying(255)
);


ALTER TABLE core.factory_customer_ids_aud OWNER TO postgres;

--
-- Name: factory_levels; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_levels (
    id uuid NOT NULL,
    factory_id uuid NOT NULL,
    level_title character varying(255) NOT NULL,
    description character varying(255),
    rate numeric(19,2)
);


ALTER TABLE core.factory_levels OWNER TO postgres;

--
-- Name: factory_levels_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.factory_levels_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    factory_id uuid,
    level_title character varying(255),
    description character varying(255),
    rate numeric(19,2)
);


ALTER TABLE core.factory_levels_aud OWNER TO postgres;

--
-- Name: note_note_tags; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_note_tags (
    note_id uuid NOT NULL,
    note_tag_id uuid NOT NULL
);


ALTER TABLE core.note_note_tags OWNER TO postgres;

--
-- Name: note_note_tags_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_note_tags_aud (
    note_id uuid NOT NULL,
    note_tag_id uuid NOT NULL,
    rev integer NOT NULL,
    revtype smallint
);


ALTER TABLE core.note_note_tags_aud OWNER TO postgres;

--
-- Name: note_tags; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_tags (
    id uuid NOT NULL,
    tag character varying(255) NOT NULL,
    entity_type character varying(255),
    entity_id character varying(255)
);


ALTER TABLE core.note_tags OWNER TO postgres;

--
-- Name: note_tags_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_tags_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    tag character varying(255),
    entity_type character varying(255),
    entity_id character varying(255)
);


ALTER TABLE core.note_tags_aud OWNER TO postgres;

--
-- Name: note_tags_notes_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_tags_notes_aud (
    note_tag_id uuid NOT NULL,
    notes_id uuid NOT NULL,
    rev integer NOT NULL,
    revtype smallint
);


ALTER TABLE core.note_tags_notes_aud OWNER TO postgres;

--
-- Name: note_thread_subscriptions; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_thread_subscriptions (
    id uuid NOT NULL,
    thread_id uuid NOT NULL,
    user_id uuid NOT NULL,
    active boolean DEFAULT true NOT NULL,
    last_read_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE core.note_thread_subscriptions OWNER TO postgres;

--
-- Name: note_thread_subscriptions_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_thread_subscriptions_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    thread_id uuid,
    user_id uuid,
    active boolean,
    last_read_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE core.note_thread_subscriptions_aud OWNER TO postgres;

--
-- Name: note_threads; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_threads (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    entity_type smallint NOT NULL,
    source_id uuid NOT NULL,
    user_owner_ids uuid[],
    status smallint NOT NULL,
    resolved_by uuid,
    resolved_at timestamp without time zone,
    last_activity_at timestamp without time zone NOT NULL,
    root_note_id uuid
);


ALTER TABLE core.note_threads OWNER TO postgres;

--
-- Name: note_threads_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.note_threads_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    entity_type smallint,
    source_id uuid,
    user_owner_ids uuid[],
    status smallint,
    resolved_by uuid,
    resolved_at timestamp without time zone,
    last_activity_at timestamp without time zone,
    root_note_id uuid
);


ALTER TABLE core.note_threads_aud OWNER TO postgres;

--
-- Name: notes; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.notes (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    entity_type smallint NOT NULL,
    source_id uuid NOT NULL,
    title character varying(255),
    content text NOT NULL,
    create_name character varying(255),
    private_note boolean NOT NULL,
    parent_id uuid,
    user_owner_ids uuid[],
    thread_id uuid,
    CONSTRAINT chk_notes_content_length CHECK ((char_length(content) <= 50000))
);


ALTER TABLE core.notes OWNER TO postgres;

--
-- Name: notes_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.notes_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    entity_type smallint,
    user_owner_ids uuid[],
    source_id uuid,
    title character varying(255),
    content text,
    create_name character varying(255),
    private_note boolean,
    parent_id uuid,
    thread_id uuid
);


ALTER TABLE core.notes_aud OWNER TO postgres;

--
-- Name: participants; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.participants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    entity_type character varying(50) NOT NULL,
    role character varying(50) NOT NULL,
    note_id uuid,
    contact_id uuid,
    source_id uuid NOT NULL,
    creation_type integer DEFAULT 1 NOT NULL,
    user_owner_ids uuid[]
);


ALTER TABLE core.participants OWNER TO postgres;

--
-- Name: participants_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.participants_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    entity_type character varying(50),
    role character varying(50),
    note_id uuid,
    contact_id uuid,
    source_id uuid,
    creation_type integer,
    user_owner_ids uuid[]
);


ALTER TABLE core.participants_aud OWNER TO postgres;

--
-- Name: product_categories; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_categories (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    factory_id uuid NOT NULL,
    commission_rate numeric NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE core.product_categories OWNER TO postgres;

--
-- Name: product_categories_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_categories_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    title character varying(255),
    factory_id uuid,
    commission_rate numeric,
    is_used boolean DEFAULT false NOT NULL
);


ALTER TABLE core.product_categories_aud OWNER TO postgres;

--
-- Name: product_commission_bands; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_commission_bands (
    id uuid NOT NULL,
    product_id uuid NOT NULL,
    lower numeric(19,2),
    upper numeric(19,2),
    rate numeric(19,2)
);


ALTER TABLE core.product_commission_bands OWNER TO postgres;

--
-- Name: product_commission_bands_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_commission_bands_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    product_id uuid,
    lower numeric(19,2),
    upper numeric(19,2),
    rate numeric(19,2)
);


ALTER TABLE core.product_commission_bands_aud OWNER TO postgres;

--
-- Name: product_cpns; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_cpns (
    id uuid NOT NULL,
    product_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    customer_part_number character varying(255) NOT NULL,
    unit_price numeric NOT NULL,
    commission_rate numeric NOT NULL
);


ALTER TABLE core.product_cpns OWNER TO postgres;

--
-- Name: product_cpns_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_cpns_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    product_id uuid,
    customer_id uuid,
    customer_part_number character varying(255),
    unit_price numeric,
    commission_rate numeric
);


ALTER TABLE core.product_cpns_aud OWNER TO postgres;

--
-- Name: product_measurements; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_measurements (
    id uuid NOT NULL,
    product_id uuid NOT NULL,
    net_weight numeric(19,2),
    gross_weight numeric(19,2),
    weight_uom character varying(255),
    length numeric(19,2),
    width numeric(19,2),
    height numeric(19,2),
    length_uom character varying(255),
    volume numeric(19,2),
    volume_uom character varying(255),
    units_per_case integer,
    tare_weight numeric(19,3)
);


ALTER TABLE core.product_measurements OWNER TO postgres;

--
-- Name: product_measurements_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_measurements_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    product_id uuid,
    net_weight numeric(19,2),
    gross_weight numeric(19,2),
    weight_uom character varying(255),
    length numeric(19,2),
    width numeric(19,2),
    height numeric(19,2),
    length_uom character varying(255),
    volume numeric(19,2),
    volume_uom character varying(255),
    units_per_case integer,
    tare_weight numeric(19,3)
);


ALTER TABLE core.product_measurements_aud OWNER TO postgres;

--
-- Name: product_quantity_pricing; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_quantity_pricing (
    id uuid NOT NULL,
    product_id uuid NOT NULL,
    quantity_low integer NOT NULL,
    quantity_high integer NOT NULL,
    unit_price numeric NOT NULL,
    commission_rate numeric(19,3)
);


ALTER TABLE core.product_quantity_pricing OWNER TO postgres;

--
-- Name: product_quantity_pricing_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_quantity_pricing_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    product_id uuid,
    quantity_low integer,
    quantity_high integer,
    unit_price numeric,
    commission_rate numeric(19,3)
);


ALTER TABLE core.product_quantity_pricing_aud OWNER TO postgres;

--
-- Name: product_uoms; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_uoms (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    description character varying(255),
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    multiply boolean DEFAULT false NOT NULL,
    multiply_by integer DEFAULT 1 NOT NULL
);


ALTER TABLE core.product_uoms OWNER TO postgres;

--
-- Name: product_uoms_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.product_uoms_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    title character varying(255),
    description character varying(255),
    is_used boolean DEFAULT false NOT NULL,
    multiply boolean DEFAULT false NOT NULL,
    multiply_by integer DEFAULT 1 NOT NULL
);


ALTER TABLE core.product_uoms_aud OWNER TO postgres;

--
-- Name: products; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.products (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    factory_part_number character varying(255) NOT NULL,
    factory_id uuid NOT NULL,
    product_category_id uuid NOT NULL,
    product_uom_id uuid NOT NULL,
    lead_time character varying(255),
    description character varying(5000),
    unit_price numeric NOT NULL,
    min_order_qty integer,
    default_commission_rate numeric NOT NULL,
    commission_discount_rate numeric,
    overall_discount_rate numeric,
    cost numeric,
    individual_upc character varying(255),
    published boolean NOT NULL,
    approval_needed boolean NOT NULL,
    approval_date date,
    approval_comments character varying(255),
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    logo_url text,
    sales_model character varying(255),
    inventory_source character varying(255),
    invoice_party character varying(255),
    warehouse_ids uuid[],
    payout_type character varying(255),
    overage_allowed boolean DEFAULT false NOT NULL,
    overage_allowed_type character varying(255),
    overage_unit_price numeric(19,2)
);


ALTER TABLE core.products OWNER TO postgres;

--
-- Name: products_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.products_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    factory_part_number character varying(255),
    factory_id uuid,
    product_category_id uuid,
    product_uom_id uuid,
    lead_time character varying(255),
    description character varying(5000),
    unit_price numeric,
    min_order_qty integer,
    default_commission_rate numeric,
    commission_discount_rate numeric,
    overall_discount_rate numeric,
    cost numeric,
    individual_upc character varying(255),
    published boolean,
    approval_needed boolean,
    approval_date character varying(255),
    approval_comments character varying(255),
    is_used boolean DEFAULT false NOT NULL,
    logo_url text,
    sales_model character varying(255),
    inventory_source character varying(255),
    invoice_party character varying(255),
    warehouse_ids uuid[],
    payout_type character varying(255),
    overage_allowed boolean DEFAULT false,
    overage_allowed_type character varying(255),
    overage_unit_price numeric(19,2)
);


ALTER TABLE core.products_aud OWNER TO postgres;

--
-- Name: revinfo; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.revinfo (
    rev integer NOT NULL,
    revtstmp bigint
);


ALTER TABLE core.revinfo OWNER TO postgres;

--
-- Name: revinfo_seq; Type: SEQUENCE; Schema: core; Owner: postgres
--

CREATE SEQUENCE core.revinfo_seq
    START WITH 1
    INCREMENT BY 50
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE core.revinfo_seq OWNER TO postgres;

--
-- Name: sales_rep_selection_split_rates; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.sales_rep_selection_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    sales_pep_selection_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL
);


ALTER TABLE core.sales_rep_selection_split_rates OWNER TO postgres;

--
-- Name: sales_rep_selection_split_rates_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.sales_rep_selection_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    sales_pep_selection_id uuid,
    split_rate numeric,
    "position" numeric DEFAULT 0
);


ALTER TABLE core.sales_rep_selection_split_rates_aud OWNER TO postgres;

--
-- Name: sales_rep_selections; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.sales_rep_selections (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    customer_id uuid NOT NULL,
    factory_id uuid NOT NULL
);


ALTER TABLE core.sales_rep_selections OWNER TO postgres;

--
-- Name: sales_rep_selections_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.sales_rep_selections_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    customer_id uuid,
    factory_id uuid
);


ALTER TABLE core.sales_rep_selections_aud OWNER TO postgres;

--
-- Name: site_options; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.site_options (
    id uuid NOT NULL,
    key smallint NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE core.site_options OWNER TO postgres;

--
-- Name: site_options_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.site_options_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    key smallint,
    value character varying(255)
);


ALTER TABLE core.site_options_aud OWNER TO postgres;

--
-- Name: stepped_commission_tiers; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.stepped_commission_tiers (
    id uuid NOT NULL,
    factory_id uuid NOT NULL,
    sales_min numeric(19,2),
    sales_max numeric(19,2),
    commission_rate numeric(19,2)
);


ALTER TABLE core.stepped_commission_tiers OWNER TO postgres;

--
-- Name: stepped_commission_tiers_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.stepped_commission_tiers_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    factory_id uuid,
    sales_min numeric(19,2),
    sales_max numeric(19,2),
    commission_rate numeric(19,2)
);


ALTER TABLE core.stepped_commission_tiers_aud OWNER TO postgres;

--
-- Name: subdivisions; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.subdivisions (
    iso_code character varying(16) NOT NULL,
    country_code character(2) NOT NULL,
    code character varying(16) NOT NULL,
    name character varying(150) NOT NULL,
    type character varying(50)
);


ALTER TABLE core.subdivisions OWNER TO postgres;

--
-- Name: subdivisions_aud; Type: TABLE; Schema: core; Owner: postgres
--

CREATE TABLE core.subdivisions_aud (
    rev integer NOT NULL,
    revtype smallint,
    iso_code character varying(16) NOT NULL,
    country_code character(2) NOT NULL,
    code character varying(16) NOT NULL,
    name character varying(150) NOT NULL,
    type character varying(50)
);


ALTER TABLE core.subdivisions_aud OWNER TO postgres;

--
-- Name: databasechangelog; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.databasechangelog (
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


ALTER TABLE crm.databasechangelog OWNER TO postgres;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE crm.databasechangeloglock OWNER TO postgres;

--
-- Name: jobs; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.jobs (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    status character varying(255) NOT NULL,
    is_used boolean DEFAULT false NOT NULL,
    job_name character varying(255) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    description text,
    requester_id uuid,
    job_owner_id uuid NOT NULL,
    participant_ids uuid[]
);


ALTER TABLE crm.jobs OWNER TO postgres;

--
-- Name: jobs_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.jobs_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    status character varying(255),
    is_used boolean DEFAULT false NOT NULL,
    job_name character varying(255),
    start_date date,
    end_date date,
    description text,
    requester_id uuid,
    job_owner_id uuid,
    participant_ids uuid[]
);


ALTER TABLE crm.jobs_aud OWNER TO postgres;

--
-- Name: pre_opportunities; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunities (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    user_owner_ids uuid[],
    creation_type smallint NOT NULL,
    status character varying(255) NOT NULL,
    published boolean NOT NULL,
    balance_id uuid NOT NULL,
    entity_number character varying(255) NOT NULL,
    sold_to_customer_id uuid NOT NULL,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    job_id uuid,
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    entity_date date NOT NULL,
    exp_date date,
    revise_date date,
    accept_date date,
    participant_ids uuid[]
);


ALTER TABLE crm.pre_opportunities OWNER TO postgres;

--
-- Name: pre_opportunities_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunities_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    balance_id uuid,
    status character varying(255),
    entity_number character varying(255),
    sold_to_customer_id uuid,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    job_id uuid,
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    entity_date date,
    exp_date date,
    revise_date date,
    accept_date date,
    participant_ids uuid[]
);


ALTER TABLE crm.pre_opportunities_aud OWNER TO postgres;

--
-- Name: pre_opportunity_balances; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_balances (
    id uuid NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    total numeric NOT NULL,
    quantity integer NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount numeric DEFAULT 0 NOT NULL,
    discount_rate numeric DEFAULT 0 NOT NULL
);


ALTER TABLE crm.pre_opportunity_balances OWNER TO postgres;

--
-- Name: pre_opportunity_balances_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quantity integer,
    total numeric,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    subtotal numeric DEFAULT 0,
    discount numeric DEFAULT 0,
    discount_rate numeric DEFAULT 0
);


ALTER TABLE crm.pre_opportunity_balances_aud OWNER TO postgres;

--
-- Name: pre_opportunity_details; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_details (
    id uuid NOT NULL,
    pre_opportunity_id uuid NOT NULL,
    status character varying(255) NOT NULL,
    quantity integer NOT NULL,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    total numeric NOT NULL,
    unit_price numeric NOT NULL,
    product_id uuid NOT NULL,
    product_cpn_id uuid,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount_rate numeric NOT NULL,
    discount numeric NOT NULL,
    item_number integer NOT NULL,
    end_user_id uuid NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    lead_time character varying(255),
    lost_reason_id uuid,
    lost_reason_other character varying(255),
    factory_id uuid NOT NULL
);


ALTER TABLE crm.pre_opportunity_details OWNER TO postgres;

--
-- Name: pre_opportunity_details_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    pre_opportunity_id uuid,
    item_number integer,
    status character varying(255),
    quantity integer,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    total numeric,
    unit_price numeric,
    product_id uuid,
    product_cpn_id uuid,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount_rate numeric,
    discount numeric,
    end_user_id uuid,
    subtotal numeric DEFAULT 0,
    lead_time character varying(255),
    lost_reason_id uuid,
    lost_reason_other character varying(255),
    factory_id uuid
);


ALTER TABLE crm.pre_opportunity_details_aud OWNER TO postgres;

--
-- Name: pre_opportunity_inside_reps; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_inside_reps (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    pre_opportunity_id uuid NOT NULL
);


ALTER TABLE crm.pre_opportunity_inside_reps OWNER TO postgres;

--
-- Name: pre_opportunity_inside_reps_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_inside_reps_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    pre_opportunity_id uuid
);


ALTER TABLE crm.pre_opportunity_inside_reps_aud OWNER TO postgres;

--
-- Name: pre_opportunity_lost_reasons; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_lost_reasons (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    title character varying(255) NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL
);


ALTER TABLE crm.pre_opportunity_lost_reasons OWNER TO postgres;

--
-- Name: pre_opportunity_lost_reasons_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_lost_reasons_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    title character varying(255),
    "position" numeric DEFAULT 0
);


ALTER TABLE crm.pre_opportunity_lost_reasons_aud OWNER TO postgres;

--
-- Name: pre_opportunity_split_rates; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    pre_opportunity_detail_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    commission_amount numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL,
    sales_amount numeric DEFAULT 0 NOT NULL,
    created_by uuid NOT NULL
);


ALTER TABLE crm.pre_opportunity_split_rates OWNER TO postgres;

--
-- Name: pre_opportunity_split_rates_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.pre_opportunity_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    pre_opportunity_detail_id uuid,
    split_rate numeric,
    commission_amount numeric,
    "position" numeric DEFAULT 0,
    sales_amount numeric DEFAULT 0,
    created_by uuid
);


ALTER TABLE crm.pre_opportunity_split_rates_aud OWNER TO postgres;

--
-- Name: quote_balances; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_balances (
    id uuid NOT NULL,
    total numeric NOT NULL,
    quantity integer NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount numeric DEFAULT 0 NOT NULL,
    discount_rate numeric DEFAULT 0 NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL
);


ALTER TABLE crm.quote_balances OWNER TO postgres;

--
-- Name: quote_balances_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_balances_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quantity integer,
    total numeric,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount numeric DEFAULT 0,
    discount_rate numeric DEFAULT 0,
    subtotal numeric DEFAULT 0
);


ALTER TABLE crm.quote_balances_aud OWNER TO postgres;

--
-- Name: quote_details; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_details (
    id uuid NOT NULL,
    quote_id uuid NOT NULL,
    status smallint NOT NULL,
    quantity integer NOT NULL,
    total numeric NOT NULL,
    unit_price numeric NOT NULL,
    product_id uuid NOT NULL,
    commission_rate numeric NOT NULL,
    commission numeric NOT NULL,
    commission_discount_rate numeric NOT NULL,
    commission_discount numeric NOT NULL,
    discount_rate numeric NOT NULL,
    discount numeric NOT NULL,
    item_number integer NOT NULL,
    end_user_id uuid NOT NULL,
    lead_time character varying(255),
    lost_reason_id uuid,
    lost_reason_other character varying(255),
    product_cpn_id uuid,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    subtotal numeric DEFAULT 0 NOT NULL,
    factory_id uuid,
    base_unit_price numeric(19,4),
    overage_commission numeric(19,4),
    rep_share numeric(19,4),
    level_rate numeric(19,4),
    level_unit_price numeric(19,4),
    overage_commission_rate numeric(19,4),
    base_commission_rate numeric(19,4),
    note character varying(2000),
    base_commission numeric(19,4)
);


ALTER TABLE crm.quote_details OWNER TO postgres;

--
-- Name: quote_details_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_details_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    quote_id uuid,
    item_number integer,
    status smallint,
    quantity integer,
    total numeric,
    unit_price numeric,
    product_id uuid,
    commission_rate numeric,
    commission numeric,
    commission_discount_rate numeric,
    commission_discount numeric,
    discount_rate numeric,
    discount numeric,
    end_user_id uuid,
    lead_time character varying(255),
    lost_reason_id uuid,
    lost_reason_other character varying(255),
    product_cpn_id uuid,
    uom_multiply boolean DEFAULT false NOT NULL,
    uom_multiply_by integer DEFAULT 1 NOT NULL,
    subtotal numeric DEFAULT 0,
    factory_id uuid,
    base_unit_price numeric(19,4),
    overage_commission numeric(19,4),
    rep_share numeric(19,4),
    level_rate numeric(19,4),
    level_unit_price numeric(19,4),
    overage_commission_rate numeric(19,4),
    base_commission_rate numeric(19,4),
    note character varying(2000),
    base_commission numeric(19,4)
);


ALTER TABLE crm.quote_details_aud OWNER TO postgres;

--
-- Name: quote_inside_reps; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_inside_reps (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    quote_id uuid NOT NULL
);


ALTER TABLE crm.quote_inside_reps OWNER TO postgres;

--
-- Name: quote_inside_reps_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_inside_reps_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    quote_id uuid
);


ALTER TABLE crm.quote_inside_reps_aud OWNER TO postgres;

--
-- Name: quote_lost_reasons; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_lost_reasons (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    user_owner_ids uuid[],
    is_used boolean DEFAULT false NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL
);


ALTER TABLE crm.quote_lost_reasons OWNER TO postgres;

--
-- Name: quote_lost_reasons_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_lost_reasons_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    title character varying(255),
    is_used boolean DEFAULT false NOT NULL,
    "position" numeric DEFAULT 0
);


ALTER TABLE crm.quote_lost_reasons_aud OWNER TO postgres;

--
-- Name: quote_split_rates; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_split_rates (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    user_id uuid NOT NULL,
    quote_detail_id uuid NOT NULL,
    split_rate numeric NOT NULL,
    commission_amount numeric NOT NULL,
    "position" numeric DEFAULT 0 NOT NULL,
    sales_amount numeric DEFAULT 0 NOT NULL,
    created_by uuid NOT NULL
);


ALTER TABLE crm.quote_split_rates OWNER TO postgres;

--
-- Name: quote_split_rates_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quote_split_rates_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    user_id uuid,
    quote_detail_id uuid,
    split_rate numeric,
    commission_amount numeric,
    "position" numeric DEFAULT 0,
    sales_amount numeric DEFAULT 0,
    created_by uuid
);


ALTER TABLE crm.quote_split_rates_aud OWNER TO postgres;

--
-- Name: quotes; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quotes (
    id uuid NOT NULL,
    entry_date timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    creation_type smallint NOT NULL,
    status smallint NOT NULL,
    published boolean NOT NULL,
    balance_id uuid NOT NULL,
    quote_number character varying(255) NOT NULL,
    sold_to_customer_id uuid,
    job_name character varying(255),
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    entity_date date NOT NULL,
    exp_date date,
    revise_date date,
    accept_date date,
    blanket boolean NOT NULL,
    user_owner_ids uuid[],
    job_id uuid,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    duplicated_from uuid,
    participant_ids uuid[]
);


ALTER TABLE crm.quotes OWNER TO postgres;

--
-- Name: quotes_aud; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.quotes_aud (
    rev integer NOT NULL,
    revtype smallint,
    id uuid NOT NULL,
    entry_date timestamp without time zone,
    created_by uuid,
    creation_type smallint,
    user_owner_ids uuid[],
    published boolean,
    balance_id uuid,
    status smallint,
    quote_number character varying(255),
    sold_to_customer_id uuid,
    job_name character varying(255),
    payment_terms character varying(255),
    customer_ref character varying(255),
    freight_terms character varying(255),
    entity_date date,
    exp_date date,
    revise_date date,
    accept_date date,
    blanket boolean,
    job_id uuid,
    sold_to_customer_address_id uuid,
    bill_to_customer_id uuid,
    bill_to_customer_address_id uuid,
    duplicated_from uuid,
    participant_ids uuid[]
);


ALTER TABLE crm.quotes_aud OWNER TO postgres;

--
-- Name: revinfo; Type: TABLE; Schema: crm; Owner: postgres
--

CREATE TABLE crm.revinfo (
    rev integer NOT NULL,
    revtstmp bigint
);


ALTER TABLE crm.revinfo OWNER TO postgres;

--
-- Name: revinfo_seq; Type: SEQUENCE; Schema: crm; Owner: postgres
--

CREATE SEQUENCE crm.revinfo_seq
    START WITH 1
    INCREMENT BY 50
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE crm.revinfo_seq OWNER TO postgres;

--
-- Name: extension_icons; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.extension_icons (
    extension character varying NOT NULL,
    icon character varying NOT NULL
);


ALTER TABLE files.extension_icons OWNER TO postgres;

--
-- Name: file_entity_details; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_entity_details (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    file_id uuid NOT NULL,
    entity_type public.entity_types,
    entity_id uuid,
    action smallint
);


ALTER TABLE files.file_entity_details OWNER TO postgres;

--
-- Name: COLUMN file_entity_details.action; Type: COMMENT; Schema: files; Owner: postgres
--

COMMENT ON COLUMN files.file_entity_details.action IS 'Action performed on the entity detail';


--
-- Name: file_meta; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_meta (
    file_id uuid NOT NULL,
    file_content text NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


ALTER TABLE files.file_meta OWNER TO postgres;

--
-- Name: file_service_alembic_version; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_service_alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE files.file_service_alembic_version OWNER TO postgres;

--
-- Name: file_summary; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_summary (
    file_id uuid NOT NULL,
    requested_by uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    id uuid NOT NULL,
    summary text
);


ALTER TABLE files.file_summary OWNER TO postgres;

--
-- Name: file_upload_details; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_upload_details (
    id uuid NOT NULL,
    file_upload_id uuid NOT NULL,
    message text NOT NULL,
    data json,
    file_upload_process_dto_id uuid
);


ALTER TABLE files.file_upload_details OWNER TO postgres;

--
-- Name: file_upload_process; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_upload_process (
    id uuid NOT NULL,
    file_id uuid NOT NULL,
    status public.processstatusgql NOT NULL,
    meta_data json,
    create_date timestamp with time zone DEFAULT now() NOT NULL,
    fields json,
    tabular_meta_data json,
    sub_process_entities json,
    queue_status public.queue_status DEFAULT 'QUEUED'::public.queue_status NOT NULL,
    batch_id uuid,
    message text,
    task_id uuid,
    entity_type public.entity_types,
    similar_file_upload_process_ids uuid[] DEFAULT ARRAY[]::uuid[] NOT NULL,
    retry_attempts integer,
    current_dto_id uuid,
    flowbot_workfile_path character varying,
    paused_action smallint,
    archived boolean NOT NULL,
    archived_at timestamp without time zone,
    archived_by uuid,
    pending_document_id uuid
);


ALTER TABLE files.file_upload_process OWNER TO postgres;

--
-- Name: COLUMN file_upload_process.flowbot_workfile_path; Type: COMMENT; Schema: files; Owner: postgres
--

COMMENT ON COLUMN files.file_upload_process.flowbot_workfile_path IS 'Path to the flowbot workfile at DoSpaces';


--
-- Name: COLUMN file_upload_process.paused_action; Type: COMMENT; Schema: files; Owner: postgres
--

COMMENT ON COLUMN files.file_upload_process.paused_action IS 'Action to take when the process is paused. This can be used to resume the process later.';


--
-- Name: COLUMN file_upload_process.pending_document_id; Type: COMMENT; Schema: files; Owner: postgres
--

COMMENT ON COLUMN files.file_upload_process.pending_document_id IS 'ID of the pending document associated with this file upload process.';


--
-- Name: file_upload_process_dtos; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_upload_process_dtos (
    id uuid NOT NULL,
    file_upload_process_id uuid NOT NULL,
    dto json NOT NULL,
    processed boolean NOT NULL
);


ALTER TABLE files.file_upload_process_dtos OWNER TO postgres;

--
-- Name: file_upload_process_stats; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.file_upload_process_stats (
    id uuid NOT NULL,
    file_upload_process_id uuid NOT NULL,
    task_id uuid NOT NULL,
    execution_time double precision NOT NULL,
    process_status public.processstatusgql NOT NULL,
    created_at timestamp without time zone NOT NULL,
    meta_data json NOT NULL
);


ALTER TABLE files.file_upload_process_stats OWNER TO postgres;

--
-- Name: files; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.files (
    file_name character varying(500) NOT NULL,
    file_path character varying(2000) NOT NULL,
    created_by uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    file_type character varying,
    id uuid NOT NULL,
    archived boolean DEFAULT false NOT NULL,
    archived_at timestamp with time zone,
    archived_by uuid,
    thumbnail_path character varying,
    thumbnail character varying,
    folder_id uuid,
    file_size integer NOT NULL,
    vectorized boolean NOT NULL,
    converted_key character varying,
    tabular_converted_key character varying,
    file_sha character varying
);


ALTER TABLE files.files OWNER TO postgres;

--
-- Name: flowbot_file; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.flowbot_file (
    id uuid NOT NULL,
    file_name character varying NOT NULL,
    file_path character varying NOT NULL,
    file_size integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    created_by uuid NOT NULL,
    updated_at timestamp without time zone,
    deleted boolean NOT NULL,
    deleted_at timestamp without time zone,
    deleted_by uuid
);


ALTER TABLE files.flowbot_file OWNER TO postgres;

--
-- Name: COLUMN flowbot_file.deleted; Type: COMMENT; Schema: files; Owner: postgres
--

COMMENT ON COLUMN files.flowbot_file.deleted IS 'Is the file deleted from DigitalOcean';


--
-- Name: folders; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.folders (
    id uuid NOT NULL,
    name character varying NOT NULL,
    create_date timestamp with time zone DEFAULT now() NOT NULL,
    created_by uuid NOT NULL,
    updated_by uuid,
    update_date timestamp with time zone DEFAULT now() NOT NULL,
    count_of_files integer NOT NULL,
    archived boolean NOT NULL,
    s3_path character varying(2000) NOT NULL,
    is_public boolean NOT NULL
);


ALTER TABLE files.folders OWNER TO postgres;

--
-- Name: ocr_meta; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.ocr_meta (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_id character varying NOT NULL,
    file_id uuid NOT NULL,
    parsed_text text NOT NULL,
    tables json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta_data json
);


ALTER TABLE files.ocr_meta OWNER TO postgres;

--
-- Name: ocr_pages; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.ocr_pages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    meta_id uuid NOT NULL,
    page integer NOT NULL,
    text text NOT NULL,
    tables json NOT NULL,
    forms json NOT NULL
);


ALTER TABLE files.ocr_pages OWNER TO postgres;

--
-- Name: tags; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.tags (
    id uuid NOT NULL,
    color character varying(12) NOT NULL,
    created_by uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    tag_name character varying(255) NOT NULL,
    file_id uuid NOT NULL,
    archived boolean DEFAULT false NOT NULL
);


ALTER TABLE files.tags OWNER TO postgres;

--
-- Name: vectorization; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.vectorization (
    file_id uuid NOT NULL,
    page_content text NOT NULL,
    page_number integer NOT NULL,
    content_hash character varying NOT NULL,
    embedding public.vector(1536) NOT NULL,
    created_at timestamp with time zone,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);
ALTER TABLE ONLY files.vectorization ALTER COLUMN embedding SET STORAGE PLAIN;


ALTER TABLE files.vectorization OWNER TO postgres;

--
-- Name: vectorization_status; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.vectorization_status (
    id uuid NOT NULL,
    file_id uuid NOT NULL,
    vectorization_status public.processstatusgql NOT NULL,
    message character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE files.vectorization_status OWNER TO postgres;

--
-- Name: votes; Type: TABLE; Schema: files; Owner: postgres
--

CREATE TABLE files.votes (
    summary_id uuid NOT NULL,
    positive boolean NOT NULL,
    voted_by uuid NOT NULL,
    voted_at timestamp with time zone NOT NULL,
    id uuid NOT NULL
);


ALTER TABLE files.votes OWNER TO postgres;

--
-- Name: addresses; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.addresses (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    company_id uuid NOT NULL,
    address_type smallint NOT NULL,
    address_line_1 character varying(255),
    address_line_2 character varying(255),
    city character varying(100),
    state character varying(100),
    zip_code character varying(20)
);


ALTER TABLE pycrm.addresses OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE pycrm.alembic_version OWNER TO postgres;

--
-- Name: campaign_criteria; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.campaign_criteria (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    criteria_json jsonb NOT NULL,
    is_dynamic boolean NOT NULL
);


ALTER TABLE pycrm.campaign_criteria OWNER TO postgres;

--
-- Name: campaign_recipients; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.campaign_recipients (
    id uuid NOT NULL,
    campaign_id uuid NOT NULL,
    contact_id uuid NOT NULL,
    email_status integer NOT NULL,
    sent_at timestamp with time zone,
    personalized_content text
);


ALTER TABLE pycrm.campaign_recipients OWNER TO postgres;

--
-- Name: campaign_send_logs; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.campaign_send_logs (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    campaign_id uuid NOT NULL,
    send_date date NOT NULL,
    emails_sent integer NOT NULL,
    last_sent_at timestamp with time zone
);


ALTER TABLE pycrm.campaign_send_logs OWNER TO postgres;

--
-- Name: campaigns; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.campaigns (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    status integer NOT NULL,
    recipient_list_type integer NOT NULL,
    description text,
    email_subject character varying(500),
    email_body text,
    ai_personalization_enabled boolean NOT NULL,
    send_pace integer NOT NULL,
    max_emails_per_day integer,
    scheduled_at timestamp with time zone,
    send_immediately boolean NOT NULL
);


ALTER TABLE pycrm.campaigns OWNER TO postgres;

--
-- Name: companies; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.companies (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    company_source_type smallint NOT NULL,
    website character varying(255),
    phone character varying(50),
    tags character varying[],
    parent_company_id uuid
);


ALTER TABLE pycrm.companies OWNER TO postgres;

--
-- Name: contacts; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.contacts (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255),
    phone character varying(50),
    role character varying(100),
    territory character varying(100),
    tags character varying[],
    notes text
);


ALTER TABLE pycrm.contacts OWNER TO postgres;

--
-- Name: gmail_user_tokens; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.gmail_user_tokens (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id uuid NOT NULL,
    google_user_id character varying(255) NOT NULL,
    google_email character varying(255) NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    token_type character varying(50) DEFAULT 'Bearer'::character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    scope text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_used_at timestamp with time zone
);


ALTER TABLE pycrm.gmail_user_tokens OWNER TO postgres;

--
-- Name: job_statuses; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.job_statuses (
    id uuid NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE pycrm.job_statuses OWNER TO postgres;

--
-- Name: jobs; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.jobs (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    job_name character varying(255) NOT NULL,
    status_id uuid NOT NULL,
    start_date date,
    end_date date,
    description text,
    job_type text,
    structural_details text,
    structural_information text,
    additional_information text,
    requester_id uuid,
    job_owner_id uuid,
    tags character varying[]
);


ALTER TABLE pycrm.jobs OWNER TO postgres;

--
-- Name: link_relations; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.link_relations (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    source_entity_type smallint NOT NULL,
    source_entity_id uuid NOT NULL,
    target_entity_type smallint NOT NULL,
    target_entity_id uuid NOT NULL
);


ALTER TABLE pycrm.link_relations OWNER TO postgres;

--
-- Name: manufacturer_order; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.manufacturer_order (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    factory_id uuid NOT NULL,
    sort_order integer DEFAULT 0 NOT NULL
);


ALTER TABLE pycrm.manufacturer_order OWNER TO postgres;

--
-- Name: note_conversations; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.note_conversations (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    note_id uuid NOT NULL,
    content text NOT NULL
);


ALTER TABLE pycrm.note_conversations OWNER TO postgres;

--
-- Name: notes; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.notes (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    tags character varying[],
    mentions uuid[]
);


ALTER TABLE pycrm.notes OWNER TO postgres;

--
-- Name: o365_user_tokens; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.o365_user_tokens (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id uuid NOT NULL,
    microsoft_user_id character varying(255) NOT NULL,
    microsoft_email character varying(255) NOT NULL,
    access_token text NOT NULL,
    refresh_token text NOT NULL,
    token_type character varying(50) DEFAULT 'Bearer'::character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    scope text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    last_used_at timestamp with time zone
);


ALTER TABLE pycrm.o365_user_tokens OWNER TO postgres;

--
-- Name: pre_opportunities; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.pre_opportunities (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
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
    tags character varying[]
);


ALTER TABLE pycrm.pre_opportunities OWNER TO postgres;

--
-- Name: pre_opportunity_balances; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.pre_opportunity_balances (
    id uuid NOT NULL,
    subtotal numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    total numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    quantity numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    discount numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    discount_rate numeric(5,2) DEFAULT '0'::numeric NOT NULL
);


ALTER TABLE pycrm.pre_opportunity_balances OWNER TO postgres;

--
-- Name: pre_opportunity_details; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.pre_opportunity_details (
    id uuid NOT NULL,
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
    lead_time character varying(255)
);


ALTER TABLE pycrm.pre_opportunity_details OWNER TO postgres;

--
-- Name: spec_sheet_highlight_regions; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.spec_sheet_highlight_regions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version_id uuid NOT NULL,
    page_number integer NOT NULL,
    x double precision NOT NULL,
    y double precision NOT NULL,
    width double precision NOT NULL,
    height double precision NOT NULL,
    shape_type character varying(50) NOT NULL,
    color character varying(20) NOT NULL,
    annotation text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_highlight_regions_shape_type CHECK (((shape_type)::text = ANY ((ARRAY['rectangle'::character varying, 'oval'::character varying, 'highlight'::character varying])::text[])))
);


ALTER TABLE pycrm.spec_sheet_highlight_regions OWNER TO postgres;

--
-- Name: spec_sheet_highlight_versions; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.spec_sheet_highlight_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    spec_sheet_id uuid NOT NULL,
    name character varying(255) DEFAULT 'Default Highlights'::character varying NOT NULL,
    description text,
    version_number integer DEFAULT 1 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE pycrm.spec_sheet_highlight_versions OWNER TO postgres;

--
-- Name: spec_sheets; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.spec_sheets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    factory_id uuid NOT NULL,
    file_name character varying(255) NOT NULL,
    display_name character varying(255) NOT NULL,
    upload_source character varying(50) NOT NULL,
    source_url text,
    file_url text NOT NULL,
    file_size bigint NOT NULL,
    page_count integer DEFAULT 1 NOT NULL,
    categories character varying[] NOT NULL,
    tags character varying[],
    needs_review boolean DEFAULT false NOT NULL,
    published boolean DEFAULT true NOT NULL,
    usage_count integer DEFAULT 0 NOT NULL,
    highlight_count integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id uuid NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    folder_path character varying(500),
    CONSTRAINT ck_spec_sheets_upload_source CHECK (((upload_source)::text = ANY ((ARRAY['url'::character varying, 'file'::character varying])::text[])))
);


ALTER TABLE pycrm.spec_sheets OWNER TO postgres;

--
-- Name: task_conversations; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.task_conversations (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    task_id uuid NOT NULL,
    content text NOT NULL
);


ALTER TABLE pycrm.task_conversations OWNER TO postgres;

--
-- Name: tasks; Type: TABLE; Schema: pycrm; Owner: postgres
--

CREATE TABLE pycrm.tasks (
    id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    status smallint NOT NULL,
    priority smallint NOT NULL,
    description text,
    assigned_to_id uuid,
    due_date date,
    tags character varying[],
    reminder_date date
);


ALTER TABLE pycrm.tasks OWNER TO postgres;

--
-- Name: alembic_version; Type: TABLE; Schema: report; Owner: postgres
--

CREATE TABLE report.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE report.alembic_version OWNER TO postgres;

--
-- Name: report_templates; Type: TABLE; Schema: report; Owner: postgres
--

CREATE TABLE report.report_templates (
    id uuid NOT NULL,
    report_template_name character varying NOT NULL,
    report_type smallint NOT NULL,
    report_config jsonb NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE report.report_templates OWNER TO postgres;

--
-- Name: signatures; Type: TABLE; Schema: uploader; Owner: postgres
--

CREATE TABLE uploader.signatures (
    id uuid NOT NULL,
    created_at timestamp without time zone NOT NULL,
    file_upload_process_id uuid NOT NULL,
    file_name character varying NOT NULL,
    sample_data character varying,
    original_columns character varying,
    skip_rows integer,
    embedding public.vector(1536) DEFAULT NULL::public.vector,
    feature_vector public.vector(11) DEFAULT NULL::public.vector,
    image_hashes character varying[] DEFAULT '{}'::character varying[]
);


ALTER TABLE uploader.signatures OWNER TO postgres;

--
-- Name: similar_matches; Type: TABLE; Schema: uploader; Owner: postgres
--

CREATE TABLE uploader.similar_matches (
    id uuid NOT NULL,
    match_id uuid NOT NULL,
    match_title character varying NOT NULL,
    original_title character varying NOT NULL,
    entity_type character varying NOT NULL,
    confidence_score double precision NOT NULL,
    address json,
    updated_at timestamp without time zone NOT NULL,
    last_used_file_upload_process_id uuid NOT NULL,
    similar_file_upload_process_ids uuid[],
    created_at timestamp without time zone NOT NULL,
    created_by_id uuid,
    last_modified_by_id uuid,
    confirmed_times integer DEFAULT 1 NOT NULL
);


ALTER TABLE uploader.similar_matches OWNER TO postgres;

--
-- Name: COLUMN similar_matches.match_id; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.match_id IS 'The id of the match';


--
-- Name: COLUMN similar_matches.match_title; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.match_title IS 'The title of the match';


--
-- Name: COLUMN similar_matches.original_title; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.original_title IS 'The original title of the match';


--
-- Name: COLUMN similar_matches.entity_type; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.entity_type IS 'The type of the entity';


--
-- Name: COLUMN similar_matches.confidence_score; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.confidence_score IS 'The confidence score of the match';


--
-- Name: COLUMN similar_matches.address; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.address IS 'The address of the match';


--
-- Name: COLUMN similar_matches.last_used_file_upload_process_id; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.last_used_file_upload_process_id IS 'The last used file upload process id';


--
-- Name: COLUMN similar_matches.similar_file_upload_process_ids; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.similar_file_upload_process_ids IS 'The list of similar file upload process ids';


--
-- Name: COLUMN similar_matches.created_by_id; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.created_by_id IS 'The ID of the user who created the match';


--
-- Name: COLUMN similar_matches.last_modified_by_id; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.last_modified_by_id IS 'The ID of the user who last modified the match';


--
-- Name: COLUMN similar_matches.confirmed_times; Type: COMMENT; Schema: uploader; Owner: postgres
--

COMMENT ON COLUMN uploader.similar_matches.confirmed_times IS 'The number of times the match has been confirmed';


--
-- Name: uploader_alembic_version; Type: TABLE; Schema: uploader; Owner: postgres
--

CREATE TABLE uploader.uploader_alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE uploader.uploader_alembic_version OWNER TO postgres;

--
-- Name: uploader_settings; Type: TABLE; Schema: uploader; Owner: postgres
--

CREATE TABLE uploader.uploader_settings (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE uploader.uploader_settings OWNER TO postgres;

--
-- Name: dashboards; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".dashboards (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    sub_title character varying(255) NOT NULL,
    version character varying(5) NOT NULL,
    components json NOT NULL,
    user_id uuid NOT NULL,
    last_accessed timestamp without time zone NOT NULL,
    filters json NOT NULL,
    "position" integer
);


ALTER TABLE "user".dashboards OWNER TO postgres;

--
-- Name: databasechangelog; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".databasechangelog (
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


ALTER TABLE "user".databasechangelog OWNER TO postgres;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE "user".databasechangeloglock OWNER TO postgres;

--
-- Name: event_entity; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".event_entity (
    uuid uuid NOT NULL,
    user_id uuid NOT NULL,
    subject character varying(255) NOT NULL,
    start character varying(255) NOT NULL,
    "end" character varying(255) NOT NULL,
    location character varying(255) NOT NULL,
    attendees character varying(255) NOT NULL
);


ALTER TABLE "user".event_entity OWNER TO postgres;

--
-- Name: followings; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".followings (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    entity_type character varying(64) NOT NULL,
    entity_id uuid NOT NULL,
    follow_date timestamp without time zone DEFAULT now() NOT NULL,
    task_id uuid,
    source_due_at timestamp without time zone,
    source_reminder_at timestamp without time zone
);


ALTER TABLE "user".followings OWNER TO postgres;

--
-- Name: message_entity; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".message_entity (
    uuid uuid NOT NULL,
    user_id uuid NOT NULL,
    message character varying(255),
    created_at timestamp without time zone,
    sender_id uuid NOT NULL,
    read boolean NOT NULL,
    read_at timestamp without time zone
);


ALTER TABLE "user".message_entity OWNER TO postgres;

--
-- Name: setting_keys; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".setting_keys (
    id uuid NOT NULL,
    key character varying(128) NOT NULL,
    display_name character varying(256),
    group_name character varying(128),
    description character varying(1024),
    data_type character varying(24) NOT NULL,
    default_value character varying(2048),
    is_mutable boolean NOT NULL,
    entry_date timestamp without time zone
);


ALTER TABLE "user".setting_keys OWNER TO postgres;

--
-- Name: tasks; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".tasks (
    id uuid NOT NULL,
    title character varying(255) NOT NULL,
    body text,
    importance character varying(32) NOT NULL,
    status character varying(32) NOT NULL,
    is_reminder_on boolean,
    reminder_at timestamp without time zone,
    due_at timestamp without time zone,
    completed_at timestamp without time zone,
    "position" integer,
    private boolean,
    steps json,
    categories json,
    user_id uuid NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE "user".tasks OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".user_roles (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    is_default boolean DEFAULT true,
    keycloak_role_id uuid
);


ALTER TABLE "user".user_roles OWNER TO postgres;

--
-- Name: user_settings; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".user_settings (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    setting_key_id uuid NOT NULL,
    value character varying(4096),
    entry_date timestamp without time zone
);


ALTER TABLE "user".user_settings OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: user; Owner: postgres
--

CREATE TABLE "user".users (
    id uuid NOT NULL,
    username character varying(255) NOT NULL,
    first_name character varying(255) NOT NULL,
    last_name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    enabled boolean NOT NULL,
    role_id uuid NOT NULL,
    inside boolean,
    outside boolean,
    created_by uuid,
    entry_date timestamp without time zone DEFAULT now() NOT NULL,
    keycloak_id uuid NOT NULL,
    supervisor_id uuid
);


ALTER TABLE "user".users OWNER TO postgres;

--
-- Name: aisles; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.aisles (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    aisle_number integer,
    zone character varying(100),
    orientation_deg integer,
    start_latitude numeric(9,6),
    start_longitude numeric(9,6),
    end_latitude numeric(9,6),
    end_longitude numeric(9,6),
    description text,
    is_active boolean DEFAULT true NOT NULL,
    warehouse_id uuid NOT NULL,
    section_id uuid
);


ALTER TABLE warehouse.aisles OWNER TO postgres;

--
-- Name: bays; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.bays (
    id uuid NOT NULL,
    code character varying(50) NOT NULL,
    bay_number integer NOT NULL,
    description text,
    qr_code bytea,
    qr_content character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    shelf_id uuid NOT NULL
);


ALTER TABLE warehouse.bays OWNER TO postgres;

--
-- Name: bins; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.bins (
    id uuid NOT NULL,
    letter_code character varying(10) NOT NULL,
    width numeric(10,2),
    height numeric(10,2),
    depth numeric(10,2),
    max_weight numeric(10,2),
    description text,
    qr_code bytea,
    qr_content character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    row_id uuid NOT NULL
);


ALTER TABLE warehouse.bins OWNER TO postgres;

--
-- Name: databasechangelog; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.databasechangelog (
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


ALTER TABLE warehouse.databasechangelog OWNER TO postgres;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE warehouse.databasechangeloglock OWNER TO postgres;

--
-- Name: fiducial_markers; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.fiducial_markers (
    id uuid NOT NULL,
    identifier character varying(3) NOT NULL,
    marker_number integer,
    qr_code bytea,
    x_offset numeric(10,2),
    y_offset numeric(10,2),
    z_offset numeric(10,2),
    orientation_deg integer,
    is_active boolean DEFAULT true NOT NULL,
    description text,
    shelf_id uuid NOT NULL
);


ALTER TABLE warehouse.fiducial_markers OWNER TO postgres;

--
-- Name: fulfillments; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.fulfillments (
    id uuid NOT NULL,
    order_id uuid NOT NULL,
    product_id uuid NOT NULL,
    inventory_id uuid,
    qr_code character varying(255) NOT NULL,
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    quantity integer NOT NULL,
    picked_quantity integer DEFAULT 0 NOT NULL,
    packed_quantity integer DEFAULT 0 NOT NULL,
    shipped_quantity integer DEFAULT 0 NOT NULL,
    sku character varying(100),
    product_name character varying(500),
    tracking_number character varying(100),
    carrier character varying(100),
    notes character varying(1000),
    picked_at timestamp without time zone,
    packed_at timestamp without time zone,
    shipped_at timestamp without time zone,
    delivered_at timestamp without time zone,
    cancelled_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid,
    wave_id uuid,
    delivery_type character varying(50),
    warehouse_id uuid NOT NULL
);


ALTER TABLE warehouse.fulfillments OWNER TO postgres;

--
-- Name: inventory; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.inventory (
    id uuid NOT NULL,
    sku character varying(100) NOT NULL,
    product_name character varying(500) NOT NULL,
    unit_of_measure character varying(20),
    total_quantity integer DEFAULT 0 NOT NULL,
    available_quantity integer DEFAULT 0 NOT NULL,
    reserved_quantity integer DEFAULT 0 NOT NULL,
    picking_quantity integer DEFAULT 0 NOT NULL,
    picked_quantity integer DEFAULT 0 NOT NULL,
    quarantine_quantity integer DEFAULT 0 NOT NULL,
    damaged_quantity integer DEFAULT 0 NOT NULL,
    expired_quantity integer DEFAULT 0 NOT NULL,
    in_transit_quantity integer DEFAULT 0 NOT NULL,
    on_hold_quantity integer DEFAULT 0 NOT NULL,
    returned_quantity integer DEFAULT 0 NOT NULL,
    reorder_point integer,
    max_quantity integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    product_id uuid
);


ALTER TABLE warehouse.inventory OWNER TO postgres;

--
-- Name: inventory_items; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.inventory_items (
    id uuid NOT NULL,
    inventory_id uuid NOT NULL,
    sku character varying(100) NOT NULL,
    product_name character varying(500) NOT NULL,
    quantity integer DEFAULT 0 NOT NULL,
    unit_of_measure character varying(20),
    weight_per_unit numeric(10,3),
    total_weight numeric(10,3),
    barcode character varying(100),
    lot_number character varying(100),
    serial_number character varying(100),
    expiration_date timestamp without time zone,
    received_date timestamp without time zone,
    status character varying(50) DEFAULT 'AVAILABLE'::character varying NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    bin_id uuid NOT NULL,
    product_id uuid,
    supplier_id uuid
);


ALTER TABLE warehouse.inventory_items OWNER TO postgres;

--
-- Name: locations; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.locations (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address_line_1 character varying(255),
    address_line_2 character varying(255),
    city character varying(100),
    state character varying(100),
    postal_code character varying(20),
    country character varying(100),
    latitude numeric(9,6),
    longitude numeric(9,6),
    description text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE warehouse.locations OWNER TO postgres;

--
-- Name: rmas; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.rmas (
    id uuid NOT NULL,
    rma_number character varying(50) NOT NULL,
    fulfillment_id uuid NOT NULL,
    order_id uuid NOT NULL,
    product_id uuid NOT NULL,
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    quantity integer NOT NULL,
    received_quantity integer DEFAULT 0 NOT NULL,
    reason_code character varying(50),
    reason character varying(1000),
    refund_amount numeric(10,2),
    restocking_fee numeric(10,2),
    return_tracking_number character varying(100),
    inspection_notes character varying(2000),
    can_restock boolean,
    qr_code character varying(255),
    approved_at timestamp without time zone,
    received_at timestamp without time zone,
    completed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE warehouse.rmas OWNER TO postgres;

--
-- Name: rows; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.rows (
    id uuid NOT NULL,
    row_number integer NOT NULL,
    description text,
    qr_code bytea,
    qr_content character varying(500),
    is_active boolean DEFAULT true NOT NULL,
    bay_id uuid NOT NULL
);


ALTER TABLE warehouse.rows OWNER TO postgres;

--
-- Name: sections; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.sections (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    width numeric(10,2) NOT NULL,
    length numeric(10,2) NOT NULL,
    height numeric(10,2),
    x_offset numeric(10,2) NOT NULL,
    y_offset numeric(10,2) NOT NULL,
    orientation_deg integer,
    is_active boolean DEFAULT true NOT NULL,
    warehouse_id uuid NOT NULL
);


ALTER TABLE warehouse.sections OWNER TO postgres;

--
-- Name: shelves; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.shelves (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    height numeric(10,2),
    width numeric(10,2),
    length numeric(10,2),
    warehouse_id uuid NOT NULL,
    latitude numeric(9,6),
    longitude numeric(9,6),
    description text,
    is_active boolean DEFAULT true NOT NULL,
    aisle_id uuid,
    section_id uuid
);


ALTER TABLE warehouse.shelves OWNER TO postgres;

--
-- Name: shipments; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.shipments (
    id uuid NOT NULL,
    tracking_number character varying(100) NOT NULL,
    carrier character varying(100) NOT NULL,
    service_level character varying(100),
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    weight numeric(10,3),
    weight_unit character varying(10) DEFAULT 'LBS'::character varying,
    cost numeric(10,2),
    label_url character varying(500),
    fulfillment_id uuid,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    shipped_at timestamp without time zone,
    expected_delivery_at timestamp without time zone,
    delivered_at timestamp without time zone,
    delivery_address character varying(1000),
    notes character varying(1000),
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid
);


ALTER TABLE warehouse.shipments OWNER TO postgres;

--
-- Name: warehouse; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.warehouse (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address_line_1 character varying(255),
    address_line_2 character varying(255),
    city character varying(100),
    state character varying(100),
    postal_code character varying(20),
    country character varying(100),
    latitude numeric(9,6),
    longitude numeric(9,6),
    description text,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE warehouse.warehouse OWNER TO postgres;

--
-- Name: warehouse_info; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.warehouse_info (
    id uuid NOT NULL,
    service_name character varying(100) NOT NULL,
    version character varying(50) NOT NULL,
    initialized_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE warehouse.warehouse_info OWNER TO postgres;

--
-- Name: waves; Type: TABLE; Schema: warehouse; Owner: postgres
--

CREATE TABLE warehouse.waves (
    id uuid NOT NULL,
    wave_number character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'PENDING'::character varying NOT NULL,
    priority integer DEFAULT 0 NOT NULL,
    fulfillment_count integer DEFAULT 0 NOT NULL,
    total_items integer DEFAULT 0 NOT NULL,
    picked_items integer DEFAULT 0 NOT NULL,
    picker_id uuid,
    released_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    notes character varying(1000),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by uuid,
    updated_by uuid
);


ALTER TABLE warehouse.waves OWNER TO postgres;

--
-- Name: queries id; Type: DEFAULT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.queries ALTER COLUMN id SET DEFAULT nextval('chats.queries_id_seq'::regclass);


--
-- Name: types id; Type: DEFAULT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.types ALTER COLUMN id SET DEFAULT nextval('chats.types_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cluster_contexts cluster_contexts_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.cluster_contexts
    ADD CONSTRAINT cluster_contexts_pkey PRIMARY KEY (id);


--
-- Name: document_clusters document_clusters_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.document_clusters
    ADD CONSTRAINT document_clusters_pkey PRIMARY KEY (id);


--
-- Name: entity_match_candidates entity_match_candidates_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.entity_match_candidates
    ADD CONSTRAINT entity_match_candidates_pkey PRIMARY KEY (id);


--
-- Name: extracted_data_versions extracted_data_versions_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.extracted_data_versions
    ADD CONSTRAINT extracted_data_versions_pkey PRIMARY KEY (id);


--
-- Name: pending_document_correction_changes pending_document_correction_changes_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_correction_changes
    ADD CONSTRAINT pending_document_correction_changes_pkey PRIMARY KEY (id);


--
-- Name: pending_document_entities pending_document_entities_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_entities
    ADD CONSTRAINT pending_document_entities_pkey PRIMARY KEY (id);


--
-- Name: pending_document_pages pending_document_pages_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_pages
    ADD CONSTRAINT pending_document_pages_pkey PRIMARY KEY (id);


--
-- Name: pending_documents pending_documents_file_upload_process_id_key; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_documents
    ADD CONSTRAINT pending_documents_file_upload_process_id_key UNIQUE (file_upload_process_id);


--
-- Name: pending_documents pending_documents_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_documents
    ADD CONSTRAINT pending_documents_pkey PRIMARY KEY (id);


--
-- Name: pending_entities pending_entities_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_entities
    ADD CONSTRAINT pending_entities_pkey PRIMARY KEY (id);


--
-- Name: chat_message_feedback pk_ai_chat_message_feedback; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.chat_message_feedback
    ADD CONSTRAINT pk_ai_chat_message_feedback PRIMARY KEY (id);


--
-- Name: chat_messages pk_ai_chat_messages; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.chat_messages
    ADD CONSTRAINT pk_ai_chat_messages PRIMARY KEY (id);


--
-- Name: chats pk_ai_chats; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.chats
    ADD CONSTRAINT pk_ai_chats PRIMARY KEY (id);


--
-- Name: email_attachments pk_ai_email_attachments; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.email_attachments
    ADD CONSTRAINT pk_ai_email_attachments PRIMARY KEY (id);


--
-- Name: emails pk_ai_emails; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.emails
    ADD CONSTRAINT pk_ai_emails PRIMARY KEY (id);


--
-- Name: emails uq_ai_emails_external_id; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.emails
    ADD CONSTRAINT uq_ai_emails_external_id UNIQUE (external_id);


--
-- Name: entity_match_candidates uq_match_candidate_entity; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.entity_match_candidates
    ADD CONSTRAINT uq_match_candidate_entity UNIQUE (pending_entity_id, existing_entity_id);


--
-- Name: entity_match_candidates uq_match_candidate_rank; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.entity_match_candidates
    ADD CONSTRAINT uq_match_candidate_rank UNIQUE (pending_entity_id, rank);


--
-- Name: workflow_executions workflow_executions_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.workflow_executions
    ADD CONSTRAINT workflow_executions_pkey PRIMARY KEY (id);


--
-- Name: workflow_files workflow_files_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.workflow_files
    ADD CONSTRAINT workflow_files_pkey PRIMARY KEY (id);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chats_alembic_version chats_alembic_version_pkc; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.chats_alembic_version
    ADD CONSTRAINT chats_alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: queries queries_name_key; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.queries
    ADD CONSTRAINT queries_name_key UNIQUE (name);


--
-- Name: queries queries_pkey; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.queries
    ADD CONSTRAINT queries_pkey PRIMARY KEY (id);


--
-- Name: types types_pkey; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.types
    ADD CONSTRAINT types_pkey PRIMARY KEY (id);


--
-- Name: types unique_type_name; Type: CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.types
    ADD CONSTRAINT unique_type_name UNIQUE (name, type);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: check_balances pk_check_balances; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_balances
    ADD CONSTRAINT pk_check_balances PRIMARY KEY (id);


--
-- Name: check_balances_aud pk_check_balances_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_balances_aud
    ADD CONSTRAINT pk_check_balances_aud PRIMARY KEY (rev, id);


--
-- Name: check_details pk_check_details; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details
    ADD CONSTRAINT pk_check_details PRIMARY KEY (id);


--
-- Name: check_details_aud pk_check_details_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details_aud
    ADD CONSTRAINT pk_check_details_aud PRIMARY KEY (rev, id);


--
-- Name: checks pk_checks; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks
    ADD CONSTRAINT pk_checks PRIMARY KEY (id);


--
-- Name: checks_aud pk_checks_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks_aud
    ADD CONSTRAINT pk_checks_aud PRIMARY KEY (rev, id);


--
-- Name: credit_balances pk_credit_balances; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_balances
    ADD CONSTRAINT pk_credit_balances PRIMARY KEY (id);


--
-- Name: credit_balances_aud pk_credit_balances_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_balances_aud
    ADD CONSTRAINT pk_credit_balances_aud PRIMARY KEY (rev, id);


--
-- Name: credit_details pk_credit_details; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_details
    ADD CONSTRAINT pk_credit_details PRIMARY KEY (id);


--
-- Name: credit_details_aud pk_credit_details_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_details_aud
    ADD CONSTRAINT pk_credit_details_aud PRIMARY KEY (rev, id);


--
-- Name: credit_reasons pk_credit_reasons; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_reasons
    ADD CONSTRAINT pk_credit_reasons PRIMARY KEY (id);


--
-- Name: credit_reasons_aud pk_credit_reasons_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_reasons_aud
    ADD CONSTRAINT pk_credit_reasons_aud PRIMARY KEY (rev, id);


--
-- Name: credits pk_credits; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits
    ADD CONSTRAINT pk_credits PRIMARY KEY (id);


--
-- Name: credits_aud pk_credits_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits_aud
    ADD CONSTRAINT pk_credits_aud PRIMARY KEY (rev, id);


--
-- Name: deduction_sales_reps pk_deduction_sales_reps; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.deduction_sales_reps
    ADD CONSTRAINT pk_deduction_sales_reps PRIMARY KEY (id);


--
-- Name: deduction_sales_reps_aud pk_deduction_sales_reps_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.deduction_sales_reps_aud
    ADD CONSTRAINT pk_deduction_sales_reps_aud PRIMARY KEY (rev, id);


--
-- Name: expense_categories pk_expense_categories; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_categories
    ADD CONSTRAINT pk_expense_categories PRIMARY KEY (id);


--
-- Name: expense_categories_aud pk_expense_categories_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_categories_aud
    ADD CONSTRAINT pk_expense_categories_aud PRIMARY KEY (rev, id);


--
-- Name: expense_split_rates pk_expense_split_rates; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_split_rates
    ADD CONSTRAINT pk_expense_split_rates PRIMARY KEY (id);


--
-- Name: expense_split_rates_aud pk_expense_split_rates_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_split_rates_aud
    ADD CONSTRAINT pk_expense_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: expenses pk_expenses; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses
    ADD CONSTRAINT pk_expenses PRIMARY KEY (id);


--
-- Name: expenses_aud pk_expenses_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses_aud
    ADD CONSTRAINT pk_expenses_aud PRIMARY KEY (rev, id);


--
-- Name: invoice_balances pk_invoice_balances; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_balances
    ADD CONSTRAINT pk_invoice_balances PRIMARY KEY (id);


--
-- Name: invoice_balances_aud pk_invoice_balances_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_balances_aud
    ADD CONSTRAINT pk_invoice_balances_aud PRIMARY KEY (rev, id);


--
-- Name: invoice_details pk_invoice_details; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_details
    ADD CONSTRAINT pk_invoice_details PRIMARY KEY (id);


--
-- Name: invoice_details_aud pk_invoice_details_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_details_aud
    ADD CONSTRAINT pk_invoice_details_aud PRIMARY KEY (rev, id);


--
-- Name: invoice_split_rates pk_invoice_split_rates; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_split_rates
    ADD CONSTRAINT pk_invoice_split_rates PRIMARY KEY (id);


--
-- Name: invoice_split_rates_aud pk_invoice_split_rates_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_split_rates_aud
    ADD CONSTRAINT pk_invoice_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: invoices pk_invoices; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT pk_invoices PRIMARY KEY (id);


--
-- Name: invoices_aud pk_invoices_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices_aud
    ADD CONSTRAINT pk_invoices_aud PRIMARY KEY (rev, id);


--
-- Name: order_acknowledgements pk_order_acknowledgements; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_acknowledgements
    ADD CONSTRAINT pk_order_acknowledgements PRIMARY KEY (id);


--
-- Name: order_acknowledgements_aud pk_order_acknowledgements_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_acknowledgements_aud
    ADD CONSTRAINT pk_order_acknowledgements_aud PRIMARY KEY (rev, id);


--
-- Name: order_balances pk_order_balances; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_balances
    ADD CONSTRAINT pk_order_balances PRIMARY KEY (id);


--
-- Name: order_balances_aud pk_order_balances_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_balances_aud
    ADD CONSTRAINT pk_order_balances_aud PRIMARY KEY (rev, id);


--
-- Name: order_details pk_order_details; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_details
    ADD CONSTRAINT pk_order_details PRIMARY KEY (id);


--
-- Name: order_details_aud pk_order_details_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_details_aud
    ADD CONSTRAINT pk_order_details_aud PRIMARY KEY (rev, id);


--
-- Name: order_inside_reps pk_order_inside_reps; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_inside_reps
    ADD CONSTRAINT pk_order_inside_reps PRIMARY KEY (id);


--
-- Name: order_inside_reps_aud pk_order_inside_reps_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_inside_reps_aud
    ADD CONSTRAINT pk_order_inside_reps_aud PRIMARY KEY (rev, id);


--
-- Name: order_split_rates pk_order_split_rates; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_split_rates
    ADD CONSTRAINT pk_order_split_rates PRIMARY KEY (id);


--
-- Name: order_split_rates_aud pk_order_split_rates_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_split_rates_aud
    ADD CONSTRAINT pk_order_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: orders pk_orders; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT pk_orders PRIMARY KEY (id);


--
-- Name: orders_aud pk_orders_aud; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders_aud
    ADD CONSTRAINT pk_orders_aud PRIMARY KEY (rev, id);


--
-- Name: revinfo pk_revinfo; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.revinfo
    ADD CONSTRAINT pk_revinfo PRIMARY KEY (rev);


--
-- Name: checks uc_checks_balance_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks
    ADD CONSTRAINT uc_checks_balance_id UNIQUE (balance_id);


--
-- Name: checks uc_checks_check_number_factory_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks
    ADD CONSTRAINT uc_checks_check_number_factory_id UNIQUE (check_number, factory_id);


--
-- Name: credit_reasons uc_credit_reasons_title; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_reasons
    ADD CONSTRAINT uc_credit_reasons_title UNIQUE (title);


--
-- Name: credits uc_credits_balance_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits
    ADD CONSTRAINT uc_credits_balance_id UNIQUE (balance_id);


--
-- Name: expense_categories uc_expense_categories_title; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_categories
    ADD CONSTRAINT uc_expense_categories_title UNIQUE (title);


--
-- Name: expenses uc_expenses_expense_number; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses
    ADD CONSTRAINT uc_expenses_expense_number UNIQUE (expense_number);


--
-- Name: invoices uc_invoices_balance_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT uc_invoices_balance_id UNIQUE (balance_id);


--
-- Name: invoices uc_invoices_invoice_number_factory_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT uc_invoices_invoice_number_factory_id UNIQUE (invoice_number, factory_id);


--
-- Name: orders uc_orders_balance_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT uc_orders_balance_id UNIQUE (balance_id);


--
-- Name: orders uc_orders_order_number_customer_id; Type: CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT uc_orders_order_number_customer_id UNIQUE (order_number, sold_to_customer_id);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (code);


--
-- Name: customer_territory_boundaries customer_territory_boundaries_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_boundaries
    ADD CONSTRAINT customer_territory_boundaries_pkey PRIMARY KEY (id);


--
-- Name: customer_territory_boundaries customer_territory_boundaries_territory_id_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_boundaries
    ADD CONSTRAINT customer_territory_boundaries_territory_id_key UNIQUE (territory_id);


--
-- Name: customer_territory_customers customer_territory_customers_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_customers
    ADD CONSTRAINT customer_territory_customers_pkey PRIMARY KEY (id);


--
-- Name: customer_territory_regions customer_territory_regions_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_regions
    ADD CONSTRAINT customer_territory_regions_pkey PRIMARY KEY (id);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: document_templates document_templates_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.document_templates
    ADD CONSTRAINT document_templates_pkey PRIMARY KEY (id);


--
-- Name: addresses pk_addresses; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.addresses
    ADD CONSTRAINT pk_addresses PRIMARY KEY (id);


--
-- Name: addresses_aud pk_addresses_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.addresses_aud
    ADD CONSTRAINT pk_addresses_aud PRIMARY KEY (rev, id);


--
-- Name: auto_increment_id pk_auto_increment_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.auto_increment_id
    ADD CONSTRAINT pk_auto_increment_id PRIMARY KEY (id);


--
-- Name: contacts pk_contacts; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.contacts
    ADD CONSTRAINT pk_contacts PRIMARY KEY (id);


--
-- Name: contacts_aud pk_contacts_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.contacts_aud
    ADD CONSTRAINT pk_contacts_aud PRIMARY KEY (rev, id);


--
-- Name: countries_aud pk_countries_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.countries_aud
    ADD CONSTRAINT pk_countries_aud PRIMARY KEY (rev, code);


--
-- Name: customer_branches pk_customer_branches; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_branches
    ADD CONSTRAINT pk_customer_branches PRIMARY KEY (id);


--
-- Name: customer_branches_aud pk_customer_branches_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_branches_aud
    ADD CONSTRAINT pk_customer_branches_aud PRIMARY KEY (rev, id);


--
-- Name: customer_levels pk_customer_levels; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels
    ADD CONSTRAINT pk_customer_levels PRIMARY KEY (id);


--
-- Name: customer_levels_aud pk_customer_levels_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels_aud
    ADD CONSTRAINT pk_customer_levels_aud PRIMARY KEY (rev, id);


--
-- Name: customer_split_rates pk_customer_split_rates; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_split_rates
    ADD CONSTRAINT pk_customer_split_rates PRIMARY KEY (id);


--
-- Name: customer_split_rates_aud pk_customer_split_rates_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_split_rates_aud
    ADD CONSTRAINT pk_customer_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: customer_territories pk_customer_territories; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territories
    ADD CONSTRAINT pk_customer_territories PRIMARY KEY (id);


--
-- Name: customer_territories_aud pk_customer_territories_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territories_aud
    ADD CONSTRAINT pk_customer_territories_aud PRIMARY KEY (rev, id);


--
-- Name: customer_territory_boundaries_aud pk_customer_territory_boundaries_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_boundaries_aud
    ADD CONSTRAINT pk_customer_territory_boundaries_aud PRIMARY KEY (rev, id);


--
-- Name: customer_territory_customers_aud pk_customer_territory_customers_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_customers_aud
    ADD CONSTRAINT pk_customer_territory_customers_aud PRIMARY KEY (rev, id);


--
-- Name: customer_territory_regions_aud pk_customer_territory_regions_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_regions_aud
    ADD CONSTRAINT pk_customer_territory_regions_aud PRIMARY KEY (rev, id);


--
-- Name: customers pk_customers; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers
    ADD CONSTRAINT pk_customers PRIMARY KEY (id);


--
-- Name: customers_aud pk_customers_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers_aud
    ADD CONSTRAINT pk_customers_aud PRIMARY KEY (rev, id);


--
-- Name: factories pk_factories; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factories
    ADD CONSTRAINT pk_factories PRIMARY KEY (id);


--
-- Name: factories_aud pk_factories_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factories_aud
    ADD CONSTRAINT pk_factories_aud PRIMARY KEY (rev, id);


--
-- Name: factory_commission_bands pk_factory_commission_bands; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_commission_bands
    ADD CONSTRAINT pk_factory_commission_bands PRIMARY KEY (id);


--
-- Name: factory_commission_bands_aud pk_factory_commission_bands_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_commission_bands_aud
    ADD CONSTRAINT pk_factory_commission_bands_aud PRIMARY KEY (rev, id);


--
-- Name: factory_customer_ids pk_factory_customer_ids; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids
    ADD CONSTRAINT pk_factory_customer_ids PRIMARY KEY (id);


--
-- Name: factory_customer_ids_aud pk_factory_customer_ids_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids_aud
    ADD CONSTRAINT pk_factory_customer_ids_aud PRIMARY KEY (rev, id);


--
-- Name: factory_levels pk_factory_levels; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_levels
    ADD CONSTRAINT pk_factory_levels PRIMARY KEY (id);


--
-- Name: factory_levels_aud pk_factory_levels_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_levels_aud
    ADD CONSTRAINT pk_factory_levels_aud PRIMARY KEY (rev, id);


--
-- Name: note_note_tags_aud pk_note_note_tags_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_note_tags_aud
    ADD CONSTRAINT pk_note_note_tags_aud PRIMARY KEY (note_id, note_tag_id, rev);


--
-- Name: note_tags pk_note_tags; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags
    ADD CONSTRAINT pk_note_tags PRIMARY KEY (id);


--
-- Name: note_tags_aud pk_note_tags_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags_aud
    ADD CONSTRAINT pk_note_tags_aud PRIMARY KEY (rev, id);


--
-- Name: note_tags_notes_aud pk_note_tags_notes_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags_notes_aud
    ADD CONSTRAINT pk_note_tags_notes_aud PRIMARY KEY (note_tag_id, notes_id, rev);


--
-- Name: note_thread_subscriptions pk_note_thread_subscriptions; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_thread_subscriptions
    ADD CONSTRAINT pk_note_thread_subscriptions PRIMARY KEY (id);


--
-- Name: note_thread_subscriptions_aud pk_note_thread_subscriptions_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_thread_subscriptions_aud
    ADD CONSTRAINT pk_note_thread_subscriptions_aud PRIMARY KEY (rev, id);


--
-- Name: note_threads pk_note_threads; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_threads
    ADD CONSTRAINT pk_note_threads PRIMARY KEY (id);


--
-- Name: note_threads_aud pk_note_threads_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_threads_aud
    ADD CONSTRAINT pk_note_threads_aud PRIMARY KEY (rev, id);


--
-- Name: notes pk_notes; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notes
    ADD CONSTRAINT pk_notes PRIMARY KEY (id);


--
-- Name: notes_aud pk_notes_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notes_aud
    ADD CONSTRAINT pk_notes_aud PRIMARY KEY (rev, id);


--
-- Name: participants pk_participants; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.participants
    ADD CONSTRAINT pk_participants PRIMARY KEY (id);


--
-- Name: participants_aud pk_participants_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.participants_aud
    ADD CONSTRAINT pk_participants_aud PRIMARY KEY (rev, id);


--
-- Name: product_categories pk_product_categories; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories
    ADD CONSTRAINT pk_product_categories PRIMARY KEY (id);


--
-- Name: product_categories_aud pk_product_categories_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories_aud
    ADD CONSTRAINT pk_product_categories_aud PRIMARY KEY (rev, id);


--
-- Name: product_commission_bands pk_product_commission_bands; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_commission_bands
    ADD CONSTRAINT pk_product_commission_bands PRIMARY KEY (id);


--
-- Name: product_commission_bands_aud pk_product_commission_bands_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_commission_bands_aud
    ADD CONSTRAINT pk_product_commission_bands_aud PRIMARY KEY (rev, id);


--
-- Name: product_cpns pk_product_cpns; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns
    ADD CONSTRAINT pk_product_cpns PRIMARY KEY (id);


--
-- Name: product_cpns_aud pk_product_cpns_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns_aud
    ADD CONSTRAINT pk_product_cpns_aud PRIMARY KEY (rev, id);


--
-- Name: product_measurements pk_product_measurements; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_measurements
    ADD CONSTRAINT pk_product_measurements PRIMARY KEY (id);


--
-- Name: product_measurements_aud pk_product_measurements_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_measurements_aud
    ADD CONSTRAINT pk_product_measurements_aud PRIMARY KEY (rev, id);


--
-- Name: product_quantity_pricing pk_product_quantity_pricing; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_quantity_pricing
    ADD CONSTRAINT pk_product_quantity_pricing PRIMARY KEY (id);


--
-- Name: product_quantity_pricing_aud pk_product_quantity_pricing_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_quantity_pricing_aud
    ADD CONSTRAINT pk_product_quantity_pricing_aud PRIMARY KEY (rev, id);


--
-- Name: product_uoms pk_product_uoms; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_uoms
    ADD CONSTRAINT pk_product_uoms PRIMARY KEY (id);


--
-- Name: product_uoms_aud pk_product_uoms_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_uoms_aud
    ADD CONSTRAINT pk_product_uoms_aud PRIMARY KEY (rev, id);


--
-- Name: products pk_products; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products
    ADD CONSTRAINT pk_products PRIMARY KEY (id);


--
-- Name: products_aud pk_products_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products_aud
    ADD CONSTRAINT pk_products_aud PRIMARY KEY (rev, id);


--
-- Name: revinfo pk_revinfo; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.revinfo
    ADD CONSTRAINT pk_revinfo PRIMARY KEY (rev);


--
-- Name: sales_rep_selection_split_rates pk_sales_rep_selection_split_rates; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selection_split_rates
    ADD CONSTRAINT pk_sales_rep_selection_split_rates PRIMARY KEY (id);


--
-- Name: sales_rep_selection_split_rates_aud pk_sales_rep_selection_split_rates_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selection_split_rates_aud
    ADD CONSTRAINT pk_sales_rep_selection_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: sales_rep_selections pk_sales_rep_selections; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections
    ADD CONSTRAINT pk_sales_rep_selections PRIMARY KEY (id);


--
-- Name: sales_rep_selections_aud pk_sales_rep_selections_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections_aud
    ADD CONSTRAINT pk_sales_rep_selections_aud PRIMARY KEY (rev, id);


--
-- Name: site_options pk_site_options; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.site_options
    ADD CONSTRAINT pk_site_options PRIMARY KEY (id);


--
-- Name: site_options_aud pk_site_options_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.site_options_aud
    ADD CONSTRAINT pk_site_options_aud PRIMARY KEY (rev, id);


--
-- Name: stepped_commission_tiers pk_stepped_commission_tiers; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.stepped_commission_tiers
    ADD CONSTRAINT pk_stepped_commission_tiers PRIMARY KEY (id);


--
-- Name: stepped_commission_tiers_aud pk_stepped_commission_tiers_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.stepped_commission_tiers_aud
    ADD CONSTRAINT pk_stepped_commission_tiers_aud PRIMARY KEY (rev, id);


--
-- Name: subdivisions_aud pk_subdivisions_aud; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions_aud
    ADD CONSTRAINT pk_subdivisions_aud PRIMARY KEY (rev, iso_code);


--
-- Name: subdivisions subdivisions_pkey; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions
    ADD CONSTRAINT subdivisions_pkey PRIMARY KEY (iso_code);


--
-- Name: customer_branches uc_customer_branches_title; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_branches
    ADD CONSTRAINT uc_customer_branches_title UNIQUE (title);


--
-- Name: customer_territories uc_customer_territories_title; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territories
    ADD CONSTRAINT uc_customer_territories_title UNIQUE (title);


--
-- Name: customers uc_customers_company_name; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers
    ADD CONSTRAINT uc_customers_company_name UNIQUE (company_name);


--
-- Name: factories uc_factories_title; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factories
    ADD CONSTRAINT uc_factories_title UNIQUE (title);


--
-- Name: note_tags uc_note_tags_tag; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags
    ADD CONSTRAINT uc_note_tags_tag UNIQUE (tag);


--
-- Name: product_categories uc_product_categories_factory_id_title; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories
    ADD CONSTRAINT uc_product_categories_factory_id_title UNIQUE (factory_id, title);


--
-- Name: product_categories uc_product_categories_title_factory_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories
    ADD CONSTRAINT uc_product_categories_title_factory_id UNIQUE (title, factory_id);


--
-- Name: product_cpns uc_product_cpns_product_id_customer_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns
    ADD CONSTRAINT uc_product_cpns_product_id_customer_id UNIQUE (product_id, customer_id);


--
-- Name: product_uoms uc_product_uoms_title; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_uoms
    ADD CONSTRAINT uc_product_uoms_title UNIQUE (title);


--
-- Name: products uc_products_factory_part_number_factory_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products
    ADD CONSTRAINT uc_products_factory_part_number_factory_id UNIQUE (factory_part_number, factory_id);


--
-- Name: sales_rep_selections uc_sales_rep_selections_customer_id_factory_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections
    ADD CONSTRAINT uc_sales_rep_selections_customer_id_factory_id UNIQUE (customer_id, factory_id);


--
-- Name: site_options uc_site_options_key; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.site_options
    ADD CONSTRAINT uc_site_options_key UNIQUE (key);


--
-- Name: countries uk_countries_alpha3; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.countries
    ADD CONSTRAINT uk_countries_alpha3 UNIQUE (alpha3);


--
-- Name: customer_territory_customers uk_ct_customer_unique; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_customers
    ADD CONSTRAINT uk_ct_customer_unique UNIQUE (territory_id, customer_id);


--
-- Name: customer_territory_regions uk_ct_region_unique; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_regions
    ADD CONSTRAINT uk_ct_region_unique UNIQUE (territory_id, region_type, region_code);


--
-- Name: customer_levels uk_customer_level_customer_factory; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels
    ADD CONSTRAINT uk_customer_level_customer_factory UNIQUE (customer_id, factory_id);


--
-- Name: factory_customer_ids uk_factory_customer_id_factory_id; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids
    ADD CONSTRAINT uk_factory_customer_id_factory_id UNIQUE (factory_customer_id, factory_id);


--
-- Name: subdivisions uk_subdiv_country_code; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions
    ADD CONSTRAINT uk_subdiv_country_code UNIQUE (country_code, code);


--
-- Name: note_thread_subscriptions uk_subscription_thread_user; Type: CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_thread_subscriptions
    ADD CONSTRAINT uk_subscription_thread_user UNIQUE (thread_id, user_id);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_job_name_key; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.jobs
    ADD CONSTRAINT jobs_job_name_key UNIQUE (job_name);


--
-- Name: jobs pk_jobs; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.jobs
    ADD CONSTRAINT pk_jobs PRIMARY KEY (id);


--
-- Name: jobs_aud pk_jobs_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.jobs_aud
    ADD CONSTRAINT pk_jobs_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunities pk_pre_opportunities; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities
    ADD CONSTRAINT pk_pre_opportunities PRIMARY KEY (id);


--
-- Name: pre_opportunities_aud pk_pre_opportunities_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities_aud
    ADD CONSTRAINT pk_pre_opportunities_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunity_balances pk_pre_opportunity_balances; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_balances
    ADD CONSTRAINT pk_pre_opportunity_balances PRIMARY KEY (id);


--
-- Name: pre_opportunity_balances_aud pk_pre_opportunity_balances_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_balances_aud
    ADD CONSTRAINT pk_pre_opportunity_balances_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunity_details pk_pre_opportunity_details; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details
    ADD CONSTRAINT pk_pre_opportunity_details PRIMARY KEY (id);


--
-- Name: pre_opportunity_details_aud pk_pre_opportunity_details_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details_aud
    ADD CONSTRAINT pk_pre_opportunity_details_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunity_inside_reps pk_pre_opportunity_inside_reps; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_inside_reps
    ADD CONSTRAINT pk_pre_opportunity_inside_reps PRIMARY KEY (id);


--
-- Name: pre_opportunity_inside_reps_aud pk_pre_opportunity_inside_reps_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_inside_reps_aud
    ADD CONSTRAINT pk_pre_opportunity_inside_reps_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunity_lost_reasons pk_pre_opportunity_lost_reasons; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_lost_reasons
    ADD CONSTRAINT pk_pre_opportunity_lost_reasons PRIMARY KEY (id);


--
-- Name: pre_opportunity_lost_reasons_aud pk_pre_opportunity_lost_reasons_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_lost_reasons_aud
    ADD CONSTRAINT pk_pre_opportunity_lost_reasons_aud PRIMARY KEY (rev, id);


--
-- Name: pre_opportunity_split_rates pk_pre_opportunity_split_rates; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_split_rates
    ADD CONSTRAINT pk_pre_opportunity_split_rates PRIMARY KEY (id);


--
-- Name: pre_opportunity_split_rates_aud pk_pre_opportunity_split_rates_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_split_rates_aud
    ADD CONSTRAINT pk_pre_opportunity_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: quote_balances pk_quote_balances; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_balances
    ADD CONSTRAINT pk_quote_balances PRIMARY KEY (id);


--
-- Name: quote_balances_aud pk_quote_balances_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_balances_aud
    ADD CONSTRAINT pk_quote_balances_aud PRIMARY KEY (rev, id);


--
-- Name: quote_details pk_quote_details; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details
    ADD CONSTRAINT pk_quote_details PRIMARY KEY (id);


--
-- Name: quote_details_aud pk_quote_details_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details_aud
    ADD CONSTRAINT pk_quote_details_aud PRIMARY KEY (rev, id);


--
-- Name: quote_inside_reps pk_quote_inside_reps; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_inside_reps
    ADD CONSTRAINT pk_quote_inside_reps PRIMARY KEY (id);


--
-- Name: quote_inside_reps_aud pk_quote_inside_reps_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_inside_reps_aud
    ADD CONSTRAINT pk_quote_inside_reps_aud PRIMARY KEY (rev, id);


--
-- Name: quote_lost_reasons pk_quote_lost_reasons; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_lost_reasons
    ADD CONSTRAINT pk_quote_lost_reasons PRIMARY KEY (id);


--
-- Name: quote_lost_reasons_aud pk_quote_lost_reasons_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_lost_reasons_aud
    ADD CONSTRAINT pk_quote_lost_reasons_aud PRIMARY KEY (rev, id);


--
-- Name: quote_split_rates pk_quote_split_rates; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_split_rates
    ADD CONSTRAINT pk_quote_split_rates PRIMARY KEY (id);


--
-- Name: quote_split_rates_aud pk_quote_split_rates_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_split_rates_aud
    ADD CONSTRAINT pk_quote_split_rates_aud PRIMARY KEY (rev, id);


--
-- Name: quotes pk_quotes; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes
    ADD CONSTRAINT pk_quotes PRIMARY KEY (id);


--
-- Name: quotes_aud pk_quotes_aud; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes_aud
    ADD CONSTRAINT pk_quotes_aud PRIMARY KEY (rev, id);


--
-- Name: revinfo pk_revinfo; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.revinfo
    ADD CONSTRAINT pk_revinfo PRIMARY KEY (rev);


--
-- Name: jobs uc_jobs_job_name; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.jobs
    ADD CONSTRAINT uc_jobs_job_name UNIQUE (job_name);


--
-- Name: pre_opportunities uc_pre_opportunities_balance_id; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities
    ADD CONSTRAINT uc_pre_opportunities_balance_id UNIQUE (balance_id);


--
-- Name: pre_opportunities uc_pre_opportunities_entity_number_sold_to_customer_id; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities
    ADD CONSTRAINT uc_pre_opportunities_entity_number_sold_to_customer_id UNIQUE (entity_number, sold_to_customer_id);


--
-- Name: pre_opportunity_lost_reasons uc_pre_opportunity_lost_reasons_title; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_lost_reasons
    ADD CONSTRAINT uc_pre_opportunity_lost_reasons_title UNIQUE (title);


--
-- Name: quote_lost_reasons uc_quote_lost_reasons_title; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_lost_reasons
    ADD CONSTRAINT uc_quote_lost_reasons_title UNIQUE (title);


--
-- Name: quotes uc_quotes_balance_id; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes
    ADD CONSTRAINT uc_quotes_balance_id UNIQUE (balance_id);


--
-- Name: quotes uc_quotes_quote_number_sold_to_customer_id; Type: CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes
    ADD CONSTRAINT uc_quotes_quote_number_sold_to_customer_id UNIQUE (quote_number, sold_to_customer_id);


--
-- Name: extension_icons extension_icons_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.extension_icons
    ADD CONSTRAINT extension_icons_pkey PRIMARY KEY (extension);


--
-- Name: file_entity_details file_entity_details_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_entity_details
    ADD CONSTRAINT file_entity_details_pkey PRIMARY KEY (id);


--
-- Name: file_meta file_meta_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_meta
    ADD CONSTRAINT file_meta_pkey PRIMARY KEY (id);


--
-- Name: file_service_alembic_version file_service_alembic_version_pkc; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_service_alembic_version
    ADD CONSTRAINT file_service_alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: file_summary file_summary_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_summary
    ADD CONSTRAINT file_summary_pkey PRIMARY KEY (id);


--
-- Name: file_upload_details file_upload_details_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_details
    ADD CONSTRAINT file_upload_details_pkey PRIMARY KEY (id);


--
-- Name: file_upload_process_dtos file_upload_process_dtos_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process_dtos
    ADD CONSTRAINT file_upload_process_dtos_pkey PRIMARY KEY (id);


--
-- Name: file_upload_process file_upload_process_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process
    ADD CONSTRAINT file_upload_process_pkey PRIMARY KEY (id);


--
-- Name: file_upload_process_stats file_upload_process_stats_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process_stats
    ADD CONSTRAINT file_upload_process_stats_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: flowbot_file flowbot_file_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.flowbot_file
    ADD CONSTRAINT flowbot_file_pkey PRIMARY KEY (id);


--
-- Name: folders folders_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.folders
    ADD CONSTRAINT folders_pkey PRIMARY KEY (id);


--
-- Name: ocr_meta ocr_meta_file_id_key; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.ocr_meta
    ADD CONSTRAINT ocr_meta_file_id_key UNIQUE (file_id);


--
-- Name: ocr_meta ocr_meta_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.ocr_meta
    ADD CONSTRAINT ocr_meta_pkey PRIMARY KEY (id);


--
-- Name: ocr_pages ocr_pages_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.ocr_pages
    ADD CONSTRAINT ocr_pages_pkey PRIMARY KEY (id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: vectorization vectorization_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.vectorization
    ADD CONSTRAINT vectorization_pkey PRIMARY KEY (id);


--
-- Name: vectorization_status vectorization_status_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.vectorization_status
    ADD CONSTRAINT vectorization_status_pkey PRIMARY KEY (id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (id);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: campaign_criteria campaign_criteria_campaign_id_key; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT campaign_criteria_campaign_id_key UNIQUE (campaign_id);


--
-- Name: campaign_criteria campaign_criteria_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT campaign_criteria_pkey PRIMARY KEY (id);


--
-- Name: campaign_recipients campaign_recipients_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT campaign_recipients_pkey PRIMARY KEY (id);


--
-- Name: campaign_send_logs campaign_send_logs_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT campaign_send_logs_pkey PRIMARY KEY (id);


--
-- Name: campaigns campaigns_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaigns
    ADD CONSTRAINT campaigns_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: gmail_user_tokens gmail_user_tokens_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT gmail_user_tokens_pkey PRIMARY KEY (id);


--
-- Name: job_statuses job_statuses_name_key; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.job_statuses
    ADD CONSTRAINT job_statuses_name_key UNIQUE (name);


--
-- Name: job_statuses job_statuses_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.job_statuses
    ADD CONSTRAINT job_statuses_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_job_name_key; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_job_name_key UNIQUE (job_name);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: link_relations link_relations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.link_relations
    ADD CONSTRAINT link_relations_pkey PRIMARY KEY (id);


--
-- Name: manufacturer_order manufacturer_order_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.manufacturer_order
    ADD CONSTRAINT manufacturer_order_pkey PRIMARY KEY (id);


--
-- Name: note_conversations note_conversations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.note_conversations
    ADD CONSTRAINT note_conversations_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: o365_user_tokens o365_user_tokens_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT o365_user_tokens_pkey PRIMARY KEY (id);


--
-- Name: pre_opportunities pre_opportunities_entity_number_key; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_entity_number_key UNIQUE (entity_number);


--
-- Name: pre_opportunities pre_opportunities_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT pre_opportunities_pkey PRIMARY KEY (id);


--
-- Name: pre_opportunity_balances pre_opportunity_balances_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunity_balances
    ADD CONSTRAINT pre_opportunity_balances_pkey PRIMARY KEY (id);


--
-- Name: pre_opportunity_details pre_opportunity_details_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT pre_opportunity_details_pkey PRIMARY KEY (id);


--
-- Name: spec_sheet_highlight_regions spec_sheet_highlight_regions_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_regions
    ADD CONSTRAINT spec_sheet_highlight_regions_pkey PRIMARY KEY (id);


--
-- Name: spec_sheet_highlight_versions spec_sheet_highlight_versions_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT spec_sheet_highlight_versions_pkey PRIMARY KEY (id);


--
-- Name: spec_sheets spec_sheets_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheets
    ADD CONSTRAINT spec_sheets_pkey PRIMARY KEY (id);


--
-- Name: task_conversations task_conversations_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.task_conversations
    ADD CONSTRAINT task_conversations_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: campaign_send_logs uq_campaign_send_date; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT uq_campaign_send_date UNIQUE (campaign_id, send_date);


--
-- Name: companies uq_companies_name_source_type; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.companies
    ADD CONSTRAINT uq_companies_name_source_type UNIQUE (name, company_source_type);


--
-- Name: gmail_user_tokens uq_gmail_user_tokens_user_id; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT uq_gmail_user_tokens_user_id UNIQUE (user_id);


--
-- Name: manufacturer_order uq_manufacturer_order_factory_id; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.manufacturer_order
    ADD CONSTRAINT uq_manufacturer_order_factory_id UNIQUE (factory_id);


--
-- Name: o365_user_tokens uq_o365_user_tokens_user_id; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT uq_o365_user_tokens_user_id UNIQUE (user_id);


--
-- Name: pre_opportunities uq_pre_opportunities_balance_id; Type: CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT uq_pre_opportunities_balance_id UNIQUE (balance_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: report; Owner: postgres
--

ALTER TABLE ONLY report.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: report_templates report_templates_pkey; Type: CONSTRAINT; Schema: report; Owner: postgres
--

ALTER TABLE ONLY report.report_templates
    ADD CONSTRAINT report_templates_pkey PRIMARY KEY (id);


--
-- Name: signatures signatures_pkey; Type: CONSTRAINT; Schema: uploader; Owner: postgres
--

ALTER TABLE ONLY uploader.signatures
    ADD CONSTRAINT signatures_pkey PRIMARY KEY (id);


--
-- Name: similar_matches similar_matches_pkey; Type: CONSTRAINT; Schema: uploader; Owner: postgres
--

ALTER TABLE ONLY uploader.similar_matches
    ADD CONSTRAINT similar_matches_pkey PRIMARY KEY (id);


--
-- Name: uploader_alembic_version uploader_alembic_version_pkc; Type: CONSTRAINT; Schema: uploader; Owner: postgres
--

ALTER TABLE ONLY uploader.uploader_alembic_version
    ADD CONSTRAINT uploader_alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: uploader_settings uploader_settings_pkey; Type: CONSTRAINT; Schema: uploader; Owner: postgres
--

ALTER TABLE ONLY uploader.uploader_settings
    ADD CONSTRAINT uploader_settings_pkey PRIMARY KEY (key);


--
-- Name: similar_matches uq_match_id_match_title_original_title_entity_type; Type: CONSTRAINT; Schema: uploader; Owner: postgres
--

ALTER TABLE ONLY uploader.similar_matches
    ADD CONSTRAINT uq_match_id_match_title_original_title_entity_type UNIQUE (match_id, match_title, original_title, entity_type);


--
-- Name: dashboards dashboard_entity_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".dashboards
    ADD CONSTRAINT dashboard_entity_pkey PRIMARY KEY (id);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: event_entity event_entity_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".event_entity
    ADD CONSTRAINT event_entity_pkey PRIMARY KEY (uuid);


--
-- Name: followings followings_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".followings
    ADD CONSTRAINT followings_pkey PRIMARY KEY (id);


--
-- Name: message_entity message_entity_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".message_entity
    ADD CONSTRAINT message_entity_pkey PRIMARY KEY (uuid);


--
-- Name: user_roles role_entity_name_key; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".user_roles
    ADD CONSTRAINT role_entity_name_key UNIQUE (name);


--
-- Name: user_roles role_entity_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".user_roles
    ADD CONSTRAINT role_entity_pkey PRIMARY KEY (id);


--
-- Name: setting_keys setting_keys_key_key; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".setting_keys
    ADD CONSTRAINT setting_keys_key_key UNIQUE (key);


--
-- Name: setting_keys setting_keys_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".setting_keys
    ADD CONSTRAINT setting_keys_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: user_settings uk_user_settings_user_key; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".user_settings
    ADD CONSTRAINT uk_user_settings_user_key UNIQUE (user_id, setting_key_id);


--
-- Name: message_entity unique_message_uuid; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".message_entity
    ADD CONSTRAINT unique_message_uuid UNIQUE (uuid);


--
-- Name: users user_entity_email_key; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT user_entity_email_key UNIQUE (email);


--
-- Name: users user_entity_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT user_entity_pkey PRIMARY KEY (id);


--
-- Name: users user_entity_username_key; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT user_entity_username_key UNIQUE (username);


--
-- Name: user_settings user_settings_pkey; Type: CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".user_settings
    ADD CONSTRAINT user_settings_pkey PRIMARY KEY (id);


--
-- Name: aisles aisles_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.aisles
    ADD CONSTRAINT aisles_pkey PRIMARY KEY (id);


--
-- Name: bays bays_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bays
    ADD CONSTRAINT bays_pkey PRIMARY KEY (id);


--
-- Name: bins bins_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bins
    ADD CONSTRAINT bins_pkey PRIMARY KEY (id);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: fiducial_markers fiducial_markers_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fiducial_markers
    ADD CONSTRAINT fiducial_markers_pkey PRIMARY KEY (id);


--
-- Name: fulfillments fulfillments_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fulfillments
    ADD CONSTRAINT fulfillments_pkey PRIMARY KEY (id);


--
-- Name: fulfillments fulfillments_qr_code_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fulfillments
    ADD CONSTRAINT fulfillments_qr_code_key UNIQUE (qr_code);


--
-- Name: inventory_items inventory_items_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory_items
    ADD CONSTRAINT inventory_items_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_sku_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory
    ADD CONSTRAINT inventory_sku_key UNIQUE (sku);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: rmas rmas_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rmas
    ADD CONSTRAINT rmas_pkey PRIMARY KEY (id);


--
-- Name: rmas rmas_qr_code_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rmas
    ADD CONSTRAINT rmas_qr_code_key UNIQUE (qr_code);


--
-- Name: rmas rmas_rma_number_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rmas
    ADD CONSTRAINT rmas_rma_number_key UNIQUE (rma_number);


--
-- Name: rows rows_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rows
    ADD CONSTRAINT rows_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: shelves shelves_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shelves
    ADD CONSTRAINT shelves_pkey PRIMARY KEY (id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (id);


--
-- Name: shipments shipments_tracking_number_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shipments
    ADD CONSTRAINT shipments_tracking_number_key UNIQUE (tracking_number);


--
-- Name: bays uk_bay_shelf_number; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bays
    ADD CONSTRAINT uk_bay_shelf_number UNIQUE (shelf_id, bay_number);


--
-- Name: bins uk_bin_row_letter; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bins
    ADD CONSTRAINT uk_bin_row_letter UNIQUE (row_id, letter_code);


--
-- Name: inventory_items uk_inventory_item_bin_status_lot; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory_items
    ADD CONSTRAINT uk_inventory_item_bin_status_lot UNIQUE (bin_id, inventory_id, status, lot_number);


--
-- Name: rows uk_row_bay_number; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rows
    ADD CONSTRAINT uk_row_bay_number UNIQUE (bay_id, row_number);


--
-- Name: aisles uq_aisle_warehouse_name; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.aisles
    ADD CONSTRAINT uq_aisle_warehouse_name UNIQUE (warehouse_id, name);


--
-- Name: fiducial_markers uq_fiducial_marker_shelf_identifier; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fiducial_markers
    ADD CONSTRAINT uq_fiducial_marker_shelf_identifier UNIQUE (shelf_id, identifier);


--
-- Name: sections uq_section_warehouse_name; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.sections
    ADD CONSTRAINT uq_section_warehouse_name UNIQUE (warehouse_id, name);


--
-- Name: warehouse_info warehouse_info_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.warehouse_info
    ADD CONSTRAINT warehouse_info_pkey PRIMARY KEY (id);


--
-- Name: warehouse warehouse_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.warehouse
    ADD CONSTRAINT warehouse_pkey PRIMARY KEY (id);


--
-- Name: waves waves_pkey; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.waves
    ADD CONSTRAINT waves_pkey PRIMARY KEY (id);


--
-- Name: waves waves_wave_number_key; Type: CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.waves
    ADD CONSTRAINT waves_wave_number_key UNIQUE (wave_number);


--
-- Name: ix_ai_chat_message_feedback_message_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_chat_message_feedback_message_id ON ai.chat_message_feedback USING btree (message_id);


--
-- Name: ix_ai_chat_message_feedback_user_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_chat_message_feedback_user_id ON ai.chat_message_feedback USING btree (user_id);


--
-- Name: ix_ai_chat_messages_chat_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_chat_messages_chat_id ON ai.chat_messages USING btree (chat_id);


--
-- Name: ix_ai_chats_session_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_chats_session_id ON ai.chats USING btree (session_id);


--
-- Name: ix_ai_chats_user_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_chats_user_id ON ai.chats USING btree (user_id);


--
-- Name: ix_ai_cluster_contexts_cluster_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_cluster_contexts_cluster_id ON ai.cluster_contexts USING btree (cluster_id);


--
-- Name: ix_ai_email_attachments_document_type; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_email_attachments_document_type ON ai.email_attachments USING btree (document_type);


--
-- Name: ix_ai_email_attachments_email_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_email_attachments_email_id ON ai.email_attachments USING btree (email_id);


--
-- Name: ix_ai_emails_category; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_category ON ai.emails USING btree (category);


--
-- Name: ix_ai_emails_conversation_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_conversation_id ON ai.emails USING btree (conversation_id);


--
-- Name: ix_ai_emails_external_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_external_id ON ai.emails USING btree (external_id);


--
-- Name: ix_ai_emails_from_email; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_from_email ON ai.emails USING btree (from_email);


--
-- Name: ix_ai_emails_status; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_status ON ai.emails USING btree (status);


--
-- Name: ix_ai_emails_to_email; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_to_email ON ai.emails USING btree (to_email);


--
-- Name: ix_ai_emails_urgency; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_urgency ON ai.emails USING btree (urgency);


--
-- Name: ix_ai_emails_user_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_emails_user_id ON ai.emails USING btree (user_id);


--
-- Name: ix_ai_pending_documents_cluster_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_ai_pending_documents_cluster_id ON ai.pending_documents USING btree (cluster_id);


--
-- Name: ix_entity_match_candidates_pending_entity_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_entity_match_candidates_pending_entity_id ON ai.entity_match_candidates USING btree (pending_entity_id);


--
-- Name: ix_extracted_data_versions_pending_document_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_extracted_data_versions_pending_document_id ON ai.extracted_data_versions USING btree (pending_document_id);


--
-- Name: ix_extracted_data_versions_pending_document_id_version; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE UNIQUE INDEX ix_extracted_data_versions_pending_document_id_version ON ai.extracted_data_versions USING btree (pending_document_id, version_number);


--
-- Name: ix_pending_document_correction_changes_pending_document_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_correction_changes_pending_document_id ON ai.pending_document_correction_changes USING btree (pending_document_id);


--
-- Name: ix_pending_document_entities_action; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_entities_action ON ai.pending_document_entities USING btree (action);


--
-- Name: ix_pending_document_entities_entity_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_entities_entity_id ON ai.pending_document_entities USING btree (entity_id);


--
-- Name: ix_pending_document_entities_entity_type; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_entities_entity_type ON ai.pending_document_entities USING btree (entity_type);


--
-- Name: ix_pending_document_entities_pending_document_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_entities_pending_document_id ON ai.pending_document_entities USING btree (pending_document_id);


--
-- Name: ix_pending_document_pages_pending_document_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_document_pages_pending_document_id ON ai.pending_document_pages USING btree (pending_document_id);


--
-- Name: ix_pending_documents_entity_type; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_documents_entity_type ON ai.pending_documents USING btree (entity_type);


--
-- Name: ix_pending_documents_file_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_documents_file_id ON ai.pending_documents USING btree (file_id);


--
-- Name: ix_pending_documents_sha; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_documents_sha ON ai.pending_documents USING btree (sha);


--
-- Name: ix_pending_documents_status; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_documents_status ON ai.pending_documents USING btree (status);


--
-- Name: ix_pending_entities_confirmation_status; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_entities_confirmation_status ON ai.pending_entities USING btree (confirmation_status);


--
-- Name: ix_pending_entities_entity_type; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_entities_entity_type ON ai.pending_entities USING btree (entity_type);


--
-- Name: ix_pending_entities_pending_document_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_pending_entities_pending_document_id ON ai.pending_entities USING btree (pending_document_id);


--
-- Name: ix_workflow_executions_status; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_workflow_executions_status ON ai.workflow_executions USING btree (status);


--
-- Name: ix_workflow_executions_workflow_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_workflow_executions_workflow_id ON ai.workflow_executions USING btree (workflow_id);


--
-- Name: ix_workflow_files_workflow_id; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_workflow_files_workflow_id ON ai.workflow_files USING btree (workflow_id);


--
-- Name: ix_workflows_is_public; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_workflows_is_public ON ai.workflows USING btree (is_public);


--
-- Name: ix_workflows_status; Type: INDEX; Schema: ai; Owner: postgres
--

CREATE INDEX ix_workflows_status ON ai.workflows USING btree (status);


--
-- Name: idx_check_details_adjustment_id; Type: INDEX; Schema: commission; Owner: postgres
--

CREATE INDEX idx_check_details_adjustment_id ON commission.check_details USING btree (adjustment_id);


--
-- Name: idx_check_details_deduction_id; Type: INDEX; Schema: commission; Owner: postgres
--

CREATE INDEX idx_check_details_deduction_id ON commission.check_details USING btree (deduction_id);


--
-- Name: idx_check_details_invoice_id; Type: INDEX; Schema: commission; Owner: postgres
--

CREATE INDEX idx_check_details_invoice_id ON commission.check_details USING btree (invoice_id);


--
-- Name: idx_countries_name; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_countries_name ON core.countries USING btree (name);


--
-- Name: idx_ct_customer_customer; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_ct_customer_customer ON core.customer_territory_customers USING btree (customer_id);


--
-- Name: idx_ct_customer_territory; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_ct_customer_territory ON core.customer_territory_customers USING btree (territory_id);


--
-- Name: idx_ct_region_territory; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_ct_region_territory ON core.customer_territory_regions USING btree (territory_id);


--
-- Name: idx_ct_region_type_code; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_ct_region_type_code ON core.customer_territory_regions USING btree (region_type, region_code);


--
-- Name: idx_customers_type; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_customers_type ON core.customers USING btree (type);


--
-- Name: idx_document_templates_tenant_entity_type; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_document_templates_tenant_entity_type ON core.document_templates USING btree (tenant_id, entity_type);


--
-- Name: idx_note_threads_entity; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_note_threads_entity ON core.note_threads USING btree (entity_type, source_id);


--
-- Name: idx_note_threads_last_activity; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_note_threads_last_activity ON core.note_threads USING btree (last_activity_at);


--
-- Name: idx_notes_thread; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_notes_thread ON core.notes USING btree (thread_id);


--
-- Name: idx_participants_customer; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_participants_customer ON core.participants USING btree (contact_id);


--
-- Name: idx_participants_entity_source; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_participants_entity_source ON core.participants USING btree (entity_type, source_id);


--
-- Name: idx_participants_note; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_participants_note ON core.participants USING btree (note_id);


--
-- Name: idx_subdivisions_country; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_subdivisions_country ON core.subdivisions USING btree (country_code);


--
-- Name: idx_subscription_thread; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_subscription_thread ON core.note_thread_subscriptions USING btree (thread_id);


--
-- Name: idx_subscription_user; Type: INDEX; Schema: core; Owner: postgres
--

CREATE INDEX idx_subscription_user ON core.note_thread_subscriptions USING btree (user_id);


--
-- Name: file_sha_index; Type: INDEX; Schema: files; Owner: postgres
--

CREATE INDEX file_sha_index ON files.files USING btree (file_sha);


--
-- Name: file_upload_process_file_index; Type: INDEX; Schema: files; Owner: postgres
--

CREATE INDEX file_upload_process_file_index ON files.file_upload_process USING btree (file_id);


--
-- Name: vectorization_file_index; Type: INDEX; Schema: files; Owner: postgres
--

CREATE INDEX vectorization_file_index ON files.vectorization USING btree (file_id);


--
-- Name: idx_highlight_regions_page_number; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_highlight_regions_page_number ON pycrm.spec_sheet_highlight_regions USING btree (page_number);


--
-- Name: idx_highlight_regions_version_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_highlight_regions_version_id ON pycrm.spec_sheet_highlight_regions USING btree (version_id);


--
-- Name: idx_highlight_versions_is_active; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_highlight_versions_is_active ON pycrm.spec_sheet_highlight_versions USING btree (is_active);


--
-- Name: idx_highlight_versions_spec_sheet_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_highlight_versions_spec_sheet_id ON pycrm.spec_sheet_highlight_versions USING btree (spec_sheet_id);


--
-- Name: idx_manufacturer_order_factory_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_manufacturer_order_factory_id ON pycrm.manufacturer_order USING btree (factory_id);


--
-- Name: idx_manufacturer_order_sort_order; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_manufacturer_order_sort_order ON pycrm.manufacturer_order USING btree (sort_order);


--
-- Name: idx_spec_sheets_categories; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_categories ON pycrm.spec_sheets USING gin (categories);


--
-- Name: idx_spec_sheets_created_at; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_created_at ON pycrm.spec_sheets USING btree (created_at DESC);


--
-- Name: idx_spec_sheets_display_name; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_display_name ON pycrm.spec_sheets USING btree (display_name);


--
-- Name: idx_spec_sheets_factory_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_factory_id ON pycrm.spec_sheets USING btree (factory_id);


--
-- Name: idx_spec_sheets_folder_path; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_folder_path ON pycrm.spec_sheets USING btree (folder_path);


--
-- Name: idx_spec_sheets_published; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX idx_spec_sheets_published ON pycrm.spec_sheets USING btree (published);


--
-- Name: ix_campaign_recipients_campaign_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_campaign_recipients_campaign_id ON pycrm.campaign_recipients USING btree (campaign_id);


--
-- Name: ix_campaign_recipients_contact_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_campaign_recipients_contact_id ON pycrm.campaign_recipients USING btree (contact_id);


--
-- Name: ix_campaign_send_logs_campaign_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_campaign_send_logs_campaign_id ON pycrm.campaign_send_logs USING btree (campaign_id);


--
-- Name: ix_campaign_send_logs_send_date; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_campaign_send_logs_send_date ON pycrm.campaign_send_logs USING btree (send_date);


--
-- Name: ix_campaigns_status; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_campaigns_status ON pycrm.campaigns USING btree (status);


--
-- Name: ix_crm_link_relations_source_target; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_link_relations_source_target ON pycrm.link_relations USING btree (source_entity_type, source_entity_id, target_entity_type, target_entity_id);


--
-- Name: ix_crm_link_relations_source_type_source_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_link_relations_source_type_source_id ON pycrm.link_relations USING btree (source_entity_type, source_entity_id);


--
-- Name: ix_crm_link_relations_target_type_target_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_link_relations_target_type_target_id ON pycrm.link_relations USING btree (target_entity_type, target_entity_id);


--
-- Name: ix_crm_note_conversations_note_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_note_conversations_note_id ON pycrm.note_conversations USING btree (note_id);


--
-- Name: ix_crm_pre_opportunity_details_pre_opportunity_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_pre_opportunity_details_pre_opportunity_id ON pycrm.pre_opportunity_details USING btree (pre_opportunity_id);


--
-- Name: ix_crm_task_conversations_task_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_crm_task_conversations_task_id ON pycrm.task_conversations USING btree (task_id);


--
-- Name: ix_gmail_user_tokens_google_user_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_gmail_user_tokens_google_user_id ON pycrm.gmail_user_tokens USING btree (google_user_id);


--
-- Name: ix_gmail_user_tokens_user_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_gmail_user_tokens_user_id ON pycrm.gmail_user_tokens USING btree (user_id);


--
-- Name: ix_o365_user_tokens_microsoft_user_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_o365_user_tokens_microsoft_user_id ON pycrm.o365_user_tokens USING btree (microsoft_user_id);


--
-- Name: ix_o365_user_tokens_user_id; Type: INDEX; Schema: pycrm; Owner: postgres
--

CREATE INDEX ix_o365_user_tokens_user_id ON pycrm.o365_user_tokens USING btree (user_id);


--
-- Name: idx_followings_user; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX idx_followings_user ON "user".followings USING btree (user_id);


--
-- Name: idx_tasks_position; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX idx_tasks_position ON "user".tasks USING btree ("position");


--
-- Name: idx_tasks_user_id; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX idx_tasks_user_id ON "user".tasks USING btree (user_id);


--
-- Name: ix_setting_keys_group_name; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX ix_setting_keys_group_name ON "user".setting_keys USING btree (group_name);


--
-- Name: ix_setting_keys_key; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX ix_setting_keys_key ON "user".setting_keys USING btree (key);


--
-- Name: ix_user_settings_key; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX ix_user_settings_key ON "user".user_settings USING btree (setting_key_id);


--
-- Name: ix_user_settings_user; Type: INDEX; Schema: user; Owner: postgres
--

CREATE INDEX ix_user_settings_user ON "user".user_settings USING btree (user_id);


--
-- Name: idx_aisle_is_active; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_aisle_is_active ON warehouse.aisles USING btree (is_active);


--
-- Name: idx_aisle_section; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_aisle_section ON warehouse.aisles USING btree (section_id);


--
-- Name: idx_aisle_warehouse; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_aisle_warehouse ON warehouse.aisles USING btree (warehouse_id);


--
-- Name: idx_bay_code; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_bay_code ON warehouse.bays USING btree (code);


--
-- Name: idx_bay_shelf_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_bay_shelf_id ON warehouse.bays USING btree (shelf_id);


--
-- Name: idx_bin_row_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_bin_row_id ON warehouse.bins USING btree (row_id);


--
-- Name: idx_fiducial_marker_identifier; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fiducial_marker_identifier ON warehouse.fiducial_markers USING btree (identifier);


--
-- Name: idx_fiducial_marker_shelf; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fiducial_marker_shelf ON warehouse.fiducial_markers USING btree (shelf_id);


--
-- Name: idx_fulfillment_inventory_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_inventory_id ON warehouse.fulfillments USING btree (inventory_id);


--
-- Name: idx_fulfillment_order_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_order_id ON warehouse.fulfillments USING btree (order_id);


--
-- Name: idx_fulfillment_product_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_product_id ON warehouse.fulfillments USING btree (product_id);


--
-- Name: idx_fulfillment_qr_code; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE UNIQUE INDEX idx_fulfillment_qr_code ON warehouse.fulfillments USING btree (qr_code);


--
-- Name: idx_fulfillment_status; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_status ON warehouse.fulfillments USING btree (status);


--
-- Name: idx_fulfillment_warehouse_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_warehouse_id ON warehouse.fulfillments USING btree (warehouse_id);


--
-- Name: idx_fulfillment_wave_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_fulfillment_wave_id ON warehouse.fulfillments USING btree (wave_id);


--
-- Name: idx_inventory_item_barcode; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_barcode ON warehouse.inventory_items USING btree (barcode);


--
-- Name: idx_inventory_item_bin_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_bin_id ON warehouse.inventory_items USING btree (bin_id);


--
-- Name: idx_inventory_item_inventory_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_inventory_id ON warehouse.inventory_items USING btree (inventory_id);


--
-- Name: idx_inventory_item_lot_number; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_lot_number ON warehouse.inventory_items USING btree (lot_number);


--
-- Name: idx_inventory_item_serial_number; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_serial_number ON warehouse.inventory_items USING btree (serial_number);


--
-- Name: idx_inventory_item_sku; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_sku ON warehouse.inventory_items USING btree (sku);


--
-- Name: idx_inventory_item_status; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_item_status ON warehouse.inventory_items USING btree (status);


--
-- Name: idx_inventory_product_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_product_id ON warehouse.inventory USING btree (product_id);


--
-- Name: idx_inventory_sku; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_inventory_sku ON warehouse.inventory USING btree (sku);


--
-- Name: idx_locations_city_state; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_locations_city_state ON warehouse.locations USING btree (city, state);


--
-- Name: idx_locations_is_active; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_locations_is_active ON warehouse.locations USING btree (is_active);


--
-- Name: idx_locations_name; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_locations_name ON warehouse.locations USING btree (name);


--
-- Name: idx_rma_fulfillment_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_rma_fulfillment_id ON warehouse.rmas USING btree (fulfillment_id);


--
-- Name: idx_rma_number; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE UNIQUE INDEX idx_rma_number ON warehouse.rmas USING btree (rma_number);


--
-- Name: idx_rma_order_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_rma_order_id ON warehouse.rmas USING btree (order_id);


--
-- Name: idx_rma_status; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_rma_status ON warehouse.rmas USING btree (status);


--
-- Name: idx_row_bay_id; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_row_bay_id ON warehouse.rows USING btree (bay_id);


--
-- Name: idx_section_is_active; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_section_is_active ON warehouse.sections USING btree (is_active);


--
-- Name: idx_section_warehouse; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_section_warehouse ON warehouse.sections USING btree (warehouse_id);


--
-- Name: idx_shelves_aisle; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shelves_aisle ON warehouse.shelves USING btree (aisle_id);


--
-- Name: idx_shelves_is_active; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shelves_is_active ON warehouse.shelves USING btree (is_active);


--
-- Name: idx_shelves_section; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shelves_section ON warehouse.shelves USING btree (section_id);


--
-- Name: idx_shelves_warehouse; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shelves_warehouse ON warehouse.shelves USING btree (warehouse_id);


--
-- Name: idx_shipment_carrier; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shipment_carrier ON warehouse.shipments USING btree (carrier);


--
-- Name: idx_shipment_shipped_at; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shipment_shipped_at ON warehouse.shipments USING btree (shipped_at);


--
-- Name: idx_shipment_status; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_shipment_status ON warehouse.shipments USING btree (status);


--
-- Name: idx_shipment_tracking_number; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE UNIQUE INDEX idx_shipment_tracking_number ON warehouse.shipments USING btree (tracking_number);


--
-- Name: idx_warehouse_city_state; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_warehouse_city_state ON warehouse.warehouse USING btree (city, state);


--
-- Name: idx_warehouse_is_active; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_warehouse_is_active ON warehouse.warehouse USING btree (is_active);


--
-- Name: idx_warehouse_name; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_warehouse_name ON warehouse.warehouse USING btree (name);


--
-- Name: idx_wave_created_at; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_wave_created_at ON warehouse.waves USING btree (created_at);


--
-- Name: idx_wave_status; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE INDEX idx_wave_status ON warehouse.waves USING btree (status);


--
-- Name: idx_wave_wave_number; Type: INDEX; Schema: warehouse; Owner: postgres
--

CREATE UNIQUE INDEX idx_wave_wave_number ON warehouse.waves USING btree (wave_number);


--
-- Name: cluster_contexts cluster_contexts_cluster_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.cluster_contexts
    ADD CONSTRAINT cluster_contexts_cluster_id_fkey FOREIGN KEY (cluster_id) REFERENCES ai.document_clusters(id) ON DELETE CASCADE;


--
-- Name: entity_match_candidates entity_match_candidates_pending_entity_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.entity_match_candidates
    ADD CONSTRAINT entity_match_candidates_pending_entity_id_fkey FOREIGN KEY (pending_entity_id) REFERENCES ai.pending_entities(id) ON DELETE CASCADE;


--
-- Name: extracted_data_versions extracted_data_versions_pending_document_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.extracted_data_versions
    ADD CONSTRAINT extracted_data_versions_pending_document_id_fkey FOREIGN KEY (pending_document_id) REFERENCES ai.pending_documents(id) ON DELETE CASCADE;


--
-- Name: chat_message_feedback fk_ai_chat_message_feedback_message_id_chat_messages; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.chat_message_feedback
    ADD CONSTRAINT fk_ai_chat_message_feedback_message_id_chat_messages FOREIGN KEY (message_id) REFERENCES ai.chat_messages(id);


--
-- Name: chat_messages fk_ai_chat_messages_chat_id_chats; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.chat_messages
    ADD CONSTRAINT fk_ai_chat_messages_chat_id_chats FOREIGN KEY (chat_id) REFERENCES ai.chats(id);


--
-- Name: email_attachments fk_ai_email_attachments_email_id_emails; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.email_attachments
    ADD CONSTRAINT fk_ai_email_attachments_email_id_emails FOREIGN KEY (email_id) REFERENCES ai.emails(id) ON DELETE CASCADE;


--
-- Name: pending_documents fk_pending_documents_cluster_id; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_documents
    ADD CONSTRAINT fk_pending_documents_cluster_id FOREIGN KEY (cluster_id) REFERENCES ai.document_clusters(id) ON DELETE SET NULL;


--
-- Name: pending_document_correction_changes pending_document_correction_changes_pending_document_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_correction_changes
    ADD CONSTRAINT pending_document_correction_changes_pending_document_id_fkey FOREIGN KEY (pending_document_id) REFERENCES ai.pending_documents(id) ON DELETE CASCADE;


--
-- Name: pending_document_entities pending_document_entities_pending_document_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_entities
    ADD CONSTRAINT pending_document_entities_pending_document_id_fkey FOREIGN KEY (pending_document_id) REFERENCES ai.pending_documents(id) ON DELETE CASCADE;


--
-- Name: pending_document_pages pending_document_pages_pending_document_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_document_pages
    ADD CONSTRAINT pending_document_pages_pending_document_id_fkey FOREIGN KEY (pending_document_id) REFERENCES ai.pending_documents(id);


--
-- Name: pending_entities pending_entities_pending_document_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.pending_entities
    ADD CONSTRAINT pending_entities_pending_document_id_fkey FOREIGN KEY (pending_document_id) REFERENCES ai.pending_documents(id);


--
-- Name: workflow_executions workflow_executions_workflow_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.workflow_executions
    ADD CONSTRAINT workflow_executions_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES ai.workflows(id);


--
-- Name: workflow_files workflow_files_workflow_id_fkey; Type: FK CONSTRAINT; Schema: ai; Owner: postgres
--

ALTER TABLE ONLY ai.workflow_files
    ADD CONSTRAINT workflow_files_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES ai.workflows(id);


--
-- Name: chat_messages chat_messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: chats; Owner: postgres
--

ALTER TABLE ONLY chats.chat_messages
    ADD CONSTRAINT chat_messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES chats.chats(id);


--
-- Name: check_balances_aud fk_check_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_balances_aud
    ADD CONSTRAINT fk_check_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: check_details fk_check_details_adjustment_id_on_adjustments; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details
    ADD CONSTRAINT fk_check_details_adjustment_id_on_adjustments FOREIGN KEY (adjustment_id) REFERENCES commission.expenses(id);


--
-- Name: check_details_aud fk_check_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details_aud
    ADD CONSTRAINT fk_check_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: check_details fk_check_details_check_id_on_checks; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details
    ADD CONSTRAINT fk_check_details_check_id_on_checks FOREIGN KEY (check_id) REFERENCES commission.checks(id);


--
-- Name: check_details fk_check_details_deduction_id_on_deductions; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details
    ADD CONSTRAINT fk_check_details_deduction_id_on_deductions FOREIGN KEY (deduction_id) REFERENCES commission.credits(id);


--
-- Name: check_details fk_check_details_invoice_id_on_invoices; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.check_details
    ADD CONSTRAINT fk_check_details_invoice_id_on_invoices FOREIGN KEY (invoice_id) REFERENCES commission.invoices(id);


--
-- Name: checks_aud fk_checks_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks_aud
    ADD CONSTRAINT fk_checks_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: checks fk_checks_balance_id_on_check_balances; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks
    ADD CONSTRAINT fk_checks_balance_id_on_check_balances FOREIGN KEY (balance_id) REFERENCES commission.check_balances(id);


--
-- Name: checks fk_checks_factory_id_on_factories; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.checks
    ADD CONSTRAINT fk_checks_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: credit_balances_aud fk_credit_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_balances_aud
    ADD CONSTRAINT fk_credit_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: credit_details_aud fk_credit_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_details_aud
    ADD CONSTRAINT fk_credit_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: credit_details fk_credit_details_credit_id_on_credits; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_details
    ADD CONSTRAINT fk_credit_details_credit_id_on_credits FOREIGN KEY (credit_id) REFERENCES commission.credits(id);


--
-- Name: credit_details fk_credit_details_credit_reason_id_on_credit_reasons; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_details
    ADD CONSTRAINT fk_credit_details_credit_reason_id_on_credit_reasons FOREIGN KEY (credit_reason_id) REFERENCES commission.credit_reasons(id);


--
-- Name: credit_reasons_aud fk_credit_reasons_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credit_reasons_aud
    ADD CONSTRAINT fk_credit_reasons_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: credits_aud fk_credits_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits_aud
    ADD CONSTRAINT fk_credits_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: credits fk_credits_balance_id_on_credit_balances; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits
    ADD CONSTRAINT fk_credits_balance_id_on_credit_balances FOREIGN KEY (balance_id) REFERENCES commission.credit_balances(id);


--
-- Name: credits fk_credits_order_id_on_orders; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.credits
    ADD CONSTRAINT fk_credits_order_id_on_orders FOREIGN KEY (order_id) REFERENCES commission.orders(id);


--
-- Name: deduction_sales_reps_aud fk_deduction_sales_reps_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.deduction_sales_reps_aud
    ADD CONSTRAINT fk_deduction_sales_reps_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: deduction_sales_reps fk_deduction_sales_reps_credit_id_on_credit_details; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.deduction_sales_reps
    ADD CONSTRAINT fk_deduction_sales_reps_credit_id_on_credit_details FOREIGN KEY (credit_detail_id) REFERENCES commission.credit_details(id);


--
-- Name: expense_categories_aud fk_expense_categories_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_categories_aud
    ADD CONSTRAINT fk_expense_categories_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: expense_split_rates_aud fk_expense_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_split_rates_aud
    ADD CONSTRAINT fk_expense_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: expense_split_rates fk_expense_split_rates_expense_id_on_expenses; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expense_split_rates
    ADD CONSTRAINT fk_expense_split_rates_expense_id_on_expenses FOREIGN KEY (expense_id) REFERENCES commission.expenses(id);


--
-- Name: expenses_aud fk_expenses_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses_aud
    ADD CONSTRAINT fk_expenses_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: expenses fk_expenses_expense_category_id_on_expense_categories; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses
    ADD CONSTRAINT fk_expenses_expense_category_id_on_expense_categories FOREIGN KEY (expense_category_id) REFERENCES commission.expense_categories(id);


--
-- Name: expenses fk_expenses_sold_to_customer_id_on_customers; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.expenses
    ADD CONSTRAINT fk_expenses_sold_to_customer_id_on_customers FOREIGN KEY (sold_to_customer_id) REFERENCES core.customers(id);


--
-- Name: invoice_balances_aud fk_invoice_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_balances_aud
    ADD CONSTRAINT fk_invoice_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: invoice_details_aud fk_invoice_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_details_aud
    ADD CONSTRAINT fk_invoice_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: invoice_details fk_invoice_details_invoice_id_on_invoices; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_details
    ADD CONSTRAINT fk_invoice_details_invoice_id_on_invoices FOREIGN KEY (invoice_id) REFERENCES commission.invoices(id);


--
-- Name: invoice_details fk_invoice_details_order_detail_id_on_order_details; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_details
    ADD CONSTRAINT fk_invoice_details_order_detail_id_on_order_details FOREIGN KEY (order_detail_id) REFERENCES commission.order_details(id);


--
-- Name: invoice_split_rates_aud fk_invoice_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_split_rates_aud
    ADD CONSTRAINT fk_invoice_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: invoice_split_rates fk_invoice_split_rates_invoice_id_on_invoice_details; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoice_split_rates
    ADD CONSTRAINT fk_invoice_split_rates_invoice_id_on_invoice_details FOREIGN KEY (invoice_detail_id) REFERENCES commission.invoice_details(id);


--
-- Name: invoices_aud fk_invoices_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices_aud
    ADD CONSTRAINT fk_invoices_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: invoices fk_invoices_balance_id_on_invoice_balances; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT fk_invoices_balance_id_on_invoice_balances FOREIGN KEY (balance_id) REFERENCES commission.invoice_balances(id);


--
-- Name: invoices fk_invoices_factory_id_on_factories; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT fk_invoices_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: invoices fk_invoices_order_id_on_orders; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.invoices
    ADD CONSTRAINT fk_invoices_order_id_on_orders FOREIGN KEY (order_id) REFERENCES commission.orders(id);


--
-- Name: order_acknowledgements_aud fk_order_acknowledgements_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_acknowledgements_aud
    ADD CONSTRAINT fk_order_acknowledgements_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: order_acknowledgements fk_order_acknowledgements_order_detail_id_on_order_details; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_acknowledgements
    ADD CONSTRAINT fk_order_acknowledgements_order_detail_id_on_order_details FOREIGN KEY (order_detail_id) REFERENCES commission.order_details(id) ON DELETE CASCADE;


--
-- Name: order_balances_aud fk_order_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_balances_aud
    ADD CONSTRAINT fk_order_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: order_details_aud fk_order_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_details_aud
    ADD CONSTRAINT fk_order_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: order_details fk_order_details_order_id_on_orders; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_details
    ADD CONSTRAINT fk_order_details_order_id_on_orders FOREIGN KEY (order_id) REFERENCES commission.orders(id);


--
-- Name: order_details fk_order_details_product_id_on_products; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_details
    ADD CONSTRAINT fk_order_details_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: order_inside_reps_aud fk_order_inside_reps_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_inside_reps_aud
    ADD CONSTRAINT fk_order_inside_reps_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: order_inside_reps fk_order_inside_reps_order_id_on_orders; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_inside_reps
    ADD CONSTRAINT fk_order_inside_reps_order_id_on_orders FOREIGN KEY (order_id) REFERENCES commission.orders(id);


--
-- Name: order_split_rates_aud fk_order_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_split_rates_aud
    ADD CONSTRAINT fk_order_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: order_split_rates fk_order_split_rates_order_id_on_order_details; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.order_split_rates
    ADD CONSTRAINT fk_order_split_rates_order_id_on_order_details FOREIGN KEY (order_detail_id) REFERENCES commission.order_details(id);


--
-- Name: orders_aud fk_orders_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders_aud
    ADD CONSTRAINT fk_orders_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES commission.revinfo(rev);


--
-- Name: orders fk_orders_balance_id_on_order_balances; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT fk_orders_balance_id_on_order_balances FOREIGN KEY (balance_id) REFERENCES commission.order_balances(id);


--
-- Name: orders fk_orders_factory_id_on_factories; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT fk_orders_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: orders fk_orders_job_id_on_jobs; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT fk_orders_job_id_on_jobs FOREIGN KEY (job_id) REFERENCES crm.jobs(id);


--
-- Name: orders fk_orders_sold_to_customer_id_on_customers; Type: FK CONSTRAINT; Schema: commission; Owner: postgres
--

ALTER TABLE ONLY commission.orders
    ADD CONSTRAINT fk_orders_sold_to_customer_id_on_customers FOREIGN KEY (sold_to_customer_id) REFERENCES core.customers(id);


--
-- Name: addresses_aud fk_addresses_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.addresses_aud
    ADD CONSTRAINT fk_addresses_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: addresses fk_addresses_country_code_on_countries; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.addresses
    ADD CONSTRAINT fk_addresses_country_code_on_countries FOREIGN KEY (country_code) REFERENCES core.countries(code);


--
-- Name: addresses fk_addresses_subdivision_code_on_subdivisions; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.addresses
    ADD CONSTRAINT fk_addresses_subdivision_code_on_subdivisions FOREIGN KEY (subdivision_code) REFERENCES core.subdivisions(iso_code);


--
-- Name: contacts_aud fk_contacts_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.contacts_aud
    ADD CONSTRAINT fk_contacts_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: countries_aud fk_countries_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.countries_aud
    ADD CONSTRAINT fk_countries_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_territory_boundaries fk_ct_boundary_territory; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_boundaries
    ADD CONSTRAINT fk_ct_boundary_territory FOREIGN KEY (territory_id) REFERENCES core.customer_territories(id) ON DELETE CASCADE;


--
-- Name: customer_territory_customers fk_ct_customer_territory; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_customers
    ADD CONSTRAINT fk_ct_customer_territory FOREIGN KEY (territory_id) REFERENCES core.customer_territories(id) ON DELETE CASCADE;


--
-- Name: customer_territory_regions fk_ct_region_territory; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_regions
    ADD CONSTRAINT fk_ct_region_territory FOREIGN KEY (territory_id) REFERENCES core.customer_territories(id) ON DELETE CASCADE;


--
-- Name: customer_branches_aud fk_customer_branches_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_branches_aud
    ADD CONSTRAINT fk_customer_branches_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_levels_aud fk_customer_levels_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels_aud
    ADD CONSTRAINT fk_customer_levels_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_levels fk_customer_levels_customer_id_on_customers; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels
    ADD CONSTRAINT fk_customer_levels_customer_id_on_customers FOREIGN KEY (customer_id) REFERENCES core.customers(id);


--
-- Name: customer_levels fk_customer_levels_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_levels
    ADD CONSTRAINT fk_customer_levels_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: customer_split_rates_aud fk_customer_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_split_rates_aud
    ADD CONSTRAINT fk_customer_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_split_rates fk_customer_split_rates_customer_id_on_customers; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_split_rates
    ADD CONSTRAINT fk_customer_split_rates_customer_id_on_customers FOREIGN KEY (customer_id) REFERENCES core.customers(id);


--
-- Name: customer_territories_aud fk_customer_territories_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territories_aud
    ADD CONSTRAINT fk_customer_territories_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_territory_boundaries_aud fk_customer_territory_boundaries_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_boundaries_aud
    ADD CONSTRAINT fk_customer_territory_boundaries_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_territory_customers_aud fk_customer_territory_customers_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_customers_aud
    ADD CONSTRAINT fk_customer_territory_customers_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customer_territory_regions_aud fk_customer_territory_regions_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customer_territory_regions_aud
    ADD CONSTRAINT fk_customer_territory_regions_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customers_aud fk_customers_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers_aud
    ADD CONSTRAINT fk_customers_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: customers fk_customers_customer_branch_id_on_customer_branches; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers
    ADD CONSTRAINT fk_customers_customer_branch_id_on_customer_branches FOREIGN KEY (customer_branch_id) REFERENCES core.customer_branches(id);


--
-- Name: customers fk_customers_customer_branch_id_on_customer_territories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.customers
    ADD CONSTRAINT fk_customers_customer_branch_id_on_customer_territories FOREIGN KEY (customer_territory_id) REFERENCES core.customer_territories(id);


--
-- Name: factories_aud fk_factories_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factories_aud
    ADD CONSTRAINT fk_factories_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: factory_commission_bands_aud fk_factory_commission_bands_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_commission_bands_aud
    ADD CONSTRAINT fk_factory_commission_bands_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: factory_commission_bands fk_factory_commission_bands_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_commission_bands
    ADD CONSTRAINT fk_factory_commission_bands_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: factory_customer_ids_aud fk_factory_customer_ids_aud_on_rev; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids_aud
    ADD CONSTRAINT fk_factory_customer_ids_aud_on_rev FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: factory_customer_ids fk_factory_customer_ids_on_customer; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids
    ADD CONSTRAINT fk_factory_customer_ids_on_customer FOREIGN KEY (customer_id) REFERENCES core.customers(id);


--
-- Name: factory_customer_ids fk_factory_customer_ids_on_factory; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_customer_ids
    ADD CONSTRAINT fk_factory_customer_ids_on_factory FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: factory_levels_aud fk_factory_levels_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_levels_aud
    ADD CONSTRAINT fk_factory_levels_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: factory_levels fk_factory_levels_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.factory_levels
    ADD CONSTRAINT fk_factory_levels_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: note_note_tags_aud fk_note_note_tags_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_note_tags_aud
    ADD CONSTRAINT fk_note_note_tags_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: note_note_tags fk_note_note_tags_note_id_on_notes; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_note_tags
    ADD CONSTRAINT fk_note_note_tags_note_id_on_notes FOREIGN KEY (note_id) REFERENCES core.notes(id);


--
-- Name: note_note_tags fk_note_note_tags_note_tag_id_on_note_tags; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_note_tags
    ADD CONSTRAINT fk_note_note_tags_note_tag_id_on_note_tags FOREIGN KEY (note_tag_id) REFERENCES core.note_tags(id);


--
-- Name: note_tags_aud fk_note_tags_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags_aud
    ADD CONSTRAINT fk_note_tags_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: note_tags_notes_aud fk_note_tags_notes_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_tags_notes_aud
    ADD CONSTRAINT fk_note_tags_notes_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: note_thread_subscriptions_aud fk_note_thread_subscriptions_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_thread_subscriptions_aud
    ADD CONSTRAINT fk_note_thread_subscriptions_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: note_threads_aud fk_note_threads_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_threads_aud
    ADD CONSTRAINT fk_note_threads_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: notes_aud fk_notes_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notes_aud
    ADD CONSTRAINT fk_notes_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: notes fk_notes_parent_id_on_notes; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notes
    ADD CONSTRAINT fk_notes_parent_id_on_notes FOREIGN KEY (parent_id) REFERENCES core.notes(id);


--
-- Name: notes fk_notes_thread; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.notes
    ADD CONSTRAINT fk_notes_thread FOREIGN KEY (thread_id) REFERENCES core.note_threads(id);


--
-- Name: participants fk_participant_contact; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.participants
    ADD CONSTRAINT fk_participant_contact FOREIGN KEY (contact_id) REFERENCES core.contacts(id) ON DELETE CASCADE;


--
-- Name: participants_aud fk_participants_aud_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.participants_aud
    ADD CONSTRAINT fk_participants_aud_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_categories_aud fk_product_categories_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories_aud
    ADD CONSTRAINT fk_product_categories_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_commission_bands_aud fk_product_commission_bands_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_commission_bands_aud
    ADD CONSTRAINT fk_product_commission_bands_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_commission_bands fk_product_commission_bands_product_id_on_products; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_commission_bands
    ADD CONSTRAINT fk_product_commission_bands_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: product_cpns_aud fk_product_cpns_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns_aud
    ADD CONSTRAINT fk_product_cpns_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_cpns fk_product_cpns_customer_id_on_customers; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns
    ADD CONSTRAINT fk_product_cpns_customer_id_on_customers FOREIGN KEY (customer_id) REFERENCES core.customers(id);


--
-- Name: product_cpns fk_product_cpns_product_id_on_products; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_cpns
    ADD CONSTRAINT fk_product_cpns_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: product_measurements_aud fk_product_measurements_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_measurements_aud
    ADD CONSTRAINT fk_product_measurements_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_measurements fk_product_measurements_product_id_on_products; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_measurements
    ADD CONSTRAINT fk_product_measurements_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: product_quantity_pricing_aud fk_product_quantity_pricing_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_quantity_pricing_aud
    ADD CONSTRAINT fk_product_quantity_pricing_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_quantity_pricing fk_product_quantity_pricing_product_id_products; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_quantity_pricing
    ADD CONSTRAINT fk_product_quantity_pricing_product_id_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: product_uoms_aud fk_product_uoms_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_uoms_aud
    ADD CONSTRAINT fk_product_uoms_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: products_aud fk_products_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products_aud
    ADD CONSTRAINT fk_products_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: product_categories fk_products_category_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.product_categories
    ADD CONSTRAINT fk_products_category_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: products fk_products_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products
    ADD CONSTRAINT fk_products_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: products fk_products_product_category_id_on_product_categories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products
    ADD CONSTRAINT fk_products_product_category_id_on_product_categories FOREIGN KEY (product_category_id) REFERENCES core.product_categories(id);


--
-- Name: products fk_products_product_uom_id_on_product_uoms; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.products
    ADD CONSTRAINT fk_products_product_uom_id_on_product_uoms FOREIGN KEY (product_uom_id) REFERENCES core.product_uoms(id);


--
-- Name: sales_rep_selection_split_rates_aud fk_sales_rep_selection_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selection_split_rates_aud
    ADD CONSTRAINT fk_sales_rep_selection_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: sales_rep_selection_split_rates fk_sales_rep_selection_split_rates_sales_pep_selection_id_on_sa; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selection_split_rates
    ADD CONSTRAINT fk_sales_rep_selection_split_rates_sales_pep_selection_id_on_sa FOREIGN KEY (sales_pep_selection_id) REFERENCES core.sales_rep_selections(id);


--
-- Name: sales_rep_selections_aud fk_sales_rep_selections_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections_aud
    ADD CONSTRAINT fk_sales_rep_selections_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: sales_rep_selections fk_sales_rep_selections_customer_id_on_customers; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections
    ADD CONSTRAINT fk_sales_rep_selections_customer_id_on_customers FOREIGN KEY (customer_id) REFERENCES core.customers(id);


--
-- Name: sales_rep_selections fk_sales_rep_selections_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.sales_rep_selections
    ADD CONSTRAINT fk_sales_rep_selections_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: site_options_aud fk_site_options_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.site_options_aud
    ADD CONSTRAINT fk_site_options_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: stepped_commission_tiers_aud fk_stepped_commission_tiers_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.stepped_commission_tiers_aud
    ADD CONSTRAINT fk_stepped_commission_tiers_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: stepped_commission_tiers fk_stepped_commission_tiers_factory_id_on_factories; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.stepped_commission_tiers
    ADD CONSTRAINT fk_stepped_commission_tiers_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: subdivisions fk_subdiv_country; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions
    ADD CONSTRAINT fk_subdiv_country FOREIGN KEY (country_code) REFERENCES core.countries(code);


--
-- Name: subdivisions_aud fk_subdiv_country; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions_aud
    ADD CONSTRAINT fk_subdiv_country FOREIGN KEY (country_code) REFERENCES core.countries(code);


--
-- Name: subdivisions_aud fk_subdivisions_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.subdivisions_aud
    ADD CONSTRAINT fk_subdivisions_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES core.revinfo(rev);


--
-- Name: note_thread_subscriptions fk_subscription_thread; Type: FK CONSTRAINT; Schema: core; Owner: postgres
--

ALTER TABLE ONLY core.note_thread_subscriptions
    ADD CONSTRAINT fk_subscription_thread FOREIGN KEY (thread_id) REFERENCES core.note_threads(id) ON DELETE CASCADE;


--
-- Name: pre_opportunities_aud fk_pre_opportunities_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities_aud
    ADD CONSTRAINT fk_pre_opportunities_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunities fk_pre_opportunities_balance_id_on_pre_opportunity_balances; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_balance_id_on_pre_opportunity_balances FOREIGN KEY (balance_id) REFERENCES crm.pre_opportunity_balances(id);


--
-- Name: pre_opportunities fk_pre_opportunities_sold_to_customer_id_on_customers; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_sold_to_customer_id_on_customers FOREIGN KEY (sold_to_customer_id) REFERENCES core.customers(id);


--
-- Name: pre_opportunity_balances_aud fk_pre_opportunity_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_balances_aud
    ADD CONSTRAINT fk_pre_opportunity_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunity_details_aud fk_pre_opportunity_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details_aud
    ADD CONSTRAINT fk_pre_opportunity_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_factory_id_on_factories; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_lost_reason_id_on_pre_opportunity_lo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_lost_reason_id_on_pre_opportunity_lo FOREIGN KEY (lost_reason_id) REFERENCES crm.pre_opportunity_lost_reasons(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_pre_opportunity_id_on_pre_opportunit; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_pre_opportunity_id_on_pre_opportunit FOREIGN KEY (pre_opportunity_id) REFERENCES crm.pre_opportunities(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_product_id_on_products; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: pre_opportunity_inside_reps_aud fk_pre_opportunity_inside_reps_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_inside_reps_aud
    ADD CONSTRAINT fk_pre_opportunity_inside_reps_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunity_inside_reps fk_pre_opportunity_inside_reps_pre_opportunity_id_on_pre_opport; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_inside_reps
    ADD CONSTRAINT fk_pre_opportunity_inside_reps_pre_opportunity_id_on_pre_opport FOREIGN KEY (pre_opportunity_id) REFERENCES crm.pre_opportunities(id);


--
-- Name: pre_opportunity_lost_reasons_aud fk_pre_opportunity_lost_reasons_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_lost_reasons_aud
    ADD CONSTRAINT fk_pre_opportunity_lost_reasons_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunity_split_rates_aud fk_pre_opportunity_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_split_rates_aud
    ADD CONSTRAINT fk_pre_opportunity_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: pre_opportunity_split_rates fk_pre_opportunity_split_rates_pre_opportunity_id_on_pre_opport; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.pre_opportunity_split_rates
    ADD CONSTRAINT fk_pre_opportunity_split_rates_pre_opportunity_id_on_pre_opport FOREIGN KEY (pre_opportunity_detail_id) REFERENCES crm.pre_opportunity_details(id);


--
-- Name: quote_balances_aud fk_quote_balances_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_balances_aud
    ADD CONSTRAINT fk_quote_balances_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quote_details_aud fk_quote_details_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details_aud
    ADD CONSTRAINT fk_quote_details_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quote_details fk_quote_details_factory_id_on_factories; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details
    ADD CONSTRAINT fk_quote_details_factory_id_on_factories FOREIGN KEY (factory_id) REFERENCES core.factories(id);


--
-- Name: quote_details fk_quote_details_lost_reason_id_on_quote_lost_reasons; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details
    ADD CONSTRAINT fk_quote_details_lost_reason_id_on_quote_lost_reasons FOREIGN KEY (lost_reason_id) REFERENCES crm.quote_lost_reasons(id);


--
-- Name: quote_details fk_quote_details_product_id_on_products; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details
    ADD CONSTRAINT fk_quote_details_product_id_on_products FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: quote_details fk_quote_details_quote_id_on_quotes; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_details
    ADD CONSTRAINT fk_quote_details_quote_id_on_quotes FOREIGN KEY (quote_id) REFERENCES crm.quotes(id);


--
-- Name: quote_inside_reps_aud fk_quote_inside_reps_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_inside_reps_aud
    ADD CONSTRAINT fk_quote_inside_reps_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quote_inside_reps fk_quote_inside_reps_quote_id_on_quotes; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_inside_reps
    ADD CONSTRAINT fk_quote_inside_reps_quote_id_on_quotes FOREIGN KEY (quote_id) REFERENCES crm.quotes(id);


--
-- Name: quote_lost_reasons_aud fk_quote_lost_reasons_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_lost_reasons_aud
    ADD CONSTRAINT fk_quote_lost_reasons_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quote_split_rates_aud fk_quote_split_rates_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_split_rates_aud
    ADD CONSTRAINT fk_quote_split_rates_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quote_split_rates fk_quote_split_rates_quote_id_on_quote_details; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quote_split_rates
    ADD CONSTRAINT fk_quote_split_rates_quote_id_on_quote_details FOREIGN KEY (quote_detail_id) REFERENCES crm.quote_details(id);


--
-- Name: quotes_aud fk_quotes_aud_rev_on_revinfo; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes_aud
    ADD CONSTRAINT fk_quotes_aud_rev_on_revinfo FOREIGN KEY (rev) REFERENCES crm.revinfo(rev);


--
-- Name: quotes fk_quotes_balance_id_on_quote_balances; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes
    ADD CONSTRAINT fk_quotes_balance_id_on_quote_balances FOREIGN KEY (balance_id) REFERENCES crm.quote_balances(id);


--
-- Name: quotes fk_quotes_sold_to_customer_id_on_customers; Type: FK CONSTRAINT; Schema: crm; Owner: postgres
--

ALTER TABLE ONLY crm.quotes
    ADD CONSTRAINT fk_quotes_sold_to_customer_id_on_customers FOREIGN KEY (sold_to_customer_id) REFERENCES core.customers(id);


--
-- Name: file_entity_details file_entity_details_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_entity_details
    ADD CONSTRAINT file_entity_details_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: file_meta file_meta_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_meta
    ADD CONSTRAINT file_meta_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: file_summary file_summary_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_summary
    ADD CONSTRAINT file_summary_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: file_upload_details file_upload_details_file_upload_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_details
    ADD CONSTRAINT file_upload_details_file_upload_id_fkey FOREIGN KEY (file_upload_id) REFERENCES files.file_upload_process(id);


--
-- Name: file_upload_details file_upload_details_file_upload_process_dto_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_details
    ADD CONSTRAINT file_upload_details_file_upload_process_dto_id_fkey FOREIGN KEY (file_upload_process_dto_id) REFERENCES files.file_upload_process_dtos(id);


--
-- Name: file_upload_process file_upload_process_current_dto_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process
    ADD CONSTRAINT file_upload_process_current_dto_id_fkey FOREIGN KEY (current_dto_id) REFERENCES files.file_upload_process_dtos(id);


--
-- Name: file_upload_process_dtos file_upload_process_dtos_file_upload_process_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process_dtos
    ADD CONSTRAINT file_upload_process_dtos_file_upload_process_id_fkey FOREIGN KEY (file_upload_process_id) REFERENCES files.file_upload_process(id);


--
-- Name: file_upload_process file_upload_process_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process
    ADD CONSTRAINT file_upload_process_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: file_upload_process_stats file_upload_process_stats_file_upload_process_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.file_upload_process_stats
    ADD CONSTRAINT file_upload_process_stats_file_upload_process_id_fkey FOREIGN KEY (file_upload_process_id) REFERENCES files.file_upload_process(id);


--
-- Name: ocr_meta ocr_meta_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.ocr_meta
    ADD CONSTRAINT ocr_meta_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: ocr_pages ocr_pages_meta_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.ocr_pages
    ADD CONSTRAINT ocr_pages_meta_id_fkey FOREIGN KEY (meta_id) REFERENCES files.ocr_meta(id);


--
-- Name: tags tags_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.tags
    ADD CONSTRAINT tags_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: vectorization vectorization_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.vectorization
    ADD CONSTRAINT vectorization_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: vectorization_status vectorization_status_file_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.vectorization_status
    ADD CONSTRAINT vectorization_status_file_id_fkey FOREIGN KEY (file_id) REFERENCES files.files(id);


--
-- Name: votes votes_summary_id_fkey; Type: FK CONSTRAINT; Schema: files; Owner: postgres
--

ALTER TABLE ONLY files.votes
    ADD CONSTRAINT votes_summary_id_fkey FOREIGN KEY (summary_id) REFERENCES files.file_summary(id);


--
-- Name: addresses addresses_company_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.addresses
    ADD CONSTRAINT addresses_company_id_fkey FOREIGN KEY (company_id) REFERENCES pycrm.companies(id);


--
-- Name: campaign_criteria fk_campaign_criteria_campaign_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_criteria
    ADD CONSTRAINT fk_campaign_criteria_campaign_id FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id) ON DELETE CASCADE;


--
-- Name: campaign_recipients fk_campaign_recipients_campaign_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT fk_campaign_recipients_campaign_id FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id) ON DELETE CASCADE;


--
-- Name: campaign_recipients fk_campaign_recipients_contact_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_recipients
    ADD CONSTRAINT fk_campaign_recipients_contact_id FOREIGN KEY (contact_id) REFERENCES pycrm.contacts(id);


--
-- Name: campaign_send_logs fk_campaign_send_logs_campaign_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.campaign_send_logs
    ADD CONSTRAINT fk_campaign_send_logs_campaign_id FOREIGN KEY (campaign_id) REFERENCES pycrm.campaigns(id) ON DELETE CASCADE;


--
-- Name: gmail_user_tokens fk_gmail_user_tokens_user_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.gmail_user_tokens
    ADD CONSTRAINT fk_gmail_user_tokens_user_id FOREIGN KEY (user_id) REFERENCES "user".users(id);


--
-- Name: spec_sheet_highlight_regions fk_highlight_regions_version; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_regions
    ADD CONSTRAINT fk_highlight_regions_version FOREIGN KEY (version_id) REFERENCES pycrm.spec_sheet_highlight_versions(id) ON DELETE CASCADE;


--
-- Name: spec_sheet_highlight_versions fk_highlight_versions_created_by; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT fk_highlight_versions_created_by FOREIGN KEY (created_by_id) REFERENCES "user".users(id) ON DELETE RESTRICT;


--
-- Name: spec_sheet_highlight_versions fk_highlight_versions_spec_sheet; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheet_highlight_versions
    ADD CONSTRAINT fk_highlight_versions_spec_sheet FOREIGN KEY (spec_sheet_id) REFERENCES pycrm.spec_sheets(id) ON DELETE CASCADE;


--
-- Name: note_conversations fk_note_conversations_note_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.note_conversations
    ADD CONSTRAINT fk_note_conversations_note_id FOREIGN KEY (note_id) REFERENCES pycrm.notes(id) ON DELETE CASCADE;


--
-- Name: o365_user_tokens fk_o365_user_tokens_user_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.o365_user_tokens
    ADD CONSTRAINT fk_o365_user_tokens_user_id FOREIGN KEY (user_id) REFERENCES "user".users(id) ON DELETE CASCADE;


--
-- Name: pre_opportunities fk_pre_opportunities_balance; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_balance FOREIGN KEY (balance_id) REFERENCES pycrm.pre_opportunity_balances(id);


--
-- Name: pre_opportunities fk_pre_opportunities_bill_to_customer; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_bill_to_customer FOREIGN KEY (bill_to_customer_id) REFERENCES core.customers(id);


--
-- Name: pre_opportunities fk_pre_opportunities_job; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_job FOREIGN KEY (job_id) REFERENCES pycrm.jobs(id);


--
-- Name: pre_opportunities fk_pre_opportunities_sold_to_customer; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunities
    ADD CONSTRAINT fk_pre_opportunities_sold_to_customer FOREIGN KEY (sold_to_customer_id) REFERENCES core.customers(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_end_user; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_end_user FOREIGN KEY (end_user_id) REFERENCES core.customers(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_pre_opportunity; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_pre_opportunity FOREIGN KEY (pre_opportunity_id) REFERENCES pycrm.pre_opportunities(id);


--
-- Name: pre_opportunity_details fk_pre_opportunity_details_product; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.pre_opportunity_details
    ADD CONSTRAINT fk_pre_opportunity_details_product FOREIGN KEY (product_id) REFERENCES core.products(id);


--
-- Name: spec_sheets fk_spec_sheets_created_by; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.spec_sheets
    ADD CONSTRAINT fk_spec_sheets_created_by FOREIGN KEY (created_by_id) REFERENCES "user".users(id) ON DELETE RESTRICT;


--
-- Name: task_conversations fk_task_conversations_task_id; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.task_conversations
    ADD CONSTRAINT fk_task_conversations_task_id FOREIGN KEY (task_id) REFERENCES pycrm.tasks(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_status_id_fkey; Type: FK CONSTRAINT; Schema: pycrm; Owner: postgres
--

ALTER TABLE ONLY pycrm.jobs
    ADD CONSTRAINT jobs_status_id_fkey FOREIGN KEY (status_id) REFERENCES pycrm.job_statuses(id);


--
-- Name: dashboards fk_dashboard_user; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".dashboards
    ADD CONSTRAINT fk_dashboard_user FOREIGN KEY (user_id) REFERENCES "user".users(id);


--
-- Name: followings fk_followings_task; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".followings
    ADD CONSTRAINT fk_followings_task FOREIGN KEY (task_id) REFERENCES "user".tasks(id);


--
-- Name: followings fk_followings_user; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".followings
    ADD CONSTRAINT fk_followings_user FOREIGN KEY (user_id) REFERENCES "user".users(id);


--
-- Name: message_entity fk_message_sender; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".message_entity
    ADD CONSTRAINT fk_message_sender FOREIGN KEY (sender_id) REFERENCES "user".users(id);


--
-- Name: message_entity fk_message_user; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".message_entity
    ADD CONSTRAINT fk_message_user FOREIGN KEY (user_id) REFERENCES "user".users(id);


--
-- Name: tasks fk_tasks_user; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".tasks
    ADD CONSTRAINT fk_tasks_user FOREIGN KEY (user_id) REFERENCES "user".users(id);


--
-- Name: users fk_user_role; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT fk_user_role FOREIGN KEY (role_id) REFERENCES "user".user_roles(id);


--
-- Name: user_settings fk_user_settings_setting_keys; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".user_settings
    ADD CONSTRAINT fk_user_settings_setting_keys FOREIGN KEY (setting_key_id) REFERENCES "user".setting_keys(id);


--
-- Name: users fk_users_created_by_on_users; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT fk_users_created_by_on_users FOREIGN KEY (created_by) REFERENCES "user".users(id);


--
-- Name: users fk_users_supervisor_id_on_users; Type: FK CONSTRAINT; Schema: user; Owner: postgres
--

ALTER TABLE ONLY "user".users
    ADD CONSTRAINT fk_users_supervisor_id_on_users FOREIGN KEY (supervisor_id) REFERENCES "user".users(id);


--
-- Name: aisles fk_aisle_section; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.aisles
    ADD CONSTRAINT fk_aisle_section FOREIGN KEY (section_id) REFERENCES warehouse.sections(id) ON DELETE SET NULL;


--
-- Name: aisles fk_aisle_warehouse; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.aisles
    ADD CONSTRAINT fk_aisle_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse.warehouse(id) ON DELETE CASCADE;


--
-- Name: bays fk_bay_shelf; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bays
    ADD CONSTRAINT fk_bay_shelf FOREIGN KEY (shelf_id) REFERENCES warehouse.shelves(id) ON DELETE CASCADE;


--
-- Name: bins fk_bin_row; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.bins
    ADD CONSTRAINT fk_bin_row FOREIGN KEY (row_id) REFERENCES warehouse.rows(id) ON DELETE CASCADE;


--
-- Name: fiducial_markers fk_fiducial_marker_shelf; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fiducial_markers
    ADD CONSTRAINT fk_fiducial_marker_shelf FOREIGN KEY (shelf_id) REFERENCES warehouse.shelves(id) ON DELETE CASCADE;


--
-- Name: fulfillments fk_fulfillment_inventory; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fulfillments
    ADD CONSTRAINT fk_fulfillment_inventory FOREIGN KEY (inventory_id) REFERENCES warehouse.inventory(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: fulfillments fk_fulfillment_wave; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.fulfillments
    ADD CONSTRAINT fk_fulfillment_wave FOREIGN KEY (wave_id) REFERENCES warehouse.waves(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: inventory_items fk_inventory_item_bin; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory_items
    ADD CONSTRAINT fk_inventory_item_bin FOREIGN KEY (bin_id) REFERENCES warehouse.bins(id) ON DELETE CASCADE;


--
-- Name: inventory_items fk_inventory_item_inventory; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.inventory_items
    ADD CONSTRAINT fk_inventory_item_inventory FOREIGN KEY (inventory_id) REFERENCES warehouse.inventory(id) ON DELETE CASCADE;


--
-- Name: rmas fk_rma_fulfillment; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rmas
    ADD CONSTRAINT fk_rma_fulfillment FOREIGN KEY (fulfillment_id) REFERENCES warehouse.fulfillments(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rows fk_row_bay; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.rows
    ADD CONSTRAINT fk_row_bay FOREIGN KEY (bay_id) REFERENCES warehouse.bays(id) ON DELETE CASCADE;


--
-- Name: sections fk_section_warehouse; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.sections
    ADD CONSTRAINT fk_section_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse.warehouse(id) ON DELETE CASCADE;


--
-- Name: shelves fk_shelf_aisle; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shelves
    ADD CONSTRAINT fk_shelf_aisle FOREIGN KEY (aisle_id) REFERENCES warehouse.aisles(id) ON DELETE SET NULL;


--
-- Name: shelves fk_shelf_section; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shelves
    ADD CONSTRAINT fk_shelf_section FOREIGN KEY (section_id) REFERENCES warehouse.sections(id) ON DELETE SET NULL;


--
-- Name: shelves fk_shelf_warehouse; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shelves
    ADD CONSTRAINT fk_shelf_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouse.warehouse(id) ON DELETE CASCADE;


--
-- Name: shipments fk_shipment_fulfillment; Type: FK CONSTRAINT; Schema: warehouse; Owner: postgres
--

ALTER TABLE ONLY warehouse.shipments
    ADD CONSTRAINT fk_shipment_fulfillment FOREIGN KEY (fulfillment_id) REFERENCES warehouse.fulfillments(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: FUNCTION pg_stat_statements_reset(userid oid, dbid oid, queryid bigint); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.pg_stat_statements_reset(userid oid, dbid oid, queryid bigint) TO PUBLIC;


--
-- Name: FUNCTION user_search(uname text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.user_search(uname text) TO cnpg_pooler_pgbouncer;


--
-- PostgreSQL database dump complete
--

\unrestrict IS8fTqbWAwPcFszYgpIbxczmX0MgBDPvrKTp9wOwmuiUHMrKNVa7S0X1BrlMmgq

