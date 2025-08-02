-- SMS Database Schema for Supabase
-- Generated from the new normalized ERD design

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types/enums
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'pending');
CREATE TYPE quiz_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE attempt_status AS ENUM ('in_progress', 'completed', 'expired');
CREATE TYPE enrollment_status AS ENUM ('active', 'inactive', 'completed', 'dropped');
CREATE TYPE guardian_status AS ENUM ('pending', 'accepted', 'rejected');

-- ==========================================
-- CORE USER AND ORGANIZATION TABLES
-- ==========================================

-- Users table (core user information)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255),
    supabase_user_id UUID UNIQUE,
    phone VARCHAR(20),
    avatar_url TEXT,
    status user_status DEFAULT 'active',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    website_url TEXT,
    logo_url TEXT,
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT organizations_name_check CHECK (LENGTH(name) >= 2)
);

-- User roles table (flexible role-based access control)
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    solo_teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT user_roles_role_check CHECK (role IN ('org_owner', 'org_admin', 'teacher', 'student', 'guardian', 'solo_teacher')),
    CONSTRAINT user_roles_context_check CHECK (
        (organization_id IS NOT NULL AND solo_teacher_id IS NULL) OR
        (organization_id IS NULL AND solo_teacher_id IS NOT NULL) OR
        (role IN ('student', 'guardian'))
    ),
    
    -- Unique constraints
    UNIQUE(user_id, role, organization_id),
    UNIQUE(user_id, role, solo_teacher_id)
);

-- Student profiles (additional student-specific information)
CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50),
    grade_level VARCHAR(20),
    date_of_birth DATE,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    medical_info TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id)
);

-- ==========================================
-- COURSES AND ENROLLMENT TABLES
-- ==========================================

-- Courses table
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    course_code VARCHAR(50),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    solo_teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(100),
    grade_level VARCHAR(20),
    max_students INTEGER,
    is_active BOOLEAN DEFAULT true,
    start_date DATE,
    end_date DATE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT courses_provider_check CHECK (
        (organization_id IS NOT NULL AND solo_teacher_id IS NULL) OR
        (organization_id IS NULL AND solo_teacher_id IS NOT NULL)
    ),
    CONSTRAINT courses_dates_check CHECK (end_date IS NULL OR start_date <= end_date)
);

-- Teacher-Course assignments (for organization teachers)
CREATE TABLE teacher_courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'teacher',
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CONSTRAINT teacher_courses_role_check CHECK (role IN ('teacher', 'assistant')),
    UNIQUE(teacher_id, course_id)
);

-- Organization admin course rights
CREATE TABLE org_admin_course_rights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    can_edit BOOLEAN DEFAULT true,
    can_delete BOOLEAN DEFAULT false,
    can_manage_students BOOLEAN DEFAULT true,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    UNIQUE(admin_id, course_id)
);

-- Student enrollments
CREATE TABLE student_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    status enrollment_status DEFAULT 'active',
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    enrolled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    completion_date TIMESTAMP WITH TIME ZONE,
    final_grade VARCHAR(10),
    notes TEXT,
    source VARCHAR(50) DEFAULT 'manual',
    
    -- Constraints
    UNIQUE(student_id, course_id)
);

-- ==========================================
-- QUIZ AND ASSESSMENT TABLES
-- ==========================================

-- Question bank
CREATE TABLE question_banks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB,
    correct_answer TEXT,
    explanation TEXT,
    difficulty_level VARCHAR(20),
    subject VARCHAR(100),
    tags TEXT[],
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    solo_teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT question_banks_type_check CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay')),
    CONSTRAINT question_banks_difficulty_check CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
    CONSTRAINT question_banks_provider_check CHECK (
        (organization_id IS NOT NULL AND solo_teacher_id IS NULL) OR
        (organization_id IS NULL AND solo_teacher_id IS NOT NULL)
    )
);

-- Quizzes
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    instructions TEXT,
    time_limit_minutes INTEGER,
    max_attempts INTEGER DEFAULT 1,
    passing_score DECIMAL(5,2),
    max_score DECIMAL(8,2) DEFAULT 100.00,
    status quiz_status DEFAULT 'draft',
    is_published BOOLEAN DEFAULT false,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT quizzes_score_check CHECK (passing_score <= max_score),
    CONSTRAINT quizzes_dates_check CHECK (end_date IS NULL OR start_date <= end_date)
);

-- Quiz questions
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_bank_id UUID REFERENCES question_banks(id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB,
    correct_answer TEXT,
    points DECIMAL(8,2) DEFAULT 1.00,
    order_number INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT quiz_questions_type_check CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay')),
    UNIQUE(quiz_id, order_number)
);

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attempt_number INTEGER NOT NULL,
    status attempt_status DEFAULT 'in_progress',
    score DECIMAL(8,2),
    max_possible_score DECIMAL(8,2),
    answers JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    time_taken_minutes INTEGER,
    
    -- Constraints
    UNIQUE(quiz_id, student_id, attempt_number)
);

