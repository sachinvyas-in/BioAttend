# BioAttend: Biometric Smart Attendance System

## Overview

BioAttend is a simulated biometric attendance system designed as a college project that demonstrates iris-based student identification and attendance tracking. The system simulates real biometric hardware by using image hashing to create unique "iris templates" from uploaded images. Students enroll by uploading an iris image, and attendance is marked by uploading the same image for verification through hash matching.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5.1.3 for responsive design and components
- **Icons**: FontAwesome 6.0 for consistent iconography
- **JavaScript**: Vanilla JS for client-side interactions, form validation, and file upload handling
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Web Framework**: Flask (Python) serving as the main application server
- **Route Structure**: RESTful-style routes for enrollment, verification, reports, and student management
- **File Handling**: Secure file upload processing with size and format validation
- **Session Management**: Flask sessions with configurable secret key
- **Error Handling**: Custom 404 and 500 error pages

### Data Storage
- **Database**: SQLite for lightweight, serverless data storage
- **Schema Design**: 
  - `students` table: stores student information and hashed iris templates
  - `attendance` table: records attendance entries with date constraints
- **Data Relationships**: Foreign key relationship between students and attendance records
- **Template Storage**: SHA-256 hashed iris templates instead of raw biometric data for privacy

### Biometric Simulation
- **Hash-Based Templates**: Uses SHA-256 hashing of uploaded images to simulate iris feature extraction
- **Matching Algorithm**: Direct hash comparison for identity verification
- **Privacy Protection**: No raw images stored, only computed hash templates
- **File Validation**: PIL-based image format validation and processing

### Security Features
- **Input Validation**: File type, size, and format restrictions
- **SQL Injection Protection**: Parameterized queries throughout database operations
- **Template Sanitization**: Jinja2 auto-escaping for XSS prevention
- **File Upload Security**: Secure filename handling and upload directory isolation

## External Dependencies

### Python Packages
- **Flask**: Core web framework for routing, templating, and request handling
- **Werkzeug**: Secure filename utilities and development server
- **Pillow (PIL)**: Image processing and validation for uploaded iris images
- **hashlib**: SHA-256 hashing for biometric template generation (built-in)
- **sqlite3**: Database connectivity and operations (built-in)

### Frontend Libraries
- **Bootstrap 5.1.3**: CSS framework loaded via CDN for UI components and responsive grid
- **FontAwesome 6.0**: Icon library loaded via CDN for consistent visual elements

### System Dependencies
- **SQLite**: Embedded database engine for data persistence
- **File System**: Local uploads directory for temporary file processing
- **Environment Variables**: Optional SECRET_KEY configuration for production deployment

### Development Tools
- **Flask Development Server**: Built-in server for local development and testing
- **Browser-based Testing**: Standard web browser for user interface testing
- **Image Upload Testing**: Various image formats (PNG, JPG, JPEG, BMP, TIFF) for enrollment and verification testing