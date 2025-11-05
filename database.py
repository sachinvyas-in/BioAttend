"""
Database initialization and management for BioAttend system
"""

import sqlite3
import os
from datetime import datetime


def init_database():
    """Initialize the SQLite database with required tables"""
    
    # Create database connection
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            iris_template TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Present',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE(student_id, date)
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn


def add_student(name, roll_no, iris_template):
    """Add a new student to the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO students (name, roll_no, iris_template) VALUES (?, ?, ?)',
            (name, roll_no, iris_template)
        )
        student_id = cursor.lastrowid
        conn.commit()
        return student_id
    except sqlite3.IntegrityError:
        return None  # Student with this roll number already exists
    finally:
        conn.close()


def get_student_by_roll_no(roll_no):
    """Get student by roll number"""
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE roll_no = ?', (roll_no,)
    ).fetchone()
    conn.close()
    return student


def get_student_by_iris_template(iris_template):
    """Get student by iris template hash"""
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE iris_template = ?', (iris_template,)
    ).fetchone()
    conn.close()
    return student


def mark_attendance(student_id, date=None):
    """Mark attendance for a student"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO attendance (student_id, date) VALUES (?, ?)',
            (student_id, date)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Attendance already marked for today
    finally:
        conn.close()


def get_attendance_by_date(date):
    """Get attendance records for a specific date"""
    conn = get_db_connection()
    records = conn.execute('''
        SELECT s.name, s.roll_no, a.status, a.timestamp
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY s.roll_no
    ''', (date,)).fetchall()
    conn.close()
    return records


def get_student_attendance_history(student_id, limit=30):
    """Get attendance history for a specific student"""
    conn = get_db_connection()
    records = conn.execute('''
        SELECT date, status, timestamp
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (student_id, limit)).fetchall()
    conn.close()
    return records


def get_all_students():
    """Get all registered students"""
    conn = get_db_connection()
    students = conn.execute(
        'SELECT id, name, roll_no, created_at FROM students ORDER BY roll_no'
    ).fetchall()
    conn.close()
    return students


def get_student_by_id(student_id):
    """Get student by ID"""
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (student_id,)
    ).fetchone()
    conn.close()
    return student


def update_student(student_id, name=None, roll_no=None, iris_template=None):
    """Update student information"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get current student data
        current_student = get_student_by_id(student_id)
        if not current_student:
            return False, "Student not found"
        
        # Use existing values if new ones are not provided
        new_name = name if name is not None else current_student['name']
        new_roll_no = roll_no if roll_no is not None else current_student['roll_no']
        new_iris_template = iris_template if iris_template is not None else current_student['iris_template']
        
        cursor.execute(
            'UPDATE students SET name = ?, roll_no = ?, iris_template = ? WHERE id = ?',
            (new_name, new_roll_no, new_iris_template, student_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, "Student updated successfully"
        else:
            return False, "Student not found"
            
    except sqlite3.IntegrityError:
        return False, "Roll number already exists"
    finally:
        conn.close()


def delete_student(student_id):
    """Delete a student and their attendance records"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if student exists
        student = get_student_by_id(student_id)
        if not student:
            return False, "Student not found"
        
        # Delete attendance records first (due to foreign key constraint)
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        
        # Delete the student
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, f"Student {student['name']} and all attendance records deleted successfully"
        else:
            return False, "Failed to delete student"
            
    except Exception as e:
        return False, f"Error deleting student: {str(e)}"
    finally:
        conn.close()


def get_student_stats(student_id):
    """Get statistics for a specific student"""
    conn = get_db_connection()
    try:
        # Get total attendance count
        total_attendance = conn.execute(
            'SELECT COUNT(*) as count FROM attendance WHERE student_id = ?', 
            (student_id,)
        ).fetchone()['count']
        
        # Get first attendance date
        first_attendance = conn.execute('''
            SELECT MIN(date) as first_date FROM attendance WHERE student_id = ?
        ''', (student_id,)).fetchone()['first_date']
        
        # Get last attendance date
        last_attendance = conn.execute('''
            SELECT MAX(date) as last_date FROM attendance WHERE student_id = ?
        ''', (student_id,)).fetchone()['last_date']
        
        return {
            'total_attendance': total_attendance,
            'first_attendance': first_attendance,
            'last_attendance': last_attendance
        }
    except Exception:
        return {
            'total_attendance': 0,
            'first_attendance': None,
            'last_attendance': None
        }
    finally:
        conn.close()


if __name__ == '__main__':
    init_database()