<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# School Management System Frontend - Copilot Instructions

This is a React/Next.js TypeScript frontend for a School Management System (SMS) that connects to a FastAPI backend.

## Project Context
- **Backend API**: Running on http://localhost:8000 (FastAPI with PostgreSQL)
- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, and App Router
- **Authentication**: JWT-based with role-based access (teacher, student, guardian)
- **Primary Features**: Login, dashboards, quiz management, student progress tracking

## Key Components to Build
1. **Authentication System**
   - Login page with role-based routing
   - JWT token management and API integration
   - Protected routes for different user types

2. **Teacher Dashboard**
   - Class management interface
   - Quiz creation and management
   - Student progress monitoring
   - Grade book functionality

3. **Student Interface**
   - Quiz taking experience with timer
   - Progress tracking and results
   - Class enrollment view
   - Profile management

4. **Guardian Portal**
   - Child progress monitoring
   - Communication with teachers
   - Academic reports and notifications

## API Integration Guidelines
- **Base URL**: http://localhost:8000
- **Authentication**: Bearer token in headers
- **Key Endpoints**:
  - POST /auth/login - User authentication
  - GET /teacher/classes - Teacher's classes
  - GET /student/quizzes - Available quizzes
  - POST /student/quiz-attempts - Submit quiz attempt
  - GET /guardian/students - Guardian's children

## Test Data Available
- **Teacher**: teacher@schoolsms.com (password: teacher123)
- **Students**: emma.smith@student.schoolsms.com, noah.jones@student.schoolsms.com (password: student123)
- **Guardians**: john.smith@email.com, mary.jones@email.com (password: guardian123)
- **Sample Classes**: Grade 5 English, Grade 5 Science
- **Sample Quizzes**: Reading Comprehension, Human Body Systems

## UI/UX Guidelines
- Use Tailwind CSS for styling with a modern, clean design
- Implement responsive design for mobile and desktop
- Use React Hook Form for form management
- Implement proper loading states and error handling
- Follow accessibility best practices

## Code Style Preferences
- Use TypeScript with strict mode
- Implement proper error boundaries
- Use React Query/SWR for API state management
- Follow Next.js 15 App Router conventions
- Implement proper SEO and meta tags

## Security Considerations
- Validate all user inputs
- Implement proper CORS handling
- Store JWT tokens securely
- Implement route protection based on user roles
- Add rate limiting for quiz submissions
