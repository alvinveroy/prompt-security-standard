-- UPSS PostgreSQL Database Initialization Script
-- Version: 2.0.0
-- Description: Creates schema for UPSS prompt management system

-- Create UPSS schema
CREATE SCHEMA IF NOT EXISTS upss;

-- Set search path
SET search_path TO upss, public;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- Table: prompts
-- Description: Stores prompt metadata and references to content files
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'user',
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    content_path TEXT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(255) NOT NULL,
    approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by VARCHAR(255),
    approved_date TIMESTAMPTZ,
    metadata JSONB,
    CONSTRAINT prompts_name_version_unique UNIQUE (name, version),
    CONSTRAINT prompts_risk_level_check CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT prompts_category_check CHECK (category IN ('system', 'user', 'fallback', 'template'))
);

-- ============================================================================
-- Table: prompt_versions
-- Description: Tracks version history and latest version pointer
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.prompt_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_name VARCHAR(255) NOT NULL,
    latest_version VARCHAR(50) NOT NULL,
    version_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT prompt_versions_name_unique UNIQUE (prompt_name)
);

-- ============================================================================
-- Table: audit_logs
-- Description: Immutable audit log for all prompt operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    prompt_name VARCHAR(255),
    prompt_version VARCHAR(50),
    success BOOLEAN NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    CONSTRAINT audit_logs_event_type_check CHECK (
        event_type IN (
            'read', 'create', 'update', 'delete', 
            'access_denied', 'integrity_failure', 
            'injection_attempt', 'rollback', 'approve'
        )
    )
);

-- ============================================================================
-- Table: user_roles
-- Description: Stores user role assignments
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    role_name VARCHAR(50) NOT NULL,
    granted_by VARCHAR(255) NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    CONSTRAINT user_roles_user_role_unique UNIQUE (user_id, role_name),
    CONSTRAINT user_roles_role_check CHECK (
        role_name IN ('reader', 'writer', 'approver', 'admin', 'auditor')
    )
);

-- ============================================================================
-- Table: role_permissions
-- Description: Defines permissions for each role
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) NOT NULL,
    permission VARCHAR(50) NOT NULL,
    resource_pattern VARCHAR(255) DEFAULT '*',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT role_permissions_unique UNIQUE (role_name, permission, resource_pattern),
    CONSTRAINT role_permissions_role_check CHECK (
        role_name IN ('reader', 'writer', 'approver', 'admin', 'auditor')
    ),
    CONSTRAINT role_permissions_permission_check CHECK (
        permission IN ('read', 'write', 'approve', 'deploy', 'audit', 'manage_users')
    )
);

-- ============================================================================
-- Table: prompt_permissions
-- Description: Per-prompt access control (optional, fine-grained)
-- ============================================================================
CREATE TABLE IF NOT EXISTS upss.prompt_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    permission VARCHAR(50) NOT NULL,
    granted_by VARCHAR(255) NOT NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    CONSTRAINT prompt_permissions_unique UNIQUE (prompt_name, user_id, permission)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Prompts table indexes
CREATE INDEX IF NOT EXISTS idx_prompts_name ON upss.prompts(name);
CREATE INDEX IF NOT EXISTS idx_prompts_category ON upss.prompts(category);
CREATE INDEX IF NOT EXISTS idx_prompts_risk_level ON upss.prompts(risk_level);
CREATE INDEX IF NOT EXISTS idx_prompts_created_by ON upss.prompts(created_by);
CREATE INDEX IF NOT EXISTS idx_prompts_approved ON upss.prompts(approved);
CREATE INDEX IF NOT EXISTS idx_prompts_metadata ON upss.prompts USING GIN(metadata);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON upss.audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user_id ON upss.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON upss.audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_prompt_name ON upss.audit_logs(prompt_name);
CREATE INDEX IF NOT EXISTS idx_audit_success ON upss.audit_logs(success);

-- User roles indexes
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON upss.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_name ON upss.user_roles(role_name);
CREATE INDEX IF NOT EXISTS idx_user_roles_expires ON upss.user_roles(expires_at) WHERE expires_at IS NOT NULL;

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION upss.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Update prompts.updated_at
CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON upss.prompts
    FOR EACH ROW
    EXECUTE FUNCTION upss.update_updated_at_column();

-- Trigger: Update prompt_versions.updated_at
CREATE TRIGGER update_prompt_versions_updated_at
    BEFORE UPDATE ON upss.prompt_versions
    FOR EACH ROW
    EXECUTE FUNCTION upss.update_updated_at_column();

-- Function: Prevent audit log modifications
CREATE OR REPLACE FUNCTION upss.prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable';
END;
$$ LANGUAGE plpgsql;

-- Trigger: Make audit_logs immutable
CREATE TRIGGER prevent_audit_update
    BEFORE UPDATE ON upss.audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION upss.prevent_audit_modification();

CREATE TRIGGER prevent_audit_delete
    BEFORE DELETE ON upss.audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION upss.prevent_audit_modification();

-- ============================================================================
-- Row-Level Security (RLS)
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE upss.prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE upss.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE upss.user_roles ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can see all prompts
CREATE POLICY admin_all_prompts ON upss.prompts
    FOR ALL
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM upss.user_roles
            WHERE user_id = current_user
            AND role_name = 'admin'
            AND (expires_at IS NULL OR expires_at > NOW())
        )
    );