-- ==========================================
-- GUARDIAN-CHILD RELATIONSHIPS
-- ==========================================

-- Guardian-child relationships
CREATE TABLE guardian_children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    guardian_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,
    status guardian_status DEFAULT 'pending',
    can_view_grades BOOLEAN DEFAULT true,
    can_view_attendance BOOLEAN DEFAULT true,
    can_receive_notifications BOOLEAN DEFAULT true,
    emergency_contact BOOLEAN DEFAULT false,
    notes TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT guardian_children_relationship_check CHECK (relationship IN ('parent', 'guardian', 'relative', 'other')),
    UNIQUE(guardian_id, student_id)
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_supabase_id ON users(supabase_user_id);

-- User roles indexes
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_organization ON user_roles(organization_id);
CREATE INDEX idx_user_roles_role ON user_roles(role);

-- Organizations indexes
CREATE INDEX idx_organizations_owner ON organizations(owner_user_id);
CREATE INDEX idx_organizations_active ON organizations(is_active);

-- Courses indexes
CREATE INDEX idx_courses_organization ON courses(organization_id);
CREATE INDEX idx_courses_solo_teacher ON courses(solo_teacher_id);
CREATE INDEX idx_courses_active ON courses(is_active);

-- Student enrollments indexes
CREATE INDEX idx_enrollments_student ON student_enrollments(student_id);
CREATE INDEX idx_enrollments_course ON student_enrollments(course_id);
CREATE INDEX idx_enrollments_status ON student_enrollments(status);

-- Quizzes indexes
CREATE INDEX idx_quizzes_course ON quizzes(course_id);
CREATE INDEX idx_quizzes_status ON quizzes(status);
CREATE INDEX idx_quizzes_published ON quizzes(is_published);

-- Quiz attempts indexes
CREATE INDEX idx_attempts_quiz ON quiz_attempts(quiz_id);
CREATE INDEX idx_attempts_student ON quiz_attempts(student_id);
CREATE INDEX idx_attempts_status ON quiz_attempts(status);

-- Guardian relationships indexes
CREATE INDEX idx_guardian_children_guardian ON guardian_children(guardian_id);
CREATE INDEX idx_guardian_children_student ON guardian_children(student_id);

-- ==========================================
-- FUNCTIONS FOR UPDATED_AT TIMESTAMPS
-- ==========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_profiles_updated_at BEFORE UPDATE ON student_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_question_banks_updated_at BEFORE UPDATE ON question_banks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quizzes_updated_at BEFORE UPDATE ON quizzes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_admin_course_rights ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_banks ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE guardian_children ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (customize based on your specific needs)

-- Users can read their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = supabase_user_id);

-- Users can update their own data
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = supabase_user_id);

-- Organization owners can manage their organization
CREATE POLICY "Organization owners can manage org" ON organizations
    FOR ALL USING (
        owner_user_id IN (
            SELECT u.id FROM users u WHERE u.supabase_user_id = auth.uid()
        )
    );

-- Students can view their enrollments
CREATE POLICY "Students can view own enrollments" ON student_enrollments
    FOR SELECT USING (
        student_id IN (
            SELECT u.id FROM users u WHERE u.supabase_user_id = auth.uid()
        )
    );

-- Teachers can view courses they teach
CREATE POLICY "Teachers can view assigned courses" ON courses
    FOR SELECT USING (
        id IN (
            SELECT tc.course_id FROM teacher_courses tc
            JOIN users u ON tc.teacher_id = u.id
            WHERE u.supabase_user_id = auth.uid()
        ) OR
        solo_teacher_id IN (
            SELECT u.id FROM users u WHERE u.supabase_user_id = auth.uid()
        )
    );

-- ==========================================
-- SAMPLE DATA (OPTIONAL)
-- ==========================================

-- Insert sample organization
INSERT INTO organizations (name, description, email) VALUES 
('Demo School', 'A sample educational institution', 'admin@demoschool.edu');

-- Note: Users will be created through Supabase Auth, then synced to this table
-- The sync will happen through your backend API when users sign up

COMMENT ON TABLE users IS 'Core user information for all user types';
COMMENT ON TABLE organizations IS 'Educational institutions and organizations';
COMMENT ON TABLE user_roles IS 'Flexible role-based access control system';
COMMENT ON TABLE courses IS 'Courses offered by organizations or solo teachers';
COMMENT ON TABLE student_enrollments IS 'Student course enrollment tracking';
COMMENT ON TABLE quizzes IS 'Assessments and quizzes for courses';
COMMENT ON TABLE guardian_children IS 'Parent/guardian relationships with students';
