
-- Asana Simulation Database Schema
-- Designed for realistic B2B SaaS company with 5000-10000 employees

-- ============================================================================
-- CORE ORGANIZATIONAL ENTITIES
-- ============================================================================

CREATE TABLE organizations (
    org_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    is_organization BOOLEAN DEFAULT TRUE, -- TRUE for org, FALSE for workspace
    employee_count INTEGER,
    industry TEXT
);

CREATE TABLE teams (
    team_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    team_type TEXT CHECK(team_type IN ('product', 'engineering', 'marketing', 'sales', 'operations', 'design', 'data', 'hr', 'finance', 'legal')),
    created_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'member', 'guest', 'limited_access')),
    job_title TEXT,
    department TEXT,
    created_at TIMESTAMP NOT NULL,
    last_active_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    timezone TEXT DEFAULT 'America/Los_Angeles',
    FOREIGN KEY (org_id) REFERENCES organizations(org_id)
);

CREATE TABLE team_memberships (
    membership_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('member', 'admin')),
    joined_at TIMESTAMP NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(team_id, user_id)
);

-- ============================================================================
-- PROJECT MANAGEMENT ENTITIES
-- ============================================================================

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    team_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    project_type TEXT CHECK(project_type IN ('sprint', 'ongoing', 'campaign', 'bug_tracking', 'onboarding', 'planning')),
    status TEXT CHECK(status IN ('active', 'archived', 'on_hold', 'completed')),
    owner_id TEXT,
    created_at TIMESTAMP NOT NULL,
    due_date DATE,
    archived_at TIMESTAMP,
    color TEXT, -- Asana uses colors for projects
    is_template BOOLEAN DEFAULT FALSE,
    privacy_setting TEXT CHECK(privacy_setting IN ('public', 'private', 'team_visible')),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE project_members (
    project_member_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('member', 'editor', 'commenter', 'viewer')),
    added_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(project_id, user_id)
);

CREATE TABLE sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL, -- Order within project
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

-- ============================================================================
-- TASK ENTITIES
-- ============================================================================

CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT,
    section_id TEXT,
    parent_task_id TEXT, -- NULL for top-level tasks, set for subtasks
    name TEXT NOT NULL,
    description TEXT,
    assignee_id TEXT,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    completed_by TEXT,
    due_date DATE,
    start_date DATE,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    num_subtasks INTEGER DEFAULT 0,
    num_completed_subtasks INTEGER DEFAULT 0,
    num_likes INTEGER DEFAULT 0,
    num_comments INTEGER DEFAULT 0,
    is_milestone BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (assignee_id) REFERENCES users(user_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (completed_by) REFERENCES users(user_id)
);

CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

CREATE TABLE task_followers (
    follower_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    added_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(task_id, user_id)
);

-- ============================================================================
-- ACTIVITY & COLLABORATION
-- ============================================================================

CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    edited_at TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    parent_comment_id TEXT, -- For threaded replies
    num_likes INTEGER DEFAULT 0,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(comment_id)
);

CREATE TABLE stories (
    story_id TEXT PRIMARY KEY,
    task_id TEXT,
    project_id TEXT,
    user_id TEXT NOT NULL,
    action_type TEXT CHECK(action_type IN ('created', 'completed', 'assigned', 'due_date_changed', 'commented', 'attachment_added', 'custom_field_changed', 'moved', 'duplicated')),
    text TEXT,
    created_at TIMESTAMP NOT NULL,
    old_value TEXT,
    new_value TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE attachments (
    attachment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    file_type TEXT,
    file_size INTEGER, -- bytes
    url TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================================================
-- CUSTOM FIELDS & TAGS
-- ============================================================================

CREATE TABLE custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    field_type TEXT CHECK(field_type IN ('text', 'number', 'enum', 'multi_enum', 'date', 'people')),
    description TEXT,
    created_at TIMESTAMP NOT NULL,
    is_global BOOLEAN DEFAULT FALSE, -- Global custom fields vs project-specific
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE custom_field_enum_options (
    option_id TEXT PRIMARY KEY,
    field_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    position INTEGER,
    enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id)
);

CREATE TABLE custom_field_values (
    value_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    text_value TEXT,
    number_value REAL,
    date_value DATE,
    enum_option_id TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(field_id),
    FOREIGN KEY (enum_option_id) REFERENCES custom_field_enum_options(option_id),
    UNIQUE(task_id, field_id)
);

CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id),
    UNIQUE(org_id, name)
);

CREATE TABLE task_tags (
    task_tag_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    added_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id),
    UNIQUE(task_id, tag_id)
);

-- ============================================================================
-- DEPENDENCIES & RELATIONSHIPS
-- ============================================================================

CREATE TABLE task_dependencies (
    dependency_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL, -- The dependent task
    depends_on_task_id TEXT NOT NULL, -- The task it depends on
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(task_id),
    UNIQUE(task_id, depends_on_task_id)
);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

CREATE VIEW task_details AS
SELECT 
    t.task_id,
    t.name,
    t.description,
    t.completed,
    t.due_date,
    t.priority,
    t.created_at,
    p.name as project_name,
    s.name as section_name,
    u.name as assignee_name,
    creator.name as creator_name,
    parent.name as parent_task_name
FROM tasks t
LEFT JOIN projects p ON t.project_id = p.project_id
LEFT JOIN sections s ON t.section_id = s.section_id
LEFT JOIN users u ON t.assignee_id = u.user_id
LEFT JOIN users creator ON t.created_by = creator.user_id
LEFT JOIN tasks parent ON t.parent_task_id = parent.task_id;

CREATE VIEW user_workload AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(CASE WHEN t.completed = FALSE THEN 1 END) as active_tasks,
    COUNT(CASE WHEN t.completed = FALSE AND t.due_date < date('now') THEN 1 END) as overdue_tasks,
    COUNT(CASE WHEN t.completed = TRUE THEN 1 END) as completed_tasks
FROM users u
LEFT JOIN tasks t ON u.user_id = t.assignee_id
GROUP BY u.user_id, u.name, u.email;
