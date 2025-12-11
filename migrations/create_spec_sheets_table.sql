-- Migration: Create spec_sheets table
-- Description: Add spec_sheets table for storing manufacturer specification sheets

CREATE TABLE IF NOT EXISTS spec_sheets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Information
    manufacturer_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,

    -- Upload Information
    upload_source VARCHAR(50) NOT NULL CHECK (upload_source IN ('url', 'file')),
    source_url TEXT,
    file_url TEXT NOT NULL,

    -- File Metadata
    file_size BIGINT NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 1,

    -- Categorization
    categories VARCHAR[] NOT NULL,
    tags VARCHAR[],
    folder_path VARCHAR(500),

    -- Status
    needs_review BOOLEAN NOT NULL DEFAULT FALSE,
    published BOOLEAN NOT NULL DEFAULT TRUE,

    -- Usage tracking
    usage_count INTEGER NOT NULL DEFAULT 0,
    highlight_count INTEGER NOT NULL DEFAULT 0,

    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT fk_created_by FOREIGN KEY (created_by_id) REFERENCES "user".users(id) ON DELETE RESTRICT
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_spec_sheets_manufacturer_id ON spec_sheets(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_spec_sheets_categories ON spec_sheets USING GIN(categories);
CREATE INDEX IF NOT EXISTS idx_spec_sheets_published ON spec_sheets(published);
CREATE INDEX IF NOT EXISTS idx_spec_sheets_created_at ON spec_sheets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_spec_sheets_display_name ON spec_sheets(display_name);
CREATE INDEX IF NOT EXISTS idx_spec_sheets_folder_path ON spec_sheets(folder_path);

-- Add comment to table
COMMENT ON TABLE spec_sheets IS 'Stores manufacturer specification sheets and cut sheets';
COMMENT ON COLUMN spec_sheets.manufacturer_id IS 'Reference to the factory/manufacturer';
COMMENT ON COLUMN spec_sheets.upload_source IS 'Source of upload: url or file';
COMMENT ON COLUMN spec_sheets.categories IS 'Array of category tags (indoor, outdoor, sports_lighting, etc.)';
COMMENT ON COLUMN spec_sheets.folder_path IS 'Path for folder organization within manufacturer (e.g., Indoor/Commercial/Linear)';
COMMENT ON COLUMN spec_sheets.usage_count IS 'Number of times this spec sheet has been used';
COMMENT ON COLUMN spec_sheets.highlight_count IS 'Number of highlights/annotations on this spec sheet';
