-- Migration: Create submittals tables
-- Description: Add tables for submittal workflow management

-- =============================================================================
-- Table: submittals
-- Main submittal entity
-- =============================================================================

CREATE TABLE IF NOT EXISTS pycrm.submittals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Submittal Identification
    submittal_number VARCHAR(50) NOT NULL,

    -- References
    quote_id UUID REFERENCES pycrm.quotes(id) ON DELETE SET NULL,
    job_id UUID REFERENCES pycrm.jobs(id) ON DELETE SET NULL,

    -- Status (0=DRAFT, 1=SUBMITTED, 2=APPROVED, 3=APPROVED_AS_NOTED, 4=REVISE_AND_RESUBMIT, 5=REJECTED)
    status SMALLINT NOT NULL DEFAULT 0,

    -- Transmittal Purpose (0=FOR_APPROVAL, 1=FOR_REVIEW, 2=FOR_INFORMATION, 3=FOR_RECORD, 4=RESUBMITTAL)
    transmittal_purpose SMALLINT,

    -- Description/Notes
    description TEXT,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID NOT NULL REFERENCES pyuser.users(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_submittals_quote_id ON pycrm.submittals(quote_id);
CREATE INDEX IF NOT EXISTS idx_submittals_job_id ON pycrm.submittals(job_id);
CREATE INDEX IF NOT EXISTS idx_submittals_status ON pycrm.submittals(status);
CREATE INDEX IF NOT EXISTS idx_submittals_submittal_number ON pycrm.submittals(submittal_number);
CREATE INDEX IF NOT EXISTS idx_submittals_created_at ON pycrm.submittals(created_at DESC);

COMMENT ON TABLE pycrm.submittals IS 'Main submittal entity for managing spec sheet packages for approval';

-- =============================================================================
-- Table: submittal_items
-- Individual items within a submittal
-- =============================================================================

CREATE TABLE IF NOT EXISTS pycrm.submittal_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Parent submittal
    submittal_id UUID NOT NULL REFERENCES pycrm.submittals(id) ON DELETE CASCADE,

    -- Item ordering
    item_number INTEGER NOT NULL,

    -- References
    quote_detail_id UUID REFERENCES pycrm.quote_details(id) ON DELETE SET NULL,
    spec_sheet_id UUID REFERENCES pycrm.spec_sheets(id) ON DELETE SET NULL,
    highlight_version_id UUID REFERENCES pycrm.spec_sheet_highlight_versions(id) ON DELETE SET NULL,

    -- Item details (can be copied from quote or entered manually)
    part_number VARCHAR(100),
    description TEXT,
    quantity DECIMAL(18, 6),

    -- Approval Status (0=PENDING, 1=APPROVED, 2=APPROVED_AS_NOTED, 3=REVISE, 4=REJECTED)
    approval_status SMALLINT NOT NULL DEFAULT 0,

    -- Match Status (0=NO_MATCH, 1=PARTIAL_MATCH, 2=EXACT_MATCH)
    match_status SMALLINT NOT NULL DEFAULT 0,

    -- Notes/Comments
    notes TEXT,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_submittal_items_submittal_id ON pycrm.submittal_items(submittal_id);
CREATE INDEX IF NOT EXISTS idx_submittal_items_spec_sheet_id ON pycrm.submittal_items(spec_sheet_id);
CREATE INDEX IF NOT EXISTS idx_submittal_items_quote_detail_id ON pycrm.submittal_items(quote_detail_id);

COMMENT ON TABLE pycrm.submittal_items IS 'Individual items within a submittal linking to spec sheets and quote details';

-- =============================================================================
-- Table: submittal_stakeholders
-- Stakeholders associated with a submittal
-- =============================================================================

CREATE TABLE IF NOT EXISTS pycrm.submittal_stakeholders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Parent submittal
    submittal_id UUID NOT NULL REFERENCES pycrm.submittals(id) ON DELETE CASCADE,

    -- Role (0=CUSTOMER, 1=ENGINEER, 2=ARCHITECT, 3=GENERAL_CONTRACTOR, 4=OTHER)
    role SMALLINT NOT NULL,

    -- Customer reference (optional)
    customer_id UUID REFERENCES pycore.customers(id) ON DELETE SET NULL,

    -- Is this the primary contact for this role?
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,

    -- Contact information (can be manual or from customer)
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    company_name VARCHAR(255)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_submittal_stakeholders_submittal_id ON pycrm.submittal_stakeholders(submittal_id);
CREATE INDEX IF NOT EXISTS idx_submittal_stakeholders_customer_id ON pycrm.submittal_stakeholders(customer_id);

COMMENT ON TABLE pycrm.submittal_stakeholders IS 'Stakeholders (customer, engineer, architect, GC) associated with a submittal';

-- =============================================================================
-- Table: submittal_revisions
-- PDF revisions of a submittal
-- =============================================================================

CREATE TABLE IF NOT EXISTS pycrm.submittal_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Parent submittal
    submittal_id UUID NOT NULL REFERENCES pycrm.submittals(id) ON DELETE CASCADE,

    -- Revision number (auto-incremented per submittal)
    revision_number INTEGER NOT NULL DEFAULT 0,

    -- Generated PDF file reference
    pdf_file_id UUID,
    pdf_file_url TEXT,
    pdf_file_name VARCHAR(255),

    -- Notes for this revision
    notes TEXT,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID NOT NULL REFERENCES pyuser.users(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_submittal_revisions_submittal_id ON pycrm.submittal_revisions(submittal_id);

COMMENT ON TABLE pycrm.submittal_revisions IS 'PDF revision history for a submittal';

-- =============================================================================
-- Table: submittal_emails
-- Email send history for submittals
-- =============================================================================

CREATE TABLE IF NOT EXISTS pycrm.submittal_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Parent submittal
    submittal_id UUID NOT NULL REFERENCES pycrm.submittals(id) ON DELETE CASCADE,

    -- Optional revision reference
    revision_id UUID REFERENCES pycrm.submittal_revisions(id) ON DELETE SET NULL,

    -- Email content
    subject VARCHAR(500) NOT NULL,
    body TEXT,

    -- Recipients stored as JSONB [{"email": "...", "name": "...", "type": "to|cc|bcc"}, ...]
    recipients JSONB,

    -- Simple array for quick lookup
    recipient_emails VARCHAR[],

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID NOT NULL REFERENCES pyuser.users(id) ON DELETE RESTRICT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_submittal_emails_submittal_id ON pycrm.submittal_emails(submittal_id);
CREATE INDEX IF NOT EXISTS idx_submittal_emails_revision_id ON pycrm.submittal_emails(revision_id);

COMMENT ON TABLE pycrm.submittal_emails IS 'Email send history for submittal transmittals';