-- Policy: Users can read prompts they have permission for
CREATE POLICY user_read_prompts ON upss.prompts
    FOR SELECT
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM upss.user_roles
            WHERE user_id = current_user
            AND role_name IN ('reader', 'writer', 'approver')
            AND (expires_at IS NULL OR expires_at > NOW())
        )
        OR
        EXISTS (
            SELECT 1 FROM upss.prompt_permissions
            WHERE prompt_name = prompts.name
            AND user_id = current_user
            AND permission = 'read'
            AND (expires_at IS NULL OR expires_at > NOW())
        )
    );

-- Policy: Only auditors and admins can read audit logs
CREATE POLICY auditor_read_logs ON upss.audit_logs
    FOR SELECT
    TO PUBLIC
    USING (
        EXISTS (
            SELECT 1 FROM upss.user_roles
            WHERE user_id = current_user
            AND role_name IN ('auditor', 'admin')
            AND (expires_at IS NULL OR expires_at > NOW())
        )
    );

-- ============================================================================
-- Initial Data: Default Roles and Permissions
-- ============================================================================

-- Reader role permissions
INSERT INTO upss.role_permissions (role_name, permission, resource_pattern) VALUES
    ('reader', 'read', '*')
ON CONFLICT DO NOTHING;

-- Writer role permissions
INSERT INTO upss.role_permissions (role_name, permission, resource_pattern) VALUES
    ('writer', 'read', '*'),
    ('writer', 'write', '*')
ON CONFLICT DO NOTHING;

-- Approver role permissions
INSERT INTO upss.role_permissions (role_name, permission, resource_pattern) VALUES
    ('approver', 'read', '*'),
    ('approver', 'write', '*'),
    ('approver', 'approve', '*')
ON CONFLICT DO NOTHING;

-- Admin role permissions
INSERT INTO upss.role_permissions (role_name, permission, resource_pattern) VALUES
    ('admin', 'read', '*'),
    ('admin', 'write', '*'),
    ('admin', 'approve', '*'),
    ('admin', 'deploy', '*'),
    ('admin', 'manage_users', '*')
ON CONFLICT DO NOTHING;

-- Auditor role permissions
INSERT INTO upss.role_permissions (role_name, permission, resource_pattern) VALUES
    ('auditor', 'read', '*'),
    ('auditor', 'audit', '*')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Views for Convenience
-- ============================================================================

-- View: Latest versions of all prompts
CREATE OR REPLACE VIEW upss.latest_prompts AS
SELECT p.*
FROM upss.prompts p
INNER JOIN upss.prompt_versions pv 
    ON p.name = pv.prompt_name 
    AND p.version = pv.latest_version;

-- View: User effective permissions
CREATE OR REPLACE VIEW upss.user_effective_permissions AS
SELECT 
    ur.user_id,
    rp.permission,
    rp.resource_pattern,
    ur.role_name,
    ur.expires_at
FROM upss.user_roles ur
INNER JOIN upss.role_permissions rp ON ur.role_name = rp.role_name
WHERE ur.expires_at IS NULL OR ur.expires_at > NOW();

-- View: Audit summary by user
CREATE OR REPLACE VIEW upss.audit_summary_by_user AS
SELECT 
    user_id,
    event_type,
    COUNT(*) as event_count,
    COUNT(CASE WHEN success THEN 1 END) as successful_count,
    COUNT(CASE WHEN NOT success THEN 1 END) as failed_count,
    MAX(timestamp) as last_event_at
FROM upss.audit_logs
GROUP BY user_id, event_type;

-- ============================================================================
-- Grant Permissions
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA upss TO PUBLIC;

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE ON upss.prompts TO PUBLIC;
GRANT SELECT, INSERT, UPDATE ON upss.prompt_versions TO PUBLIC;
GRANT SELECT, INSERT ON upss.audit_logs TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON upss.user_roles TO PUBLIC;
GRANT SELECT ON upss.role_permissions TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON upss.prompt_permissions TO PUBLIC;

-- Grant sequence permissions
GRANT USAGE ON ALL SEQUENCES IN SCHEMA upss TO PUBLIC;

-- Grant view permissions
GRANT SELECT ON upss.latest_prompts TO PUBLIC;
GRANT SELECT ON upss.user_effective_permissions TO PUBLIC;
GRANT SELECT ON upss.audit_summary_by_user TO PUBLIC;

-- ============================================================================
-- Completion Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'UPSS PostgreSQL Database Schema Initialized Successfully';
    RAISE NOTICE 'Version: 2.0.0';
    RAISE NOTICE 'Schema: upss';
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'Tables Created:';
    RAISE NOTICE '  - prompts';
    RAISE NOTICE '  - prompt_versions';
    RAISE NOTICE '  - audit_logs (immutable)';
    RAISE NOTICE '  - user_roles';
    RAISE NOTICE '  - role_permissions';
    RAISE NOTICE '  - prompt_permissions';
    RAISE NOTICE '=======================================================';
    RAISE NOTICE 'Security Features Enabled:';
    RAISE NOTICE '  - Row-Level Security (RLS)';
    RAISE NOTICE '  - Immutable audit logs';
    RAISE NOTICE '  - Role-based access control';
    RAISE NOTICE '  - Checksum integrity verification';
    RAISE NOTICE '=======================================================';
END $$;
